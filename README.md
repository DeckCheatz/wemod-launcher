# WeMod Launcher (Wemod for Linux)

**The WeMod Launcher is currently on version 1.540.**

![Alert](https://cdn.discordapp.com/emojis/1049837871772729354.gif?size=20&quality=lossless) **The 1.x line is in bugfix-only mode.** It is no longer getting new features, only bug fixes.  
Active development is happening in the rewrite (see the [Rework Project](#rework-project) below).

## Quick Jump

* [Disclaimer](#disclaimer)
* [Support & Contributions](#support--contributions)
* [Rework Project](#rework-project)
* [Quick Guide](#quick-guide)
* [Common Issues](#common-issues)
* [Additional](#-additional)

## DISCLAIMER
This project is *NOT* affiliated with, funded by, or paid by WeMod.  
The work done here is purely from the contributors who donate their time and effort.  
WeMod (the company) makes WeMod (the mod tool).  
We (`wemod-launcher`) enable you to run it on Linux (and by extension, the Steam Deck).

## Support & Contributions
If this tool helps you, please consider one or more of the following:

* **Star the project** to show support and visibility.  
* **Read the [Contribution Policy](CONTRIBUTING.md)** to learn what the project strives for, what a good PR looks like, and how AI-assisted contributions are handled.
* **Contribute code** we are actively looking for developers to improve the current launcher, to help with the modern rework in areas like GUI, Wine handling, config logic, and Python code structure, and to improve Flatpak compatibility (see [Rework Project](#rework-project) below).
* **Help with docs and issues** — document known issues, write new guides, or help others by referencing existing solutions. See the [Wiki](https://github.com/DeckCheatz/wemod-launcher/wiki) or [file / answer an Issue](https://github.com/DeckCheatz/wemod-launcher/issues).
* **Financial and regular support for developers**:
  * Support Marvin1099 (current maintainer):  
    [Buymeacoffee](https://www.buymeacoffee.com/marvin1099), [Patreon](https://www.patreon.com/marvin1099), [Tipeeestream](https://www.tipeeestream.com/marvin1099/tip)
  * Support shymega (rework leader):  
    [GitHub Sponsors](https://github.com/sponsors/shymega)
  * Support DaniAsh551 (original creator):  
    [Buymeacoffee](https://www.buymeacoffee.com/TIjUvF1), [Patreon](https://www.patreon.com/daniash551), [PayPal](https://www.paypal.com/donate/?hosted_button_id=D7Y43PT9HUEUY)
  * Support JohnHamwi (contributor):  
    [GitHub](https://github.com/JohnHamwi)

For more help:
* Suggest improvements via [GitHub Discussions](https://github.com/DeckCheatz/wemod-launcher/discussions)
* See the [Wiki Suggestions](https://github.com/DeckCheatz/wemod-launcher/wiki/Suggestions) and [Changes](https://github.com/DeckCheatz/wemod-launcher/wiki/Changes)

## Rework Project

The project has a **rework**, currently on the /rewrite/v2 branch (NOT USEABLE).  
This rework focuses on **modular design, better maintainability, improved UX, and modern code practices**.

We are calling for contributors to assist with:
* **Python developers**: Help refactor or implement core modules (GUI, Wine prefix handling, config, launch logic).
* **Testers**: Provide feedback, test new code, and report issues across different distros and devices (especially Steam Deck).
* **Wiki writers & documenters**: Help write guides and technical documentation for the rework.

Want to get involved?
* [Join the Discussion on GitHub](https://github.com/DeckCheatz/wemod-launcher/discussions)
* [Track the Rework Progress](https://github.com/orgs/DeckCheatz/projects/3/)
* Or reach out to the maintainers directly via GitHub.

## Quick Guide
![Alert](https://cdn.discordapp.com/emojis/1049837871772729354.gif?size=20&quality=lossless) **This guide only includes the most relevant info and might not be enough to run WeMod;**  
in which case, check out the [Full Guide](https://github.com/DeckCheatz/wemod-launcher/wiki/Full-Guide) **OR** the [video tutorial by Marvin1099](https://youtu.be/5UlVCZvIl1E).

- **Optional:** If you have access to another PC and wish to control the Steam Deck remotely,  
consider using **[RustDesk](https://github.com/rustdesk/rustdesk/releases/latest)** for easier setup (the `.AppImage` is easiest).

- **Info:** [License Change to AGPL3](https://github.com/DeckCheatz/wemod-launcher/discussions/131)

- **Info:** Games no longer seem to be detected by **Wemod**. If anyone has info on how **Wemod** finds games, please make a new issue. If you have no idea, please **don't** make a bug report.  
  We can't fix this if we don't know how. You will have to add the game manually for now.

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

## Common Issues

### Dot Net Error

If you see a .net error in Wemod that means your prefix is messed up.  
1. After you close the game the troubleshooter should come up (close ingame not from steam).
2. There select "delete prefix" or something like that.
3. Rerun the game, and when it asks you to use an already installed prefix, with some version, say no.
4. Then click Download.
5. After you managed to find and click download, a tested prefix will be downloaded.
6. After that it should work.

## ![Heart](https://cdn.discordapp.com/emojis/1113579886439833690.gif?size=20&quality=lossless) Additional

![WeModApp](https://cdn.discordapp.com/emojis/761419274945953842.webp?size=20&quality=lossless) **Video Tutorial:** [WeMod-launcher Setup Tutorial by Marvin1099](https://youtu.be/5UlVCZvIl1E)  
![WeModApp](https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless) **Guide was created by Trippin and updated by Marvin1099.**  
![WeModApp](https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless) **The WeMod Launcher was created by DaniAsh551, with the current maintainer Marvin1099.**  


<a href="https://star-history.com/#DeckCheatz/wemod-launcher&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=DeckCheatz/wemod-launcher&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=DeckCheatz/wemod-launcher&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=DeckCheatz/wemod-launcher&type=Date" />
 </picture>
</a>
