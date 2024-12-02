#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only

# Navigate to the project root
cd "$(dirname "$0")/.."

PDM_DIR="$HOME/.local/share/pdm/venv/bin"
PDM_BIN="$PDM_DIR/pdm"
PDM_ACTIVATE="$PDM_DIR/activate"

install_pdm() {
    echo "Installing PDM..."
    curl -sSL https://pdm-project.org/install-pdm.py | python3 -
}

activate_pdm() {
    echo "Activating PDM..."
    source "$PDM_ACTIVATE"
    export PATH="$PDM_DIR:$PATH"
}

install_dependencies() {
    echo "Installing PDM updates and dependencies..."
    pdm self update 2>/dev/null
    pdm install
}

run_installer() {
    if [ ! -f "$PDM_BIN" ] || [ ! -f "$PDM_ACTIVATE" ]; then
        install_pdm
    else
        activate_pdm
    fi

    if install_dependencies; then
        return 0
    else
        echo "Possible issue with the PDM install. Reinstalling..."
        install_pdm
        if install_dependencies; then
            return 0
        else
            return 1
        fi
    fi
}

if run_installer; then
    echo "PDM Project setup complete."
else
    exit 1
fi

