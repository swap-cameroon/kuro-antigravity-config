#!/usr/bin/env python3
"""Team Kuro PreInvocation hook: automatic session bootstrap + per-instruction huddle.

Runs before every agent turn. Reads the last user instruction from the transcript, routes it
deterministically (no model tokens) to roster members and installed skills, and injects a short
ephemeral message telling the orchestrator how to convene the team for THIS instruction.

Hook protocol (same as token-saver's interceptor):
  stdin : JSON with "transcriptPath"
  stdout: {"injectSteps": [{"ephemeralMessage": "..."}]}   or   {}

Tiers (smallest safe workflow wins):
  SOLO     chit-chat                      -> answer directly
  TRIVIAL  rename, typo, explain, lookup  -> do it yourself, no subagents
  FOCUSED  one or two domains             -> the owning role does it, cross-review only where it matters
  FEATURE  three or more domains, or a new product -> wave plan from roster.lifecycle, parallel inside a wave

Config: team/config.json  ->  "concertation": "always" | "auto" | "off"  (env KURO_CONCERTATION overrides;
default "auto": SOLO and TRIVIAL turns inject nothing after the first turn).
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
import unicodedata
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

# All patterns below run on accent-folded, lower-cased text (see fold()).
PRODUCT_WORDS = re.compile(
    r"\b(projet|project|application|app|plateforme|platform|mvp|produit|product|saas|site|systeme|system|"
    r"full[- ]?stack|fonctionnalite|feature|module)\b")
BUILD_WORDS = re.compile(
    r"\b(cree\w*|creat\w*|construi\w*|build\w*|develop\w*|implement\w*|concevoir|concois|lance\w*|"
    r"from scratch|de zero|nouveau projet|new project|refonte|rewrite|reecri\w*|migr\w+)\b")
TRIVIAL_WORDS = re.compile(
    r"\b(typo|faute de frappe|fautes? d.orthographe|orthographe|renomm\w*|rename\w*|reformat\w*|formate\w*|"
    r"expliqu\w*|explain\w*|c.est quoi|qu.est[- ]ce que|que fait|what is|what does|how does|comment fonctionne|"
    r"commentaire\w*|traduis\w*|traduction|translate\w*|resume\w*|summari[sz]e\w*|montre\w*|affiche\w*|liste\w*|"
    r"show me|list the|ou est|ou se trouve|where is)\b")


def fold(text: str) -> str:
    """Lower-case and strip accents so 'sécurité' and 'securite' route the same way."""
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


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


SHORT_OK = {"go", "ai", "ia", "ui", "ux", "ci", "cd", "db", "qa", "pr", "c#", "k8s", "jwt", "sql", "api", "xss", "csp"}

# Common French dev vocabulary -> the English words used in skill descriptions
SYN = {
    "charge": "load", "lenteur": "slow", "lent": "slow", "lente": "slow", "securite": "security",
    "securise": "security", "securiser": "security", "authentification": "authentication",
    "autorisation": "authorization", "donnees": "data", "donnee": "data", "base": "database",
    "deploiement": "deployment", "deployer": "deploy", "deploie": "deploy", "erreur": "error", "bogue": "bug",
    "plantage": "crash", "plante": "crash", "echoue": "failing bug", "echec": "failing bug", "casse": "failing bug",
    "corrige": "fix", "corriger": "fix", "repare": "fix", "debogue": "debugging", "deboguer": "debugging",
    "doc": "documentation", "tests": "test", "tester": "test", "teste": "test", "revue": "review",
    "relis": "review", "refonte": "refactoring", "refactorise": "refactoring", "refactoriser": "refactoring",
    "nettoie": "refactoring", "interface": "ui", "accessibilite": "accessibility", "reservation": "booking",
    "conteneur": "container", "surveillance": "monitoring", "journaux": "logs", "faille": "vulnerability",
    "vulnerabilite": "vulnerability", "exigences": "requirements", "besoin": "requirements",
    "spec": "specification", "versions": "version", "livraison": "release", "publication": "release",
    "apprentissage": "learning", "stockage": "storage", "latence": "latency", "optimise": "optimization",
    "optimiser": "optimization", "requete": "query", "requetes": "query", "recette": "acceptance uat",
    "navigateur": "browser", "exploratoire": "exploratory", "bout": "end-to-end e2e", "e2e": "end-to-end e2e",
    "playwright": "playwright e2e", "ergonomie": "ui usability", "testeur": "test tester",
    "jeton": "token", "jetons": "token", "equipe": "team", "avancement": "progress", "reprise": "resume handoff",
}


def stem(w: str) -> str:
    return w[:-1] if len(w) > 4 and w.endswith("s") else w


def tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9+#./\-]{2,}", fold(text))
    out = []
    for w in words:
        w = w.strip(".-/")
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
            res.update(stem(part) for part in SYN[w].split())
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
    """skill name -> routing tokens (description + name); name tokens are also stored as 'name:<tok>'."""
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
        name_toks = norm_tokens(name.replace("-", " "))
        toks = name_toks | norm_tokens(fm.get("description", "")) | {"name:" + t for t in name_toks}
        toks.add(name.lower())
        skills[name] = toks
    return skills


def last_prompt_and_count(transcript: str) -> tuple[str | None, int]:
    prompt, count = None, 0
    try:
        with open(transcript, "r", encoding="utf-8-sig") as fh:
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


NAME_BONUS = 1.5     # a prompt word that is part of a skill's name is a stronger signal than its description


def match_members(prompt: str, roster: dict) -> list[tuple[str, int]]:
    """Members whose roster `triggers` appear in the prompt, best match first: [(name, hits)]."""
    ptoks = norm_tokens(prompt)
    low = " " + re.sub(r"\s+", " ", fold(prompt)) + " "
    hits: list[tuple[str, int]] = []
    for m in roster.get("members", []):
        n = 0
        for t in m.get("triggers", []):
            t = fold(t)
            if " " in t:
                n += 1 if f" {t}" in low else 0
            elif stem(t) in ptoks:
                n += 1
        if n:
            hits.append((m["name"], n))
    hits.sort(key=lambda x: -x[1])
    return hits


def route(prompt: str, skills: dict[str, set[str]], roster: dict):
    """Return (skills [(name, score)], participants [names], domains {str}, gap bool)."""
    ptoks = norm_tokens(prompt)
    low = fold(prompt)
    df: dict[str, int] = {}
    for toks in skills.values():
        for t in toks:
            df[t] = df.get(t, 0) + 1
    n = max(len(skills), 1)
    all_scores: dict[str, float] = {}
    for name, toks in skills.items():
        sc = 0.0
        for t in ptoks & toks:
            sc += math.log(1 + n / df[t])
            if "name:" + t in toks:
                sc += NAME_BONUS
        if name in low:
            sc += 6.0
        if sc > 0:
            all_scores[name] = sc
    ranked = sorted(all_scores.items(), key=lambda x: -x[1])
    best = ranked[0][1] if ranked else 0.0
    top = [(n_, sc) for n_, sc in ranked if sc >= 3.0 and sc >= 0.5 * best][:4]   # drop weak, noisy matches

    members = {m["name"]: m for m in roster.get("members", [])}
    primary: dict[str, list[str]] = {}
    optional: dict[str, list[str]] = {}
    for m in members.values():
        for sk in m.get("skills", []):
            primary.setdefault(sk, []).append(m["name"])
        for sk in m.get("optional_skills", []):
            optional.setdefault(sk, []).append(m["name"])

    triggered = [name for name, _ in match_members(prompt, roster)]
    shared = set(roster.get("shared_skills", []))
    if triggered:
        # Explicit intent wins: keep only playbooks these members own, so a stray word ("test", "page")
        # cannot pull in an unrelated skill or a third domain.
        people = list(triggered)
        mine = {sk for w in people for sk in members[w].get("skills", []) + members[w].get("optional_skills", [])}
        top = [(n_, sc) for n_, sc in top if n_ in mine or n_ in shared]
    else:
        people = []
        for name, _ in top:                                  # primary owners of matched skills
            for o in primary.get(name, []):
                if o not in people:
                    people.append(o)
        if not people:                                       # optional owners only as a last resort
            for name, _ in top:
                for o in optional.get(name, []):
                    if o not in people:
                        people.append(o)

    # A triggered member with no matched skill still brings their best playbook (e.g. Matip -> systematic-debugging).
    names = [n_ for n_, _ in top]
    for who in triggered[:2]:
        own = members[who].get("skills", [])
        if own and not any(sk in names for sk in own) and len(names) < 4:
            names.append(max(own, key=lambda sk: all_scores.get(sk, 0.0)))
    top = [(n_, all_scores.get(n_, 0.0)) for n_ in names]

    domains = {members[p].get("domain", p) for p in people if p in members}
    gap = not top and not people and len(tokens(prompt)) >= 3   # nothing installed and nobody on the team covers it
    return top, people, domains, gap


def tier_for(prompt: str, top, people, domains) -> str:
    low = fold(prompt)
    content = len(tokens(prompt))          # meaningful words left after stop-word removal
    product = bool(PRODUCT_WORDS.search(low))
    build = bool(BUILD_WORDS.search(low))
    if not top and not people and not product and content <= 2:
        return "SOLO"                       # chit-chat, thanks, one-word follow-ups
    if len(domains) >= 3 or (build and product and len(domains) >= 2):
        return "FEATURE"                    # breadth, not prompt length, is what makes a feature
    if TRIVIAL_WORDS.search(low) and not build and len(domains) <= 1:
        return "TRIVIAL"                    # rename, typo, explanation, lookup: never worth a subagent
    return "FOCUSED"


def waves(roster: dict) -> str:
    """'Ngono > Njoya > Kouam+Kamdem > ...' from roster.lifecycle (a list of waves; a bare name is a 1-member wave)."""
    out = []
    for w in roster.get("lifecycle", []):
        out.append("+".join(w) if isinstance(w, list) else str(w))
    return " > ".join(out)


def build_message(mode: str, first: bool, tier: str, top, people, gap: bool, cfg: dict, roster: dict) -> str:
    lines = [f"[TEAM KURO HUDDLE | mode={mode} | tier={tier}]"]
    if first:
        lines.append("SESSION START: load team/roster.json; read PROJECT_STATE.md and CONVENTIONS.md if present "
                     "(skill project-state; they outrank skill defaults); greet in 2 lines; spawn subagents lazily "
                     "and reuse them (manage_subagents).")
    maxp = int(cfg.get("max_participants", 4))
    named = cfg.get("models", {}) if isinstance(cfg.get("models"), dict) else {}
    models = {}
    for m in roster.get("members", []):       # class from the roster, real model name from config when the user set one
        cls = m.get("model_tier", "")
        models[m["name"]] = f"{cls}: {named[cls]}" if named.get(cls) else cls
    ledger = (TEAM_DIR / "tools" / "kuro_ledger.py").as_posix()

    if top:
        lines.append("Candidate skills: " + ", ".join(n for n, _ in top))
    if people and tier != "SOLO":
        label = "Suggested participants" if tier == "FEATURE" else "Owner" if tier == "TRIVIAL" else "Owners"
        shown = people[:1] if tier == "TRIVIAL" else people[:min(2, maxp)] if tier == "FOCUSED" else people[:maxp]
        lines.append(f"{label}: " + ", ".join(f"{p} ({models[p]})" if models.get(p) and tier != "TRIVIAL" else p
                                              for p in shown))
    rounds = int(cfg.get("max_rounds", 2))
    if tier == "SOLO":
        lines.append("SOLO: answer directly; no subagents.")
    elif tier == "TRIVIAL":
        lines.append("TRIVIAL: do it yourself in the owner's voice; no subagents, no debate. "
                     "Read a candidate skill only if a domain rule applies.")
    elif tier == "FOCUSED":
        lines.append("FOCUSED: the owning role does the work (one subagent only if it saves context; 2 owners with "
                     "disjoint files run in parallel). No debate unless a real design choice appears. "
                     "Cross-review by Hayatou or Lukong only if auth, data or a public API changes.")
        lines.append(f'LIVE: if you delegate, `python "{ledger}" --root <project> claim|set` each task so the user '
                     "can follow with `watch`. PROOF: run the tests or build before saying done (`verify <id> --cmd`).")
    else:
        lines.append(f"FEATURE: skill team-orchestration. Waves ('+' = in parallel): {waves(roster)}. Specialists "
                     f"join the build wave. Debate only real design choices (blind, max {rounds} rounds, Njoya decides + ADR).")
        if cfg.get("reporter", {}).get("enabled", True):
            lines.append(f'REPORTER: Mbarga keeps the ledger (skill team-reporting; python "{ledger}" --root <project>): '
                         "plan tasks with files and acceptance first; `next --parallel` = batch to launch together; "
                         "agents `claim`, `verify`, `set done`; the user follows with `watch`.")
        lines.append("GATES: `kuro_check.py` (same folder): `prd` before the build wave, `adr` after architecture, "
                     "`state` at checkpoints; fix a failing check, do not argue with it.")
    if gap and tier in ("FOCUSED", "FEATURE"):
        lines.append("COVERAGE GAP: no skill or team member matches. Follow team-orchestration/references/"
                     "capability-acquisition.md "
                     f"(skill_acquisition={cfg.get('skill_acquisition', 'ask')}, agent_creation={cfg.get('agent_creation', 'ask')}).")
    lines.append("Persona = tone only; be honest about what was run. The hint can be wrong: judgement wins.")
    return "\n".join(lines)


def main() -> None:
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        transcript = json.loads(raw).get("transcriptPath") if raw else None
        cfg = load_json(TEAM_DIR / "config.json", {})
        mode = (os.environ.get("KURO_CONCERTATION") or cfg.get("concertation") or "auto").lower()
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
        top, people, domains, gap = route(prompt, skills, roster)
        tier = tier_for(prompt, top, people, domains)
        if mode == "auto" and tier in ("SOLO", "TRIVIAL") and count > 1:
            print("{}")                      # nothing useful to add: spend zero tokens
            return
        msg = build_message(mode, count == 1, tier, top, people, gap, cfg, roster)
        print(json.dumps({"injectSteps": [{"ephemeralMessage": msg}]}, ensure_ascii=False))
    except Exception:
        print("{}")


if __name__ == "__main__":
    main()
