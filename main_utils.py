#!/usr/bin/env python3

import os
import sys
import shutil

from typing import (
    Callable,
    Optional,
    List,
    Union,
    Any,
)


from corenodep import (
    parse_version,
)

from coreutils import (
    exit_with_message,
    save_conf_setting,
    load_conf_setting,
    cache,
    log,
)

SCRIPT_IMP_FILE = os.path.realpath(__file__)
SCRIPT_PATH = os.path.dirname(SCRIPT_IMP_FILE)


# Get the github releases from "USERNAME/REPO"
def get_github_releases(repo_name: str) -> List[Any]:
    try:
        import requests
    except Exception as e:
        log(f"Failed to fetch releases, the error reports:\n{e}")
        return []
    url = f"https://api.github.com/repos/{repo_name}/releases"
    response = requests.get(url)
    if response.status_code == 200:
        releases = response.json()
        return releases
    else:
        log(
            f"Failed to grab the github releases from '{url}',\nto fix this try to delete the config file"
        )
        return []


# Find the version w.x in the releases best compatible with version y.z
def find_closest_compatible_release(
    releases: list,
    current_version_parts: List[Union[int, None]] = [None, None],
) -> List[Union[Optional[List[int]], Optional[str]]]:
    closest_release = None
    closest_version = None
    closest_release_url = None
    priority = 6

    for release in releases:
        tag_name = release.get("tag_name")
        if tag_name and tag_name.startswith("PfxVer"):
            release_version_parts = parse_version(tag_name)
            if release_version_parts and current_version_parts:
                if (
                    release_version_parts[0] == current_version_parts[0]
                    and release_version_parts[1] == current_version_parts[1]
                ):
                    # Exact match
                    closest_release = release
                    closest_version = release_version_parts
                    closest_release_url = release["assets"][0][
                        "browser_download_url"
                    ]
                    break
                elif (
                    release_version_parts[0] == current_version_parts[0]
                    and release_version_parts[1] < current_version_parts[1]
                ):
                    # Same major, lower minor version
                    if priority > 2 or (
                        priority == 2
                        and (
                            not closest_release
                            or release_version_parts[1] > closest_version[1]
                        )
                    ):
                        priority = 2
                        closest_release = release
                        closest_version = release_version_parts
                        closest_release_url = release["assets"][0][
                            "browser_download_url"
                        ]
                elif (
                    release_version_parts[0] == current_version_parts[0]
                    and release_version_parts[1] > current_version_parts[1]
                ):
                    # Same major, higher minor version
                    if priority > 3 or (
                        priority == 3
                        and (
                            not closest_release
                            or release_version_parts[1] < closest_version[1]
                        )
                    ):
                        priority = 3
                        closest_release = release
                        closest_version = release_version_parts
                        closest_release_url = release["assets"][0][
                            "browser_download_url"
                        ]
                elif release_version_parts[0] < current_version_parts[0]:
                    # Lower major version
                    if priority > 4 or (
                        priority == 4
                        and (
                            not closest_release
                            or release_version_parts[0] > closest_version[0]
                            or (
                                release_version_parts[0] == closest_version[0]
                                and release_version_parts[1]
                                > closest_version[1]
                            )
                        )
                    ):
                        priority = 4
                        closest_release = release
                        closest_version = release_version_parts
                        closest_release_url = release["assets"][0][
                            "browser_download_url"
                        ]
                elif release_version_parts[0] > current_version_parts[0]:
                    # Higher major version
                    if priority > 5 or (
                        priority == 5
                        and (
                            not closest_release
                            or release_version_parts[0] < closest_version[0]
                            or (
                                release_version_parts[0] == closest_version[0]
                                and release_version_parts[1]
                                < closest_version[1]
                            )
                        )
                    ):
                        priority = 5
                        closest_release = release
                        closest_version = release_version_parts
                        closest_release_url = release["assets"][0][
                            "browser_download_url"
                        ]

    return closest_version, closest_release_url


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
        process = sp.Popen(command, stdout=sp.PIPE, shell=True)
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
            exit_with_message(
                "Window Closed", "The window was closed, exiting", timeout=5
            )
        else:
            if len(text_str[0]) < 1:
                continue
            text.update(text_str[0])

    window.close()
    return exitcode[0]


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

    file_path_end = os.path.join(cache, file_name)
    file_path = os.path.join(cache, "." + file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)

    download_func = lambda: download_progress(
        link, file_path, lambda dl, total: update_log(status, dl, total)
    )

    window.perform_long_operation(download_func, "-DL COMPLETE-")

    while True:
        event, values = window.read(timeout=1000)
        if event == "-DL COMPLETE-":
            os.rename(file_path, file_path_end)
            break
        elif event is None:
            exit_with_message(
                "Window Closed", "The window was closed, exiting", timeout=5
            )
        else:
            if len(status) < 2:
                continue
            dl, total = status
            perc = int(100 * (dl / total)) if total > 0 else 0
            text.update(f"{perc}% ({dl}/{total})")
            progress.update(perc)

    window.close()
    return file_path_end


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
            exit_with_message(
                "Window Closed", "The window was closed, exiting", timeout=5
            )

    window.close()


