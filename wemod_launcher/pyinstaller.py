import subprocess
from pathlib import Path

HERE = Path(__file__).parent.absolute()
PATH_TO_MAIN = str(HERE / "cli.py")


def install():
    args = [
        "--onefile",
        "--windowed",
        "--clean",
        "--hidden-import tkinter",
        "--collect-all tkinter",
        PATH_TO_MAIN,
    ]
    print(" ".join(args))
    subprocess.run("poetry run pyinstaller " + " ".join(args), shell=True)
