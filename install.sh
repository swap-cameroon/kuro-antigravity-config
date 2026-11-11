#!/usr/bin/env bash
# Team Kuro installer for macOS / Linux (same behaviour as install.ps1).
# Usage: ./install.sh [--dry-run] [--target DIR] [--skip-validation] [--enable-team-hook] [--enable-interceptor]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${HOME}/.gemini/config"
DRY=0
SKIP_VALIDATION=0
TEAM_HOOK=0
INTERCEPTOR=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --target) TARGET="$2"; shift ;;
    --skip-validation) SKIP_VALIDATION=1 ;;
    --enable-team-hook) TEAM_HOOK=1 ;;
    --enable-interceptor) INTERCEPTOR=1 ;;
    -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

run() { if [ "$DRY" -eq 1 ]; then echo "  [dry] $*"; else "$@"; fi; }
PY=""
for c in python3 python; do   # keep the first interpreter that really runs (skips store shims and broken links)
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys" >/dev/null 2>&1; then PY="$(command -v "$c")"; break; fi
done

echo "Team Kuro installer: $REPO -> $TARGET$([ "$DRY" -eq 1 ] && echo ' (dry run)')"

# 1. validate
if [ "$SKIP_VALIDATION" -eq 0 ] && [ -n "$PY" ]; then
  "$PY" "$REPO/scripts/validate.py" || { echo "repository validation failed (use --skip-validation to bypass)" >&2; exit 1; }
fi

# 2-3. prepare target, back up what is about to be replaced (last 3 backups kept)
run mkdir -p "$TARGET"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$TARGET/.kuro-backup/$STAMP"
for d in plugins skills team; do
  if [ -d "$TARGET/$d" ]; then
    run mkdir -p "$BACKUP"
    run cp -R "$TARGET/$d" "$BACKUP/"
  fi
done
if [ "$DRY" -eq 0 ] && [ -d "$TARGET/.kuro-backup" ]; then
  ls -1d "$TARGET/.kuro-backup"/*/ 2>/dev/null | sort -r | tail -n +4 | while IFS= read -r old; do rm -rf "$old"; done
fi

# 4. deploy
# legacy paths from earlier versions
run rm -rf "$TARGET/plugins/token-optimization/skills" "$TARGET/skills/token-optimization"

# skills a previous install put there but the repo no longer ships (your own skills are not in the manifest: kept)
MANIFEST="$TARGET/.kuro-manifest"
if [ -f "$MANIFEST" ]; then
  while IFS= read -r old; do
    old="${old%$'\r'}"
    [ -n "$old" ] || continue
    case "$old" in */*|.*) continue ;; esac
    if [ ! -d "$REPO/skills/$old" ] && [ -d "$TARGET/skills/$old" ]; then
      echo "  remove retired skill $old"
      run rm -rf "$TARGET/skills/$old"
    fi
  done < "$MANIFEST"
fi

# team/config.json holds your tuning: keep it across installs
KEPT_CFG=""
if [ -f "$TARGET/team/config.json" ]; then
  KEPT_CFG="$(mktemp)"
  cp "$TARGET/team/config.json" "$KEPT_CFG"
fi
for d in plugins skills team; do
  run mkdir -p "$TARGET/$d"
  run cp -R "$REPO/$d/." "$TARGET/$d/"
done
if [ "$DRY" -eq 0 ]; then
  find "$TARGET/plugins" "$TARGET/skills" "$TARGET/team" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
  for s in "$REPO"/skills/*/; do basename "$s"; done > "$MANIFEST"
fi
if [ -n "$KEPT_CFG" ]; then
  echo "  team/config.json exists - your settings are kept"
  run cp "$KEPT_CFG" "$TARGET/team/config.json"
  rm -f "$KEPT_CFG"
fi

# 5. machine-specific config: create only when missing
[ -e "$TARGET/config.json" ]     || run cp "$REPO/config.example.json" "$TARGET/config.json"
[ -e "$TARGET/hooks.json" ]      || run cp "$REPO/hooks.json" "$TARGET/hooks.json"
[ -e "$TARGET/mcp_config.json" ] || run cp "$REPO/mcp_config.json" "$TARGET/mcp_config.json"

# optional hooks: merged into hooks.json, existing hooks kept, previous file saved as hooks.json.bak
register_hook() {  # name, script path
  echo "  register '$1' PreInvocation hook in hooks.json"
  [ "$DRY" -eq 1 ] && return 0
  [ -f "$TARGET/hooks.json" ] && cp "$TARGET/hooks.json" "$TARGET/hooks.json.bak"
  "$PY" - "$TARGET/hooks.json" "$1" "$PY" "$2" <<'PYEOF'
import json, sys
path, name, py, script = sys.argv[1:5]
try:
    with open(path, encoding="utf-8-sig") as fh:
        hooks = json.loads(fh.read() or "{}")
except FileNotFoundError:
    hooks = {}
hooks[name] = {"PreInvocation": [{"type": "command", "command": f'"{py}" "{script}"', "timeout": 10}]}
with open(path, "w", encoding="utf-8") as fh:
    json.dump(hooks, fh, indent=2)
    fh.write("\n")
PYEOF
}
if [ "$TEAM_HOOK" -eq 1 ] || [ "$INTERCEPTOR" -eq 1 ]; then
  [ -n "$PY" ] || { echo "--enable-team-hook/--enable-interceptor need Python on PATH" >&2; exit 1; }
  [ "$INTERCEPTOR" -eq 1 ] && register_hook "kuro-token-guard" "$TARGET/skills/token-saver/resources/intercept_wasteful_prompts.py"
  [ "$TEAM_HOOK" -eq 1 ] && register_hook "kuro-team-huddle" "$TARGET/team/hooks/kuro_huddle.py"
fi

# 6. verify
if [ "$DRY" -eq 0 ]; then
  n=0
  for s in "$REPO"/skills/*/; do
    name="$(basename "$s")"
    [ -f "$TARGET/skills/$name/SKILL.md" ] || { echo "missing skill: $name" >&2; exit 1; }
    n=$((n + 1))
  done
  echo "OK: $n skills installed"
  for p in "$REPO"/plugins/*/; do
    name="$(basename "$p")"
    [ -f "$TARGET/plugins/$name/plugin.json" ] || { echo "plugin $name not installed" >&2; exit 1; }
    echo "OK: plugin $name"
  done
  [ -f "$TARGET/team/roster.json" ] || { echo "team roster missing" >&2; exit 1; }
  echo "OK: team roster"
  if command -v agy >/dev/null 2>&1; then agy plugins list || echo "note: 'agy plugins list' failed"; else
    echo "note: agy not in PATH - install Antigravity, then run: agy plugins list"; fi
  echo "Team Kuro installed. Restart agy to load the new rules."
fi
