# WeMod Launcher (Wemod for Linux)

**The legacy 1.x launcher is currently on version 1.544.**

## Project Status (November 2026)

> [!WARNING]
> This project is being wound down. The app is now called Wand (formerly WeMod). Wand 12.x introduced integrity checks that depend on Windows file-signing certificate APIs that Wine/Proton do not implement. As a result, this launcher cannot load game mods with Wand 12.x. The Wand team has said it does not plan to reverse these changes and has its own plans for official Linux support. The pre-rename WeMod 11.x release is being deprecated and will not work with Wand's services indefinitely. The Wand team has not said how long it will continue to work, so this launcher cannot offer a lasting workaround.
>
> We do not plan to continue the launcher or its rewrite. The repository has not yet been archived; remaining closeout work is tracked in [issue #362](https://github.com/DeckCheatz/wemod-launcher/issues/362).

## Quick Jump

* [Project Status](#project-status-november-2026)
* [Disclaimer](#disclaimer)
* [Official Wand Support](#official-wand-support)
* [Legacy Setup Guide](#legacy-setup-guide-unsupported)
* [Legacy Common Issues](#legacy-common-issues)
* [Credits](#credits)

## DISCLAIMER
This is an independent community project, not affiliated with, funded by, or paid by Wand (formerly WeMod). The Wand company makes the Wand mod tool. This repository historically provided a community launcher for running it on Linux; it does not provide official Wand support.

## Official Wand Support

For questions about Wand (formerly WeMod) or its official Linux plans, use [Wand's official community forums](https://community.wemod.com/), including the [Wand Linux discussion](https://community.wemod.com/t/wand-linux/378772). This project cannot provide support for the Wand app or its future Linux client.

## Legacy Setup Guide (Unsupported)

> **Historical reference only:** These instructions are no longer maintained and are not a way to get current Wand releases working on Linux. Wand 12.x is incompatible with this launcher under Wine/Proton, and the pre-rename WeMod 11.x release is being deprecated. The old guide and troubleshooting notes below may not apply to current versions.

- **Optional:** If you have access to another PC and wish to control the Steam Deck remotely,  
consider using **[RustDesk](https://github.com/rustdesk/rustdesk/releases/latest)** for easier setup (the `.AppImage` is easiest).

- **Info:** [License Change to AGPL3](https://github.com/DeckCheatz/wemod-launcher/discussions/131)

1. Python `python-venv` (or `python3-venv` or `venv` or `virtualenv`; use first one found)  
   and `Tk` need to be installed.  
	Tk / Tkinter may be under a different name in your distribution's repos.  
	If none of the below options work (or your distro is missing), search on the internet for `install Tkinter for YOURDISTRO`.
	- Ubuntu/Debian: `sudo apt install python3-tk`
	- Arch Linux: `sudo pacman -S tk`.
	- Fedora: `sudo dnf install python3-tkinter`
2. Install GE-Proton, which is necessary to run the game and WeMod with. Using Valve's own Proton seems to work, but using GE-Proton is recommended:  
	1. Search for and install `ProtonUp-QT` via your distro's software center. If using Flatpak, command is: `flatpak install net.davidotek.pupgui2`.
	2. Download the latest GE-Proton in `ProtonUp-QT`  
3. Restart Steam/SteamOS.
4. In a terminal session (Konsole if using KDE Plasma):
	1. Change directory to a location of your choosing, then run `git clone https://github.com/DeckCheatz/wemod-launcher`.  
	Make note of the directory obtained with `readlink -f wemod-launcher` (which will be labeled `{path/to/wemod-launcher}` for the rest of this guide).
	2. Run `chmod -R ug+x wemod-launcher`.  
	**NOTE:** To use this tool with the Flatpak version of Steam (not recommended), continue [here](https://github.com/DeckCheatz/wemod-launcher/wiki/Steam-Flatpak-Usage).
5. In your Steam Library, open the game settings with which to run WeMod with. Make sure you ran the game once before doing this!
	1. In the `Compatibility` tab, change the Proton version to the one picked in Step 2, or otherwise to the latest numbered Proton (e.g. Proton-9.0).
	2. Under `Launch Options`, input `{path/to/wemod-launcher}/wemod %command%`.
6. Start the game.
7. Select "no" to the "copy prefix question" if it appears and says `might work`.  
   If it mentions `likely works` (or better) go to step 8 (accept all).
8. Select download.
9. Select Yes/Ok until no more windows appear.  
    All rundll32.exe errors can safely be ignored (by clicking `no`).  
	WeMod should start with the game.
10. (Only done once): Login to your WeMod account.
11. Select the game you're running from the library, then click the Play to start the WeMod engine.   
12. You may now set or switch mods. Closing the WeMod window will keep it running in the background.

wemod-launcher will automatically update if you installed it using step 4.  
**But**: This will only work if you have [launcher version 1.092 or older](https://github.com/DeckCheatz/wemod-launcher/wiki/The-Self-Update).

**Optionally**: Check out tutorials on how to use specific [WeMod Launcher features](https://github.com/DeckCheatz/wemod-launcher/wiki/Launcher-Tutorials)  
**Like**: Check how to [Use External Launchers](https://github.com/DeckCheatz/wemod-launcher/wiki/Using-External-Launchers) (Use The WeMod Launcher outside of Steam)  
**OR**: Check out how to [Edit The Config](https://github.com/DeckCheatz/wemod-launcher/wiki/Config-Usage)

## Legacy Common Issues

### Dot Net Error

These troubleshooting steps are also kept for historical reference and may not work with current Wand releases.

If you see a .net error in Wemod that means your prefix is messed up.  
1. After you close the game the troubleshooter should come up (close ingame not from steam).
2. There select "delete prefix" or something like that.
3. Rerun the game, and when it asks you to use an already installed prefix, with some version, say no.
4. Then click Download.
5. After you managed to find and click download, a tested prefix will be downloaded.
6. After that it should work.

## Credits

- **Launcher creator:** DaniAsh551.
- **Legacy launcher maintainer:** Marvin1099.
- **Planned rewrite lead:** shymega; the rewrite has since been stopped.
- **Project contributor:** JohnHamwi.
- **Guide:** Created by Trippin and later updated by Marvin1099.

Historical setup video: [WeMod Launcher setup tutorial by Marvin1099](https://youtu.be/5UlVCZvIl1E) (may be outdated).
