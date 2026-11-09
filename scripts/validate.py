#!/usr/bin/env python3
"""Validate the Team Kuro configuration repository.

Checks (errors fail the run, warnings do not unless --strict):
  * every skills/<dir>/SKILL.md has YAML frontmatter with `name` == <dir> and a description
  * relative markdown links in SKILL.md files resolve (warning for vendored reference files)
  * team/roster.json only references skills that exist, and every skill is owned by someone
  * JSON files parse, plugin.json files have the required keys
  * the install scripts and README skill count agree with the real number of skills
  * token budgets: always-on rules, total skill descriptions, per-description and per-SKILL.md size
  * docs/SKILLS.md is up to date (use --write-catalog to regenerate it)

Usage:  python scripts/validate.py [--strict] [--write-catalog] [--report]
Only the standard library is used, so it runs anywhere (CI, Windows, macOS, Linux).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

# Token budgets (1 token ~ 4 chars). Descriptions and rules are paid on EVERY turn; SKILL.md bodies on activation.
BUDGET_RULES_TOKENS = 1400        # all plugins/*/rules/AGENTS.md combined (error)
BUDGET_DESCRIPTIONS_TOKENS = 3900  # sum of all skill frontmatter descriptions (error)
MAX_DESCRIPTION_CHARS = 520       # one description (error)
WARN_SKILL_MD_TOKENS = 3500       # one SKILL.md body (warning: split into references/)
# Authored as a single workflow with their own progressive disclosure in sibling folders; not split mechanically.
SIZE_EXEMPT = {"system-design-architect", "backend-performance-review"}


def tokens(text: str) -> int:
    return (len(text) + 3) // 4


errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Tiny frontmatter reader: top-level `key:` entries only (enough for presence checks)."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    out: dict[str, str] = {}
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            out[key] = m.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            out[key] = (out[key] + " " + line.strip()).strip()
    return None  # never closed


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def check_skills() -> dict[str, dict[str, str]]:
    meta: dict[str, dict[str, str]] = {}
    for d in skill_dirs():
        f = d / "SKILL.md"
        if not f.exists():
            err(f"{d.relative_to(ROOT)}: missing SKILL.md")
            continue
        fm = parse_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        if fm is None:
            err(f"{f.relative_to(ROOT)}: missing or unterminated YAML frontmatter")
            continue
        if fm.get("name") != d.name:
            err(f"{f.relative_to(ROOT)}: name '{fm.get('name')}' must equal directory '{d.name}'")
        desc = fm.get("description", "")
        if desc in ("", "|", ">", "|-", ">-") or len(desc) < 20:
            err(f"{f.relative_to(ROOT)}: description missing or too short (it drives skill routing)")
        meta[d.name] = fm
    return meta


def check_links() -> None:
    for md in sorted(ROOT.glob("skills/**/*.md")) + sorted(ROOT.glob("plugins/**/*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        text = INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))
        for target in LINK_RE.findall(text):
            if re.match(r"^(https?:|mailto:|#|<|\{)", target) or "://" in target:
                continue
            path = target.split("#", 1)[0]
            if not path or path.startswith(("/", "~")) or any(c in path for c in "*<>{}$"):
                continue
            if not (md.parent / path).exists():
                (err if md.name == "SKILL.md" else warn)(
                    f"{md.relative_to(ROOT)}: broken relative link -> {target}"
                )


def check_budgets(meta: dict[str, dict[str, str]], report: bool) -> None:
    rules = {p: tokens(p.read_text(encoding="utf-8")) for p in ROOT.glob("plugins/*/rules/AGENTS.md")}
    rules_total = sum(rules.values())
    desc_total = sum(tokens(m.get("description", "")) + tokens(m.get("name", "")) for m in meta.values())
    if rules_total > BUDGET_RULES_TOKENS:
        err(f"always-on rules cost ~{rules_total} tokens/turn (budget {BUDGET_RULES_TOKENS}); move detail into a skill")
    if desc_total > BUDGET_DESCRIPTIONS_TOKENS:
        err(f"skill descriptions cost ~{desc_total} tokens/turn (budget {BUDGET_DESCRIPTIONS_TOKENS}); shorten descriptions")
    sizes = {}
    for n, m in meta.items():
        d = m.get("description", "")
        if len(d.strip('"')) > MAX_DESCRIPTION_CHARS:
            err(f"skills/{n}: description is {len(d)} chars (max {MAX_DESCRIPTION_CHARS})")
        body = (SKILLS / n / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        sizes[n] = tokens(body)
        if sizes[n] > WARN_SKILL_MD_TOKENS and n not in SIZE_EXEMPT:
            warn(f"skills/{n}/SKILL.md is ~{sizes[n]} tokens; split it (python scripts/split_skill.py {n} --keep ...)")
    if report:
        print("== Token budget report (1 token ~ 4 chars) ==")
        print(f"always-on rules      : ~{rules_total:>5} tokens/turn  (budget {BUDGET_RULES_TOKENS})")
        print(f"skill descriptions   : ~{desc_total:>5} tokens/turn  (budget {BUDGET_DESCRIPTIONS_TOKENS})")
        print(f"baseline per turn    : ~{rules_total + desc_total:>5} tokens")
        print("heaviest SKILL.md on activation:")
        for n, s in sorted(sizes.items(), key=lambda x: -x[1])[:8]:
            print(f"  {s:>6}  {n}")
        print()


def check_team_config_and_hook() -> None:
    f = ROOT / "team" / "config.json"
    if not f.exists():
        err("team/config.json missing")
    else:
        try:
            cfg = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"team/config.json: invalid JSON ({e})")
            cfg = {}
        enums = {"concertation": {"always", "auto", "off"},
                 "skill_acquisition": {"ask", "auto-if-scanned", "off"},
                 "agent_creation": {"ask", "auto", "off"}}
        for k, allowed in enums.items():
            if cfg.get(k) not in allowed:
                err(f"team/config.json: '{k}' must be one of {sorted(allowed)}")
        rep = cfg.get("reporter", {})
        if not isinstance(rep, dict) or not isinstance(rep.get("channels"), list):
            err("team/config.json: 'reporter.channels' must be a list")
        else:
            for c in rep["channels"]:
                if c not in {"file", "toast", "ntfy", "webhook"}:
                    err(f"team/config.json: unknown reporter channel '{c}'")
        for k in ("max_participants", "max_rounds"):
            if not isinstance(cfg.get(k), int) or cfg[k] < 1:
                err(f"team/config.json: '{k}' must be a positive integer")
    for rel in ("team/hooks/kuro_huddle.py", "team/tools/kuro_ledger.py"):
        f = ROOT / rel
        if not f.exists():
            err(f"{rel} missing")
            continue
        try:
            compile(f.read_text(encoding="utf-8"), str(f), "exec")
        except SyntaxError as e:
            err(f"{rel}: syntax error ({e})")


def check_roster(skill_names: set[str]) -> dict:
    f = ROOT / "team" / "roster.json"
    if not f.exists():
        err("team/roster.json missing")
        return {}
    roster = json.loads(f.read_text(encoding="utf-8"))
    owned: set[str] = set()
    for m in roster["members"]:
        for s in m["skills"] + m.get("optional_skills", []):
            owned.add(s)
            if s not in skill_names:
                err(f"team/roster.json: {m['name']} references unknown skill '{s}'")
    names = [m["name"] for m in roster["members"]]
    if len(set(names)) != len(names):
        err("team/roster.json: duplicate member names")
    for m in roster["members"]:
        p = m.get("persona", {})
        for k in ("origin", "inspiration", "traits", "voice", "blind_spot"):
            if not p.get(k):
                err(f"team/roster.json: {m['name']} persona is missing '{k}'")
    for n in roster.get("lifecycle", []):
        if n not in names:
            err(f"team/roster.json: lifecycle references unknown member '{n}'")
    for s in sorted(skill_names - owned - set(roster.get("shared_skills", []))):
        warn(f"skill '{s}' is not owned by any team member (add it to team/roster.json)")
    for s in roster.get("shared_skills", []):
        if s not in skill_names:
            err(f"team/roster.json: shared skill '{s}' does not exist")
    return roster


def check_json_and_plugins() -> None:
    for f in ROOT.glob("*.json"):
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"{f.name}: invalid JSON ({e})")
    for p in ROOT.glob("plugins/*/plugin.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"{p.relative_to(ROOT)}: invalid JSON ({e})")
            continue
        for k in ("name", "version", "description"):
            if k not in data:
                err(f"{p.relative_to(ROOT)}: missing '{k}'")
        if data.get("name") != p.parent.name:
            err(f"{p.relative_to(ROOT)}: name must equal directory '{p.parent.name}'")


def category(name: str) -> str:
    table = [
        ("Frontend & mobile", ("angular", "react", "mobile", "ui-design")),
        ("Backend, data & AI", ("spring", "postgres", "backend", "http-resilience", "perf", "node-",
                                "python-", "api-design", "data-engineering", "llm-app")),
        ("Security", ("security", "sast", "dast", "pentest", "secrets", "dependency", "compliance",
                      "remediation", "secure-by", "threat-")),
        ("Architecture & product", ("system-design", "first-principles", "spec-miner", "product-req")),
        ("Delivery, cloud & reliability", ("devops", "cloud", "sre", "observability", "git-workflow")),
        ("Quality & maintenance", ("code-review", "api-contract", "test-strategy", "systematic-",
                                   "refactoring", "technical-writing")),
        ("Team & tokens", ("team-", "project-state", "token")),
    ]
    for label, prefixes in table:
        if name.startswith(prefixes):
            return label
    return "Other"


def build_catalog(meta: dict[str, dict[str, str]], roster: dict) -> str:
    owners: dict[str, list[str]] = {}
    for m in roster.get("members", []):
        for s in m["skills"] + m.get("optional_skills", []):
            owners.setdefault(s, []).append(m["name"])
    groups: dict[str, list[str]] = {}
    for n in meta:
        groups.setdefault(category(n), []).append(n)
    out = ["# Skill catalog", "",
           "_Generated by `python scripts/validate.py --write-catalog` - do not edit by hand._", "",
           f"**{len(meta)} skills**", ""]
    for label in sorted(groups):
        out += [f"## {label}", "", "| Skill | Owner(s) | Description |", "| :-- | :-- | :-- |"]
        for n in sorted(groups[label]):
            d = meta[n].get("description", "").replace("|", "\\|")
            d = d if len(d) <= 160 else d[:157].rstrip() + "..."
            out.append(f"| `{n}` | {', '.join(owners.get(n, ['shared']))} | {d} |")
        out.append("")
    return "\n".join(out)


def build_team_doc(roster: dict) -> str:
    out = ["# Team Kuro roster", "",
           "_Generated by `python scripts/validate.py --write-catalog` from `team/roster.json` - do not edit by hand._", "",
           f"> {roster.get('persona_note', '')}", "",
           "Lifecycle: " + " -> ".join(roster["lifecycle"]), ""]
    for tier, label in (("core", "Core roles"), ("specialist", "Specialists (summoned on demand)"),
                        ("support", "Support (continuity and reporting)")):
        out += [f"## {label}", ""]
        for m in roster["members"]:
            if m.get("tier") != tier:
                continue
            p = m["persona"]
            out += [f"### {m['name']} - {m['title']}", "",
                    f"- **Heritage**: {p['origin']}",
                    f"- **Inspiration**: {p['inspiration']}",
                    f"- **Traits**: {', '.join(p['traits'])}",
                    f"- **Voice**: {p['voice']}",
                    f"- **Blind spot (peers challenge it)**: {p['blind_spot']}",
                    f"- **Mission**: {m['mission']}",
                    f"- **Skills**: {', '.join('`' + s + '`' for s in m['skills'])}"
                    + (f" (optional: {', '.join('`' + s + '`' for s in m['optional_skills'])})" if m.get("optional_skills") else ""),
                    f"- **Deliverable**: {m['deliverable']}",
                    f"- **Gate**: {m['gate']}"]
            if m.get("when"):
                out.append(f"- **Summoned when**: {m['when']}")
            out.append("")
    return "\n".join(out)


def check_counts(n_skills: int) -> None:
    for rel in ("README.md", "install.ps1", "install.sh"):
        f = ROOT / rel
        if not f.exists():
            continue
        for m in re.finditer(r"\b(\d+)\s+(?:specialized\s+|specialised\s+|domain\s+)*skills\b",
                             f.read_text(encoding="utf-8")):
            if int(m.group(1)) != n_skills:
                err(f"{rel}: claims {m.group(1)} skills but {n_skills} exist")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--report", action="store_true", help="print the token budget report")
    ap.add_argument("--write-catalog", action="store_true", help="regenerate docs/SKILLS.md")
    args = ap.parse_args()

    meta = check_skills()
    check_links()
    roster = check_roster(set(meta))
    check_json_and_plugins()
    check_team_config_and_hook()
    check_counts(len(meta))
    check_budgets(meta, args.report)

    catalog = build_catalog(meta, roster)
    cat_file = ROOT / "docs" / "SKILLS.md"
    team_doc = build_team_doc(roster) if roster else ""
    team_file = ROOT / "docs" / "TEAM.md"
    if args.write_catalog:
        cat_file.parent.mkdir(exist_ok=True)
        cat_file.write_text(catalog + "\n", encoding="utf-8", newline="\n")
        team_file.write_text(team_doc + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {cat_file.relative_to(ROOT)} and {team_file.relative_to(ROOT)}")
    else:
        if not cat_file.exists() or cat_file.read_text(encoding="utf-8").strip() != catalog.strip():
            err("docs/SKILLS.md is out of date - run: python scripts/validate.py --write-catalog")
        if not team_file.exists() or team_file.read_text(encoding="utf-8").strip() != team_doc.strip():
            err("docs/TEAM.md is out of date - run: python scripts/validate.py --write-catalog")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(meta)} skills | {len(errors)} error(s) | {len(warnings)} warning(s)")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
