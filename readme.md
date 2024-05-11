# WeMod Launcher (Wemod for Linux)

## DISCLAIMER
This project is *NOT* affiliated with, funded by, or paid by WeMod.  
The work done here is purely from the contributors who donate their time and efforts. WeMod (the company) makes WeMod (the mod tool). We (`wemod-launcher`) enable you to run it on Linux (and by extension, the Steam Deck).

## Support
If this helps you, please star the project.
If you would like to support me and/or the project, you could:
<br/>
<div align="center">
  <a href="https://www.buymeacoffee.com/TIjUvF1" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-violet.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;"></a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://www.patreon.com/daniash551" target="_blank"><img src="https://c5.patreon.com/external/logo/become_a_patron_button.png" alt="Become a Patreon" style="height: 60px !important;width: 217px !important;"></a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://www.paypal.com/donate/?hosted_button_id=D7Y43PT9HUEUY" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="Donate via PayPal" style="height: 60px !important;width: 217px !important;"></a>
</div>

## Suggestions
This is a small tool made to launch the popular Game Trainer/Cheat tool WeMod along with your game (made for the steam-runtime version in Linux). I have tested this only on a handful of games, and you are welcome to report your findings/suggestions.

## Changes
- Added a copyer that will copy working WeMod prefixes so you don't have to rebuild all the time.
- Prefix Windows directory dereferenced (fixes dotnet4.8 bug on Proton Version 8 and above) - thanks to Reddit user /u/pickworthi for finding it out.

## Guide
<table>
  <td>
    <img src="https://www.wemod.com/static/images/wemod-logo-40777eae11.webp" alt="WeMod logo "/> 
  </td>
  <td>
    <b>How to Install WeMod on a Steam Deck (Linux)</b><br> 
    In this guide, we'll walk you through the process of installing WeMod on a Steam Deck running Linux.<br>  
    We'll cover all the steps required to set up the necessary components and configurations to seamlessly integrate WeMod with your games.<br> 
</td>
</table>
‎
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=20&quality=lossless" alt="Heart"/>&nbsp;You will need:</h3>

