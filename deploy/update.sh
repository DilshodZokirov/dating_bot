#!/usr/bin/env bash
# VPS da: kodni yangilab production stack ni qayta ishga tushirish
set -euo pipefail
cd "$(dirname "$0")/.."

git pull origin main
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
docker compose -f docker-compose.prod.yml ps
curl -fsS "https://${DOMAIN:-localhost}/health" || curl -fsS http://127.0.0.1/health || true
echo "OK — deploy tugadi"
