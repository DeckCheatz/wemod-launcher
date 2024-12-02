#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only

# Navigate to the project root
cd "$(dirname "$0")/.."

# Setup PDM
if ! ./scripts/pdm.sh; then
    echo "PDM setup failed. Exiting."
    exit 1
fi

# Build by running pyinstaller
./src/wemod_launcher/pyinstaller.py
