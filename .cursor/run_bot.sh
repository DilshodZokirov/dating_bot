#!/usr/bin/env bash
# Runs the aiogram Telegram bot. The bot needs a real Telegram token to connect.
# If no BOT_TOKEN secret is provided, stay idle instead of crash-looping.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"
# shellcheck disable=SC1091
. .venv/bin/activate

# A secret is injected as an environment variable and takes precedence over the
# placeholder in .env. Only launch the live bot when a real token is present.
if [ -z "${BOT_TOKEN:-}" ] || [ "${BOT_TOKEN:-}" = "dev-placeholder-token" ]; then
  echo "BOT_TOKEN secret is not set — the Telegram bot is idle."
  echo "Add BOT_TOKEN (and optionally WEBAPP_URL / LIVEKIT_*) as Cloud Agent secrets,"
  echo "then restart this terminal to run the live bot."
  exec tail -f /dev/null
fi

exec python -m app.bot.bot
