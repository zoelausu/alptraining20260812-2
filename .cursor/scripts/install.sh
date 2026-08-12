#!/usr/bin/env bash
# Idempotent Cloud Agent install script for the Agent Chat App stack.
# Prepares toolchain (uv, pnpm) and installs project deps when scaffold exists.
set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

export PATH="${HOME}/.local/bin:${PATH}"

log() { echo "[install] $*"; }

# uv — Python package manager for Agno backend (see specs/001-agent-chat-app/quickstart.md)
if ! command -v uv >/dev/null 2>&1; then
  log "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi
log "uv: $(uv --version)"

# pnpm — frontend package manager
if ! command -v pnpm >/dev/null 2>&1; then
  log "Enabling pnpm via corepack..."
  corepack enable
  corepack prepare pnpm@latest --activate
fi
log "pnpm: $(pnpm --version)"

log "node: $(node --version)"
log "python: $(python3 --version)"

# Project deps — run when implementation scaffold exists
if [[ -f Makefile ]]; then
  log "Running make install..."
  make install
elif [[ -f backend/pyproject.toml ]]; then
  log "Syncing backend Python dependencies..."
  (cd backend && uv sync)
fi

if [[ -f frontend/package.json ]] && [[ ! -f Makefile ]]; then
  log "Installing frontend dependencies..."
  (cd frontend && pnpm install --frozen-lockfile 2>/dev/null || pnpm install)
fi

log "Environment install complete."
