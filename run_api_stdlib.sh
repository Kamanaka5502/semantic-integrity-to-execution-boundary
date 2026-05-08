#!/usr/bin/env bash
set -euo pipefail

# Public-safe launcher.
# Runs from the repository root instead of a machine-specific local path.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python -m app.api_stdlib
