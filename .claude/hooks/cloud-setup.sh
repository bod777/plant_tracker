#!/bin/bash
# Cloud-session setup (claude.ai/code). No-op on the laptop: CLAUDE_CODE_REMOTE is only set in the cloud VM.
[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0

[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q -r server/requirements.txt pytest; }

# Put the venv on PATH for the rest of the session.
[ -n "$CLAUDE_ENV_FILE" ] && echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
[ -d plant-tracker-client/node_modules ] || (cd plant-tracker-client && npm ci --no-audit --no-fund --loglevel=error)

echo "Cloud setup: .venv on PATH (run pytest from the repo root; tests stub MongoDB), client deps installed. No MongoDB or R2 in the cloud VM."
exit 0