*   A Steam Deck running Linux (or any Linux-based x86\_64 system).
*   A external Mouse and Keyboard (Recommended for Steam Deck).
*   To Install TK through you package manager (If not on SteamOS) as posted in [Issue 29](https://github.com/DaniAsh551/wemod-launcher/issues/29)
*   A WeMod Pro Subscription (Recommended for Steam Deck).  
    **OR** Use a Keyboard to send the key shortcuts to toggle cheats.  
    **OR** Use a Keyboard and Desktop mode to switch the game and WeMod with alt+tab.
*   A stable Internet Connection.
*   **Optional:** If you have access to another PC and wish to control the Steam Deck remotely,  
    consider using **[RustDesk (download the .flatpak file)](https://github.com/rustdesk/rustdesk/releases/latest)** for easier setup. ‎‎  
    **NOTE:** You can also use any alternative approach to install RustDesk for your distro.


****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=20&quality=lossless" alt="Heart"/>&nbsp;Step 1: Access Desktop Mode and Discovery Store</h3>

1.  Go to the Desktop Mode on your Steam Deck _(Skip if you are not using a Steam Deck)_.
2.  Open the Discovery Store _(or any other Flatpak-compatible store on your OS)_.
3.  Search for and install **"ProtonUp-QT"** in the store.
4.  Search for and install **“Protontricks”** in the store.  
    **NOTE:** This is used to find the Game ID for your games,  
    if you know how to find the Game ID without Protontricks you can skip this step.  
    **NOTE:** You can use any alternative approach to install **"ProtonUp-QT"** that is available in your distro.


****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=20&quality=lossless" alt="Heart"/>&nbsp;Step 2: Install Recommended Version of Proton</h3>

1.  Open **"ProtonUp-QT"**
2.  Click on "Add Version" under GE-Proton and select the newest version.  
    **NOTE** At the time of writing this, any **"GE-Proton9"** version will work,  
    but versions above 9 are untested, so maybe stick with any version 9
4.  Restart the Steam Deck _(or Steam if you are not on Steam OS)_.

****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=20&quality=lossless" alt="Heart"/>&nbsp;Step 3: Installing WeMod Launcher</h3>

1.  Open Konsole/Terminal and run: `git clone https://github.com/DaniAsh551/wemod-launcher.git`
2.  In Dolphin/File Browser, navigate to your home at /home/$USER to find the **wemod-launcher** folder and make sure it's there.  
    **NOTE** $USER will need to be replaced with your username.  
    On SteamOS, this will be /home/deck.
    <div><img src="https://cdn.discordapp.com/emojis/1049837871772729354.webp?size=20&quality=lossless" alt="Alert"/>&nbsp;<b>Meta Step:</b> Deleting Game Prefix (If Needed)</div> 
    
      -  **IMPORTANT:** It may be needed to delete the old game prefix. If you run into problems, follow these steps:    
      1.  Open Protontricks and note the "Game ID" next to the game.
      2.  Open Dolphin file manager and enable "Show Hidden Files".
      3.   Navigate to the ".steam" directory (on the drive where you installed your game):  
          `‘home/$USER/.steam/steam/steamapps/compatdata/GameID’`  
          **NOTE** $USER will need to be replaced with your username.  
          On SteamOS, this will be `‘home/deck/.steam/steam/steamapps/compatdata/GameID’`  
      5.  Delete the folder with the corresponding Game ID.

****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=20&quality=lossless" alt="Heart"/>&nbsp;Step 4: Configure Steam Play Compatibility and Launch Options</h3>

1.  Click the game you want to use WeMod with from Steam.
2.  Click on the gear icon and select "Properties".
3.  Go to the Compatibility tab.
4.  Enable "Force the use of a specific Steam Play compatibility tool".
5.  Choose "GE-Proton9" _(restart Steam if not listed)_.
    **NOTE:** GE-Proton9.x is also fine (x can be any number)
7.  Under Launch Options, paste: `WEMOD_LOG=/home/$USER/wemod-launcher/wemod.log /home/$USER/wemod-launcher/wemod %command%`.  
    **NOTE** $USER will need to be replaced with your username.
    On SteamOS, this will be `WEMOD_LOG=/home/deck/wemod-launcher/wemod.log /home/deck/wemod-launcher/wemod %command%`
9.  Launch the game and exit after you reach the game's Main Menu.


****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=20&quality=lossless" alt="Heart"/>&nbsp;Step 5: Install WeMod for Your Game</h3>

1.  Launch the game.
2.  If you have built the launcher in the past, you can try the option of copying the prefix.  
    The launcher will ask you if it can be done and do it for you.  
    **IMPORTANT:** If WeMod fails to start, go to the Meta Step of Step 3 and delete the prefix.  
    In that case, if the launcher asks you if you want to copy, select no.
3.  Select "Build" and then "Winetricks" _(this process takes around 10 minutes on a Steam Deck)_.  
    **IMPORTANT:** if you are using Proton version 7 or earlier, select wemod-launcher instead of winetricks.
5.  Once the build is complete, launch the game _(in Desktop mode again, if you are on a Steam Deck)_.


****

<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.webp?size=20&quality=lossless" alt="Heart"/>&nbsp;Step 6: Configuring WeMod Account and Installing Game Mods</h3>

1.  When you launch the game now, WeMod should Launch with it.
2.  If not logged in, log in or create an account in WeMod _(One time only)_.
3.  Search for the game you launched in WeMod. 
    **IMPORTANT:** It may be needed to add your game in WeMod.
    But if your game gets detected, you can skip the following steps.
4.  Click the arrow next to install.
5.  Locate the game's executable file: Navigate to `/home/$USER/`.
    **NOTE** $USER will need to be replaced with your username.
    On SteamOS, this will be `/home/deck/`
6.  Go to the ".steam" folder and then go to `/steam/steamapps/common/Game/Game.exe`.
    <div><img src="https://cdn.discordapp.com/emojis/1049837871772729354.webp?size=20&quality=lossless" alt="Alert"/>&nbsp;<b>Game Locations may differ</b></div>   
    <b>IMPORTANT:</b> You might have a different installation location than the one provided in the guide,  
    especially if your game is installed on your SD card.  
    This location can vary from person to person. To locate it,  
    you'll need to determine the drive where your SD card is located and then navigate to   
    `/run/media/SDCardName/steamapps/common/Game/Game.exe`.
7.  It may be needed to Restart the Steam Deck _(or Steam if you are not on Steam OS)_.  
    If so relaunch the game after Restart 

****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.gif?size=20&quality=lossless" alt="Heart"/>&nbsp;Final Step: Enabling Mods</h3>
‎

**NOTE:** If you wish to enable or disable mods within SteamOS you will need:
 - A WeMod Pro subscription is required for controlling cheats using a mobile device
 - **OR** you can do it by sending over the keystrokes to toggle mods with a Keyboard.  
Nevertheless, with the free version of WeMod, you can solely manage toggle settings at game start.  
- If this doesn't work you will have to start the game in desktop mode,  
  so you can use alt+tab to switch between open windows.  
- Then just set the cheats you use and start the game in Desktop mode.  
<div><img src="https://cdn.discordapp.com/emojis/1049837871772729354.webp?size=20&quality=lossless" alt="Alert"/>&nbsp;<b>If you find games where WeMod doesn't go on top at game start on SteamOS, please report it.</b></div>     

If WeMod goes on top as expected,  
you will have to click play, even if the game is running.  
You also want to set your cheats at this point  
and after that, you can close the window  
and still use the hotkeys to toggle them on the fly.  
You may need to initiate game launches from WeMod.  
Also, it's important to be aware that certain games may require launching exclusively  
through WeMod in desktop mode to access its features.

****

<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.gif?size=20&quality=lossless" alt="Heart"/>&nbsp;Guide Info</h3>
<div><img src="https://cdn.discordapp.com/emojis/1049837871772729354.gif?size=20&quality=lossless" alt="Alert"/>&nbsp;<b>This guide is designed to remain adaptable and open to improvements in the future.</b><br>
We welcome any ideas, suggestions, or feedback you may have.<br>
Please feel free to share them on GitHub,<br>
as we strive to ensure this guide continues to provide the best possible assistance to our users.<br>
Your input is valuable in making this guide a valuable resource.</div>      

****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.gif?size=20&quality=lossless" alt="Heart"/>&nbsp;Additional</h3>

<div><img src="https://cdn.discordapp.com/emojis/761419274945953842.webp?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>Video Tutorial:</b> Soon!</div>   

<div><img src="https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>Guide was written by Trippin and updated by Marvin1099.</b></div>  

<div><img src="https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>WeMod Linux is developed by DaniAsh551 in recent support by Marvin1099.</b></div>  

<div><img src="https://cdn.discordapp.com/emojis/999743709677633536.gif?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>If you find this guide helpful, we encourage you to star the project.</b></div><br>   

[![Star History Chart](https://api.star-history.com/svg?repos=DaniAsh551/wemod-launcher&type=Date)](https://star-history.com/#DaniAsh551/wemod-launcher&Date)
