#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only

# Navigate to the project root
cd "$(dirname "$0")/.."

# Setup PDM
./scripts/pdm.sh

# Set your preferred shell
read -p "Input your preferred shell path: " VAR

if command -v $VAR &> /dev/null; then
    # Drop into the user PDM shell
    echo "Dropping into PDM shell..."
    pdm run "$VAR"
else
    # If command non-existent Drop into the default PDM shell
    echo "The shell '$VAR' is non-existent"
    echo "Falling back into default PDM shell..."
    pdm run "$SHELL"
fi