# Function to copy a folder from a to b, with an ignore and allow (has priority) list
def copy_folder_with_progress(
    source: str,
    dest: str,
    zipup: bool = False,
    ignore: Optional[List[Union[None, str]]] = None,
    include_override: Optional[List[Union[None, str]]] = None,
) -> None:
    import zipfile
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
        if zipup:
            extra.update("Zipping file, please be patient...")
        else:
            extra.update("Copying prefix, please be patient...")
        window.refresh()

        if zipup:
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zipf:
                for i, f in enumerate(copy):
                    arcname = f
                    zipf.write(os.path.join(source, f), arcname)
                    update_progress(i + 1, total_files)
        else:
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

    if zipup:
        window = sg.Window("Copying Prefix", layout, finalize=True)
    else:
        window = sg.Window("Zipping File", layout, finalize=True)

    window.refresh()
    window.perform_long_operation(copy_files, "-COPY DONE-")

    while True:
        event, values = window.read(timeout=1000)
        if event == "-COPY DONE-":
            break
        elif event is None:
            exit_with_message(
                "Window Closed", "The window was closed, exiting", timeout=5
            )

    window.close()


def unpack_zip_with_progress(zip_path: str, dest_path: str) -> None:
    import zipfile
    import subprocess
    import FreeSimpleGUI as sg

    def update_progress(unzipped: int, total: int) -> None:
        """Update the GUI with the current progress."""
        percentage = int(100 * (unzipped / total)) if total > 0 else 0
        text.update(f"{percentage}% ({unzipped}/{total})")
        progress.update(percentage)
        window.refresh()

    def unpack_files() -> None:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            files = zip_ref.namelist()
            total_files = len(files)

            extra.update("Unpacking prefix, please be patient...")
            window.refresh()

            for i, file in enumerate(files):
                full_file = os.path.join(dest_path, file)
                try:  # try to create folder if missing
                    if len(
                        os.path.dirname(full_file)
                    ) > 0 and not os.path.isdir(os.path.dirname(full_file)):
                        os.makedirs(os.path.dirname(full_file), exist_ok=True)
                except Exception as e:
                    log(
                        "failed to make dir '"
                        + os.path.dirname(full_file)
                        + "' with error:\n\t"
                        + e
                    )
                try:  # try to delete old file
                    if os.path.isfile(full_file) or os.path.islink(full_file):
                        os.remove(full_file)
                except Exception as e:
                    log(
                        f"failed to remove file '{full_file}' with error:\n\t{e}"
                    )
                try:
                    zip_ref.extract(file, dest_path)
                except Exception as e:
                    log(
                        f"Failed to extract '{file}' from the zip to '{dest_path}' with error:\n\t{e}"
                    )

                update_progress(i + 1, total_files)

    sg.theme("systemdefault")

    progress = sg.ProgressBar(100, orientation="h", s=(50, 10))
    text = sg.Text("0% (0/?)")
    extra = sg.Text("Reading ZIP file, please wait...")
    layout = [[extra], [progress], [text]]
    window = sg.Window("Unpacking Prefix", layout, finalize=True)
    window.refresh()

    try:  # try own dest folder
        subprocess.run(
            ["chown", "-R", os.getlogin(), dest_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        log(
            "failed to own folder as '"
            + os.getlogin()
            + "' for '"
            + dest_path
            + "' with error:\n\t"
            + str(e)
        )
    try:  # try to allow read and write on dest folder
        subprocess.run(
            ["chmod", "-R", "ug+rw", dest_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        log(
            "failed to allow rw on '"
            + dest_path
            + "' with error:\n\t"
            + str(e)
        )

    window.perform_long_operation(unpack_files, "-UNPACK DONE-")

    while True:
        event, values = window.read(timeout=1000)
        if event == "-UNPACK DONE-":
            break
        elif event is None:
            exit_with_message(
                "Window Closed", "The window was closed, exiting", timeout=5
            )

    window.close()


def flatpakrunner():
    import subprocess
    import time

    cachedir = os.path.join(SCRIPT_PATH, ".cache")
    os.makedirs(cachedir, exist_ok=True)

    flatpakrunfile = os.path.join(cachedir, "insideflatpak.tmp")
    errorfile = os.path.join(cachedir, "flatpakerror.tmp")
    warnfile = os.path.join(cachedir, "flatpakwarn.tmp")

    log(f"Looking for runfile '{flatpakrunfile}'")

    save_conf_setting("FlatpakRunning", "new")

    time.sleep(2)
    if load_conf_setting("FlatpakRunning") != "true" and os.path.isfile(
        flatpakrunfile
    ):
        os.remove(flatpakrunfile)

    while not os.path.isfile(flatpakrunfile):
        time.sleep(1)
        print("Looking")
    time.sleep(0.5)
    flcmd = []
    with open(flatpakrunfile, "r") as frf:
        for line in frf:
            flcmd.append(line.rstrip("\n"))
    log(f"Running inside flatpak:\n\t{flcmd}")
    try:
        process = subprocess.run(flcmd, capture_output=True, text=True)
    except Exception as e:
        with open(errorfile, "w") as fef:
            fef.write(str(e))
    else:
        print(str(process.stdout))
        print(str(process.stderr))
    try:
        if os.getenv("SteamCompatDataPath") == None:
            wserver = subprocess.run(
                ["wineserver", "--wait"],
                bufsize=1,
                capture_output=True,
                text=True,
            )
            print(str(wserver.stdout))
            print(str(wserver.stderr))
    except Exception as e:
        with open(warnfile, "w") as fwf:
            fwf.write(str(e))
    if os.path.isfile(flatpakrunfile):
        os.remove(flatpakrunfile)
