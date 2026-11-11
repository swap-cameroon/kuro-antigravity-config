#!/usr/bin/env python3
"""Team Kuro quality checks: deterministic gates on the documents that decide the quality of the work.

No model tokens, standard library only. Each check prints PASS / WARN / FAIL lines and the command exits 1
when anything FAILs, so an agent (or CI) cannot wave a gate through by saying it looks fine.

  prd          PRD.md has outcomes, scope, non-goals and numbered Given/When/Then criteria without vague words
  adr          every docs/adr/*.md has status, context, decision, rejected alternatives and consequences
  state        PROJECT_STATE.md is filled in, short, secret-free and not behind git HEAD
  conventions  CONVENTIONS.md exists and is filled in; `conventions --init` drafts it from repo evidence
  all          every check whose document exists

Usage:  python kuro_check.py [--root DIR] <check> [options]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from kuro_ledger import SECRET_PATTERNS          # one definition of "looks like a secret"
except Exception:                                     # pragma: no cover - the checker still works alone
    SECRET_PATTERNS = []

VAGUE = ("fast", "quick", "quickly", "intuitive", "robust", "user-friendly", "easy", "simple", "scalable", "secure",
         "seamless", "performant", "efficient", "modern", "rapide", "rapidement", "intuitif", "intuitive", "robuste",
         "facile", "convivial", "ergonomique", "securise", "efficace", "moderne", "fluide")
PLACEHOLDER = re.compile(r"<[a-zA-Z][^<>\n]{0,60}>|\bTODO\b|\bTBD\b|\bA COMPLETER\b", re.I)
STALE_COMMITS = 20


def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


class Report:
    def __init__(self) -> None:
        self.fails = 0
        self.lines: list[str] = []

    def add(self, level: str, check: str, detail: str) -> None:
        self.fails += level == "FAIL"
        self.lines.append(f"{level:<4} {check}: {detail}")

    def ok(self, cond: bool, check: str, good: str, bad: str, level: str = "FAIL") -> bool:
        self.add("PASS" if cond else level, check, good if cond else bad)
        return cond


def headings(text: str) -> list[str]:
    return [fold(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+)$", text, re.M)]


def has_heading(heads: list[str], *words: str) -> bool:
    return any(any(w in h for w in words) for h in heads)


def strip_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


# ----------------------------------------------------------------------------- PRD
def check_prd(root: Path, rep: Report, name: str = "PRD.md") -> None:
    f = root / name
    if not f.is_file():
        rep.add("FAIL", "prd", f"{name} not found: no implementation starts without acceptance criteria")
        return
    text = f.read_text(encoding="utf-8", errors="replace")
    heads = headings(text)
    for label, words in (("problem and outcomes", ("problem", "outcome", "probleme", "objectif", "resultat")),
                         ("users", ("user", "persona", "utilisateur")),
                         ("journeys", ("journey", "parcours", "flow")),
                         ("scope", ("scope", "perimetre", "portee")),
                         ("requirements", ("requirement", "exigence", "stor")),
                         ("non-functional", ("non-functional", "non functional", "non-fonctionnel", "nfr", "qualite"))):
        rep.ok(has_heading(heads, *words), "prd", f"section '{label}' present", f"section '{label}' is missing")
    rep.ok(bool(re.search(r"non[- ]goals?|hors[- ]perimetre|hors[- ]scope|non[- ]objectifs?", fold(text))), "prd",
           "non-goals stated", "no non-goals: anything not excluded will creep into scope")

    body = strip_code(text)
    marks = list(re.finditer(r"\bAC-\d+(?:\.\d+)*\b", body))
    if not rep.ok(bool(marks), "prd", f"{len({m.group(0) for m in marks})} numbered acceptance criteria",
                  "no numbered acceptance criterion (AC-1.1 ...): tests and reviews have nothing to cite"):
        return
    blocks: dict[str, str] = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        nxt = re.search(r"^#{1,6}\s", body[m.end():end], re.M)
        chunk = body[m.end():m.end() + nxt.start()] if nxt else body[m.end():end]
        blocks[m.group(0)] = blocks.get(m.group(0), "") + " " + chunk
    bad_form, vague = [], []
    for ac, chunk in blocks.items():
        low = fold(chunk)
        gwt = (re.search(r"\b(given|etant donne|soit)\b", low) and re.search(r"\b(when|quand|lorsqu)", low)
               and re.search(r"\b(then|alors)\b", low))
        if not gwt:
            bad_form.append(ac)
        words = [w for w in VAGUE if re.search(rf"\b{re.escape(w)}\b", low)]
        if words and not re.search(r"\d", chunk):
            vague.append(f"{ac} ({', '.join(sorted(set(words)))})")
    rep.ok(not bad_form, "prd", "every criterion is Given/When/Then",
           f"not Given/When/Then: {', '.join(bad_form[:8])}")
    rep.ok(not vague, "prd", "no vague criterion", f"vague words without a number: {'; '.join(vague[:6])}")
    left = len(PLACEHOLDER.findall(body))
    rep.ok(left == 0, "prd", "no placeholder left", f"{left} placeholder(s) or TODO left", "WARN")


# ----------------------------------------------------------------------------- ADR
def check_adr(root: Path, rep: Report, folder: str = "docs/adr") -> None:
    d = root / folder
    files = sorted(p for p in d.glob("*.md") if not re.match(r"(readme|index|template|0000)", p.name.lower())) \
        if d.is_dir() else []
    if not files:
        designed = any((root / n).is_file() for n in ("ARCHITECTURE.md", "DESIGN.md"))
        rep.add("FAIL" if designed else "WARN", "adr",
                f"no ADR in {folder}" + (": an architecture exists but no decision is recorded" if designed else ""))
        return
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        low, heads = fold(text), headings(text)
        missing = [label for label, words in (
            ("status", ("status", "statut")), ("context", ("context",)), ("decision", ("decision",)),
            ("rejected alternatives", ("alternative", "rejected", "rejete", "option")),
            ("consequences", ("consequence",)))
            if not (has_heading(heads, *words) or any(re.search(rf"^\W*{w}\w*\W*:", low, re.M) for w in words))]
        status = re.search(r"\b(proposed|accepted|superseded|deprecated|rejected|propose|accepte|remplace)\b", low)
        if not status and "status" not in missing:
            missing.append("status value (proposed|accepted|superseded|deprecated|rejected)")
        rep.ok(not missing, "adr", f"{f.name} complete", f"{f.name} is missing: {', '.join(missing)}")


# ----------------------------------------------------------------------------- PROJECT_STATE
def git(root: Path, *args: str) -> tuple[int, str]:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=20)
        return r.returncode, r.stdout.strip()
    except Exception:
        return 1, ""


def check_state(root: Path, rep: Report, name: str = "PROJECT_STATE.md") -> None:
    f = root / name
    if not f.is_file():
        rep.add("FAIL", "state", f"{name} not found: the next session will have to re-read the whole repo")
        return
    text = f.read_text(encoding="utf-8", errors="replace")
    n = len(text.splitlines())
    rep.ok(n <= 200, "state", f"{n} lines", f"{n} lines (keep under ~200: link to ADRs/PRD instead)", "WARN")
    left = len(PLACEHOLDER.findall(strip_code(text)))
    rep.ok(left <= 3, "state", "filled in", f"{left} template placeholders left: it describes nothing yet")
    leaked = sum(1 for p in SECRET_PATTERNS if p.search(text))
    rep.ok(leaked == 0, "state", "no secret", "looks like it contains a secret: name the variable, never its value")
    low = fold(text)
    nxt = re.search(r"next 3 actions(.*?)(?:\n#|\Z)", low, re.S) or re.search(r"prochaines? actions?(.*?)(?:\n#|\Z)", low, re.S)
    items = [x for x in re.findall(r"^\s*\d+\.\s*(.+)$", nxt.group(1), re.M) if not PLACEHOLDER.search(x)] if nxt else []
    rep.ok(bool(items), "state", f"{len(items)} next action(s)", "no concrete next action")
    m = re.search(r"last verified commit\W*`?([0-9a-f]{7,40})`?", low)
    code, head = git(root, "rev-parse", "--short", "HEAD")
    if code != 0:
        rep.add("WARN", "state", "not a git repository: freshness cannot be checked")
    elif not m:
        rep.add("FAIL", "state", "no 'Last verified commit': nobody can tell how old this file is")
    else:
        sha = m.group(1)
        code, behind = git(root, "rev-list", "--count", f"{sha}..HEAD")
        if code != 0:
            rep.add("FAIL", "state", f"last verified commit {sha} is unknown to this repository")
        elif int(behind) == 0:
            rep.add("PASS", "state", f"verified at HEAD ({head})")
        else:
            rep.add("FAIL" if int(behind) > STALE_COMMITS else "WARN", "state",
                    f"{behind} commit(s) behind HEAD ({head}): read `git log --oneline {sha}..HEAD` and reconcile")


# ----------------------------------------------------------------------------- CONVENTIONS
def detect(root: Path) -> dict[str, list[str]]:
    """Facts read from the repository. Nothing here was executed: commands are reported as detected."""
    out: dict[str, list[str]] = {"stack": [], "commands": [], "style": [], "tests": [], "ci": []}
    has = lambda *names: [n for n in names if (root / n).exists()]  # noqa: E731
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        pm = "pnpm" if has("pnpm-lock.yaml") else "yarn" if has("yarn.lock") else "bun" if has("bun.lockb") else "npm"
        out["stack"].append(f"Node ({pm})" + (", TypeScript" if "typescript" in deps or has("tsconfig.json") else ""))
        for lib, label in (("@angular/core", "Angular"), ("next", "Next.js"), ("react", "React"), ("vue", "Vue"),
                           ("@nestjs/core", "NestJS"), ("express", "Express"), ("fastify", "Fastify")):
            if lib in deps:
                out["stack"].append(f"{label} {deps[lib]}")
        for s in ("dev", "start", "build", "test", "lint", "typecheck", "e2e", "format"):
            if s in data.get("scripts", {}):
                out["commands"].append(f"{s}: `{pm} run {s}`")
        for lib, label in (("jest", "Jest"), ("vitest", "Vitest"), ("@playwright/test", "Playwright"),
                           ("cypress", "Cypress"), ("karma", "Karma")):
            if lib in deps:
                out["tests"].append(label)
        for lib in ("eslint", "prettier", "@biomejs/biome"):
            if lib in deps:
                out["style"].append(lib)
        ts = root / "tsconfig.json"
        if ts.is_file() and re.search(r'"strict"\s*:\s*true', ts.read_text(encoding="utf-8", errors="replace")):
            out["style"].append("TypeScript strict mode")
    if has("pom.xml"):
        pom = (root / "pom.xml").read_text(encoding="utf-8", errors="replace")
        wrap = "./mvnw" if has("mvnw") else "mvn"
        out["stack"].append("Java / Maven" + (", Spring Boot" if "spring-boot" in pom else ""))
        out["commands"] += [f"build: `{wrap} -q verify`", f"test: `{wrap} test`"]
        out["tests"].append("JUnit")
    if has("build.gradle", "build.gradle.kts"):
        wrap = "./gradlew" if has("gradlew") else "gradle"
        out["stack"].append("JVM / Gradle")
        out["commands"] += [f"build: `{wrap} build`", f"test: `{wrap} test`"]
    py = "".join((root / n).read_text(encoding="utf-8", errors="replace") for n in has("pyproject.toml", "requirements.txt"))
    if py:
        out["stack"].append("Python" + "".join(f", {label}" for lib, label in (("fastapi", "FastAPI"), ("django", "Django"),
                                                                                ("flask", "Flask")) if lib in py.lower()))
        if "pytest" in py.lower() or has("pytest.ini"):
            out["tests"].append("pytest")
            out["commands"].append("test: `pytest`")
        for tool in ("ruff", "black", "mypy", "flake8"):
            if tool in py.lower():
                out["style"].append(tool)
    for name, label in (("go.mod", "Go"), ("Cargo.toml", "Rust"), ("pubspec.yaml", "Dart / Flutter"),
                        ("composer.json", "PHP")):
        if has(name):
            out["stack"].append(label)
    if has("Dockerfile"):
        out["stack"].append("Docker")
    if has("docker-compose.yml", "docker-compose.yaml", "compose.yaml", "compose.yml"):
        out["commands"].append("stack: `docker compose up -d`")
    if has(".editorconfig"):
        out["style"].append(".editorconfig")
    wf = root / ".github" / "workflows"
    if wf.is_dir():
        out["ci"].append("GitHub Actions: " + ", ".join(sorted(p.name for p in wf.glob("*.y*ml"))[:6]))
    if has(".gitlab-ci.yml"):
        out["ci"].append("GitLab CI")
    code, log = git(root, "log", "-30", "--pretty=%s")
    if code == 0 and log:
        subjects = log.splitlines()
        conv = sum(bool(re.match(r"(feat|fix|docs|chore|refactor|test|perf|build|ci|style|revert)(\(.+\))?!?:", s))
                   for s in subjects)
        if conv * 2 >= len(subjects):
            out["style"].append(f"Conventional Commits ({conv}/{len(subjects)} recent commits)")
    return out


def draft_conventions(root: Path) -> str:
    d = detect(root)
    lst = lambda items: [f"- {i}" for i in items] or ["- TODO(user): nothing detected"]  # noqa: E731
    return "\n".join([
        "# CONVENTIONS", "",
        "> How THIS project is written. It overrides the generic advice of any skill. Keep it short and concrete;",
        "> every agent reads it before touching code. Lines marked UNVERIFIED were detected, not run.", "",
        "## Stack (detected)", *lst(d["stack"]), "",
        "## Commands (UNVERIFIED until someone runs them)", *lst(d["commands"]), "",
        "## Tests", *lst(d["tests"]),
        "- TODO(user): what must be tested before a change is accepted (unit, integration, e2e) and the coverage floor", "",
        "## Code style and tooling", *lst(d["style"]),
        "- TODO(user): naming rules (files, classes, variables, database objects)", "",
        "## Architecture rules",
        "- TODO(user): layers or modules and which may depend on which",
        "- TODO(user): where new code goes (feature folder, package, bounded context)",
        "- TODO(user): patterns we use on purpose, and patterns we refuse", "",
        "## Git and review", *lst(d["ci"]),
        "- TODO(user): branch naming, PR size, who reviews, what blocks a merge", "",
        "## Never",
        "- TODO(user): things that must not be done here (libraries, shortcuts, files not to touch)", ""])


def check_conventions(root: Path, rep: Report, name: str = "CONVENTIONS.md", init: bool = False,
                      force: bool = False) -> None:
    f = root / name
    if init:
        if f.exists() and not force:
            rep.add("FAIL", "conventions", f"{name} already exists (use --force to overwrite)")
            return
        f.write_text(draft_conventions(root), encoding="utf-8", newline="\n")
        rep.add("PASS", "conventions", f"drafted {name} from repo evidence: fill in the TODO(user) lines")
        return
    if not f.is_file():
        rep.add("WARN", "conventions", f"{name} not found: agents will apply generic skill advice. "
                                       "Draft it with: kuro_check.py conventions --init")
        return
    text = f.read_text(encoding="utf-8", errors="replace")
    todo, unv = text.count("TODO(user)"), len(re.findall(r"^- .*`", text, re.M)) if "UNVERIFIED until" in text else 0
    rep.ok(todo == 0, "conventions", "team rules filled in", f"{todo} TODO(user) line(s) still to fill in", "WARN")
    if unv:
        rep.add("WARN", "conventions", "commands are still marked UNVERIFIED: run them, then remove the mark")
    n = len(text.splitlines())
    rep.ok(n <= 150, "conventions", f"{n} lines", f"{n} lines (keep under ~150 so every agent can read it)", "WARN")


# ----------------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.environ.get("KURO_ROOT", "."))
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("prd").add_argument("--file", default="PRD.md")
    sp.add_parser("adr").add_argument("--dir", default="docs/adr")
    sp.add_parser("state").add_argument("--file", default="PROJECT_STATE.md")
    p = sp.add_parser("conventions")
    p.add_argument("--file", default="CONVENTIONS.md")
    p.add_argument("--init", action="store_true", help="draft the file from repo evidence")
    p.add_argument("--force", action="store_true")
    sp.add_parser("all")
    a = ap.parse_args(argv)
    root, rep = Path(a.root).resolve(), Report()
    if a.cmd == "prd":
        check_prd(root, rep, a.file)
    elif a.cmd == "adr":
        check_adr(root, rep, a.dir)
    elif a.cmd == "state":
        check_state(root, rep, a.file)
    elif a.cmd == "conventions":
        check_conventions(root, rep, a.file, a.init, a.force)
    else:
        if (root / "PRD.md").is_file():
            check_prd(root, rep)
        check_adr(root, rep)
        check_state(root, rep)
        check_conventions(root, rep)
    print("\n".join(rep.lines))
    print(f"\n{'FAILED' if rep.fails else 'OK'}: {rep.fails} failing check(s)")
    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
