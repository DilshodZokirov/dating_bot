#!/usr/bin/env bash
# Per-boot service reconciliation: bring up PostgreSQL and Redis, then return.
# Must be idempotent and must not block. Safe to invoke concurrently (e.g. from
# both the environment `start` hook and a terminal) — a lock serializes runs.
set -euo pipefail

# Serialize concurrent invocations so two callers never race to start a service.
exec 9>/tmp/soyla-start.lock
flock 9

PG_VERSION=16
PG_CLUSTER=main

echo "==> Starting PostgreSQL ($PG_VERSION/$PG_CLUSTER)"
PGDATA="/var/lib/postgresql/$PG_VERSION/$PG_CLUSTER"
# A snapshot/base image can carry a stale postmaster.pid without a live process.
# Remove it so the cluster can start cleanly.
if [ -f "$PGDATA/postmaster.pid" ] && ! sudo -u postgres pg_isready -q 2>/dev/null; then
  echo "    Removing stale postmaster.pid"
  sudo rm -f "$PGDATA/postmaster.pid"
fi
sudo pg_ctlcluster "$PG_VERSION" "$PG_CLUSTER" start 2>/dev/null || true
for i in $(seq 1 30); do
  if sudo -u postgres pg_isready -q 2>/dev/null; then
    echo "    PostgreSQL ready"
    break
  fi
  sleep 1
done

# Safety: ensure the dev database exists (e.g. first boot from a fresh base).
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='dating_bot'" 2>/dev/null | grep -q 1; then
  sudo -u postgres createdb dating_bot || true
fi

echo "==> Starting Redis"
if ! redis-cli ping >/dev/null 2>&1; then
  sudo redis-server /etc/redis/redis.conf --daemonize yes
fi
for i in $(seq 1 15); do
  if redis-cli ping >/dev/null 2>&1; then
    echo "    Redis ready"
    break
  fi
  sleep 1
done

echo "==> Services up"
