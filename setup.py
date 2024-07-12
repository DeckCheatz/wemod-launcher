#!/usr/bin/env python3

import os
import sys
import stat
import shutil
import subprocess

from coreutils import (
    log,
    pip,
    exit_with_message,
)

from corenodep import (
    load_conf_setting,
    save_conf_setting,
    check_dependencies,
)

from coreutils import (
    show_message,
)

from mainutils import (
    download_progress,
)

from typing import (
    Optional,
    Union,
    List,
)

SCRIPT_IMP_FILE = os.path.realpath(__file__)
SCRIPT_PATH = os.path.dirname(SCRIPT_IMP_FILE)


def welcome() -> bool:
    import FreeSimpleGUI as sg
    import requests

    wemod_logo = requests.get(
        "https://www.wemod.com/static/images/device-icons/favicon-192-ce0bc030f3.png",
        stream=False,
    )

    sg.theme("systemdefault")

    ret = sg.popup_ok_cancel(
        "Welcome to WeMod Installer!\nPress ok to start the setup.",
        title="WeMod Launcher Setup",
        image=wemod_logo.content,
        icon=wemod_logo.content,
    )
    return ret == "OK"


def download_wemod(temp_dir: str) -> str:
    import FreeSimpleGUI as sg

    sg.theme("systemdefault")

    status = [0, 0]

    progress = sg.ProgressBar(100, orientation="h", s=(50, 10))
    text = sg.Text("0%")
    # text = sg.Multiline(str.join("", log), key="-LOG-", autoscroll=True, size=(50,50), disabled=True)
    layout = [[progress], [text]]
    window = sg.Window("Downloading WeMod", layout, finalize=True)

    def update_log(status: list[int], dl: int, total: int) -> None:
        status.clear()
        status.append(dl)
        status.append(total)

    setup_file = os.path.join(temp_dir, "wemod_setup.exe")
    download_func = lambda: download_progress(
        "https://api.wemod.com/client/download",
        setup_file,
        lambda dl, total: update_log(status, dl, total),
    )
    # download_func = lambda: download_progress("http://localhost:8000/WeMod-8.3.15.exe", setup_file, lambda dl,total: update_log(status, dl, total))

    window.perform_long_operation(download_func, "-DL COMPLETE-")

    while True:  # Event Loop
        event, values = window.read(timeout=1000)
        if event == "-DL COMPLETE-":
            break
        elif event == None:
            exit_with_message(
                "Window Closed", "The window was closed, exiting", timeout=5
            )
        else:
            if len(status) < 2:
                continue
            [dl, total] = status
            perc = int(100 * (dl / total)) if total > 0 else 0
            text.update("{}% ({}/{})".format(perc, dl, total))
            progress.update(perc)

    window.close()
    return setup_file


def unpack_wemod(
    setup_file: str, temp_dir: str, install_location: str
) -> bool:
    try:
        import zipfile
        import tempfile

        archive = zipfile.ZipFile(setup_file, mode="r")
        names = archive.filelist

        nupkg = list(
            filter(lambda name: str(name.filename).endswith(".nupkg"), names)
        )[0]
        tmp_nupkgd = tempfile.mktemp(prefix="wemod-nupkg-")
        archive.extract(nupkg, tmp_nupkgd)
        tmp_nupkg = os.path.join(tmp_nupkgd, nupkg.filename)
        archive.close()

        archive = zipfile.ZipFile(tmp_nupkg, mode="r")

        net = list(
            filter(
                lambda name: name.filename.startswith("lib/net"),
                archive.filelist,
            )
        )

        tmp_net = tempfile.mkdtemp(prefix="wemod-net")
        archive.extractall(tmp_net, net)

        shutil.move(os.path.join(tmp_net, net[0].filename), install_location)
        shutil.rmtree(tmp_net, ignore_errors=True)
        shutil.rmtree(tmp_nupkgd, ignore_errors=True)
        shutil.rmtree(tmp_nupkg, ignore_errors=True)
        shutil.rmtree(temp_dir, ignore_errors=True)

        return True
    except:
        return False


