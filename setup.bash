#!/usr/bin/env bash
set -e

#-----------------------------------
#-------- PACKAGE MANAGER ----------
#-----------------------------------
echo
echo "#1 Detecting package manager..."
for pkg in pacman rpm-ostree dnf apt; do
    if command -v "$pkg" >/dev/null 2>&1; then
        pkg_manager="$pkg"
        break
    fi
done

[ -z "$pkg_manager" ] && { echo "No supported package manager found."; exit 1; }

echo "→ $pkg_manager detected"

# Installation commands per package manager
declare -A INSTALL_CMD=(
    [pacman]="sudo pacman -S --noconfirm"
    [rpm-ostree]="sudo rpm-ostree install -y"
    [dnf]="sudo dnf install -y"
    [apt]="sudo apt install -y"
)

# Update repositories if required
if [ "$pkg_manager" = "apt" ]; then
    sudo apt update
fi

#-----------------------------------
#---------- DEPENDENCIES -----------
#-----------------------------------
echo
# Package mappings per distribution
declare -A PKG_GIT=(
    [pacman]="git"
    [rpm-ostree]="git"
    [dnf]="git"
    [apt]="git"
)
declare -A PKG_PYTHON=(
    [pacman]="python"
    [rpm-ostree]="python3"
    [dnf]="python3"
    [apt]="python3"
)
declare -A PKG_VENV=(
    [pacman]=""          # included in python
    [rpm-ostree]=""      # included in python3
    [dnf]=""             # included in python3
    [apt]="python3-venv"
)
declare -A PKG_TK=(
    [pacman]="tk"
    [rpm-ostree]="python3-tkinter"
    [dnf]="python3-tkinter"
    [apt]="python3-tk"
)

install_if_missing() {
    local check_cmd=$1
    local package_name=$2

    [ -z "$package_name" ] && return

    if ! command -v "$check_cmd" >/dev/null 2>&1; then
        echo "→ Installing $package_name..."
        ${INSTALL_CMD[$pkg_manager]} "$package_name"
    else
        echo "✓ $package_name is already installed"
    fi
}

echo "#2 Checking dependencies..."
install_if_missing git "${PKG_GIT[$pkg_manager]}"
install_if_missing python3 "${PKG_PYTHON[$pkg_manager]}"
install_if_missing python3 "${PKG_VENV[$pkg_manager]}"
install_if_missing python3 "${PKG_TK[$pkg_manager]}"

#-----------------------------------
#--------- WEMOD-LAUNCHER ----------
#-----------------------------------
echo
echo "#3 Checking project directory..."
# Clone if not already present (or current folder)
WEMOD_DIR=""
GIT_PROJECT_NAME="wemod-launcher"
if [ ! -d "$GIT_PROJECT_NAME" -a ! -d "../$GIT_PROJECT_NAME" ]; then
    echo "'$GIT_PROJECT_NAME' directory not found."
    REPO_URL="https://github.com/DeckCheatz/wemod-launcher.git"

    read -rp "Enter installation path (leave empty to clone here): " install_path
    if [ -z "$install_path" ]; then
        echo "Cloning repository into current directory..."
        git clone "$REPO_URL"
        WEMOD_DIR="$(realpath $GIT_PROJECT_NAME)"
    else
        echo "Cloning repository into $install_path..."
        mkdir -p "$install_path"
        git clone "$REPO_URL" "$install_path/$GIT_PROJECT_NAME"
        WEMOD_DIR="$(realpath $install_path/$GIT_PROJECT_NAME)"
    fi
else
    echo "'$GIT_PROJECT_NAME' directory already exists."

    # If we are already inside the project directory
    if [ "$(basename "$PWD")" = "$GIT_PROJECT_NAME" ]; then
        WEMOD_DIR="$(realpath "$PWD")"
    else
        WEMOD_DIR="$(realpath "$GIT_PROJECT_NAME")"
    fi
fi
# Make wemod python script executable
chmod +x "$WEMOD_DIR/wemod"
# Add a txt file to always have the launch command at hand
"$WEMOD_DIR %command%" > $WEMOD_DIR/launch-command.txt

#-----------------------------------
#-------- SHOW NEXT STEPS ----------
#-----------------------------------
# 1. Detects when `### Setup Automatically` starts
# 2. Stops when `### Setup Manually` is reached
# 3. Begins printing only after `#### Next`:
awk '
/^### Setup Automatically/ {in_auto=1; next}
/^### Setup Manually/ {in_auto=0}
in_auto && /^#### Next:/ {in_next=1}
in_auto && in_next
' readme.md

