"""Tests for the Team Kuro quality checks. Run: python -m unittest discover -s team/tools"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "kuro_check.py"
ENV = dict(os.environ, PYTHONUTF8="1")

GOOD_PRD = """# PRD: Room booking
## 1. Problem & outcomes
Staff lose 20 min per booking; target 2 min.
## 2. Users & jobs
Office manager.
## 3. Journeys
1. Open the calendar. 2. Pick a slot.
## 4. Scope
Must: booking. Non-goals: payments.
## 5. Requirements
- US-1 As a manager I book a room so that meetings are not double-booked.
  - AC-1.1 Given a free slot, when I confirm, then the booking appears within 2 seconds.
  - AC-1.2 Given a taken slot, when I confirm, then I get error 409 and no booking is created.
## 6. Non-functional
p95 under 300 ms.
"""

GOOD_ADR = """# 0001 Use PostgreSQL
Status: accepted
## Context
We need transactions.
## Decision
PostgreSQL 16.
## Alternatives considered
MongoDB rejected: no multi-document invariants needed elsewhere.
## Consequences
One more service to operate.
"""


def run(root, *args):
    r = subprocess.run([sys.executable, str(TOOL), "--root", str(root), *args], capture_output=True, text=True,
                       env=ENV, encoding="utf-8", timeout=60)
    return r.returncode, r.stdout + r.stderr


def git(root, *args):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.com",
                    "-c", "commit.gpgsign=false", *args], capture_output=True, text=True, check=True)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")

    # ---- PRD
    def test_good_prd_passes(self):
        self.write("PRD.md", GOOD_PRD)
        code, out = run(self.root, "prd")
        self.assertEqual(code, 0, out)
        self.assertIn("2 numbered acceptance criteria", out)

    def test_missing_prd_fails(self):
        code, out = run(self.root, "prd")
        self.assertEqual(code, 1)
        self.assertIn("not found", out)

    def test_prd_without_criteria_or_non_goals_fails(self):
        self.write("PRD.md", GOOD_PRD.replace("AC-1.1 ", "").replace("AC-1.2 ", "").replace("Non-goals: payments.", ""))
        code, out = run(self.root, "prd")
        self.assertEqual(code, 1)
        self.assertIn("no numbered acceptance criterion", out)
        self.assertIn("no non-goals", out)

    def test_vague_or_unstructured_criteria_fail(self):
        self.write("PRD.md", GOOD_PRD.replace("then the booking appears within 2 seconds", "then it is fast and intuitive")
                   .replace("Given a taken slot, when I confirm, then I get error 409 and no booking is created",
                            "Double booking is impossible"))
        code, out = run(self.root, "prd")
        self.assertEqual(code, 1)
        self.assertIn("vague words without a number: AC-1.1", out)
        self.assertIn("not Given/When/Then: AC-1.2", out)

    def test_french_prd_is_understood(self):
        self.write("PRD.md", """# PRD