def mk_venv() -> Optional[str]:
    venv_path = load_conf_setting("VirtualEnvironment")
    if not venv_path:
        venv_path = "wemod_venv"
    try:
        if os.path.isabs(venv_path):
            subprocess.run(
                [sys.executable, "-m", "venv", venv_path], check=True
            )
        else:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "venv",
                    os.path.abspath(os.path.join(SCRIPT_PATH, venv_path)),
                ],
                check=True,
            )
        log("Virtual environment created successfully.")
    except Exception as e:
        log(f"Failed to create virtual environment, with error {e}")
        return None
    else:
        save_conf_setting("VirtualEnvironment", venv_path)
        return venv_path


def tk_check() -> None:
    try:
        if not bool(check_flatpak(None)):
            import tkinter
    except ImportError:
        exit_with_message(
            "Tkinter missing",
            "Critical error, tkinter is not installed,\nmake shure you have installed the correct tkinter package for your system,\nsearch the internet for 'install tkinter for YOURDISTRO',\nreplace YOURDISTRO with your actual distro",
        )


def venv_manager() -> List[Optional[str]]:
    requirements_txt = os.path.join(SCRIPT_PATH, "requirements.txt")
    tk_check()
    if not check_dependencies(requirements_txt):
        pip_install = f"install -r '{requirements_txt}'"
        return_code = pip(pip_install)
        if return_code == 0:
            return []
        # if dependencies cant just be installed
        else:
            # go the venv route
            venv_path = mk_venv()
            if not venv_path:
                log(
                    "Failed to create virtual environment, trying to force install venv"
                )
                return_code = pip("install --break-system-packages venv")
                if return_code == 0:
                    venv_path = mk_venv()
                    if not venv_path:
                        log(
                            "CRITICAL: Backup failed to create virtual environment, exiting"
                        )
                        exit_with_message(
                            "Error on package venv",
                            "Failed to create virtual environment. Error.",
                            ask_for_log=True,
                        )
                else:
                    log(
                        "CRITICAL: The python package 'venv' is not installed and could not be downloaded"
                    )
                    exit_with_message(
                        "Missing python-venv",
                        "The python package 'venv' is not installed and could not be downloaded. Error.",
                        ask_for_log=True,
                    )
            # At this point we have a venv
            if venv_path and not os.path.isabs(venv_path):
                venv_path = os.path.join(SCRIPT_PATH, venv_path)

            # Determine the path to the Python executable within the virtual environment
            venv_python = os.path.join(venv_path, "bin", "python")

            # Preinstall dependencies in the virtual environment
            return_code = pip(pip_install, venv_path)
            if return_code != 0:
                log("CRITICAL: Dependencies can't be installed")
                exit_with_message(
                    "Dependencies install error",
                    "Failed to install dependencies. Error.",
                    ask_for_log=True,
                )
            return [venv_python]


