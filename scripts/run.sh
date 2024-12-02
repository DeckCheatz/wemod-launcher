#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only

# Navigate to the project root
cd "$(dirname "$0")/.."

# Setup PDM
./scripts/pdm.sh

# Run the application with passed arguments
pdm run wemod-launcher "$@"
