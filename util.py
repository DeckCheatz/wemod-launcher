import io
import subprocess
import os
import sys
import tempfile
import configparser
from typing import Callable, Optional, List, Union
from urllib import request

# Set the script path and define the Wine prefix for Windows compatibility
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
WINEPREFIX = os.path.join(os.getenv("STEAM_COMPAT_DATA_PATH"), "pfx")
# Set config location, and start config paser
CONFIG_PATH = os.path.join(SCRIPT_PATH, "wemod.conf")
DEF_SECTION = "Settings"
CONFIG = configparser.ConfigParser()
CONFIG.optionxform = str
if os.path.exists(CONFIG_PATH):
    CONFIG.read(CONFIG_PATH)


# Read a setting of the configfile
def load_conf_setting(
    setting: str, section: str = DEF_SECTION
) -> Optional[str]:
    if section in CONFIG and setting in CONFIG[section]:
        return CONFIG[section][setting]
    return None


# Function to grab the Steam Compat Data Path
def get_compat() -> str:
    ccompat = load_conf_setting("SteamCompatDataPath")
    ecompat = os.getenv("STEAM_COMPAT_DATA_PATH")
    if not ecompat:
        exit_with_message(
            "Not running GE-Proton",
            "Error, GE-Proton was not selected in the compatibility settings, exiting",
        )
    if ccompat:
        return os.path.join(ccompat, ecompat.split(os.sep)[-1])
    return ecompat


# Grab steam compat path
BASE_STEAM_COMPAT = get_compat()


# Save a value onto a setting of the configfile
def save_conf_setting(
    setting: str, value: Optional[str] = None, section: str = DEF_SECTION
) -> None:
    if not isinstance(section, str):
        log("Error adding the given section it wasn't a string")
        return
    if section not in CONFIG:
        CONFIG[section] = {}
    if value == None:
        if setting in CONFIG[section]:
            del CONFIG[section][setting]
    elif isinstance(value, str):
        CONFIG[section][setting] = value
    else:
        log("Error saving given value it wasn't a sting")
        return
    with open(CONFIG_PATH, "w") as configfile:
        CONFIG.write(configfile)


