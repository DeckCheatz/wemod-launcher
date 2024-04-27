# WeMod Launcher (For Linux)

## DISCLAIMER: For everyone asking: This project is *NOT* affiliated with / funded or paid by / made by WeMod.
The works done here are purely from the contributors who donate their time and efforts. WeMod (the company) makes WeMod (the mod tool). We (`wemod-launcher`) enable you to run it on Linux (and by extension the Steam Deck).

## This is a small tool made to launch the popular Game Trainer / Cheat tool WeMod along with your game (made for steam-runtime version in Linux). I have tested this only on a handful of games and you are welcome to report your findings / suggestions.

## If this Helps you, please star the project.
If you would like to support me and/or the project, you could:
<br/>
<p align="center">
  <a href="https://www.buymeacoffee.com/TIjUvF1" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-violet.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
</p>
<p align="center"><b>OR</b></p>

<p align="center">
  <a href="https://www.patreon.com/daniash551" target="_blank"><img src="https://c5.patreon.com/external/logo/become_a_patron_button.png" alt="Become a Patreon" style="height: 60px !important;width: 217px !important;" ></a>
</p>
<p align="center"><b>OR</b></p>

<p align="center">
  <a href="https://www.paypal.com/donate/?hosted_button_id=D7Y43PT9HUEUY" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="Donate via PayPal" style="height: 60px !important;width: 217px !important;" ></a>
</p>

<hr/>

<p align="center">
  <img src="https://www.wemod.com/static/images/wemod-logo-40777eae11.webp" alt="WeMod logo"/>
</p>

## Changes
- Prefix Windows directory dereferenced (fixes dotnet4.8 bug on Proton Version 8 and above) - thanks to reddit user /u/pickworthi for finding it out

![:wemod:](https://cdn.discordapp.com/emojis/761419420211740672.webp?size=44&quality=lossless) **How to Install WeMod on a Steam Deck (Linux)** In this guide, we'll walk you through the process of installing WeMod on a Steam Deck running Linux. We'll cover all the steps required to set up the necessary components and configurations to seamlessly integrate WeMod with your games. ‎

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728375444258956/sl.png?width=550&height=17)

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728445338124338/123.jpg?width=550&height=309)

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728475117690960/sl.png?width=550&height=17)

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728565966311424/1.png?width=550&height=46)

‎

*   Steam Deck running Linux (or any Linux-based x86\_64 system).
*   External Mouse and Keyboard (Recommended for Steam Deck).
*   WeMod Pro Subscription (Recommended for Steam Deck).
*   Stable Internet Connection.

‎ ![:1_:](https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=44&quality=lossless) **NOTE:** If you have access to another PC and wish to control the Steam Deck remotely, consider using **AnyDesk** for an easier setup. ‎‎

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728689358557184/sl.png?width=550&height=17)

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728715765886976/3.png?width=550&height=46)

‎ **Step 1: Access Desktop Mode and Discovery Store**

1.  Go to the Desktop Mode on your Steam Deck _(Skip if you are not using a Steam Deck)_.
2.  Open the Discovery Store _(or any other Flatpak-compatible store on your OS)_.
3.  Search for and install **"ProtonUp-QT"** in the store.
4.  Search for and install **“Protontricks”** in the store _(this is used to find the Game ID for your games - if you know how to find the Game ID without Protontricks you can skip this step)_.

![:1_:](https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=44&quality=lossless) **NOTE:** You can use any alternative approach to install **"ProtonUp-QT"** that is available in your distro.

**Step 2: Install Recommended Version of Proton**

1.  Open **"ProtonUp-QT"**
2.  Click on "Add Version" under GE-Proton and select **"GE-Proton7-35"** or any **"GE-Proton8"** or  any **"GE-Proton9"** version and download it
3.  Restart Steam Deck _(or Steam if you are not on Steam OS)_.

**Step 3: Installing WeMod Launcher**

1.  Open Konsole/Terminal and run: `git clone https://github.com/DaniAsh551/wemod-launcher.git`
2.  In Dolphin/File Browser, navigate to home/deck to find the **wemod-launcher** folder and make sure it's there. ‎

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728815854563388/sl.png?width=550&height=17)

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728863829016666/2.png?width=550&height=46)

‎ **Meta Step:** Deleting Game Prefix _(If Needed)_

