#!/usr/bin/env python3

import os
from pathlib import Path
from wemod_launcher.utils.configuration import Configuration
from wemod_launcher.utils.consts import Consts
from wemod_launcher.pfx.wine_utils import WineUtils

cfg: Configuration = Configuration()

from wemod_launcher.core_nodeps import (
    load_conf_setting,
    winpath,
)

from wemod_launcher.core_utils import (
    exit_with_message,
    log,
)


# Function to grab the Steam Compat Data path
def get_compat() -> str:
    ccompat = load_conf_setting("SteamCompatDataPath")
    wcompat = load_conf_setting("WinePrefixPath")
    if not wcompat and os.getenv("WINE_PREFIX_PATH"):
        os.environ["WINEPREFIX"] = os.getenv(
            "WINE_PREFIX_PATH", ""
        )  # TODO: Either use try/except here, or a sane default.
    ecompat = os.getenv(
        "STEAM_COMPAT_DATA_PATH", ""
    )  # TODO: Either use try/except here, or a sane default.
    nogame = False
    # STEAM_COMPAT_DATA_PATH not set
    if not ecompat:
        if os.getenv("WINEPREFIX") or wcompat:
            ecompat = wcompat
            if not ecompat:
                ecompat = os.getenv(
                    "WINEPREFIX", ""
                )  # TODO: Either use try/except here, or a sane default.
            nogame = True
            wine = os.getenv(
                "WINE", ""
            )  # TODO: Either use try/except here, or a sane default.
            tools = os.getenv(
                "STEAM_COMPAT_TOOL_PATHS", ""
            )  # TODO: Either use try/except here, or a sane default.
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
                        "Error, The WINE environment variable needs to be set if using extenal runners, exiting"
                    )
                    exit_with_message(
                        "Not wine not found",
                        "Error, wine not found,\nthe WINE environment variable needs to be set if using extenal runners, exiting",
                    )
                # set wine compat tool
                os.environ["STEAM_COMPAT_TOOL_PATHS"] = os.path.dirname(wine)
        else:
            log(
                "The STEAM_COMPAT_DATA_PATH and the WINEPREFIX / WINE_PREFIX_PATH environment variables were not set.\nMost likely this is not running under wine, exiting"
            )
            exit_with_message(
                "Not running wine",
                "Error, not running with wine,\nto run with wine you could select Proton in the compatibility settings, exiting",
            )

    if ccompat and not nogame:
        ecompat = os.path.join(ccompat, ecompat.split(os.sep)[-1])
    if wcompat and nogame:
        ecompat = wcompat
    os.makedirs(ecompat, exist_ok=True)
    return ecompat


def get_scan_folder() -> str:
    scan_folder: str
    try:
        scan_folder = os.getenv("SCANFOLDER") or ""
    except KeyError:
        scan_folder = ""
        pass

    if not Path(scan_folder).exists():
        scan_folder = load_conf_setting("ScanFolder") or ""

    if not Path(scan_folder).exists():
        scan_folder = STEAM_COMPAT_FOLDER

    return scan_folder


CONSTS = Consts()
WINE_UTILS = WineUtils()


SCRIPT_IMP_FILE = str(CONSTS.SCRIPT_PATH)
SCRIPT_PATH = str(CONSTS.SCRIPT_RUNTIME_DIR)
BAT_COMMAND = [
    "start",
    WINE_UTILS.native_path(os.path.join(SCRIPT_IMP_FILE, "wemod.bat")),
]
BASE_STEAM_COMPAT = get_scan_folder()
STEAM_COMPAT_FOLDER = str(CONSTS.STEAM_COMPAT_DATA_DIR)
SCAN_FOLDER = get_scan_folder()
WINETRICKS = os.path.join(SCRIPT_PATH, "winetricks")
WINEPREFIX = os.path.join(BASE_STEAM_COMPAT, "pfx")
INIT_FILE = os.path.join(WINEPREFIX, ".wemod_installer")
