#!/usr/bin/env python3

import os
import shutil
import pathlib
import PySimpleGUI as sg


def copy_folder_with_progress(source: str, dest: str, ignore=None, include_override=None) -> None:
    if ignore is None:
        ignore = set()

    if include_override is None:
        include_override = set()

    def traverse_folders(path):
        allf = []
        directory = pathlib.Path(path)
        for item in directory.rglob('*'): #sorted(, key=lambda x: str(x).count('/')):
            if item.is_file():
                allf.append(item)
        return allf

    def update_progress(copied, total):
        """ Update the GUI with the current progress. """
        percentage = int(100 * (copied / total)) if total > 0 else 0
        text.update(f"{percentage}% ({copied}/{total})")
        progress.update(percentage)
        window.refresh()

    sg.theme("systemdefault")

    progress = sg.ProgressBar(100, orientation="h", s=(50, 10))
    text = sg.Text("0%")
    extra = sg.Text("Reading prefix directory, please wait..")
    layout = [[extra] ,[progress], [text]]
    window = sg.Window('Copying Prefix', layout, finalize=True)
    window.refresh()

    files = traverse_folders(source)

    copy=[]
    for f in files:
        rfile = os.path.relpath(f, source)  # get file path relative to source
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

    extra.update("Copying prefix, please be patient...")
    window.refresh()

    total_files = len(files)
    copied_files = 0

    for f in copy:
        src_path = os.path.join(source, f)
        dest_path = os.path.join(dest, f)
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path, follow_symlinks=False)
        except:
            pass
        copied_files += 1
        update_progress(copied_files, total_files)


    window.close()
