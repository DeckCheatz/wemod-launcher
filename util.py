import io
import subprocess
import os
import sys
from typing import Callable
from urllib import request

# Set the script path and define the Wine prefix for Windows compatibility
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
WINEPREFIX = os.path.join(os.getenv("STEAM_COMPAT_DATA_PATH"), "pfx")

# Function to install or execute pip commands
def pip(command: str) -> int:
    # Define the path for pip.pyz
    pip_pyz = os.path.join(SCRIPT_PATH, "pip.pyz")

    # Check and download pip.pyz if not present
    if not os.path.isfile(pip_pyz):
        log("pip not found. Downloading...")
        request.urlretrieve("https://bootstrap.pypa.io/pip/pip.pyz", pip_pyz)

        # Exit if pip.pyz still not present after download
        if not os.path.isfile(pip_pyz):
            log("CRITICAL: Failed to download pip. Exiting!")
            sys.exit(1)

    # Execute the pip command and log the output
    process = subprocess.Popen("python3 {} {}".format(pip_pyz, command), shell=True, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, ''):
        if line is None or line == b'':
            break
        log(line.decode("utf8"))

    # Return the exit code of the process
    return process.wait()

# Function for logging messages
def log(message: str):
    if "WEMOD_LOG" in os.environ:
        message = str(message)
        message = message if list(message)[-1] == "\n" else message + "\n"
        with open(os.getenv("WEMOD_LOG"), "a") as f:
            f.write(message)

# Function to display a popup with options using PySimpleGUI
def popup_options(title: str, message: str, options: list[str]) -> str:
    import PySimpleGUI as sg
    layout = [
        [sg.Text(message, auto_size_text=True)],
        [list(map(lambda option: sg.Button(option), options))]
    ]
    window = sg.Window(title, layout, finalize=True)

    selected = None
    while selected is None:
        event, values = window.read()
        selected = event if options.index(event) > -1 else None

    window.close()
    return selected

# Function to execute a command and display output in a popup
def popup_execute(title: str, command: str, onwrite: Callable[[str], None] = None) -> int:
    import PySimpleGUI as sg
    import subprocess as sp

    sg.theme("systemdefault")

    text_str = [""]
    text = sg.Multiline("", disabled=True, autoscroll=True, size=(80, 30))
    layout = [[text]]
    window = sg.Window(title, layout, finalize=True)
    exitcode = [-1]

    def process_func():
        process = sp.Popen(command, stdout=subprocess.PIPE, shell=True)
        for line in iter(process.stdout.readline, ''):
            if line is None or line == b'':
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
def popup_download(title: str, link: str, file_name: str):
    import PySimpleGUI as sg
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
    download_func = lambda: download_progress(link, file_path, lambda dl, total: update_log(status, dl, total))

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
def download_progress(link: str, file_name: str, set_progress):
    import requests

    with open(file_name, "wb") as f:
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')

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
        request.urlretrieve("https://raw.githubusercontent.com/Winetricks/winetricks/20240105/src/winetricks", winetricks_sh)
        log(f"setting exec permissions on '{winetricks_sh}'")
        process = subprocess.Popen(f"sh -c 'chmod +x {winetricks_sh}'", shell=True)
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
def exit_with_message(title: str, exit_message: str, exit_code: int = 1) -> None:
    import PySimpleGUI as sg
    sg.theme("systemdefault")

    log(exit_message)
    sg.popup_ok(exit_message)
    sys.exit(exit_code)

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
    LINK = "https://download.visualstudio.microsoft.com/download/pr/7afca223-55d2-470a-8edc-6a1739ae3252/abd170b4b0ec15ad0222a809b761a036/ndp48-x86-x64-allos-enu.exe"
    cache_func = lambda FILE: popup_download("Downloading dotnet48", LINK, FILE)

    dotnet48 = cache("ndp48-x86-x64-allos-enu.exe", cache_func)
    return dotnet48

# Main execution block, example of using popup_execute
if __name__ == "__main__":
    popup_execute("HELLO", "sh -c \"echo hello && sleep 5 && echo bye\"")