![:alert:](https://cdn.discordapp.com/emojis/1049837871772729354.webp?size=44&quality=lossless) **IMPORTANT:** If you've played the game before with any other proton version or if you are unsure, follow these steps to delete its prefix:

1.  Open Protontricks and note the "Game ID" next to the game.
2.  Open Dolphin file manager and enable "Show Hidden Files".
3.  Navigate to the ".steam" directory (on the drive where you installed your game): `‘home/deck/.steam/steam/steamapps/compatdata/GameID’`
4.  Delete the folder with the corresponding Game ID.

**Step 1: Configure Steam Play Compatibility**

1.  **C**lick the game you want to use WeMod with from Steam.
2.  Click on the gear icon and select "Properties".
3.  Go to the Compatibility tab.
4.  Enable "Force the use of a specific Steam Play compatibility tool".
5.  Choose "GE-Proton7-35" _(restart Steam if not listed)_.
6.  Launch the game and exit after you reach the game's Main Menu.

**Step 2: Configure Launch Options**

1.  Click the game you want to use WeMod with from Steam.
2.  Click the gear icon again.
3.  Under Launch Options and paste: `WEMOD_LOG=/home/deck/wemod-launcher/wemod.log /home/deck/wemod-launcher/wemod %command%`

**Step 3: Install WeMod for Your Game**

1.  Launch the game.
2.  Select "Build" and then "WeMod launcher" _(this process takes around 10 minutes on a Steam Deck)_.
3.  Once the build is complete, launch the game _(in Desktop mode again, if you are on a Steam Deck)_.

NOTE: if the installer asks you whether you want to use wemod-launcher or winetricks to install:
 - Choose wemod-launcher if you are using Proton version 7 or earlier
 - Choose winetricks if you are using Proton version 8 or later

**Step 4: Configuring WeMod Account and Installing Game Mods**

1.  When you launch the game now WeMod should Launch with it
2.  If not logged in, log in or create an account in WeMod _(One time only)_.
3.  Search for the game you launched in WeMod.
4.  Click the arrow next to install.
5.  Locate the game's executable file: Navigate to `/home/deck/`.
6.  Type in the file name ".local" and pick an exe file.
7.  It should take you to the ".local" folder and then go to `share/steam/steamapps/common/Game/Game.exe`.  
    ![:alert:](https://cdn.discordapp.com/emojis/1049837871772729354.webp?size=44&quality=lossless) **IMPORTANT:** You might have a different installation location than the one provided in the guide, especially if your game is installed on your SD card. This location can vary from person to person. To locate it, you'll need to determine the drive where your SD card is located and then navigate to `/run/media/SDCardName/steamapps/common/Game/Game.exe`.
8.  Restart Steam.
9.  Launch the game from SteamOS or Desktop Mode. ‎

![Image](https://media.discordapp.net/attachments/1148707740953362583/1148728947538923580/sl.png?width=550&height=17)

‎ ![:1_:](https://cdn.discordapp.com/emojis/1113579886439833690.gif?size=44&quality=lossless) **NOTE:** If you wish to enable or disable mods within SteamOS, a WeMod Pro subscription is required for controlling cheats using a mobile device. However, with the free version of WeMod, you can solely manage toggle settings within Desktop Mode. Consequently, you will need to initiate game launches from there. Also, It's important to be aware that certain games may require launching exclusively through WeMod in desktop mode to access its features.

![:alert:](https://cdn.discordapp.com/emojis/1049837871772729354.gif?size=44&quality=lossless) This guide is designed to remain adaptable and open to improvements in the future. We welcome any ideas, suggestions, or feedback you may have. Please feel free to share them in the ⁠guide-feedback channel, as we strive to ensure this guide continues to provide the best possible assistance to our users. Your input is valuable in making this guide a valuable resource.

‎![:wemodapp:](https://cdn.discordapp.com/emojis/761419274945953842.webp?size=44&quality=lossless) **Video Tutorial:** Soon!

‎ ![:2_:](https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=44&quality=lossless) **Guide is written by Trippin (Discord: Trippixn)**

![:2_:](https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=44&quality=lossless) **WeMod Linux is developed by DaniAsh551**

‎![:birb:](https://cdn.discordapp.com/emojis/999743709677633536.gif?size=44&quality=lossless) If you find this guide helpful, we encourage you to star the project.

[![Star History Chart](https://api.star-history.com/svg?repos=DaniAsh551/wemod-launcher&type=Date)](https://star-history.com/#DaniAsh551/wemod-launcher&Date)
