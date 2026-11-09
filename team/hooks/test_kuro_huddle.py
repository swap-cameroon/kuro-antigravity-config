"""Tests for the Team Kuro huddle hook (stdlib only). Run: python -m unittest discover -s team/hooks"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "kuro_huddle.py"


def run_hook(prompts, env_extra=None, transcript=True):
    """Feed the hook a transcript whose user inputs are `prompts`; return the parsed stdout."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "transcript.jsonl"
        lines = []
        for p in prompts:
            lines.append(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT",
                                     "content": f"<USER_REQUEST>{p}</USER_REQUEST>"}))
            lines.append(json.dumps({"source": "MODEL", "type": "PLANNER_RESPONSE", "content": "ok"}))
        path.write_text("\n".join(lines), encoding="utf-8")
        env = dict(os.environ, PYTHONUTF8="1")
        env.pop("KURO_CONCERTATION", None)
        env.update(env_extra or {})
        stdin = json.dumps({"transcriptPath": str(path) if transcript else None})
        out = subprocess.run([sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True,
                             env=env, timeout=30, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def message(result):
    steps = result.get("injectSteps") or []
    return steps[0]["ephemeralMessage"] if steps else ""


class HuddleTests(unittest.TestCase):
    def test_trivial_is_solo(self):
        m = message(run_hook(["bonjour, ca va ?"]))
        self.assertIn("tier=SOLO", m)
        self.assertIn("no subagents", m)

    def test_session_start_only_on_first_prompt(self):
        self.assertIn("SESSION START", message(run_hook(["bonjour"])))
        self.assertNotIn("SESSION START", message(run_hook(["bonjour", "merci"])))

    def test_jwt_spring_routes_to_security_and_backend(self):
        m = message(run_hook(["ajouter une authentification JWT a une API Spring Boot avec refresh token"]))
        self.assertNotIn("tier=SOLO", m)
        self.assertTrue(any(s in m for s in ("spring-security", "secure-by-design-coding")), m)
        self.assertTrue(any(p in m for p in ("Hayatou", "Kamdem")), m)

    def test_big_project_is_feature(self):
        m = message(run_hook(["Je veux creer une application de reservation de salles avec backend API, "
                              "frontend Angular, base PostgreSQL, authentification, tests et deploiement Docker"]))
        self.assertIn("tier=FEATURE", m)
        self.assertIn("team-orchestration", m)

    def test_unknown_domain_flags_coverage_gap(self):
        m = message(run_hook(["ecris un compilateur de shaders en Zig pour un GPU embarque"]))
        self.assertIn("COVERAGE GAP", m)
        self.assertIn("capability-acquisition", m)

    def test_off_mode_injects_nothing(self):
        self.assertEqual(run_hook(["ajouter JWT a une API Spring"], {"KURO_CONCERTATION": "off"}), {})

    def test_auto_mode_skips_trivial_after_first_turn(self):
        self.assertEqual(run_hook(["bonjour", "merci beaucoup"], {"KURO_CONCERTATION": "auto"}), {})

    def test_missing_transcript_is_safe(self):
        self.assertEqual(run_hook(["x"], transcript=False), {})

    def test_never_echoes_user_text(self):
        secret = "SECRET-TOKEN-12345"
        m = message(run_hook([f"ajouter JWT a Spring avec la cle {secret}"]))
        self.assertNotIn(secret, m)

    def test_feature_mentions_reporter_with_ledger_path(self):
        m = message(run_hook(["Je veux creer une application de reservation de salles avec backend API, "
                              "frontend Angular, base PostgreSQL, authentification, tests et deploiement Docker"]))
        self.assertIn("REPORTER: Mbarga", m)
        self.assertIn("kuro_ledger.py", m)
        self.assertLess(len(m) // 4, 330)

    def test_focused_has_no_reporter_line(self):
        self.assertNotIn("REPORTER", message(run_hook(["ajouter JWT a une API Spring Boot"])))

    def test_subagent_briefs_are_not_injected(self):
        brief = "Tu es Kamdem, Lead Backend de Team Kuro (persona Bamileke). Tu es en mode PLAN. Analyse le PRD."
        self.assertEqual(run_hook([brief]), {})
        self.assertEqual(run_hook(["You are Hayatou, Principal Security Architect of Team Kuro. Review this."]), {})

    def test_injected_once_per_instruction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.jsonl"
            path.write_text(json.dumps({"source": "USER_EXPLICIT", "type": "USER_INPUT",
                                        "content": "ajouter JWT a une API Spring Boot"}), encoding="utf-8")
            env = dict(os.environ, PYTHONUTF8="1")
            env.pop("KURO_CONCERTATION", None)
            def call():
                r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"transcriptPath": str(path)}),
                                   capture_output=True, text=True, env=env, encoding="utf-8")
                return json.loads(r.stdout)
            self.assertTrue(call().get("injectSteps"))
            self.assertEqual(call(), {})          # same instruction, hook called again before another model step
            path.write_text(path.read_text(encoding="utf-8") + chr(10) + json.dumps(
                {"source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "ajoute aussi un rate limiting"}),
                encoding="utf-8")
            self.assertTrue(call().get("injectSteps"))   # new instruction -> injected again

    def test_output_is_short(self):
        m = message(run_hook(["ajouter JWT a une API Spring Boot"]))
        self.assertLess(len(m) // 4, 260, "huddle message must stay cheap (<260 tokens)")


if __name__ == "__main__":
    unittest.main()
