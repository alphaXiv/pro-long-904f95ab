#!/usr/bin/env bash
set -euo pipefail

NODE_VERSION="22.17.1"
CODEX_VERSION="0.145.0"
RUNTIME_DIR="${TMPDIR:-/tmp}/prolong-runtime"
mkdir -p "$RUNTIME_DIR"

machine="$(uname -m)"
case "$machine" in
  x86_64) node_arch="x64" ;;
  aarch64|arm64) node_arch="arm64" ;;
  *) echo "Unsupported architecture: $machine"; exit 2 ;;
esac

node_root="$RUNTIME_DIR/node-v${NODE_VERSION}-linux-${node_arch}"
if [ ! -x "$node_root/bin/node" ]; then
  archive="$RUNTIME_DIR/node.tar.xz"
  curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${node_arch}.tar.xz" -o "$archive"
  tar -xJf "$archive" -C "$RUNTIME_DIR"
fi
export PATH="$node_root/bin:$PATH"
export npm_config_prefix="$RUNTIME_DIR/npm"
export PATH="$npm_config_prefix/bin:$PATH"
npm install --global "@openai/codex@${CODEX_VERSION}" --silent

python -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -e .

echo "=== PRO-LONG Kubernetes reproduction ==="
echo "started_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "python=$(python --version 2>&1)"
echo "codex=$(codex --version 2>&1)"
echo "node=$(node --version 2>&1)"
echo "gpu_visible=${NVIDIA_VISIBLE_DEVICES:-none}"

export PROLONG_DIRECT_CODEX=1
.venv/bin/python reproduction/run_condition.py
