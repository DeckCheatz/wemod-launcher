#!/usr/bin/env python3

import os
import sys
import subprocess

from urllib import request

from typing import (
    Callable,
    Optional,
    Union,
    List,
    Any,
)

from corenodep import (
    join_lists_with_delimiter,
    load_conf_setting,
    save_conf_setting,
    read_file,
)

SCRIPT_IMP_FILE = os.path.realpath(__file__)
SCRIPT_PATH = os.path.dirname(SCRIPT_IMP_FILE)


# Function for logging messages
def log(message: Optional[str] = None, open_log: bool = False) -> None:
    oswemodlog = os.getenv("WEMOD_LOG")
    wemodlog = oswemodlog
    cowemodlog = load_conf_setting("WeModLog")
    if not wemodlog:
        wemodlog = cowemodlog
    if wemodlog != "":
        try:
            if not wemodlog:
                raise Exception("wemodlog unset")
            elif os.path.isabs(wemodlog):
                os.makedirs(os.path.dirname(wemodlog), exist_ok=True)
            else:
                os.makedirs(
                    os.path.dirname(
                        os.path.abspath(os.path.join(SCRIPT_PATH, wemodlog))
                    ),
                    exist_ok=True,
                )
        except:
            wemodlog = "wemod.log"
            if not oswemodlog:  # Only save if not a environment var
                save_conf_setting("WeModLog", wemodlog)

            new_message = f"WeModLog path was not given or invalid using path '{wemodlog}'\nIf you don't want to generate a logfile use WEMOD_LOG='' or set the config to WeModLog=''"
            if message == None:
                message = new_message
            else:
                message = new_message + "\n" + message
        if message != None:
            message = str(message)
        if message and message[-1] != "\n":
            message += "\n"
        if not os.path.isabs(wemodlog):
            wemodlog = os.path.abspath(os.path.join(SCRIPT_PATH, wemodlog))
        with open(wemodlog, "a") as f:
            if message != None:
                f.write(message)
        if open_log:
            os.system(f"xdg-open '{wemodlog}'")


# Function to display a message
def show_message(
    message: str,
    title: str,
    timeout: Optional[int] = 30,
    yesno: bool = False,
    show_log_if_gui_missing: bool = False,
) -> Optional[str]:
    try:
        import FreeSimpleGUI as sg
    except Exception as e:
        log(message, show_log_if_gui_missing)
        if yesno:
            return "Yes"
        else:
            return "Ok"
    else:
        sg.theme("systemdefault")
        close = True
        if timeout == None:
            close = False
        if yesno:
            response = sg.popup_yes_no(
                message,
                title=title,
                auto_close=close,
                auto_close_duration=timeout,
            )
        else:
            response = sg.popup_ok(
                message,
                title=title,
                auto_close=close,
                auto_close_duration=timeout,
            )
        return response


# Function to display a message and exit
def exit_with_message(
    title: str,
    exit_message: str,
    exit_code: int = 1,
    timeout: Optional[int] = 20,
    ask_for_log: bool = False,
) -> None:
    if ask_for_log:
        exit_message += (
            "\nDo you want to open the log for more info on the exit error?"
        )
    ret = show_message(
        exit_message,
        title,
        timeout,
        show_log_if_gui_missing=(not ask_for_log),
        yesno=ask_for_log,
    )
    log("\n\n\n")
    if ask_for_log and ret and ret == "Yes":
        log(open_log=True)

    sys.exit(exit_code)


