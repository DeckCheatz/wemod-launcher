#!/usr/bin/env python3

import os
import shutil
import subprocess

from urllib import request

# Import consts
from consts import (
    STEAM_COMPAT_FOLDER,
    BASE_STEAM_COMPAT,
    SCAN_FOLDER,
    WINEPREFIX,
    INIT_FILE,
)

from coreutils import (
    exit_with_message,
    get_user_input,
    popup_options,
    show_message,
)

from corenodep import (
    load_conf_setting,
    save_conf_setting,
    parse_version,
    read_file,
)

from typing import (
    List,
    Union,
    Optional,
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
def enshure_wine(verstr: Optional[str] = None) -> str:
    WinePfx = os.path.join(BASE_STEAM_COMPAT, "drive_c")
    ProtonPfx = os.path.join(WINEPREFIX, "drive_c")
    if os.path.isdir(WinePfx):
        try:
            os.symlink(BASE_STEAM_COMPAT, WINEPREFIX)
        except Exception as e:
            pass
    if os.path.isdir(ProtonPfx):
        ProtonVersion = os.path.join(BASE_STEAM_COMPAT, "version")
        if verstr:
            with open(ProtonVersion, "w") as pver:
                pver.write(verstr)
        elif not os.path.isfile(ProtonVersion):
            got = None
            resp = None
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
            if resp != None:
                with open(ProtonVersion, "w") as pver:
                    pver.write(resp)
        return ProtonVersion
    else:
        exit_with_message(
            "Missing Prefix",
            "Error, wineprefix is missing,\nmake shure you run the game without the wemod-laucher once",
            ask_for_log=True,
        )


# Scan the steam compat folder for wemod installed prefixes
def scanfolderforversions(
    current_version_parts: List[Union[int, None]] = [None, None]
) -> List[Union[Optional[List[int]], Optional[str]]]:
    # At default, we don't know of any available version
    closest_version_folder = None
    closest_version_number = None
    priority = 6

    # var to note a working protonge 7 prefix
    prefix_path_seven = None

    # For all folders in steam compat
    for folder in os.listdir(SCAN_FOLDER):
        # Get the version file, folder path and check if wemod is installed
        folder_path = os.path.join(SCAN_FOLDER, folder)
        version_file = os.path.join(folder_path, "version")

        if os.path.isdir(folder_path) and os.path.exists(
            os.path.join(folder_path, "pfx", ".wemod_installer")
        ):
            folder_version_str = read_file(version_file)
            folder_version_parts = parse_version(folder_version_str)

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
                    priority = 1
                    # Same major and minor version
                    closest_version_folder = folder_path
                    closest_version_number = folder_version_parts
                    # break # enable if ver 7 was found by the users
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
                # try to find any Proton7 prefix that the user might have for uploading
                if (
                    folder_version_parts[0] == 7
                    and folder_version_str.find("GE-Proton") >= 0
                ):
                    minseven = load_conf_setting("ProtonMinorSeven")
                    if minseven:
                        minseven = int(minseven)
                        if minseven < folder_version_parts[1]:
                            save_conf_setting(
                                "ProtonMinorSeven",
                                str(folder_version_parts[1]),
                            )
                            prefix_path_seven = folder_path
                    else:
                        save_conf_setting(
                            "ProtonMinorSeven", str(folder_version_parts[1])
                        )
                        prefix_path_seven = folder_path

    if prefix_path_seven:
        from mainutils import copy_folder_with_progress

        prefixesfolder = os.path.join(SCAN_FOLDER, "prefix")
        os.makedirs(prefixesfolder, exists_ok=True)
        protonconfminor = load_conf_setting("ProtonMinorSeven")
        prefixesfile = os.path.join(
            prefixesfolder, f"Proton7.{protonconfminor}.zip"
        )
        # ask the user to upload the prefix if they have one
        prresp = show_message(
            f"In your scanfolder the online missing prefix version with GE-Proton 7 (.{protonconfminor}) was found,\nplease be so kind and click yes to zip the prefix\nafter that upload it to something like https://www.sendgb.com/\nand lastly paste the link in a wemod issue",
            "Proton7 found",
            60,
            True,
        )
        if prresp == "Yes":
            sevenpfx = os.path.join(prefix_path_seven, "pfx")
            seveninit = os.path.join(sevenpfx, ".wemod_installer")

            initcont = read_file(seveninit)
            with open(seveninit, "w") as init:
                init.write("")

            waslink = False
            if os.path.islink(WINEPREFIX):
                os.remove(WINEPREFIX)
                waslink = True

            copy_folder_with_progress(
                prefix_path_seven, prefixesfile, True, [None], [None]
            )

            if waslink:
                try:
                    os.symlink(prefix_path_seven, sevenpfx)
                except Exception as e:
                    pass

            if not initcont:
                initcont = ""
            with open(seveninit, "w") as init:
                init.write(initcont)

            os.system(f"xdg-open '{prefixesfolder}'")
        elif prresp == "No":
            save_conf_setting("ProtonMinorSeven", "99")

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
            exit_with_message("ERROR", message, ask_for_log=True)

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


def troubleshooter() -> None:
    trouble = os.getenv("TROUBLESHOOT")
    if not trouble and os.path.isfile(INIT_FILE):
        trouble = read_file(INIT_FILE)
    if not trouble:
        trouble = load_conf_setting("Troubleshoot")
    runtro = False
    if trouble == None or (trouble and trouble.lower() == "true"):
        runtro = True
    else:
        log("Troubleshooter was disabled, continuing")
    while runtro:
        log("Starting troubleshooter")
        ret = popup_options(
            "Troubleshooter",
            "Did WeMod work as expected,\nif not troubleshoot common problems with wemod.\nDeleteing the gameprefix helps often.\nDelete Wemod.exe helps if wemod updates their progamm\nTo use the Troubleshooter after it was disabled,\nyou can add TROUBLESHOOT=true in front of the launch command",
            [
                [
                    "Disable troubleshooter globaly",
                    "Disable troubleshooter for this game",
                ],
                [
                    "Enable troubleshooter globaly",
                    "Enable troubleshooter for this game",
                ],
                ["Delete Gameprefix", "Delete Wemod.exe"],
                ["Close wemod-laucher"],
            ],
            120,
        )
        log(f"Selected in the troubleshooter was '{ret}'")
        if ret == "Disable troubleshooter globaly":
            save_conf_setting("Troubleshoot", "false")
        elif ret == "Disable troubleshooter for this game":
            with open(INIT_FILE, "w") as init:
                init.write("false")
        elif ret == "Enable troubleshooter globaly":
            save_conf_setting("Troubleshoot", "true")
        elif ret == "Enable troubleshooter for this game":
            with open(INIT_FILE, "w") as init:
                init.write("true")
        elif ret == "Delete Wemod.exe":
            try:
                os.remove(os.path.join(SCRIPT_PATH, "wemod_bin", "WeMod.exe"))
            except Exception as e:
                pass
        elif ret == "Delete Gameprefix":
            try:
                shutil.rmtree(STEAM_COMPAT_FOLDER)
            except Exception as e:
                pass
        elif not ret or ret == "Close wemod-laucher":
            runtro = False
            log("Closing troubleshooter as requested")