## Problème et objectifs
## Utilisateurs
## Parcours
## Périmètre
Hors périmètre : paiement.
## Exigences
- AC-1.1 Étant donné un créneau libre, quand je confirme, alors la réservation apparaît en moins de 2 s.
## Exigences non-fonctionnelles
""")
        code, out = run(self.root, "prd")
        self.assertEqual(code, 0, out)

    # ---- ADR
    def test_adr_complete_and_incomplete(self):
        self.write("docs/adr/0001-postgres.md", GOOD_ADR)
        self.assertEqual(run(self.root, "adr")[0], 0)
        self.write("docs/adr/0002-cache.md", "# 0002 Add Redis\nStatus: accepted\n## Context\nSlow.\n## Decision\nRedis.\n")
        code, out = run(self.root, "adr")
        self.assertEqual(code, 1)
        self.assertIn("0002-cache.md is missing: rejected alternatives, consequences", out)

    def test_architecture_without_adr_fails(self):
        self.assertEqual(run(self.root, "adr")[0], 0)            # nothing designed yet: only a warning
        self.write("ARCHITECTURE.md", "# Architecture\n")
        code, out = run(self.root, "adr")
        self.assertEqual(code, 1)
        self.assertIn("no decision is recorded", out)

    # ---- PROJECT_STATE
    def state(self, sha, extra=""):
        return (f"# PROJECT_STATE\n## 1. Active context\n- **Branch**: main | **Last verified commit**: {sha} on 2026-01-01\n"
                f"## 5. Next 3 actions\n1. Wire the login form\n2. Add the migration\n{extra}")

    def test_state_freshness_against_git_head(self):
        git(self.root, "init", "-q")
        self.write("a.txt", "1")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "one")
        sha = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True).stdout.strip()
        self.write("PROJECT_STATE.md", self.state(sha))
        code, out = run(self.root, "state")
        self.assertEqual(code, 0, out)
        self.assertIn("verified at HEAD", out)
        self.write("a.txt", "2")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "two")
        code, out = run(self.root, "state")
        self.assertEqual(code, 0, out)                            # slightly behind: warning with the command to run
        self.assertIn("1 commit(s) behind HEAD", out)
        self.write("PROJECT_STATE.md", self.state("deadbee"))
        code, out = run(self.root, "state")
        self.assertEqual(code, 1)
        self.assertIn("unknown to this repository", out)

    def test_state_template_or_secret_fails(self):
        self.write("PROJECT_STATE.md", "# PROJECT_STATE\n- **Project**: <name> - <purpose>\n- **Branch**: <branch>\n"
                                       "- **Stack**: <stack>\n- **Docs**: <docs>\n## 5. Next 3 actions\n1. <action>\n")
        code, out = run(self.root, "state")
        self.assertEqual(code, 1)
        self.assertIn("template placeholders left", out)
        self.assertIn("no concrete next action", out)
        self.write("PROJECT_STATE.md", self.state("abc1234", "api_key=SUPERSECRETVALUE123\n"))
        self.assertIn("contains a secret", run(self.root, "state")[1])

    # ---- CONVENTIONS
    def test_conventions_init_reads_repo_evidence(self):
        self.write("package.json", json.dumps({"scripts": {"test": "vitest", "lint": "eslint .", "build": "ng build"},
                                               "dependencies": {"@angular/core": "^20.0.0"},
                                               "devDependencies": {"typescript": "^5", "vitest": "^3", "eslint": "^9"}}))
        self.write("pnpm-lock.yaml", "")
        self.write("tsconfig.json", '{"compilerOptions": {"strict": true}}')
        code, out = run(self.root, "conventions")
        self.assertEqual(code, 0)                                  # absent: a warning, not a failure
        self.assertIn("conventions --init", out)
        self.assertEqual(run(self.root, "conventions", "--init")[0], 0)
        text = (self.root / "CONVENTIONS.md").read_text(encoding="utf-8")
        for needle in ("Node (pnpm), TypeScript", "Angular ^20.0.0", "`pnpm run test`", "Vitest", "eslint",
                       "TypeScript strict mode", "TODO(user)", "UNVERIFIED"):
            self.assertIn(needle, text)
        code, out = run(self.root, "conventions", "--init")
        self.assertEqual(code, 1)                                  # never overwrites the user's file
        code, out = run(self.root, "conventions")
        self.assertIn("TODO(user) line(s) still to fill in", out)

    def test_all_runs_every_existing_document(self):
        self.write("PRD.md", GOOD_PRD)
        self.write("docs/adr/0001-postgres.md", GOOD_ADR)
        code, out = run(self.root, "all")
        self.assertEqual(code, 1)                                  # PROJECT_STATE.md is missing
        self.assertIn("PASS prd", out)
        self.assertIn("PASS adr", out)
        self.assertIn("FAIL state", out)
        self.assertIn("FAILED: 1 failing check(s)", out)


if __name__ == "__main__":
    unittest.main()