# Function to check if dependencies are installed
def check_dependencies(requirements_file: str) -> bool:
    ret = True
    # Check if dependencies have been installed
    with open(requirements_file) as f:
        for line in f:
            package = line.strip().split("==")[0]
            try:
                __import__(package)
            except ImportError:
                log(f"{package} is missing")
                ret = False
    return ret


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
    if pos_pip:
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
            log("pip finished")
            return process.returncode
        elif b"externally-managed-environment" in stderr:
            log("ERROR: Externally managed environment detected.")
            return 99

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
        log("pip finished")
        return process.returncode
    elif b"externally-managed-environment" in stderr:
        log("ERROR: Externally managed environment detected.")
        return 99

    # If -m pip failed, fallback to using pip.pyz
    if venv_path:
        pip_pyz = os.path.join(venv_path, "bin", "pip.pyz")
    else:
        pip_pyz = os.path.join(SCRIPT_PATH, "pip.pyz")

    # Check and download pip.pyz if not present
    if not os.path.isfile(pip_pyz):
        log("pip not found. Downloading...")
        request.urlretrieve("https://bootstrap.pypa.io/pip/pip.pyz", pip_pyz)

        # Exit if pip.pyz still not present after download
        if not os.path.isfile(pip_pyz):
            log("CRITICAL: Failed to download pip. Exiting!")
            sys.exit(1)
    else:
        log("pip not installed. Using local pip.pyz")

    # Execute the pip command using pip.pyz
    process = subprocess.Popen(
        f"{python_executable} {pip_pyz} {command}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    if process.wait() == 0:
        log("pip finished")
    elif b"externally-managed-environment" in stderr:
        log("ERROR: Externally managed environment detected.")
        return 99
    # Return the exit code of the process
    return process.returncode


# Function for logging messages
def log(message: str) -> None:
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

            message = f"WeModLog path was not given or invalid using path '{wemodlog}'\nIf you don't want to generate a logfile use WEMOD_LOG='' or set the config to WeModLog=''\n{message}"
        message = str(message)
        if message and message[-1] != "\n":
            message += "\n"
        if not os.path.isabs(wemodlog):
            wemodlog = os.path.abspath(os.path.join(SCRIPT_PATH, wemodlog))
        with open(wemodlog, "a") as f:
            f.write(message)


# Function to display a popup with options using FreeSimpleGUI
def popup_options(
    title: str, message: str, options: list[str], timeout: Optional[int] = 30
) -> str:
    import FreeSimpleGUI as sg

    # Define the layout based on provided options
    buttons = [sg.Button(option) for option in options]
    layout = [[sg.Text(message)], buttons]

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

        if (
            event in options
        ):  # If a recognized button is clicked, return that option
            window.close()
            return event
        elif (
            event == sg.WIN_CLOSED or event is None
        ):  # If window is closed manually or times out
            window.close()
            return None  # You could return a default or handle this


# Function to execute a command and display output in a popup
def popup_execute(
    title: str, command: str, onwrite: Optional[Callable[[str], None]] = None
) -> int:
    import FreeSimpleGUI as sg
    import subprocess as sp

    sg.theme("systemdefault")

    text_str = [""]
    text = sg.Multiline("", disabled=True, autoscroll=True, size=(80, 30))
    layout = [[text]]
    window = sg.Window(title, layout, finalize=True)
    exitcode = [-1]

    def process_func() -> None:
        process = sp.Popen(command, stdout=subprocess.PIPE, shell=True)
        for line in iter(process.stdout.readline, ""):
            if line is None or line == b"":
                break
            s_line = line.decode("utf8")
            log(s_line)
            text_str[0] = text_str[0] + s_line + "\n"
            if onwrite is not None:
                onwrite(s_line)
        exitcode[0] = process.wait()

    window.perform_long_operation(process_func, "-PROCESS COMPLETE-")

    while True:
        event, values = window.read(timeout=1000)
        if event == "-PROCESS COMPLETE-":
            break
        elif event is None:
            sys.exit(0)
        else:
            if len(text_str[0]) < 1:
                continue
            text.update(text_str[0])

    window.close()
    return exitcode[0]


# Function to download a file with progress display
def popup_download(title: str, link: str, file_name: str) -> str:
    import FreeSimpleGUI as sg

    sg.theme("systemdefault")

    status = [0, 0]

    cache = os.path.join(SCRIPT_PATH, ".cache")
    if not os.path.isdir(cache):
        os.makedirs(cache)

    progress = sg.ProgressBar(100, orientation="h", s=(50, 10))
    text = sg.Text("0%")
    layout = [[progress], [text]]
    window = sg.Window(title, layout, finalize=True)

    def update_log(status: list[int], dl: int, total: int) -> None:
        status.clear()
        status.append(dl)
        status.append(total)

    file_path = os.path.join(cache, file_name)
    download_func = lambda: download_progress(
        link, file_path, lambda dl, total: update_log(status, dl, total)
    )

    window.perform_long_operation(download_func, "-DL COMPLETE-")

    while True:
        event, values = window.read(timeout=1000)
        if event == "-DL COMPLETE-":
            break
        elif event is None:
            sys.exit(0)
        else:
            if len(status) < 2:
                continue
            dl, total = status
            perc = int(100 * (dl / total)) if total > 0 else 0
            text.update(f"{perc}% ({dl}/{total})")
            progress.update(perc)

    window.close()
    return file_path


# Function to handle download progress
def download_progress(
    link: str, file_name: str, set_progress: Callable[[int, int], None]
) -> None:
    import requests

    with open(file_name, "wb") as f:
        response = requests.get(link, stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                if set_progress is not None:
                    set_progress(dl, total_length)


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


# Function to display a message and exit
def exit_with_message(
    title: str,
    exit_message: str,
    exit_code: int = 1,
    timeout: Optional[int] = 20,
) -> None:
    show_message(exit_message, title, timeout)
    sys.exit(exit_code)


# Function to display a message
def show_message(
    message: str, title: str, timeout: Optional[int] = 30, yesno: bool = False
) -> Optional[str]:
    import FreeSimpleGUI as sg

    sg.theme("systemdefault")

    log(message)

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


# Function to handle caching of files
def cache(file_path: str, default: Callable[[str], None]) -> str:
    CACHE = os.path.join(SCRIPT_PATH, ".cache")
    if not os.path.isdir(CACHE):
        log("Cache dir not found. Creating...")
        os.mkdir(CACHE)

    FILE = os.path.join(CACHE, file_path)
    if os.path.isfile(FILE):
        log(f"Cached file found. Returning '{FILE}'")
        return FILE

    log(f"Cached file not found: '{FILE}'")

    default(FILE)
    return FILE


# Function to get or download .NET Framework 4.8
def get_dotnet48() -> str:
    # Newer if you like to test: "https://download.visualstudio.microsoft.com/download/pr/2d6bb6b2-226a-4baa-bdec-798822606ff1/8494001c276a4b96804cde7829c04d7f/ndp48-x86-x64-allos-enu.exe"
    LINK = "https://download.visualstudio.microsoft.com/download/pr/7afca223-55d2-470a-8edc-6a1739ae3252/abd170b4b0ec15ad0222a809b761a036/ndp48-x86-x64-allos-enu."
    cache_func = lambda FILE: popup_download(
        "Downloading dotnet48", LINK, FILE
    )

    dotnet48 = cache("ndp48-x86-x64-allos-enu.exe", cache_func)
    return dotnet48


# Function to turn syslinks into files
def deref(path: str) -> None:
    import FreeSimpleGUI as sg

    def dereference_links() -> None:
        links = find_symlinks(path)
        total_links = len(links)
        extra.update("Dereferencing links, please be patient...")
        for i, link in enumerate(links):
            target, src = link
            try:
                if os.path.exists(src):
                    with open(src, "rb") as src_file:
                        data = src_file.read()
                    os.remove(target)
                    with open(target, "wb") as target_file:
                        target_file.write(data)
                else:
                    os.remove(target)  # Remove the broken link
            except Exception as e:
                log(f"Failed to dereference {target}: {e}")
            update_progress(int((i + 1) / total_links * 100))

    def find_symlinks(path: str) -> List[List[str]]:
        import pathlib

        links = []
        directory = pathlib.Path(path)
        for item in directory.rglob("*"):
            if item.is_symlink():
                target = str(item)
                src = os.readlink(target)
                links.append([target, src])
        return links

    def update_progress(percentage: int) -> None:
        progress.update(percentage)
        text.update(f"{percentage}%")
        window.refresh()

    sg.theme("systemdefault")

    progress = sg.ProgressBar(100, orientation="h", size=(50, 10))
    text = sg.Text("0%")
    extra = sg.Text("Reading directory, please wait...")
    layout = [[extra], [progress], [text]]
    window = sg.Window("Dereferencing Links", layout, finalize=True)
    window.refresh()

    window.perform_long_operation(dereference_links, "-DEREF DONE-")

    while True:
        event, values = window.read(timeout=1000)
        if event == "-DEREF DONE-":
            break
        elif event is None:
            sys.exit(0)

    window.close()


# Function to copy a folder from a to b, with an ignore and allow (has priority) list
def copy_folder_with_progress(
    source: str,
    dest: str,
    ignore: Optional[List[Union[None, str]]] = None,
    include_override: Optional[List[Union[None, str]]] = None,
) -> None:
    import FreeSimpleGUI as sg

    if not ignore:
        ignore = []

    if not include_override:
        include_override = []

    if None in ignore:
        ignore.remove(None)
        ignore = list(ignore) + [
            "pfx/drive_c/users",
            "pfx/dosdevices",
            "pfx/drive_c/Program Files (x86)",
            "pfx/drive_c/Program Files",
            "pfx/drive_c/ProgramData",
            "drive_c/openxr",
            "pfx/drive_c/vrclient",
            "version",
            "config_info",
        ]

    if None in include_override:
        include_override.remove(None)
        include_override = list(include_override) + [
            "pfx/drive_c/ProgramData/Microsoft",
            "pfx/drive_c/Program Files (x86)/Microsoft.NET",
            "pfx/drive_c/Program Files (x86)/Windows NT",
            "pfx/drive_c/Program Files (x86)/Common Files",
            "pfx/drive_c/Program Files/Common Files",
            "pfx/drive_c/Program Files/Common Files",
            "pfx/drive_c/Program Files/Windows NT",
        ]

    log(f"ignoring: {ignore}\nincluding anyway: {include_override}")

    def traverse_folders(path: str) -> List[str]:
        import pathlib

        allf = []
        directory = pathlib.Path(path)
        for item in directory.rglob("*"):
            if item.is_file():
                allf.append(item)
        return allf

    def update_progress(copied: int, total: int) -> None:
        """Update the GUI with the current progress."""
        percentage = int(100 * (copied / total)) if total > 0 else 0
        text.update(f"{percentage}% ({copied}/{total})")
        progress.update(percentage)
        window.refresh()

    def copy_files() -> None:
        import shutil

        files = traverse_folders(source)
        copy = []
        for f in files:
            rfile = os.path.relpath(
                f, source
            )  # get file path relative to source
            use = True  # by default, use the file

            # Check if the file is in one of the dirs to ignore
            for i in ignore:
                if os.path.commonprefix([rfile, i]) == i:
                    use = False  # don't use the file if it's in an ignore directory
                    break  # break out of the ignore loop

            # If the file is not in any ignored directory, check if it's in one of the dirs to include
            if not use:
                for i in include_override:
                    if os.path.commonprefix([rfile, i]) == i:
                        use = True  # use the file if it's in an include_override directory
                        break  # break out of the include_override loop
            if use:
                copy.append(rfile)

        total_files = len(copy)
        extra.update("Copying prefix, please be patient...")
        window.refresh()

        for i, f in enumerate(copy):
            src_path = os.path.join(source, f)
            dest_path = os.path.join(dest, f)
            try:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path, follow_symlinks=False)
                update_progress(i + 1, total_files)
            except Exception as e:
                log(f"Failed to copy {src_path} to {dest_path}: {e}")

    sg.theme("systemdefault")

    progress = sg.ProgressBar(100, orientation="h", s=(50, 10))
    text = sg.Text("0% (0/?)")
    extra = sg.Text("Reading prefix directory, please wait...")
    layout = [[extra], [progress], [text]]
    window = sg.Window("Copying Prefix", layout, finalize=True)
    window.refresh()

    window.perform_long_operation(copy_files, "-COPY DONE-")

    while True:
        event, values = window.read(timeout=1000)
        if event == "-COPY DONE-":
            break
        elif event is None:
            sys.exit(0)

    window.close()
