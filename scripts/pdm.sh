#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only

# Navigate to the project root
cd "$(dirname "$0")/.."

installed=0
while [ $installed -lt 1 ]
    do
    if [ ! -f $HOME/.local/share/pdm/venv/bin/pdm ] || [ ! -f $HOME/.local/share/pdm/venv/bin/activate ] || [ $installed -eq -1 ];
    then
        curl -sSL https://pdm-project.org/install-pdm.py | python3 -
    else
        source $HOME/.local/share/pdm/venv/bin/activate
        export PATH="$HOME/.local/share/pdm/venv/bin:$PATH"
    fi

    # Send a signal to pdm to update itself if possible
    echo "Trying to run PDM update"
    pdm self update 2>/dev/null

    # Ensure dependencies are installed using PDM
    if [ ! -f "pdm.lock" ]; then
        echo "Installing dependencies for the first time..."
        pdm install || { echo "Failed to install dependencies."; installed=$((installed - 1)); }
    else
        echo "Ensuring dependencies are up-to-date..."
        pdm install || { echo "Failed to install dependencies."; installed=$((installed - 1)); }
    fi

    if [ $installed -lt -1 ]
    then
        exit 1
    elif [ $installed -eq -1 ]
    then
        echo "Retrying the install"
    else
        installed=1
    fi
done

