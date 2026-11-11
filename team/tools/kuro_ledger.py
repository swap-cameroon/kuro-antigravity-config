#!/usr/bin/env python3
"""Team Kuro ledger: crash-proof task tracking, progress journal, notifications and cross-tool handoff.

State lives in the PROJECT, in <root>/.kuro/ (Git-trackable), so it survives a dead session, an exhausted
token quota or a switch to another agentic tool:

  tasks.json     machine-readable tasks (id, owner, status, deps, acceptance, files, portable, ...)
  JOURNAL.md     append-only, timestamped log of real events
  STATUS.md      human dashboard (progress, in progress, blocked, runnable now)
  RESUME.md      "start here" file for a fresh session of ANY tool
  handoff/T-n.md self-contained task packets for Claude Code, Codex, opencode or agy

Agents call this script instead of hand-editing JSON (atomic writes, locking, validation, redaction).
Pure standard library. Usage:  python kuro_ledger.py [--root DIR] <command> ...

Parallel work: `next --parallel` lists runnable tasks that share no file with each other or with work in
progress; each agent `claim`s its task (refused if someone else holds it or files overlap), sends
`log --level heartbeat --task <id>` while working, then `set <id> done`. `watch` is the user's live board.

Quality gates (team/config.json -> "quality", env KURO_QUALITY_GATES=off to disable):
  * a task cannot start without acceptance criteria (`add --acceptance`, or `edit <id> --acceptance`)
  * a task cannot be `done` without proof: `verify <id> --cmd "<test command>"` runs the command itself and
    records the real exit code, or `set <id> done --evidence "<what was checked by hand>"` for manual checks.
    The board says which tasks are verified (the ledger ran it) and which are only declared.

Commands: init | add | edit | claim | verify | set | log | status | next | watch | handoff | notify
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

TOOL_PATH = Path(__file__).resolve()
TEAM_DIR = TOOL_PATH.parent.parent
CONFIG_ROOT = TEAM_DIR.parent

STATUSES = ("todo", "in_progress", "blocked", "done")
LEVELS = ("info", "heartbeat", "decision", "milestone", "done", "blocker", "error", "quota")
URGENT = {"blocker", "error", "quota", "done"}
DEFAULT_REPORTER = {
    "enabled": True,
    "channels": ["file", "toast"],           # file = journal (always written); toast = local OS notification
    "notify_on": ["milestone", "done", "blocker", "error", "quota", "decision"],
    "min_interval_seconds": 120,             # non-urgent notifications are batched to this rate
    "ntfy_topic": "",                        # opt-in phone push via ntfy.sh (content leaves your machine)
    "webhook_url": "",                       # opt-in generic webhook (Slack/Discord/Teams-compatible JSON)
    "inline_skill_max_chars": 6000,
}

DEFAULT_QUALITY = {
    "require_acceptance": True,      # no task starts without acceptance criteria
    "require_evidence": True,        # no task is done without a passing `verify` or a declared manual check
    "verify_timeout_seconds": 900,
}

SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|secret|token|passwd|password|pwd|authorization)\b\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{12,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(-----END [A-Z ]*PRIVATE KEY-----|$)", re.S),
]


# ----------------------------------------------------------------------------- helpers
def redact(text: str) -> str:
    for p in SECRET_PATTERNS:
        text = p.sub("[REDACTED]", text)
    return text


def now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def stamp() -> str:
    return now().strftime("%Y-%m-%d %H:%M:%S")


def age(ts: str | None) -> str:
    """'3m12s' since a stamp() value; '-' when unknown."""
    try:
        sec = int((dt.datetime.now() - dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")).total_seconds())
    except (TypeError, ValueError):
        return "-"
    sec = max(sec, 0)
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m{sec % 60:02d}s"
    return f"{sec // 3600}h{sec % 3600 // 60:02d}m"


def model_tier(owner: str) -> str:
    """Advisory model class for a roster member ('' when unknown)."""
    try:
        roster = json.loads((TEAM_DIR / "roster.json").read_text(encoding="utf-8"))
        return next((m.get("model_tier", "") for m in roster.get("members", []) if m["name"] == owner), "")
    except Exception:
        return ""


def load_config() -> dict:
    cfg = dict(DEFAULT_REPORTER)
    try:
        data = json.loads((TEAM_DIR / "config.json").read_text(encoding="utf-8"))
        cfg.update(data.get("reporter", {}))
    except Exception:
        pass
    env = os.environ.get("KURO_NOTIFY_CHANNELS")
    if env is not None:
        cfg["channels"] = [c.strip() for c in env.split(",") if c.strip()]
    return cfg


def load_quality() -> dict:
    q = dict(DEFAULT_QUALITY)
    try:
        q.update(json.loads((TEAM_DIR / "config.json").read_text(encoding="utf-8")).get("quality", {}))
    except Exception:
        pass
    if os.environ.get("KURO_QUALITY_GATES", "").lower() in ("off", "0", "false", "no"):
        q["require_acceptance"] = q["require_evidence"] = False
    return q


def proof(t: dict) -> str:
    """How a done task was proven: 'verified' (the ledger ran the command), 'declared' or 'forced'."""
    ev = t.get("evidence") or {}
    if ev.get("kind") == "run" and ev.get("exit") == 0:
        return "verified"
    return "declared" if ev.get("kind") == "declared" else "forced" if ev.get("kind") == "forced" else ""


def atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


@contextlib.contextmanager
def locked(kdir: Path):
    lock = kdir / ".lock"
    deadline = time.time() + 15
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except FileExistsError:
            with contextlib.suppress(FileNotFoundError):
                if time.time() - lock.stat().st_mtime > 30:      # stale lock from a crashed process
                    lock.unlink()
                    continue
            if time.time() > deadline:
                raise SystemExit("ledger is busy (lock held >15s)")
            time.sleep(0.05)
    try:
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock.unlink()


class Ledger:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.dir = self.root / ".kuro"
        self.tasks_file = self.dir / "tasks.json"
        self.journal = self.dir / "JOURNAL.md"

    # ---- storage
    def exists(self) -> bool:
        return self.tasks_file.exists()

    def load(self) -> dict:
        if not self.exists():
            raise SystemExit(f"no ledger in {self.dir} - run: kuro_ledger.py --root {self.root} init")
        return json.loads(self.tasks_file.read_text(encoding="utf-8"))

    def save(self, data: dict) -> None:
        atomic_write(self.tasks_file, json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    # ---- queries
    @staticmethod
    def get(data: dict, tid: str) -> dict:
        for t in data["tasks"]:
            if t["id"] == tid:
                return t
        raise SystemExit(f"unknown task '{tid}'")

    @staticmethod
    def runnable(data: dict) -> list[dict]:
        done = {t["id"] for t in data["tasks"] if t["status"] == "done"}
        return [t for t in data["tasks"] if t["status"] == "todo" and all(d in done for d in t["deps"])]

    @staticmethod
    def file_conflicts(data: dict, t: dict) -> list[tuple[str, list[str]]]:
        """In-progress tasks (other than t) that touch one of t's files: [(task id, shared files)]."""
        mine = set(t.get("files", []))
        out = []
        for o in data["tasks"]:
            if o["id"] != t["id"] and o["status"] == "in_progress":
                both = sorted(mine & set(o.get("files", [])))
                if both:
                    out.append((o["id"], both))
        return out

    @classmethod
    def parallel_batch(cls, data: dict) -> list[dict]:
        """Runnable tasks that can start together: no shared file with each other or with work in progress."""
        taken: set[str] = set()
        for o in data["tasks"]:
            if o["status"] == "in_progress":
                taken |= set(o.get("files", []))
        batch = []
        for t in cls.runnable(data):
            files = set(t.get("files", []))
            if files & taken:
                continue
            taken |= files
            batch.append(t)
        return batch

    @staticmethod
    def has_cycle(tasks: list[dict]) -> bool:
        deps = {t["id"]: t["deps"] for t in tasks}
        state: dict[str, int] = {}

        def visit(n: str) -> bool:
            if state.get(n) == 1:
                return True
            if state.get(n) == 2:
                return False
            state[n] = 1
            if any(visit(d) for d in deps.get(n, []) if d in deps):
                return True
            state[n] = 2
            return False

        return any(visit(n) for n in deps)

    # ---- rendering
    def render(self, data: dict) -> None:
        tasks = data["tasks"]
        total = len(tasks)
        done = [t for t in tasks if t["status"] == "done"]
        pct = int(100 * len(done) / total) if total else 0
        bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
        by = lambda s: [t for t in tasks if t["status"] == s]  # noqa: E731
        run = self.runnable(data)
        run_ids = {t["id"] for t in run}
        waiting = [t for t in by("todo") if t["id"] not in run_ids]

        def row(t: dict, extra: str = "") -> str:
            port = "yes" if t.get("portable") else "no"
            if t["status"] == "in_progress":
                extra = extra or (f"{t.get('agent', '?')} since {t.get('started', '?')}"
                                  + (f"; {t['note']}" if t.get("note") else ""))
            elif t["status"] == "done" and proof(t):
                extra = extra or f"[{proof(t)}] {t.get('note', '')}".strip()
            return (f"| {t['id']} | {t['title']} | {t.get('owner', '-')} | {t.get('size', '-')} | {port} | "
                    f"{', '.join(t['deps']) or '-'} | {extra or t.get('note', '')} |")

        head = "| ID | Task | Owner | Size | Portable | Depends on | Note |\n| :-- | :-- | :-- | :-- | :-- | :-- | :-- |"
        out = [f"# STATUS - {data.get('project', 'project')}", "",
               f"_Updated {stamp()} by kuro_ledger. Source of truth: `.kuro/tasks.json`._", "",
               f"**Progress: {len(done)}/{total} tasks ({pct}%)**  `[{bar}]`", ""]
        for title, items in (("In progress", by("in_progress")), ("Blocked", by("blocked")),
                             ("Runnable now (dependencies satisfied)", run),
                             ("Waiting on dependencies", waiting)):
            out += [f"## {title} ({len(items)})", ""]
            out += [head] + [row(t) for t in items] if items else ["_none_"]
            out.append("")
        out += [f"## Done ({len(done)})", ""]
        out += ([head] + [row(t) for t in done[-15:]]) if done else ["_none_"]
        launch = [t for t in run if t.get("portable")]
        batch = self.parallel_batch(data)
        out += ["", "## Parallel batch", "",
                "Can start together now (no shared files): " + (", ".join(t["id"] for t in batch) or "none") + ".",
                f"Live board: `python \"{TOOL_PATH}\" --root \"{self.root}\" watch`",
                "", "## Launch elsewhere", "",
                "Portable and runnable now: " + (", ".join(t["id"] for t in launch) or "none") + ".",
                f"Generate packets: `python \"{TOOL_PATH}\" --root \"{self.root}\" handoff --all-runnable`",
                "Packets land in `.kuro/handoff/`; each lists launch commands for Claude Code, Codex, opencode and agy.", ""]
        atomic_write(self.dir / "STATUS.md", "\n".join(out))
        self.render_resume(data, pct)

    def render_resume(self, data: dict, pct: int) -> None:
        tail = []
        if self.journal.exists():
            tail = self.journal.read_text(encoding="utf-8").splitlines()[-15:]
        text = [f"# RESUME - {data.get('project', 'project')}", "",
                "Start here in a fresh session of ANY agentic tool (Antigravity, Claude Code, Codex, opencode).", "",
                "1. Read `.kuro/STATUS.md` (what is done, blocked, runnable) and `PROJECT_STATE.md` if present.",
                "2. Pick a runnable task (dependencies done). Read its packet in `.kuro/handoff/<id>.md` "
                f"(create with `python \"{TOOL_PATH}\" --root \"{self.root}\" handoff <id>`).",
                f"3. Take it with `python \"{TOOL_PATH}\" --root \"{self.root}\" claim <id> --agent <you>`, "
                "then `set <id> done|blocked --note \"...\"`.",
                "4. Do not redo `done` tasks. Verify claims by running tests, not by trusting notes.", "",
                f"Overall progress: {pct}%.", "", "## Last journal entries", ""] + (tail or ["_empty_"])
        atomic_write(self.dir / "RESUME.md", "\n".join(text) + "\n")

    def append_journal(self, level: str, agent: str, message: str) -> None:
        with open(self.journal, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(f"- [{stamp()}] **{level}** ({agent}) {redact(message)}\n")


# ----------------------------------------------------------------------------- notifications
def toast(title: str, msg: str) -> None:
    try:
        if sys.platform.startswith("win"):
            ps = ("Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing;"
                  "$n=New-Object System.Windows.Forms.NotifyIcon;$n.Icon=[System.Drawing.SystemIcons]::Information;"
                  "$n.Visible=$true;$n.ShowBalloonTip(8000,$env:KURO_T,$env:KURO_M,'Info');Start-Sleep -Seconds 9;$n.Dispose()")
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                             env=dict(os.environ, KURO_T=title, KURO_M=msg), stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, creationflags=0x08000000)
        elif sys.platform == "darwin":
            subprocess.Popen(["osascript", "-e", "on run argv\ndisplay notification (item 2 of argv) with title (item 1 of argv)\nend run",
                              title, msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["notify-send", title, msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def post(url: str, body: bytes, headers: dict) -> None:
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        urllib.request.urlopen(req, timeout=8).read()
    except Exception:
        pass


def notify(led: Ledger, level: str, message: str, title: str = "Team Kuro", force: bool = False) -> str:
    """Send a notification on configured channels. Returns a short outcome string. Never raises."""
    cfg = load_config()
    if not cfg.get("enabled", True):
        return "disabled"
    if not force and level not in cfg.get("notify_on", []):
        return "not-in-notify_on"
    state_file = led.dir / ".notify_state.json"
    try:
        last = json.loads(state_file.read_text(encoding="utf-8")).get("last", 0)
    except Exception:
        last = 0
    if not force and level not in URGENT and time.time() - last < cfg.get("min_interval_seconds", 120):
        return "rate-limited"
    msg = redact(message)[:240]
    sent = []
    channels = cfg.get("channels", [])
    if "toast" in channels:
        toast(title, msg)
        sent.append("toast")
    if "ntfy" in channels and cfg.get("ntfy_topic"):
        post(f"https://ntfy.sh/{cfg['ntfy_topic']}", msg.encode("utf-8"),
             {"Title": title.encode("ascii", "ignore").decode() or "Team Kuro", "Tags": level})
        sent.append("ntfy")
    if "webhook" in channels and cfg.get("webhook_url"):
        post(cfg["webhook_url"], json.dumps({"text": f"[{title}] {level}: {msg}"}).encode("utf-8"),
             {"Content-Type": "application/json"})
        sent.append("webhook")
    with contextlib.suppress(Exception):
        atomic_write(state_file, json.dumps({"last": time.time()}))
    return "sent:" + ",".join(sent) if sent else "journal-only"


# ----------------------------------------------------------------------------- handoff
HOUSE_RULES = [
    "Make the smallest change that satisfies the acceptance criteria; do not touch files outside the listed scope.",
    "Run the relevant tests/linters/build and report their real results; never claim a pass you did not observe.",
    "No secrets in code, logs or commits; use env vars and placeholders.",
    "Conventional Commits, one logical change per commit, on the branch named below. No force-push.",
    "If blocked or the spec is ambiguous, stop and write the question in `.kuro/handoff/<id>.result.md` instead of guessing.",
]

LAUNCH = {
    "claude": 'claude -p "{p}"',
    "codex": 'codex exec "{p}"',
    "opencode": 'opencode run "{p}"',
    "agy": 'agy --mode accept-edits -p "{p}"',
}


def read_skill(name: str, limit: int) -> str:
    for base in (CONFIG_ROOT / "skills", Path.home() / ".gemini" / "config" / "skills"):
        f = base / name / "SKILL.md"
        if f.is_file():
            body = f.read_text(encoding="utf-8", errors="replace")
            body = re.sub(r"\A---.*?\n---\s*\n", "", body, flags=re.S)
            return body[:limit] + ("\n\n[...truncated...]" if len(body) > limit else "")
    return ""


def build_packet(led: Ledger, data: dict, t: dict, inline_skills: bool) -> str:
    cfg = load_config()
    done = {x["id"] for x in data["tasks"] if x["status"] == "done"}
    unmet = [d for d in t["deps"] if d not in done]
    branch = t.get("branch") or f"kuro/{t['id'].lower()}"
    rel = f".kuro/handoff/{t['id']}.md"
    lines = [f"# Handoff {t['id']}: {t['title']}", "",
             f"- Project: {data.get('project', '')}   Owner role: {t.get('owner', '-')}   Size: {t.get('size', '-')}"
             + (f"   Suggested model class: {model_tier(t.get('owner', ''))}" if model_tier(t.get("owner", "")) else ""),
             f"- Suggested branch: `{branch}`",
             f"- Dependencies: {', '.join(t['deps']) or 'none'}"
             + (f"  **UNMET: {', '.join(unmet)} (do not start before they are done)**" if unmet else "  (all done)"),
             "", "## Goal", "", t["title"] + (f"\n\n{t['note']}" if t.get("note") else ""), "",
             "## Read first", ""]
    ctx = t.get("files", [])
    lines += [f"- `{f}`" for f in ctx] or ["- (no files listed: start from `.kuro/STATUS.md`, `PROJECT_STATE.md`, PRD/ARCHITECTURE if present)"]
    lines += ["", "## Acceptance criteria", "", t.get("acceptance") or "_not specified: ask before assuming_", "",
              "## House rules", ""] + [f"- {r}" for r in HOUSE_RULES]
    if t.get("skills"):
        lines += ["", "## Relevant playbooks", "",
                  "These Team Kuro skills apply (SKILL.md paths in `~/.gemini/config/skills/<name>/` or the config repo): "
                  + ", ".join(f"`{s}`" for s in t["skills"]) + "."]
        if inline_skills:
            for s in t["skills"]:
                body = read_skill(s, int(cfg.get("inline_skill_max_chars", 6000)))
                if body:
                    lines += ["", f"### Playbook: {s}", "", body]
    if (led.root / "CONVENTIONS.md").is_file():
        lines.insert(lines.index("## Read first") + 2, "- `CONVENTIONS.md` (project rules: they override generic advice)")
    check = t.get("verify") or "<test/build command>"
    lines += ["", "## When finished", "",
              f"1. Prove it: `python \"{TOOL_PATH}\" --root \"{led.root}\" verify {t['id']} --cmd \"{check}\"` "
              "(the ledger runs the command and records the real exit code).",
              f"2. Record it: `python \"{TOOL_PATH}\" --root \"{led.root}\" set {t['id']} done --note \"<one line>\"` "
              f"(refused without a passing verify; for a check done by hand add `--evidence \"<what you checked>\"`; "
              f"write `.kuro/handoff/{t['id']}.result.md` if the command is unavailable).", "",
              "## Launch (from the project root; check `<tool> --help` for your permission/model flags)", ""]
    prompt = f"Read {rel} and execute that task completely, following its rules."
    for tool, tpl in LAUNCH.items():
        lines.append(f"- {tool}: `{tpl.format(p=prompt)}`")
    if t.get("needs"):
        lines += ["", f"_Needs: {', '.join(t['needs'])}. Prefer a tool that provides it._"]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- commands
def cmd_init(a, led: Ledger):
    led.dir.mkdir(parents=True, exist_ok=True)
    (led.dir / "handoff").mkdir(exist_ok=True)
    with locked(led.dir):
        if not led.exists():
            led.save({"project": a.project or led.root.name, "created": stamp(), "tasks": []})
            led.append_journal("info", "ledger", f"ledger initialised for {a.project or led.root.name}")
        led.render(led.load())
    print(f"ledger ready: {led.dir}")


def cmd_add(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        if any(t["id"] == a.id for t in data["tasks"]):
            raise SystemExit(f"task {a.id} already exists")
        deps = [d for d in (a.deps or "").split(",") if d]
        for d in deps:
            led.get(data, d)
        task = {"id": a.id, "title": a.title, "owner": a.owner or "-", "status": "todo", "deps": deps,
                "acceptance": a.acceptance or "", "files": [f for f in (a.files or "").split(",") if f],
                "size": a.size, "portable": a.portable == "yes",
                "needs": [n for n in (a.needs or "").split(",") if n], "verify": a.verify or "",
                "skills": [s for s in (a.skills or "").split(",") if s], "note": a.note or "",
                "created": stamp(), "updated": stamp()}
        if led.has_cycle(data["tasks"] + [task]):
            raise SystemExit("dependency cycle rejected")
        data["tasks"].append(task)
        led.save(data)
        led.append_journal("info", a.agent, f"task added {a.id}: {a.title}")
        led.render(data)
    print(f"added {a.id}")


def start_task(led: Ledger, data: dict, t: dict, agent: str, force: bool) -> None:
    """Shared by `claim` and `set in_progress`: dependencies done, no file shared with running work."""
    pending = [d for d in t["deps"] if led.get(data, d)["status"] != "done"]
    if pending and not force:
        raise SystemExit(f"{t['id']} depends on unfinished {pending} (use --force to override)")
    if load_quality()["require_acceptance"] and not (t.get("acceptance") or "").strip() and not force:
        raise SystemExit(f"{t['id']} has no acceptance criteria: nobody can tell when it is done. Add them with "
                         f"`edit {t['id']} --acceptance \"...\"` (use --force to override)")
    clash = led.file_conflicts(data, t)
    if clash and not force:
        detail = "; ".join(f"{i} ({', '.join(f)})" for i, f in clash)
        raise SystemExit(f"{t['id']} shares files with in-progress {detail}: run them one after the other "
                         "(use --force to override)")
    t["status"], t["agent"] = "in_progress", agent
    t["started"] = t["heartbeat"] = t["updated"] = stamp()
    for stale in ("finished", "progress", "evidence"):      # proof from an earlier attempt does not carry over
        t.pop(stale, None)


def cmd_edit(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        t = led.get(data, a.id)
        changed = []
        for field in ("title", "owner", "acceptance", "verify", "note"):
            v = getattr(a, field)
            if v is not None:
                t[field] = redact(v)
                changed.append(field)
        if a.files is not None:
            t["files"] = [f for f in a.files.split(",") if f]
            changed.append("files")
        if not changed:
            raise SystemExit("nothing to change")
        t["updated"] = stamp()
        led.save(data)
        led.append_journal("info", a.agent, f"{a.id} edited: {', '.join(changed)}")
        led.render(data)
    print(f"{a.id} updated ({', '.join(changed)})")


def cmd_verify(a, led: Ledger):
    """Run the task's check command ourselves and record what really happened."""
    data = led.load()
    t = led.get(data, a.id)
    cmd = a.cmd or t.get("verify")
    if not cmd:
        raise SystemExit(f"{a.id} has no check command: pass --cmd \"<test/build command>\"")
    timeout = int(load_quality().get("verify_timeout_seconds", 900))
    started = time.time()
    try:
        r = subprocess.run(cmd, shell=True, cwd=led.root, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        code, output = r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired as e:
        code, output = 124, f"timed out after {timeout}s\n" + str(e.stdout or "")
    tail = redact("\n".join(output.strip().splitlines()[-12:]))[-800:]
    took = int(time.time() - started)
    with locked(led.dir):
        data = led.load()
        t = led.get(data, a.id)
        t["evidence"] = {"kind": "run", "cmd": redact(cmd), "exit": code, "when": stamp(), "seconds": took, "tail": tail}
        if a.cmd and not t.get("verify"):
            t["verify"] = redact(a.cmd)
        t["heartbeat"] = t["updated"] = stamp()
        led.save(data)
        led.append_journal("info" if code == 0 else "error", a.agent,
                           f"{a.id} verify {'PASSED' if code == 0 else f'FAILED (exit {code})'} in {took}s: `{cmd}`")
        led.render(data)
    print(tail)
    print(f"\n{a.id} verify {'PASSED' if code == 0 else f'FAILED (exit {code})'} in {took}s")
    if code != 0:
        notify(led, "error", f"{a.id} verification failed: {t['title']}")
        raise SystemExit(1)


def cmd_claim(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        t = led.get(data, a.id)
        if t["status"] == "in_progress" and t.get("agent") != a.agent and not a.force:
            raise SystemExit(f"{a.id} is already held by {t.get('agent', '?')} since {t.get('started', '?')}")
        if t["status"] == "done" and not a.force:
            raise SystemExit(f"{a.id} is already done")
        start_task(led, data, t, a.agent, a.force)
        if a.note:
            t["note"] = redact(a.note)
        led.save(data)
        led.append_journal("info", a.agent, f"{a.id} claimed: {t['title']}" + (f" ({a.note})" if a.note else ""))
        led.render(data)
    print(f"{a.id} claimed by {a.agent}")


def cmd_set(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        t = led.get(data, a.id)
        if a.status == "in_progress":
            start_task(led, data, t, a.agent, a.force)
        elif a.status == "done":
            pending = [d for d in t["deps"] if led.get(data, d)["status"] != "done"]
            if pending and not a.force:
                raise SystemExit(f"{a.id} depends on unfinished {pending} (use --force to override)")
            if a.evidence:
                t["evidence"] = {"kind": "declared", "text": redact(a.evidence), "when": stamp()}
            if load_quality()["require_evidence"] and proof(t) not in ("verified", "declared"):
                if not a.force:
                    ev = t.get("evidence") or {}
                    why = (f"its last verify FAILED (exit {ev.get('exit')})" if ev.get("kind") == "run"
                           else "nothing proves it works")
                    raise SystemExit(f"{a.id} cannot be done: {why}. Run `verify {a.id} --cmd \"<test command>\"`, "
                                     f"or pass --evidence \"<what was checked by hand>\" (use --force to override)")
                t["evidence"] = {"kind": "forced", "when": stamp()}
            t["finished"] = stamp()
        t["status"], t["updated"] = a.status, stamp()
        if a.note:
            t["note"] = redact(a.note)
        if a.commit:
            t["commit"] = a.commit
        led.save(data)
        level = {"done": "done", "blocked": "blocker"}.get(a.status, "info")
        tag = f" [{proof(t)}]" if a.status == "done" and proof(t) else ""
        led.append_journal(level, a.agent, f"{a.id} -> {a.status}{tag}" + (f": {a.note}" if a.note else ""))
        led.render(data)
    out = notify(led, level, f"{a.id} {a.status}: {t['title']}") if level != "info" else "-"
    print(f"{a.id} -> {a.status} (notify: {out})")


def cmd_log(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        if a.task:
            t = led.get(data, a.task)
            t["heartbeat"] = stamp()
            if a.level == "heartbeat":
                t["progress"] = redact(a.message)[:120]
            led.save(data)
        led.append_journal(a.level, a.agent, (f"{a.task}: " if a.task else "") + a.message)
        led.render(data)
    out = notify(led, a.level, a.message, force=a.notify)
    print(f"logged (notify: {out})")


def cmd_status(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        led.render(data)
    print((led.dir / "STATUS.md").read_text(encoding="utf-8"))


def cmd_next(a, led: Ledger):
    data = led.load()
    for t in (led.parallel_batch(data) if a.parallel else led.runnable(data)):
        tier = model_tier(t.get("owner", ""))
        print(f"{t['id']}\t{t.get('owner', '-')}" + (f" ({tier})" if tier else "")
              + f"\tportable={'yes' if t.get('portable') else 'no'}\t{t['title']}")


def board(led: Ledger, width: int = 100, journal_lines: int = 8) -> str:
    """One screen for the user: who is doing what right now, what is stuck, what comes next."""
    data = led.load()
    tasks = data["tasks"]
    done = [t for t in tasks if t["status"] == "done"]
    pct = int(100 * len(done) / len(tasks)) if tasks else 0
    bar = "#" * (pct * 30 // 100) + "-" * (30 - pct * 30 // 100)

    def cut(x: str) -> str:
        return x if len(x) <= width else x[:width - 1] + "~"

    out = [f"TEAM KURO - {data.get('project', 'project')}   {stamp()}",
           f"[{bar}] {len(done)}/{len(tasks)} done ({pct}%)", "",
           "NOW (agent | task | running for | last sign of life)"]
    running = [t for t in tasks if t["status"] == "in_progress"]
    for t in running:
        out.append(cut(f"  > {t.get('agent', '?'):<9} {t['id']:<7} {t['title'][:40]:<40} {age(t.get('started')):>8}   "
                       f"{age(t.get('heartbeat'))} ago" + (f"  {t['progress']}" if t.get("progress") else "")))
    if not running:
        out.append("  (nobody is working)")
    blocked = [t for t in tasks if t["status"] == "blocked"]
    if blocked:
        out += ["", "BLOCKED"] + [cut(f"  ! {t['id']:<7} {t['title'][:40]:<40} {t.get('note', '')}") for t in blocked]
    batch = {t["id"] for t in led.parallel_batch(data)}
    run = led.runnable(data)
    if run:
        out += ["", "NEXT (* = can start in parallel right now)"]
        out += [cut(f"  {'*' if t['id'] in batch else ' '} {t['id']:<7} {t.get('owner', '-'):<9} {t['title']}")
                for t in run[:8]]
    if done:
        out += ["", "LAST DONE"] + [cut(f"  v {t['id']:<7} {t.get('agent') or t.get('owner', '-'):<9} "
                                        f"{proof(t) or 'unproven':<9} {t['title']}") for t in done[-3:]]
    if led.journal.exists() and journal_lines > 0:
        tail = led.journal.read_text(encoding="utf-8").splitlines()[-journal_lines:]
        out += ["", "JOURNAL"] + [cut("  " + line[2:].replace("**", "")) for line in tail]
    return "\n".join(out)


def cmd_watch(a, led: Ledger):
    """Live board in a second terminal. Read-only: never takes the lock, so it cannot slow the agents down."""
    if not led.exists():
        raise SystemExit(f"no ledger in {led.dir} - run: kuro_ledger.py --root {led.root} init")
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 120
    while True:
        try:
            text = board(led, width, a.journal)
        except (json.JSONDecodeError, OSError):
            text = "(ledger is being written, retrying)"
        if a.once:
            print(text)
            return
        sys.stdout.write("\x1b[2J\x1b[H" + text + f"\n\n(refresh {a.interval}s, Ctrl+C to quit)\n")
        sys.stdout.flush()
        try:
            time.sleep(a.interval)
        except KeyboardInterrupt:
            return


def cmd_handoff(a, led: Ledger):
    data = led.load()
    if a.all_runnable:
        tasks = [t for t in led.runnable(data) if t.get("portable") or a.include_non_portable]
    else:
        tasks = [led.get(data, a.id)]
    if not tasks:
        print("nothing to hand off (no runnable portable task)")
        return
    (led.dir / "handoff").mkdir(exist_ok=True)
    for t in tasks:
        atomic_write(led.dir / "handoff" / f"{t['id']}.md", build_packet(led, data, t, a.inline_skills))
        print(f"wrote .kuro/handoff/{t['id']}.md")
    # conflict check: parallel runs must not share files
    for i, x in enumerate(tasks):
        for y in tasks[i + 1:]:
            both = set(x.get("files", [])) & set(y.get("files", []))
            if both:
                print(f"WARNING: {x['id']} and {y['id']} both touch {sorted(both)}; run them sequentially, not in parallel")
    prompt = lambda t: f"Read .kuro/handoff/{t['id']}.md and execute that task completely, following its rules."  # noqa: E731
    tools = list(LAUNCH) if a.tool == "all" else [a.tool]
    for t in tasks:
        for tool in tools:
            print(f"[{t['id']}] {tool}: {LAUNCH[tool].format(p=prompt(t))}")


def cmd_notify(a, led: Ledger):
    print(notify(led, a.level, a.message, force=True))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.environ.get("KURO_ROOT", "."))
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("init"); p.add_argument("--project"); p.set_defaults(fn=cmd_init)
    p = sp.add_parser("add")
    p.add_argument("--id", required=True); p.add_argument("--title", required=True)
    p.add_argument("--owner"); p.add_argument("--deps"); p.add_argument("--acceptance"); p.add_argument("--files")
    p.add_argument("--size", choices=["S", "M", "L"], default="M")
    p.add_argument("--portable", choices=["yes", "no"], default="yes")
    p.add_argument("--needs", help="comma list, e.g. subagents,secrets,browser"); p.add_argument("--skills")
    p.add_argument("--verify", help="command that proves the task is done, e.g. \"npm test\"")
    p.add_argument("--note"); p.add_argument("--agent", default="Mbarga"); p.set_defaults(fn=cmd_add)
    p = sp.add_parser("edit", help="change a task (acceptance criteria, files, check command...)")
    p.add_argument("id"); p.add_argument("--title"); p.add_argument("--owner"); p.add_argument("--acceptance")
    p.add_argument("--files"); p.add_argument("--verify"); p.add_argument("--note")
    p.add_argument("--agent", default="Mbarga"); p.set_defaults(fn=cmd_edit)
    p = sp.add_parser("verify", help="run the task's check command and record the real result")
    p.add_argument("id"); p.add_argument("--cmd"); p.add_argument("--agent", default="Mbarga")
    p.set_defaults(fn=cmd_verify)
    p = sp.add_parser("claim", help="take a task atomically (refused if held by someone else or files overlap)")
    p.add_argument("id"); p.add_argument("--agent", required=True); p.add_argument("--note")
    p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_claim)
    p = sp.add_parser("set"); p.add_argument("id"); p.add_argument("status", choices=STATUSES)
    p.add_argument("--note"); p.add_argument("--commit"); p.add_argument("--force", action="store_true")
    p.add_argument("--evidence", help="what was checked by hand, when no command can prove it")
    p.add_argument("--agent", default="Mbarga"); p.set_defaults(fn=cmd_set)
    p = sp.add_parser("log"); p.add_argument("message"); p.add_argument("--level", choices=LEVELS, default="info")
    p.add_argument("--agent", default="Mbarga"); p.add_argument("--notify", action="store_true")
    p.add_argument("--task", help="task id this entry is about (refreshes its heartbeat on the live board)")
    p.set_defaults(fn=cmd_log)
    sp.add_parser("status").set_defaults(fn=cmd_status)
    p = sp.add_parser("next")
    p.add_argument("--parallel", action="store_true", help="only tasks that can start together (no shared files)")
    p.set_defaults(fn=cmd_next)
    p = sp.add_parser("watch", help="live board: who is doing what, refreshed in place")
    p.add_argument("--interval", type=float, default=2.0); p.add_argument("--once", action="store_true")
    p.add_argument("--journal", type=int, default=8, help="journal lines to show"); p.set_defaults(fn=cmd_watch)
    p = sp.add_parser("handoff"); p.add_argument("id", nargs="?"); p.add_argument("--all-runnable", action="store_true")
    p.add_argument("--include-non-portable", action="store_true")
    p.add_argument("--tool", choices=list(LAUNCH) + ["all"], default="all")
    p.add_argument("--inline-skills", action="store_true"); p.set_defaults(fn=cmd_handoff)
    p = sp.add_parser("notify"); p.add_argument("message"); p.add_argument("--level", choices=LEVELS, default="info")
    p.set_defaults(fn=cmd_notify)

    a = ap.parse_args(argv)
    if a.cmd == "handoff" and not a.all_runnable and not a.id:
        ap.error("handoff needs a task id or --all-runnable")
    a.fn(a, Ledger(Path(a.root)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
