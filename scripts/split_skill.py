#!/usr/bin/env python3
"""Progressive-disclosure splitter for oversized SKILL.md files.

Moves `## ` sections (or the `### ` children of chosen sections) verbatim into
skills/<name>/references/*.md and leaves, in SKILL.md, the core sections plus a
"Load on demand" index. Content is never rewritten; the tool verifies that no
line was lost.

  python scripts/split_skill.py <skill> --keep "Step 0" "Behavior Rules" [--deep "Big Section"] [--dry-run]

--keep  : section titles (prefix match) that stay in SKILL.md
--deep  : section titles whose `###` children become one reference file each
          (the section heading and intro text stay in SKILL.md)
Everything else is moved to its own reference file.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60].strip("-") or "section"


def split_level(lines: list[str], marker: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Split on headings that start with `marker` (e.g. '## '), ignoring fenced code."""
    pre: list[str] = []
    secs: list[tuple[str, list[str]]] = []
    fence = False
    for ln in lines:
        if ln.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence and ln.startswith(marker):
            secs.append((ln[len(marker):].strip(), [ln]))
        elif secs:
            secs[-1][1].append(ln)
        else:
            pre.append(ln)
    return pre, secs


def trim_blank(block: list[str]) -> list[str]:
    out = list(block)
    while out and not out[-1].strip():
        out.pop()
    while out and out[-1].strip() in ("---",):
        out.pop()
        while out and not out[-1].strip():
            out.pop()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("skill")
    ap.add_argument("--keep", nargs="*", default=[])
    ap.add_argument("--deep", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    sdir = ROOT / "skills" / a.skill
    skill_md = sdir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()

    # frontmatter stays in the preamble automatically (before the first '## ')
    pre, secs = split_level(lines, "## ")
    refdir = sdir / "references"
    used: set[str] = set(p.name for p in refdir.glob("*.md")) if refdir.exists() else set()

    def unique(name: str) -> str:
        base, n = name, 2
        while name in used:
            name = f"{base}-{n}"
            n += 1
        used.add(name)
        return name

    core: list[str] = []
    index: list[tuple[str, str]] = []
    moved: dict[str, list[str]] = {}

    for title, body in secs:
        if any(title.startswith(k) for k in a.keep):
            core += body
        elif any(title.startswith(d) for d in a.deep):
            cpre, kids = split_level(body, "### ")
            core += cpre
            for ktitle, kbody in kids:
                fname = unique(slug(ktitle)) + ".md"
                moved[fname] = trim_blank(kbody)
                index.append((f"{title} - {ktitle}", f"references/{fname}"))
        else:
            fname = unique(slug(title)) + ".md"
            moved[fname] = trim_blank(body)
            index.append((title, f"references/{fname}"))

    if not moved:
        print("nothing to move")
        return 1

    idx = ["## Load on demand", "",
           "The core rules in this file always apply. Read a reference below **only when the task needs it**:",
           "", "| Topic | File |", "| :-- | :-- |"]
    idx += [f"| {t} | [{f}]({f}) |" for t, f in index]
    idx += ["", "---", ""]

    new_lines = trim_blank(pre) + [""] + idx + [l for l in core]
    new_text = "\n".join(new_lines).rstrip() + "\n"

    # verify no line lost (multiset of non-empty lines)
    orig = Counter(l for l in lines if l.strip())
    new = Counter(l for l in new_text.splitlines() if l.strip())
    for f, body in moved.items():
        new.update(l for l in body if l.strip())
    lost = orig - new
    # separators/blank trimming may drop pure '---' rules; anything else is a bug
    lost = {l: c for l, c in lost.items() if l.strip() != "---"}
    if lost:
        print("ABORT: lines would be lost:", list(lost)[:5])
        return 2

    before = len(text) // 4
    after = len(new_text) // 4
    print(f"{a.skill}: SKILL.md ~{before} -> ~{after} tokens; {len(moved)} reference file(s)")
    if a.dry_run:
        for f in moved:
            print("  would write references/" + f)
        return 0
    refdir.mkdir(exist_ok=True)
    for f, body in moved.items():
        (refdir / f).write_text("\n".join(body).rstrip() + "\n", encoding="utf-8", newline="\n")
    skill_md.write_text(new_text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
