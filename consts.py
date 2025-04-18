#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys

from core_nodeps import (
    load_conf_setting,
    winpath,
)

from core_utils import (
    exit_with_message,
    log,
)

if getattr(sys, "frozen", False):
    SCRIPT_IMP_FILE = os.path.realpath(sys.executable)
else:
    SCRIPT_IMP_FILE = os.path.realpath(__file__)
SCRIPT_PATH = os.path.dirname(SCRIPT_IMP_FILE)


def getbatcmd():
    batf = os.path.join(SCRIPT_PATH, "wemod.bat")
    if not os.path.isfile(batf):
        try:
            import urllib.request

            repo_user = load_conf_setting("RepoUser")
            if not repo_user:
                repo_user = "DeckCheatz"
                # save_conf_setting("RepoUser", repo_user)
                log("RepoUser not set in config. Using: " + repo_user)

            repo_name = load_conf_setting("RepoName")
            if not repo_name:
                repo_name = "wemod-launcher"
                # save_conf_setting("RepoName", repo_name)
                log("RepoName not set in config. Using: " + repo_name)

            repo_parts = os.getenv("REPO_STRING")
            if repo_parts:
                repo_parts = repo_parts.split("/", 1) + [""]
                if repo_parts[0] and repo_parts[0] != "":
                    repo_user = repo_parts[0]
                if repo_parts[1] and repo_parts[1] != "":
                    repo_name = repo_parts[1]

            repo_concat = repo_user + "/" + repo_name

            url = f"https://raw.githubusercontent.com/{repo_concat}/refs/heads/main/wemod.bat"
            urllib.request.urlretrieve(url, batf)

        except Exception as e:
            pass
        if not os.path.isfile(batf):
            exit_with_message(
                "Missing bat",
                "The 'wemod.bat' file is missing and could not be downloaded. Exiting",
            )

    return ["start", winpath(batf)]


BAT_COMMAND = getbatcmd()


# Function to grab the Steam Compat Data Path
def get_compat() -> str:
    ccompat = load_conf_setting("SteamCompatDataPath")
    wcompat = load_conf_setting("WinePrefixPath")
    if not wcompat and os.getenv("WINE_PREFIX_PATH"):
        os.environ["WINEPREFIX"] = os.getenv("WINE_PREFIX_PATH")
    ecompat = os.getenv("STEAM_COMPAT_DATA_PATH")
    nogame = False
    # STEAM_COMPAT_DATA_PATH not set
    if not ecompat:
        if os.getenv("WINEPREFIX") or wcompat:
            ecompat = wcompat
            if not ecompat:
                ecompat = os.getenv("WINEPREFIX")
            nogame = True
            wine = os.getenv("WINE")
            tools = os.getenv("STEAM_COMPAT_TOOL_PATHS")
            # if tools set and wine not in compat tools
            if (
                tools
                and len(tools.strip(os.pathsep)) > 0
                and os.path.dirname(wine) not in tools.split(os.pathsep)
            ):
                if wine:
                    # add wine compat tool
                    os.environ["STEAM_COMPAT_TOOL_PATHS"] = (
                        tools.strip(os.pathsep) + ":" + os.path.dirname(wine)
                    )
            # if tools are empty
            elif not tools or len(tools.strip(os.pathsep)) == 0:
                if not wine:
                    log(
                        "Error: The WINE environment variable needs to be set if using external runners. Exiting..."
                    )
                    exit_with_message(
                        "Not wine not found",
                        "Error: wine not found.\nThe WINE environment variable needs to be set if using external runners. Exiting...",
                    )
                # set wine compat tool
                os.environ["STEAM_COMPAT_TOOL_PATHS"] = os.path.dirname(wine)
        else:
            log(
                "The STEAM_COMPAT_DATA_PATH and the WINEPREFIX / WINE_PREFIX_PATH environment variables were not set.\nMost likely this is not running under wine. Exiting..."
            )
            exit_with_message(
                "Not running wine",
                "Error: Not running with wine.\nTo run with wine, you can select Proton in the game's compatibility settings. Exiting...",
            )

    if ccompat and not nogame:
        ecompat = os.path.join(ccompat, ecompat.split(os.sep)[-1])
    if wcompat and nogame:
        ecompat = wcompat
    os.makedirs(ecompat, exist_ok=True)
    return ecompat


BASE_STEAM_COMPAT = get_compat()
STEAM_COMPAT_FOLDER = os.path.dirname(BASE_STEAM_COMPAT)


def get_scan_folder():
    wscanfolder = os.getenv("SCANFOLDER")
    cscanfolder = load_conf_setting("ScanFolder")
    if not wscanfolder:
        wscanfolder = cscanfolder
    if not wscanfolder:
        wscanfolder = STEAM_COMPAT_FOLDER
    return wscanfolder


SCAN_FOLDER = get_scan_folder()
WINETRICKS = os.path.join(SCRIPT_PATH, "winetricks")
WINEPREFIX = os.path.join(BASE_STEAM_COMPAT, "pfx")
INIT_FILE = os.path.join(WINEPREFIX, ".wemod_installer")