# Function to install or execute pip commands
def pip(command: str, venv_path: Optional[str] = None) -> int:
    if venv_path and not os.path.isabs(venv_path):
        venv_path = os.path.abspath(os.path.join(SCRIPT_PATH, venv_path))
    pos_pip = None
    if venv_path:
        python_executable = os.path.join(
            venv_path, os.path.basename(sys.executable)
        )
        pos_pip = os.path.join(venv_path, "bin", "pip")
        if not os.path.isfile(pos_pip):
            pos_pip = None
    else:
        python_executable = sys.executable

    # Try to use pip directly if possible
    if pos_pip == None:
        pos_pip = "pip"
        process = subprocess.Popen(
            f"'{pos_pip}' {command}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        process.wait()
        # Check if pip command was successful
        if process.returncode == 0:
            log(f"Pip finished successfully")
            return process.returncode
        elif b"externally-managed-environment" in stderr:
            log("Externally managed environment detected.")
            return 99
        else:
            log(f"Pip error appered:\n\t{stdout}\n\t{stderr}")
    else:
        process = subprocess.Popen(
            f"'{pos_pip}' {command}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        process.wait()
        # Check if pip command was successful
        if process.returncode == 0:
            log(f"Pip finished successfully")
            return process.returncode
        elif b"externally-managed-environment" in stderr:
            log("Externally managed environment detected.")
            return 99
        else:
            show_message(
                "The pip inside the virtual environment reported a error,\nthis may require the deletion of the virtual environment folder,\nby defalut the folder is named named wemod_venv\nand is located inside the wemod-laucher folder"
            )
            log(
                f"A pip error appered\nthis may require the deletion of the virtual environment folder,\nby defalut the folder is named named wemod_venv\nand is located inside the wemod-laucher folder,\nthe error is:\n\t{stdout}\n\t{stderr}"
            )

    # Try to use the built-in pip
    process = subprocess.Popen(
        f"'{python_executable}' -m pip {command}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    # Check if -m pip command was successful
    if process.wait() == 0:
        log(f"Pip finished successfully")
        return process.returncode
    elif b"externally-managed-environment" in stderr:
        log("Externally managed environment detected.")
        return 99
    else:
        log(f"Pip error appered:\n\t{stdout}\n\t{stderr}")

    # If -m pip failed, fallback to using pip.pyz
    if venv_path:
        pip_pyz = os.path.join(venv_path, "bin", "pip.pyz")
    else:
        pip_pyz = os.path.join(SCRIPT_PATH, "pip.pyz")

    # Check and download pip.pyz if not present
    if not os.path.isfile(pip_pyz):
        log("Pip not found. Downloading...")
        request.urlretrieve("https://bootstrap.pypa.io/pip/pip.pyz", pip_pyz)

        # Exit if pip.pyz still not present after download
        if not os.path.isfile(pip_pyz):
            log("CRITICAL: Failed to download pip. Exiting!")
            exit_with_message(
                "Pip missing",
                "CRITICAL: Failed to download pip, exiting",
                1,
                timeout=5,
                ask_for_log=True,
            )
    else:
        log("Pip not installed. Using local pip.pyz")

    # Execute the pip command using pip.pyz
    process = subprocess.Popen(
        f"{python_executable} {pip_pyz} {command}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    if process.wait() == 0:
        log(f"Pip finished and returned:\n\t{stdout}\n\t{stderr}")
        return process.returncode
    elif b"externally-managed-environment" in stderr:
        log("Externally managed environment detected.")
        return 99
    else:
        log(f"Pip error appered:\n\t{stdout}\n\t{stderr}")

    # Return the exit code of the process
    return process.returncode


def monitor_file(
    ttfile: str, tout: int, responsefile: str, bout: Optional[int] = 60
):
    import time

    cout = os.getenv("WAIT_ON_GAMECLOSE")
    if not cout:
        cout = load_conf_setting("WaitOnGameclose")
    if cout:
        if cout.lower() == "none" or cout.lower() == "false":
            bout = None
        else:
            try:
                bout = int(cout)
            except Exception as e:
                pass

    for _ in range(tout):
        time.sleep(1)
        if not os.path.exists(ttfile):
            time.sleep(1)
            bat_respond(responsefile, bout)
            return
    if os.path.exists(ttfile):
        os.remove(ttfile)
    time.sleep(1)
    bat_respond(responsefile, bout)


def bat_respond(responsefile: str, bout: Optional[int]):
    if os.path.isfile(responsefile):
        returnmessage = read_file(responsefile)
        if bout != None:
            batresp = show_message(
                returnmessage
                + f",\ndo you want to close WeMod (yes) or wait longer (no)?\nWemod will close in {bout} seconds",
                "BAT Warning",
                bout,
                True,
            )
        if bout == None or batresp == "No":
            show_message(
                returnmessage + ",\nclick ok if you are ready to close WeMod",
                "BAT Warning",
                None,
                False,
            )
        os.remove(responsefile)


# Function to handle caching of files
def cache(
    file_path: str, default: Callable[[str], None], simple: bool = False
) -> str:
    CACHE = os.path.join(SCRIPT_PATH, ".cache")
    if not os.path.isdir(CACHE):
        log("Cache dir not found. Creating...")
        os.mkdir(CACHE)

    FILE = os.path.join(CACHE, file_path)
    if os.path.isfile(FILE):
        log(f"Cached file found. Returning '{FILE}'")
        return FILE

    log(f"Cached file not found: '{FILE}'")

    if simple:
        default(file_path)
    else:
        default(FILE)
    return FILE


# Function to display options
def popup_options(
    title: str,
    message: str,
    options: List[List[str]],
    timeout: Optional[int] = 30,
) -> Optional[str]:
    import FreeSimpleGUI as sg

    # Define the layout based on provided options
    buttons_layout = [
        [sg.Button(option) for option in row] for row in options
    ]
    layout = [[sg.Text(message)]] + buttons_layout

    close = True
    if timeout == None:
        close = False

    window = sg.Window(
        title,
        layout,
        finalize=True,
        auto_close=close,
        auto_close_duration=timeout,
    )

    # Event loop to process button clicks
    while True:
        event, values = window.read()

        if event in sum(
            options, []
        ):  # Flatten the list of lists to check for the event
            window.close()
            return event
        elif (
            event == sg.WIN_CLOSED or event is None
        ):  # If window is closed manually or times out
            window.close()
            return None
    return None


def get_user_input(
    title: str, message: str, default_entry: str, timeout: Optional[int] = 30
) -> List[Union[str, bool]]:
    import FreeSimpleGUI as sg

    # Define the layout with a text element, input field, and OK/Cancel buttons
    layout = [
        [sg.Text(message)],
        [sg.InputText(default_entry, key="-INPUT-")],
        [sg.Button("OK"), sg.Button("Cancel")],
    ]

    close = True
    if timeout == None:
        close = False

    window = sg.Window(
        title,
        layout,
        finalize=True,
        auto_close=close,
        auto_close_duration=timeout,
    )

    # Event loop to process button clicks and input
    while True:
        event, values = window.read()

        if event == "OK":  # If OK is clicked, return the input value
            user_input = values["-INPUT-"]
            window.close()
            return user_input, True
        elif (
            event == "Cancel" or event == sg.WIN_CLOSED
        ):  # If Cancel is clicked or window is closed
            user_input = values["-INPUT-"]
            window.close()
            return (
                user_input,
                False,
            )  # Return None or a default value as needed


def script_manager() -> None:
    script_name = "wemod-laucher"
    script_version = "1.486"
    last_name = load_conf_setting("ScriptName")
    last_version = load_conf_setting("Version")

    if last_name and last_name != script_name:
        log("Warnig config might be for a other script, overwriting name")
    elif not last_name:
        log("Adding script name to config")
    if last_version:
        try:
            if float(last_version) < float(script_version):
                log(
                    f"Config on version {last_version} updating to {script_version}"
                )
            elif float(last_version) > float(script_version):
                log(
                    f"Warnig config on version {last_version} downgrading to {script_version}"
                )
        except Exception as e:
            log(
                f"Warnig config error '{e}' changing version to {script_version}"
            )
    else:
        log("Adding script version to config")

    save_conf_setting("ScriptName", script_name)
    save_conf_setting("Version", script_version)
    log(f"The script {script_name} is running on version {script_version}")
    print(
        f"The wemod script {script_name} is running on version {script_version}"
    )
    return
