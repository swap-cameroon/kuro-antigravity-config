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

Commands: init | add | set | log | status | next | handoff | notify
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
    return now().strftime("%Y-%m-%d %H:%M")


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
        out += ["", "## Launch elsewhere", "",
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
                f"3. Mark progress with `python \"{TOOL_PATH}\" --root \"{self.root}\" set <id> in_progress|done|blocked --note \"...\"`.",
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
             f"- Project: {data.get('project', '')}   Owner role: {t.get('owner', '-')}   Size: {t.get('size', '-')}",
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
    lines += ["", "## When finished", "",
              "1. Run the tests/build. Summarize what changed and the real results.",
              f"2. Record it: `python \"{TOOL_PATH}\" --root \"{led.root}\" set {t['id']} done --note \"<one line>\"` "
              f"(or write `.kuro/handoff/{t['id']}.result.md` if the command is unavailable).", "",
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
                "needs": [n for n in (a.needs or "").split(",") if n],
                "skills": [s for s in (a.skills or "").split(",") if s], "note": a.note or "",
                "created": stamp(), "updated": stamp()}
        if led.has_cycle(data["tasks"] + [task]):
            raise SystemExit("dependency cycle rejected")
        data["tasks"].append(task)
        led.save(data)
        led.append_journal("info", a.agent, f"task added {a.id}: {a.title}")
        led.render(data)
    print(f"added {a.id}")


def cmd_set(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        t = led.get(data, a.id)
        if a.status in ("in_progress", "done"):
            pending = [d for d in t["deps"] if led.get(data, d)["status"] != "done"]
            if pending and not a.force:
                raise SystemExit(f"{a.id} depends on unfinished {pending} (use --force to override)")
        t["status"], t["updated"] = a.status, stamp()
        if a.note:
            t["note"] = redact(a.note)
        if a.commit:
            t["commit"] = a.commit
        led.save(data)
        level = {"done": "done", "blocked": "blocker"}.get(a.status, "info")
        led.append_journal(level, a.agent, f"{a.id} -> {a.status}" + (f": {a.note}" if a.note else ""))
        led.render(data)
    out = notify(led, level, f"{a.id} {a.status}: {t['title']}") if level != "info" else "-"
    print(f"{a.id} -> {a.status} (notify: {out})")


def cmd_log(a, led: Ledger):
    with locked(led.dir):
        data = led.load()
        led.append_journal(a.level, a.agent, a.message)
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
    for t in led.runnable(data):
        print(f"{t['id']}\t{t.get('owner', '-')}\tportable={'yes' if t.get('portable') else 'no'}\t{t['title']}")


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
    p.add_argument("--note"); p.add_argument("--agent", default="Mbarga"); p.set_defaults(fn=cmd_add)
    p = sp.add_parser("set"); p.add_argument("id"); p.add_argument("status", choices=STATUSES)
    p.add_argument("--note"); p.add_argument("--commit"); p.add_argument("--force", action="store_true")
    p.add_argument("--agent", default="Mbarga"); p.set_defaults(fn=cmd_set)
    p = sp.add_parser("log"); p.add_argument("message"); p.add_argument("--level", choices=LEVELS, default="info")
    p.add_argument("--agent", default="Mbarga"); p.add_argument("--notify", action="store_true"); p.set_defaults(fn=cmd_log)
    sp.add_parser("status").set_defaults(fn=cmd_status)
    sp.add_parser("next").set_defaults(fn=cmd_next)
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
