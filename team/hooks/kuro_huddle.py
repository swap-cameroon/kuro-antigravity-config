#!/usr/bin/env python3
"""Team Kuro PreInvocation hook: automatic session bootstrap + per-instruction huddle.

Runs before every agent turn. Reads the last user instruction from the transcript, routes it
deterministically (no model tokens) to roster members and installed skills, and injects a short
ephemeral message telling the orchestrator how to convene the team for THIS instruction.

Hook protocol (same as token-saver's interceptor):
  stdin : JSON with "transcriptPath"
  stdout: {"injectSteps": [{"ephemeralMessage": "..."}]}   or   {}

Config: team/config.json  ->  "concertation": "always" | "auto" | "off"  (env KURO_CONCERTATION overrides)
The hook must never break a session: any error results in {}.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEAM_DIR = HERE.parent                       # .../team
CONFIG_ROOT = TEAM_DIR.parent                # repo root or ~/.gemini/config
SKILLS_DIR = CONFIG_ROOT / "skills"

STOP = set("""a an the and or of to in on for with from by at as is are be it this that these those you your we our
i me my can could should would will please pls do does did make add create build write need want like just
le la les un une des du de et ou en dans sur pour avec par au aux est sont ce cet cette ces tu vous nous je mon ma
mes ton ta tes peux peut veux voudrais faut fais fait faire ajoute ajouter cree creer construis besoin stp svp
comment quoi que qui quel quelle plus pas ne si se sa son ses leur leurs mais donc car""".split())

FEATURE_WORDS = re.compile(
    r"\b(projet|project|application|app|plateforme|platform|mvp|from scratch|de zero|architecture|refonte|"
    r"migration|migrate|syst[eè]me|system|feature|fonctionnalit[eé]|module|produit|product|backend|frontend|"
    r"full[- ]?stack|pipeline|service|api)\b", re.I)


def is_subagent_brief(prompt: str, roster: dict) -> bool:
    """Subagent briefs start with 'You are <Name>, ...': never re-inject the huddle into them (no recursion)."""
    names = [m["name"] for m in roster.get("members", [])]
    if names and re.match(r"^\s*(tu es|you are|vous [eê]tes)\s+(" + "|".join(map(re.escape, names)) + r")\b", prompt, re.I):
        return True
    head = prompt[:400].lower()
    return "team kuro" in head and "persona" in head


def already_injected(transcript: str, count: int, prompt: str) -> bool:
    """Inject at most once per user instruction, even if the host calls the hook before every model step."""
    key = hashlib.sha1(os.path.abspath(transcript).encode("utf-8")).hexdigest()[:16]
    sig = f"{count}:{hashlib.sha1(prompt.encode('utf-8')).hexdigest()[:12]}"
    state = Path(tempfile.gettempdir()) / "kuro_huddle_state"
    try:
        state.mkdir(exist_ok=True)
        f = state / key
        if f.exists() and f.read_text(encoding="utf-8") == sig:
            return True
        f.write_text(sig, encoding="utf-8")
    except Exception:
        pass
    return False


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


SHORT_OK = {"go", "ai", "ui", "ux", "ci", "cd", "db", "qa", "c#", "k8s", "jwt", "sql", "api", "xss", "csp"}

# Common French dev vocabulary -> the English words used in skill descriptions
SYN = {
    "charge": "load", "performance": "performance", "lenteur": "slow", "lent": "slow", "securite": "security",
    "sécurité": "security", "securise": "security", "sécurisé": "security", "authentification": "authentication",
    "autorisation": "authorization", "mot": "password", "donnees": "data", "données": "data", "base": "database",
    "deploiement": "deployment", "déploiement": "deployment", "deployer": "deploy", "déployer": "deploy",
    "erreur": "error", "bogue": "bug", "plantage": "crash", "documentation": "documentation", "doc": "documentation",
    "tests": "test", "tester": "test", "revue": "review", "refonte": "refactoring", "migration": "migration",
    "interface": "ui", "accessibilite": "accessibility", "accessibilité": "accessibility", "mobile": "mobile",
    "reservation": "booking", "réservation": "booking", "conteneur": "container", "surveillance": "monitoring",
    "journaux": "logs", "faille": "vulnerability", "vulnerabilite": "vulnerability", "vulnérabilité": "vulnerability",
    "exigences": "requirements", "besoin": "requirements", "spec": "specification", "architecture": "architecture",
    "versions": "version", "livraison": "release", "publication": "release", "apprentissage": "learning",
    "donnee": "data", "pipeline": "pipeline", "stockage": "storage", "cache": "cache", "latence": "latency",
}


def stem(w: str) -> str:
    return w[:-1] if len(w) > 4 and w.endswith("s") else w


def tokens(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9àâäçéèêëîïôöùûüœ+#.\-]{2,}", text.lower())
    out = []
    for w in words:
        w = w.strip(".-")
        if len(w) < 2 or w in STOP:
            continue
        if len(w) == 2 and w not in SHORT_OK and not any(c.isdigit() for c in w):
            continue
        out.append(w)
    return out


def norm_tokens(text: str) -> set[str]:
    res: set[str] = set()
    for w in tokens(text):
        res.add(stem(w))
        if w in SYN:
            res.add(stem(SYN[w]))
    return res


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    key = None
    for line in m.group(1).splitlines():
        k = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if k:
            key = k.group(1)
            out[key] = k.group(2).strip().strip('"').strip("'")
        elif key and line.startswith((" ", "\t")):
            out[key] += " " + line.strip()
    return out


def load_skills() -> dict[str, set[str]]:
    skills: dict[str, set[str]] = {}
    if not SKILLS_DIR.exists():
        return skills
    for d in SKILLS_DIR.iterdir():
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        try:
            fm = frontmatter(f.read_text(encoding="utf-8", errors="replace")[:4000])
        except Exception:
            continue
        name = fm.get("name") or d.name
        toks = norm_tokens(name.replace("-", " ")) | norm_tokens(fm.get("description", ""))
        # name tokens are strong signals: also add the bare hyphenated name
        toks.add(name.lower())
        skills[name] = toks
    return skills


def last_prompt_and_count(transcript: str) -> tuple[str | None, int]:
    prompt, count = None, 0
    try:
        with open(transcript, "r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("source") == "USER_EXPLICIT" and d.get("type") == "USER_INPUT":
                    content = d.get("content", "")
                    if "<USER_REQUEST>" in content:
                        a = content.find("<USER_REQUEST>") + len("<USER_REQUEST>")
                        b = content.find("</USER_REQUEST>")
                        content = content[a:b] if b != -1 else content[a:]
                    prompt = content.strip()
                    count += 1
    except Exception:
        return None, 0
    return prompt, count


def route(prompt: str, skills: dict[str, set[str]], roster: dict):
    """Return (ranked skills [(name, score)], participants [member names], gap bool)."""
    ptoks = norm_tokens(prompt)
    # also match hyphenated skill names written verbatim, e.g. "spring-security"
    low = prompt.lower()
    df: dict[str, int] = {}
    for toks in skills.values():
        for t in toks:
            df[t] = df.get(t, 0) + 1
    n = max(len(skills), 1)
    scores = []
    for name, toks in skills.items():
        s = 0.0
        for t in ptoks & toks:
            s += math.log(1 + n / df[t])
        if name in low:
            s += 6.0
        if s > 0:
            scores.append((name, s))
    scores.sort(key=lambda x: -x[1])
    best = scores[0][1] if scores else 0.0
    top = [(n_, s) for n_, s in scores if s >= 3.0 and s >= 0.5 * best][:4]   # drop weak, noisy matches
    primary: dict[str, list[str]] = {}
    optional: dict[str, list[str]] = {}
    for m in roster.get("members", []):
        for sk in m.get("skills", []):
            primary.setdefault(sk, []).append(m["name"])
        for sk in m.get("optional_skills", []):
            optional.setdefault(sk, []).append(m["name"])
    core: list[str] = []          # members who primarily own a matched skill
    people: list[str] = []        # core first, then optional owners
    for name, _ in top:
        for o in primary.get(name, []):
            if o not in core:
                core.append(o)
    people.extend(core)
    for name, _ in top:
        for o in optional.get(name, []):
            if o not in people:
                people.append(o)
    gap = not top and len(tokens(prompt)) >= 3     # technical-looking request nothing installed covers
    return top, people, core, gap


def tier_for(prompt: str, top, core) -> str:
    words = len(prompt.split())
    feature_hits = len(FEATURE_WORDS.findall(prompt))
    content = len(tokens(prompt))          # meaningful words left after stop-word removal
    if not top and feature_hits == 0 and content <= 2:
        return "SOLO"                       # chit-chat, thanks, one-word follow-ups
    if len(core) >= 4 or words > 70 or (feature_hits >= 2 and len(core) >= 2):
        return "FEATURE"
    return "FOCUSED"                        # technical request: consult, even if no skill matched


def build_message(mode: str, first: bool, prompt: str, tier: str, top, people, gap: bool, cfg: dict) -> str:
    lines = [f"[TEAM KURO HUDDLE | mode={mode} | tier={tier}]"]
    if first:
        lines.append("SESSION START: load team/roster.json; read PROJECT_STATE.md if present (skill project-state) "
                     "and greet in 2 lines; keep subagents lazy (spawn on first need, then reuse via manage_subagents).")
    maxp = int(cfg.get("max_participants", 4))
    if top:
        lines.append("Candidate skills: " + ", ".join(f"{n}" for n, _ in top))
    if people and tier != "SOLO":
        lines.append("Suggested participants: " + ", ".join(people[:maxp])
                     + (" (+ Njoya to arbitrate, Hayatou/Lukong gates if code changes)" if tier == "FEATURE" else ""))
    rounds = int(cfg.get("max_rounds", 2))
    if tier == "SOLO":
        lines.append("SOLO: answer directly after a quick self-check by the most relevant role; no subagents.")
    elif tier == "FOCUSED":
        lines.append("FOCUSED: consult the 1-2 relevant roles (real subagents, blind positions, one exchange round); "
                     "answer with their input and name who contributed.")
    else:
        lines.append(f"FEATURE: full concertation per skill team-orchestration (briefs = question not answer; blind round, "
                     f"exchange, max {rounds} rounds; Njoya decides + ADR; gates; real-message log only).")
    if gap and tier != "SOLO":
        lines.append("COVERAGE GAP: no installed skill matches well. Follow team-orchestration/references/"
                     "capability-acquisition.md (acquire a vetted skill, or author one, or create a specialist agent) "
                     f"- skill_acquisition={cfg.get('skill_acquisition', 'ask')}, agent_creation={cfg.get('agent_creation', 'ask')}.")
    if tier == "FEATURE" and cfg.get("reporter", {}).get("enabled", True):
        ledger = (TEAM_DIR / "tools" / "kuro_ledger.py").as_posix()
        lines.append(f'REPORTER: Mbarga keeps the ledger (skill team-reporting; python "{ledger}" --root <project>): '
                     "plan tasks BEFORE work, set in_progress/done write-ahead, log milestones, notify; "
                     "prepare handoff packets if quota is at risk.")
    lines.append("Protocol details: skills/team-orchestration/references/concertation.md. Persona = tone only; be honest about what was run.")
    return "\n".join(lines)


def main() -> None:
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        transcript = json.loads(raw).get("transcriptPath") if raw else None
        cfg = load_json(TEAM_DIR / "config.json", {})
        mode = (os.environ.get("KURO_CONCERTATION") or cfg.get("concertation") or "always").lower()
        if mode == "off" or not transcript:
            print("{}")
            return
        prompt, count = last_prompt_and_count(transcript)
        if not prompt:
            print("{}")
            return
        roster = load_json(TEAM_DIR / "roster.json", {})
        if is_subagent_brief(prompt, roster) or already_injected(transcript, count, prompt):
            print("{}")
            return
        skills = load_skills()
        top, people, core, gap = route(prompt, skills, roster)
        tier = tier_for(prompt, top, core)
        if mode == "auto" and tier == "SOLO" and count > 1:
            print("{}")
            return
        msg = build_message(mode, count == 1, prompt, tier, top, people, gap, cfg)
        print(json.dumps({"injectSteps": [{"ephemeralMessage": msg}]}, ensure_ascii=False))
    except Exception:
        print("{}")


if __name__ == "__main__":
    main()
