#!/usr/bin/env bash
# setup_ryusim.sh — Install RyuSim with optional version pinning
set -euo pipefail

RYUSIM_VERSION="${RYUSIM_VERSION:-latest}"

echo "Installing RyuSim (version: ${RYUSIM_VERSION})..."

if [ "$RYUSIM_VERSION" = "latest" ]; then
    curl -fsSL https://ryusim.seiraiyu.com/install.sh | bash
else
    curl -fsSL "https://ryusim.seiraiyu.com/install.sh" | bash -s -- --version "$RYUSIM_VERSION"
fi

# Verify installation
if command -v ryusim &> /dev/null; then
    echo "RyuSim installed successfully: $(ryusim --version 2>/dev/null || echo 'version unknown')"
else
    echo "ERROR: RyuSim installation failed — 'ryusim' not found in PATH"
    exit 1
fi
