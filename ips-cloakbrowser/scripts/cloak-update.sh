#!/usr/bin/env bash
# Daily CloakBrowser refresh, run by launchd: wrapper, binary, MCP server, old-binary prune.
# Every step runs even if an earlier one fails; the exit code says whether any failed.
set -u

LOG="${IPS_CLOAKBROWSER_LOG:-$HOME/Library/Logs/ips-cloakbrowser-update.log}"
CACHE="${CLOAKBROWSER_CACHE_DIR:-$HOME/.cloakbrowser}"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin${PATH:+:$PATH}"

mkdir -p "$(dirname "$LOG")"
# Keep the log short: the last ~1000 lines are plenty to see recent runs.
if [ -f "$LOG" ] && [ "$(wc -l <"$LOG")" -gt 2000 ]; then
  tail -n 1000 "$LOG" >"$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
exec >>"$LOG" 2>&1

failed=0
run() {
  echo "$(date '+%F %T') \$ $*"
  "$@" || { echo "$(date '+%F %T') FAILED ($?): $*"; failed=1; }
}

echo "$(date '+%F %T') == cloak-update start"
run uv tool upgrade cloakbrowser
run cloakbrowser update
run npm install -g @playwright/mcp@latest --no-fund --no-audit --loglevel=error

# Remove binaries the wrapper no longer launches, unless a running browser still uses one.
active="$(cloakbrowser info --quick --json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["binary"]["path"] or "")' 2>/dev/null)"
if [ -n "$active" ]; then
  for dir in "$CACHE"/chromium-*; do
    [ -d "$dir" ] || continue
    case "$active" in "$dir"/*) continue ;; esac
    if pgrep -f "$dir/" >/dev/null; then
      echo "$(date '+%F %T') keep $dir (in use)"
    else
      echo "$(date '+%F %T') prune $dir"
      rm -rf "$dir"
    fi
  done
else
  echo "$(date '+%F %T') skip prune: could not resolve the active binary"
fi

run cloakbrowser info --quick
echo "$(date '+%F %T') == cloak-update end (failed=$failed)"
exit "$failed"
