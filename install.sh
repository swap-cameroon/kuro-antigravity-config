#!/usr/bin/env bash
# Team Kuro installer for macOS / Linux (same behaviour as install.ps1).
# Usage: ./install.sh [--dry-run] [--target DIR] [--skip-validation]
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${HOME}/.gemini/config"
DRY=0
SKIP_VALIDATION=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --target) TARGET="$2"; shift ;;
    --skip-validation) SKIP_VALIDATION=1 ;;
    -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

run() { if [ "$DRY" -eq 1 ]; then echo "  [dry] $*"; else "$@"; fi; }

echo "Team Kuro installer: $REPO -> $TARGET$([ "$DRY" -eq 1 ] && echo ' (dry run)')"

if [ "$SKIP_VALIDATION" -eq 0 ] && command -v python3 >/dev/null 2>&1; then
  python3 "$REPO/scripts/validate.py"
fi

run mkdir -p "$TARGET"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$TARGET/.kuro-backup/$STAMP"
for d in plugins skills team; do
  if [ -d "$TARGET/$d" ]; then
    run mkdir -p "$BACKUP"
    run cp -R "$TARGET/$d" "$BACKUP/"
  fi
done

# legacy paths from earlier versions
run rm -rf "$TARGET/plugins/token-optimization/skills" "$TARGET/skills/token-optimization"

for d in plugins skills team; do
  run mkdir -p "$TARGET/$d"
  run cp -R "$REPO/$d/." "$TARGET/$d/"
done

# machine-specific config: create only when missing
[ -e "$TARGET/config.json" ]     || run cp "$REPO/config.example.json" "$TARGET/config.json"
[ -e "$TARGET/hooks.json" ]      || run cp "$REPO/hooks.json" "$TARGET/hooks.json"
[ -e "$TARGET/mcp_config.json" ] || run cp "$REPO/mcp_config.json" "$TARGET/mcp_config.json"

if [ "$DRY" -eq 0 ]; then
  n=0
  for s in "$REPO"/skills/*/; do
    name="$(basename "$s")"
    [ -f "$TARGET/skills/$name/SKILL.md" ] || { echo "missing skill: $name" >&2; exit 1; }
    n=$((n + 1))
  done
  echo "OK: $n skills installed"
  if command -v agy >/dev/null 2>&1; then agy plugins list || echo "note: 'agy plugins list' failed"; else
    echo "note: agy not in PATH - install Antigravity, then run: agy plugins list"; fi
fi
