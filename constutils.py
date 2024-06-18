#!/usr/bin/env python3

import os
import subprocess

from urllib import request

# Import consts
from consts import (
    BASE_STEAM_COMPAT,
    STEAM_COMPAT_FOLDER,
    WINEPREFIX,
)

from coreutils import (
    show_message,
    exit_with_message,
    get_user_input,
)

from corenodep import (
    parse_version,
    read_file,
)

from typing import (
    List,
    Union,
)

from coreutils import (
    log,
)

from mainutils import (
    popup_execute,
)

SCRIPT_IMP_FILE = os.path.realpath(__file__)
SCRIPT_PATH = os.path.dirname(SCRIPT_IMP_FILE)


# Enshure that wine is isntalled
def enshure_wine() -> str:
    WinePfx = os.path.join(BASE_STEAM_COMPAT, "drive_c")
    ProtonPfx = os.path.join(WINEPREFIX, "drive_c")
    if os.path.isdir(WinePfx):
        try:
            os.symlink(
                BASE_STEAM_COMPAT, os.path.join(BASE_STEAM_COMPAT, "pfx")
            )
        except Exception as e:
            pass
    if os.path.isdir(ProtonPfx):
        ProtonVersion = os.path.join(BASE_STEAM_COMPAT, "version")
        if not os.path.isfile(ProtonVersion):
            got = None
            while not got:
                resp, tout = get_user_input(
                    "Imput wine version", "Version file", "WineGE8.26", 40
                )
                got = parse_version(resp)
                if not got:
                    show_message(
                        "The version string was incorrect.\nMake shure you have at least 1 number in the version string",
                        "Incorect version",
                        20,
                        False,
                    )
            with open(ProtonVersion, "w") as pver:
                pver.write(resp)
        return ProtonVersion
    else:
        exit_with_message(
            "Missing Prefix",
            "Error, wineprefix is missing,\nmake shure you run the game without the wemod-laucher once",
        )


# Scan the steam compat folder for wemod installed prefixes
def scanfolderforversions(
    current_version_parts: List[Union[int, None]] = [None, None]
) -> List[Union[Optional[List[int]], Optional[str]]]:
    # At default, we don't know of any available version
    closest_version_folder = None
    closest_version_number = None
    priority = 6

    # For all folders in steam compat
    for folder in os.listdir(STEAM_COMPAT_FOLDER):
        # Get the version file, folder path and check if wemod is installed
        folder_path = os.path.join(STEAM_COMPAT_FOLDER, folder)
        version_file = os.path.join(folder_path, "version")

        if os.path.isdir(folder_path) and os.path.exists(
            os.path.join(folder_path, "pfx", ".wemod_installer")
        ):
            folder_version_parts = parse_version(read_file(version_file))

            if (
                folder_version_parts
                and isinstance(folder_version_parts, list)
                and folder_version_parts[0]
                and folder_version_parts[1]
            ):
                if (
                    folder_version_parts[0] == current_version_parts[0]
                    and folder_version_parts[1] == current_version_parts[1]
                ):
                    # Same major and minor version
                    closest_version_folder = folder_path
                    closest_version_number = folder_version_parts
                    break
                elif (
                    folder_version_parts[0] == current_version_parts[0]
                    and folder_version_parts[1] < current_version_parts[1]
                ):
                    # Same major, lower minor version
                    if priority > 2 or (
                        priority == 2
                        and (
                            not closest_version_folder
                            or folder_version_parts[1]
                            > closest_version_number[1]
                        )
                    ):
                        priority = 2
                        closest_version_folder = folder_path
                        closest_version_number = folder_version_parts
                elif (
                    folder_version_parts[0] == current_version_parts[0]
                    and folder_version_parts[1] > current_version_parts[1]
                ):
                    # Same major, higher minor version
                    if priority > 3 or (
                        priority == 3
                        and (
                            not closest_version_folder
                            or folder_version_parts[1]
                            < closest_version_number[1]
                        )
                    ):
                        priority = 3
                        closest_version_folder = folder_path
                        closest_version_number = folder_version_parts
                elif folder_version_parts[0] < current_version_parts[0]:
                    # Lower major version
                    if priority > 4 or (
                        priority == 4
                        and (
                            not closest_version_folder
                            or folder_version_parts[0]
                            > closest_version_number[0]
                            or (
                                folder_version_parts[0]
                                == closest_version_number[0]
                                and folder_version_parts[1]
                                > closest_version_number[1]
                            )
                        )
                    ):
                        priority = 4
                        closest_version_folder = folder_path
                        closest_version_number = folder_version_parts
                elif folder_version_parts[0] > current_version_parts[0]:
                    # Higher major version
                    if priority > 5 or (
                        priority == 5
                        and (
                            not closest_version_folder
                            or folder_version_parts[0]
                            < closest_version_number[0]
                            or (
                                folder_version_parts[0]
                                == closest_version_number[0]
                                and folder_version_parts[1]
                                < closest_version_number[1]
                            )
                        )
                    ):
                        priority = 5
                        closest_version_folder = folder_path
                        closest_version_number = folder_version_parts

    return closest_version_number, closest_version_folder


# Function to execute winetricks commands
def winetricks(command: str, proton_bin: str) -> int:
    winetricks_sh = os.path.join(SCRIPT_PATH, "winetricks")

    # Download winetricks if not present
    if not os.path.isfile(winetricks_sh):
        log("winetricks not found. Downloading...")
        request.urlretrieve(
            "https://github.com/Winetricks/winetricks/raw/master/src/winetricks",
            winetricks_sh,
        )
        log(f"setting exec permissions on '{winetricks_sh}'")
        process = subprocess.Popen(
            f"sh -c 'chmod +x {winetricks_sh}'", shell=True
        )
        exit_code = process.wait()

        if exit_code != 0:
            message = f"failed to set exec permission on '{winetricks_sh}'"
            log(message)
            exit_with_message("ERROR", message)

    # Prepare the command with the correct environment
    command = f"export PATH='{proton_bin}' && export WINEPREFIX='{WINEPREFIX}' && {winetricks_sh} {command}"

    # Execute the command and return the response
    resp = popup_execute("winetricks", command)
    return resp


# Function to execute wine commands
def wine(command: str, proton_bin: str) -> int:
    # Prepare the command with the correct environment
    command = f"export PATH='{proton_bin}' && export WINEPREFIX='{WINEPREFIX}' && wine {command}"

    # Execute the command and return the response
    resp = popup_execute("wine", command)
    return resp
