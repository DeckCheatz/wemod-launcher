#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only

# Navigate to the project root
cd "$(dirname "$0")/.."

# Setup PDM
./scripts/pdm.sh

# Drop into the PDM shell
echo "Dropping into PDM shell..."
pdm run "$SHELL"
