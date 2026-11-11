"""Tests for the Team Kuro ledger. Run: python -m unittest discover -s team/tools"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "kuro_ledger.py"
ENV = dict(os.environ, PYTHONUTF8="1", KURO_NOTIFY_CHANNELS="file")   # never pop real toasts in tests


def kl(root, *args, check=True):
    r = subprocess.run([sys.executable, str(TOOL), "--root", str(root), *args], capture_output=True, text=True,
                       env=ENV, encoding="utf-8", timeout=60)
    if check:
        assert r.returncode == 0, f"{args}: {r.stdout}{r.stderr}"
    return r


def tasks(root):
    return json.loads((Path(root) / ".kuro" / "tasks.json").read_text(encoding="utf-8"))["tasks"]


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        kl(self.root, "init", "--project", "Demo")

    def tearDown(self):
        self._tmp.cleanup()

    def add(self, tid, title, deps="", portable="yes", files="", **kw):
        args = ["add", "--id", tid, "--title", title, "--portable", portable]
        if deps:
            args += ["--deps", deps]
        if files:
            args += ["--files", files]
        for k, v in kw.items():
            args += [f"--{k}", v]
        return kl(self.root, *args, check=False)

    def test_init_creates_files(self):
        for name in ("tasks.json", "JOURNAL.md", "STATUS.md", "RESUME.md"):
            self.assertTrue((Path(self.root) / ".kuro" / name).exists(), name)
        self.assertTrue((Path(self.root) / ".kuro" / "handoff").is_dir())

    def test_dependencies_and_runnable(self):
        self.add("T-1", "schema")
        self.add("T-2", "api", deps="T-1")
        nxt = kl(self.root, "next").stdout
        self.assertIn("T-1", nxt)
        self.assertNotIn("T-2", nxt)
        kl(self.root, "set", "T-1", "done", "--note", "migrated")
        self.assertIn("T-2", kl(self.root, "next").stdout)

    def test_cannot_start_with_unmet_dependency(self):
        self.add("T-1", "schema")
        self.add("T-2", "api", deps="T-1")
        r = kl(self.root, "set", "T-2", "in_progress", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("depends on unfinished", r.stdout + r.stderr)

    def test_cycle_and_unknown_dependency_rejected(self):
        self.add("T-1", "a")
        self.assertNotEqual(self.add("T-2", "b", deps="T-9").returncode, 0)
        self.add("T-2", "b", deps="T-1")
        self.assertEqual(len(tasks(self.root)), 2)

    def test_status_and_resume_reflect_progress(self):
        self.add("T-1", "a")
        self.add("T-2", "b")
        kl(self.root, "set", "T-1", "done")
        status = (Path(self.root) / ".kuro" / "STATUS.md").read_text(encoding="utf-8")
        self.assertIn("1/2 tasks (50%)", status)
        resume = (Path(self.root) / ".kuro" / "RESUME.md").read_text(encoding="utf-8")
        self.assertIn("Start here in a fresh session of ANY agentic tool", resume)
        self.assertIn("T-1 -> done", resume)

    def test_handoff_packet_is_self_contained(self):
        self.add("T-1", "Add JWT login", files="src/auth.ts", acceptance="login returns 15 min token",
                 skills="secure-by-design-coding", size="M")
        out = kl(self.root, "handoff", "T-1").stdout
        packet = (Path(self.root) / ".kuro" / "handoff" / "T-1.md").read_text(encoding="utf-8")
        for needle in ("Add JWT login", "src/auth.ts", "login returns 15 min token", "House rules",
                       "never claim a pass you did not observe", "kuro/t-1"):
            self.assertIn(needle, packet)
        for tool, cmd in (("claude", "claude -p"), ("codex", "codex exec"), ("opencode", "opencode run"),
                          ("agy", "agy --mode accept-edits -p")):
            self.assertIn(f"{tool}: {cmd}", out)

    def test_handoff_all_runnable_only_portable_and_warns_on_shared_files(self):
        self.add("T-1", "a", files="x.py")
        self.add("T-2", "b", files="x.py,y.py")
        self.add("T-3", "needs agents", portable="no")
        out = kl(self.root, "handoff", "--all-runnable", "--tool", "claude").stdout
        self.assertIn("T-1.md", out)
        self.assertIn("T-2.md", out)
        self.assertNotIn("T-3.md", out)
        self.assertIn("WARNING: T-1 and T-2 both touch", out)

    def test_unmet_dependency_flagged_in_packet(self):
        self.add("T-1", "a")
        self.add("T-2", "b", deps="T-1")
        kl(self.root, "handoff", "T-2")
        packet = (Path(self.root) / ".kuro" / "handoff" / "T-2.md").read_text(encoding="utf-8")
        self.assertIn("UNMET: T-1", packet)

    def test_secrets_are_redacted_everywhere(self):
        kl(self.root, "log", "deploy used api_key=SUPERSECRETVALUE123 and Bearer abcdefghijklmnop1234")
        text = (Path(self.root) / ".kuro" / "JOURNAL.md").read_text(encoding="utf-8")
        self.assertNotIn("SUPERSECRETVALUE123", text)
        self.assertNotIn("abcdefghijklmnop1234", text)
        self.assertIn("[REDACTED]", text)

    def test_notify_rate_limit_and_urgent_bypass(self):
        env = dict(ENV, KURO_NOTIFY_CHANNELS="webhook")      # channel with no URL configured -> journal-only, no network
        def run(level):
            return subprocess.run([sys.executable, str(TOOL), "--root", self.root, "log", "x", "--level", level],
                                  capture_output=True, text=True, env=env, encoding="utf-8").stdout
        self.assertIn("journal-only", run("milestone"))
        self.assertIn("rate-limited", run("decision"))        # non-urgent inside the min interval
        self.assertIn("journal-only", run("blocker"))         # urgent is never rate limited
        self.assertIn("not-in-notify_on", run("info"))

    def test_concurrent_adds_keep_ledger_consistent(self):
        procs = [subprocess.Popen([sys.executable, str(TOOL), "--root", self.root, "add", "--id", f"C-{i}",
                                   "--title", f"task {i}"], env=ENV, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL) for i in range(8)]
        for p in procs:
            p.wait(timeout=60)
        ids = sorted(t["id"] for t in tasks(self.root))
        self.assertEqual(ids, sorted(f"C-{i}" for i in range(8)))

    def test_claim_is_exclusive_and_records_agent(self):
        self.add("T-1", "a")
        kl(self.root, "claim", "T-1", "--agent", "Kamdem")
        t = tasks(self.root)[0]
        self.assertEqual((t["status"], t["agent"]), ("in_progress", "Kamdem"))
        self.assertTrue(t["started"])
        r = kl(self.root, "claim", "T-1", "--agent", "Ondoua", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("already held by Kamdem", r.stdout + r.stderr)
        kl(self.root, "claim", "T-1", "--agent", "Kamdem")            # re-claim by the holder is fine

    def test_file_overlap_blocks_parallel_start(self):
        self.add("T-1", "a", files="x.py")
        self.add("T-2", "b", files="x.py,y.py")
        self.add("T-3", "c", files="z.py")
        batch = kl(self.root, "next", "--parallel").stdout
        self.assertIn("T-1", batch)
        self.assertIn("T-3", batch)
        self.assertNotIn("T-2", batch)
        kl(self.root, "claim", "T-1", "--agent", "Kamdem")
        r = kl(self.root, "claim", "T-2", "--agent", "Ondoua", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("shares files with in-progress T-1", r.stdout + r.stderr)
        r = kl(self.root, "set", "T-2", "in_progress", check=False)
        self.assertNotEqual(r.returncode, 0)
        kl(self.root, "claim", "T-3", "--agent", "Kouam")              # disjoint files: allowed in parallel
        kl(self.root, "set", "T-1", "done")
        kl(self.root, "claim", "T-2", "--agent", "Ondoua")             # free once T-1 is done

    def test_watch_board_shows_who_does_what(self):
        self.add("T-1", "build schema", files="x.py")
        self.add("T-2", "write docs")
        kl(self.root, "claim", "T-1", "--agent", "Kamdem")
        kl(self.root, "log", "step 2/5", "--level", "heartbeat", "--task", "T-1", "--agent", "Kamdem")
        out = kl(self.root, "watch", "--once").stdout
        for needle in ("0/2 done", "Kamdem", "T-1", "build schema", "step 2/5", "T-2", "JOURNAL"):
            self.assertIn(needle, out)
        status = (Path(self.root) / ".kuro" / "STATUS.md").read_text(encoding="utf-8")
        self.assertIn("Kamdem since", status)
        self.assertIn("Parallel batch", status)

    def test_requires_init(self):
        with tempfile.TemporaryDirectory() as empty:
            r = kl(empty, "next", check=False)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("run:", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