def self_update(path: List[Optional[str]]) -> List[Optional[str]]:
    upd = os.getenv("SELF_UPDATE")
    if not upd:
        upd = load_conf_setting("SelfUpdate")

    infinite = os.getenv("WeModInfProtect", "1")
    if (upd and upd.lower() == "false") or infinite > 2:
        log("Self update skipped")
        return path

    original_cwd = os.getcwd()
    try:
        os.chdir(SCRIPT_PATH)

        # Fetch latest changes
        subprocess.run(["git", "fetch"], text=True)

        # Get local and remote commit hashes
        local_hash = subprocess.run(
            ["git", "rev-parse", "@"], stdout=subprocess.PIPE, text=True
        ).stdout.strip()
        remote_hash = subprocess.run(
            ["git", "rev-parse", "@{u}"], stdout=subprocess.PIPE, text=True
        ).stdout.strip()
        base_hash = subprocess.run(
            ["git", "merge-base", "@", "@{u}"],
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.strip()

        if local_hash == remote_hash:
            log("No updates available")
        else:
            log("Updating...")

            # Check if there are local changes that differ from remote
            if local_hash != base_hash:
                log(
                    "Warning: Local changes detected, updating from remote anyway."
                )

            subprocess.run(["git", "reset", "--hard", "origin"], text=True)
            subprocess.run(["git", "pull"], text=True)

            # Set executable permissions (replace with specific file names if needed)
            subprocess.run(["chmod", "-R", "ug+x", "."], text=True)

            # Optionally update the path to include the executable if not already set
            if not path:
                path = [sys.executable]
            log("Update finished")
    except Exception as e:
        log(f"Failed to update, the following error appeared:\n\t{e}")
    finally:
        os.chdir(original_cwd)

    return path


def check_flatpak(flatpak_cmd: Optional[List[str]]) -> List[str]:
    if flatpak_cmd == None:
        if "FLATPAK_ID" in os.environ or os.path.exists("/.flatpak-info"):
            return ["True"]
        return []
    else:
        if "FLATPAK_ID" in os.environ or os.path.exists("/.flatpak-info"):
            flatpak_start = [
                "flatpak-spawn",
                "--host",
            ]

            envlist = [
                "STEAM_COMPAT_TOOL_PATHS",
                "STEAM_COMPAT_DATA_PATH",
                "WINE_PREFIX_PATH",
                "WINEPREFIX",
                "WINE",
                "SCANFOLDER",
                "TROUBLESHOOT",
                "WEMOD_LOG",
                "WAIT_ON_GAMECLOSE",
                "SELF_UPDATE",
                "FORCE_UPDATE_WEMOD",
                "REPO_STRING",
            ]
            for env in envlist:
                if env in os.environ:
                    flatpak_start.append(f"--env={env}={os.environ[env]}")
            infpr = os.getenv("WeModInfProtect", "1")
            infpr = str(int(infpr) + 1)

            flatpak_start.append("FROM_FLATPAK=true")
            flatpak_start.append(f"WeModInfProtect={infpr}")
            flatpak_start.append("--")  # Isolate command from command args

            if bool(flatpak_cmd):  # if venv is set use it
                flatpak_cmd = flatpak_start + flatpak_cmd
            else:  # if not use python executable
                flatpak_cmd = flatpak_start + [sys.executable]

        return flatpak_cmd


def setup_main() -> None:
    import tempfile
    import FreeSimpleGUI as sg

    if not welcome():
        print("Installation cancelled by user")
        return

    install_location = os.path.join(SCRIPT_PATH, "wemod_bin")
    winetricks = os.path.join(SCRIPT_PATH, "winetricks")

    if os.getenv("FORCE_UPDATE_WEMOD", "0") == "1" or not os.path.isfile(
        winetricks
    ):
        if os.path.isfile(winetricks):
            shutil.rmtree(winetricks)
        log("Winetricks not found...")
        log("Downloading latest winetricks...")

        download_progress(
            "https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks",
            winetricks,
            None,
        )
        os.chmod(
            winetricks,
            stat.S_IXUSR
            | stat.S_IXGRP
            | stat.S_IXOTH
            | stat.S_IRUSR
            | stat.S_IRGRP
            | stat.S_IROTH,
        )

    if (
        not os.path.isdir(install_location)
        or not os.path.isfile(os.path.join(install_location, "WeMod.exe"))
        or os.getenv("FORCE_UPDATE_WEMOD", "0") == "1"
    ):
        if os.path.isdir(install_location):
            shutil.rmtree(install_location, ignore_errors=True)

        temp_dir = tempfile.mkdtemp(prefix="wemod-launcher-")
        setup_file = download_wemod(temp_dir)
        unpacked = unpack_wemod(setup_file, temp_dir, install_location)

        show_message(
            "Setup completed successfully.\nMake shure the LAUNCH OPTIONS of the game say '"
            + str(os.path.join(SCRIPT_PATH, "wemod"))
            + " %command%'",
            title="Wemod Downloaded",
            timeout=5,
        )

        if not unpacked:
            log("Failed to unpack WeMod.")
            exit_with_message(
                "Failed Unpack",
                "Failed to unpack WeMod, exiting",
                1,
                timeout=10,
                ask_for_log=True,
            )


def run_wemod() -> None:
    script_file = os.path.join(SCRIPT_PATH, "wemod")
    command = [sys.executable, script_file] + sys.argv[1:]

    # Execute the main script so the venv gets created
    process = subprocess.run(command, capture_output=True, text=True)

    # Send output and error to steam console
    # If function log worked it gets logged by the re-run
    print(str(process.stdout))
    print(str(process.stderr))
    sys.exit(process.returncode)


if __name__ == "__main__":
    run_wemod()
