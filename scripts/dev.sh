#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only

# Navigate to the project root
cd "$(dirname "$0")/.."

# Setup PDM
if ! ./scripts/pdm.sh; then
    echo "PDM setup failed. Exiting."
    exit 1
fi

# Drop into the PDM shell
echo "Dropping into PDM shell..."
pdm run "$SHELL"
