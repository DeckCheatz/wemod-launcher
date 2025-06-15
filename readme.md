# WeMod Launcher (Wemod for Linux)

**The WeMod Launcher is currently on version 1.531.**

## DISCLAIMER
This project is *NOT* affiliated with, funded by, or paid by WeMod.  
The work done here is purely from the contributors who donate their time and effort.  
WeMod (the company) makes WeMod (the mod tool).  
We (`wemod-launcher`) enable you to run it on Linux (and by extension, the Steam Deck).

## Support & Contributions

If this tool helps you, please consider one or more of the following:

* **Star the project** to show support and visibility.  
* **Code contributions are welcome!**  
  We are actively looking for developers, especially to support and collaborate with the **rework effort** (see below).
  * General developers to improve the current launcher.
  * Developers to assist shymega’s modern rework in areas like GUI, Wine handling, config logic, and Python code structure.
  * Flatpak compatibility improvements.
  
* **Wiki contributors**:
  * Help document known issues and write new guides.
  
* **Answering issues**:
  * Help others by referencing existing solutions or adding new ones.
  
* **Financial and regular support for developers**:
  * Support Marvin1099 (current maintainer):  
    [Buymeacoffee](https://www.buymeacoffee.com/marvin1099), [Patreon](https://www.patreon.com/marvin1099), [Tipeeestream](https://www.tipeeestream.com/marvin1099/tip)
  * Support shymega (rework leader):  
    [GitHub Sponsors](https://github.com/sponsors/shymega)
  * Support DaniAsh551 (original creator):  
    [Buymeacoffee](https://www.buymeacoffee.com/TIjUvF1), [Patreon](https://www.patreon.com/daniash551), [PayPal](https://www.paypal.com/donate/?hosted_button_id=D7Y43PT9HUEUY)
  * Support JohnHamwi (contributor):  
    [GitHub](https://github.com/JohnHamwi)

For more help or to contribute:
* Suggest improvements via [GitHub Discussions](https://github.com/DeckCheatz/wemod-launcher/discussions)
* See the [Wiki Suggestions](https://github.com/DeckCheatz/wemod-launcher/wiki/Suggestions) and [Changes](https://github.com/DeckCheatz/wemod-launcher/wiki/Changes)
* Report / Help solve issues or bugs by [filing / answering an Issue](https://github.com/DeckCheatz/wemod-launcher/issues)

## Rework Project (Led by shymega)

The project has a **rework**, initiated by **shymega**.
This rework focuses on **modular design, better maintainability, improved UX, and modern code practices**.

We are calling for contributors to assist with:
* **Python developers**: Help refactor or implement core modules (GUI, Wine prefix handling, config, launch logic).
* **Testers**: Provide feedback, test new code, and report issues across different distros and devices (especially Steam Deck).
* **Wiki writers & documenters**: Help write guides and technical documentation for the rework.

Want to get involved?
* [Join the Discussion on GitHub](https://github.com/DeckCheatz/wemod-launcher/discussions)
* [Track the Rework Progress](https://github.com/DeckCheatz/wemod-launcher/issues?q=is%3Aissue+label%3Arework)
* Or reach out to shymega directly via GitHub.

## Quick Guide
![Alert](https://cdn.discordapp.com/emojis/1049837871772729354.gif?size=20&quality=lossless) **This guide only includes the most relevant info and might not be enough to run WeMod;**  
in which case, check out the [Full Guide](https://github.com/DeckCheatz/wemod-launcher/wiki/Full-Guide) **OR** the [video tutorial by Marvin1099](https://youtu.be/5UlVCZvIl1E).

- **Optional:** If you have access to another PC and wish to control the Steam Deck remotely,  
consider using **[RustDesk](https://github.com/rustdesk/rustdesk/releases/latest)** for easier setup (the `.flatpak` is easiest).

- **Info:** The Proposal to change the License of the wemod launcher from MIT to AGLP3  
  was accepted by contributions and voters [(info here)](https://github.com/DeckCheatz/wemod-launcher/discussions/131) 
  and was integrated into the project on 1st December 2024.

1. Python `virtualenv` (or `venv`) and `Tk` need to be installed.  
	`venv` should already be integrated in your `python3` installation.
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
	**NOTE:** To use this tool with the Flatpak version of Steam (not recomended), continue [here](https://github.com/DeckCheatz/wemod-launcher/wiki/Steam-Flatpak-Usage).
5. In your Steam Library, open the game settings with which to run WeMod with. Make sure you ran the game once before doing this!
	1. In the `Compatibility` tab, change the Proton version to the one picked in Step 2, or otherwise to the latest numbered Proton (e.g. Proton-9.0).
	2. Under `Launch Options`, input `{path/to/wemod-launcher}/wemod %command%`.
6. Start the game.
7. Select "no" to the "copy prefix question" if it appears and says `might work`.  
   If it mentions `likely works` (or better) go to step 9 (accept all).
8. Select download.
9. Select Yes/Ok until no more windows appear.  
    All rundll32.exe errors can safely be ignored (by clicking `no`).  
	WeMod should start with the game.
10. (Only done once): Login to your WeMod account.
11. Select the game you're running from the library, then click the Play to start the WeMod engine.   
12. You may now set or switch mods. Closing the WeMod window will keep it running in the background.

wemod-launcher will automatically update if you installed it using step 5.  
**But**: This will only work if you have [launcher version 1.092 or older](https://github.com/DeckCheatz/wemod-launcher/wiki/The-Self-Update).

**Optionally**: Check out tutorials on how to use specific [WeMod Laucher features](https://github.com/DeckCheatz/wemod-launcher/wiki/Launcher-Tutorials)  
**Like**: Check how to [Use External Launchers](https://github.com/DeckCheatz/wemod-launcher/wiki/Using-External-Launchers) (Use The WeMod Launcher outside of Steam)  
**OR**: Check out how to [Edit The Config](https://github.com/DeckCheatz/wemod-launcher/wiki/Config-Usage)

## ![Heart](https://cdn.discordapp.com/emojis/1113579886439833690.gif?size=20&quality=lossless) Additional

![WeModApp](https://cdn.discordapp.com/emojis/761419274945953842.webp?size=20&quality=lossless) **Video Tutorial:** [WeMod-launcher Setup Tutorial by Marvin1099](https://youtu.be/5UlVCZvIl1E)  
![WeModApp](https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless) **Guide was written by Trippin and updated by Marvin1099.**  
![WeModApp](https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless) **WeMod Linux is developed by DaniAsh551 with recent support by Marvin1099.**  
![WeModApp](https://cdn.discordapp.com/emojis/999743709677633536.gif?size=20&quality=lossless) **If you find this guide to be helpful, we encourage you to star the project.**


<a href="https://star-history.com/#DeckCheatz/wemod-launcher&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=DeckCheatz/wemod-launcher&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=DeckCheatz/wemod-launcher&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=DeckCheatz/wemod-launcher&type=Date" />
 </picture>
</a>
