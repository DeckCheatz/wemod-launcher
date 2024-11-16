import subprocess
from pathlib import Path

HERE = Path(__file__).parent.absolute()
PATH_TO_MAIN = str(HERE / "cli.py")


def install():
    arglist = [
        "poetry",
        "run",
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--hidden-import tkinter",
        "--collect-all tkinter",
        PATH_TO_MAIN,
    ]
    subprocess.run(" ".join(arglist), stdout=subprocess.PIPE, shell=True)
