# WeMod Launcher (Wemod for Linux)
**The WeMod Launcher is currently on version 1.470.**

## DISCLAIMER
This project is *NOT* affiliated with, funded by, or paid by WeMod.  
The work done here is purely from the contributors who donate their time and efforts.  
WeMod (the company) makes WeMod (the mod tool).  
We (`wemod-launcher`) enable you to run it on Linux (and by extension, the Steam Deck).

## Support
If this helps you, please star the project.  
If you would like to support the project, manly we need some more developers.
  <br>You can also support the original developer DaniAsh551:
    &nbsp;
    <a href="https://www.buymeacoffee.com/TIjUvF1" target="_blank">On Buymeacoffee,</a>
    <a href="https://www.patreon.com/daniash551" target="_blank">On Patreon,</a>
    <a href="https://www.paypal.com/donate/?hosted_button_id=D7Y43PT9HUEUY" target="_blank">On PayPal</a>
  <br>You can support the current developer Marvin1099: 
    &nbsp;
    <a href="https://www.patreon.com/marvin1099" target="_blank">On Patreon,</a>
    <a href="https://www.tipeeestream.com/marvin1099/tip" target="_blank">On Tipeeestream</a>
  <br>You can also suport the developer JohnHamwi:
    &nbsp;
    <a href="https://github.com/JohnHamwi" target="_blank">On Github</a>
<br>
<br>But realy if you can help with some code that would be geat.
<br>You are also welcome to report your findings/suggestions.
<br>For more infos on sugesstions check out the <a href="https://github.com/DaniAsh551/wemod-launcher/wiki/Suggestions">Wiki Suggestion info</a>

Check the [Wiki Changelog](https://github.com/DaniAsh551/wemod-launcher/wiki/Changes) or the [Wiki features section](https://github.com/DaniAsh551/wemod-launcher/wiki/Features) for changes.

## Quick Guide
<div><img src="https://cdn.discordapp.com/emojis/1049837871772729354.gif?size=20&quality=lossless" alt="Alert"/>&nbsp;<b> This guide only includes the most relevant info and might not be enough to run WeMod,</b>
<div> &nbsp; &nbsp; &nbsp; &nbsp; if so check out the <a href="https://github.com/DaniAsh551/wemod-launcher/wiki/Full-Guide">Full Guide</a> <b>OR</b> the <a href="https://youtu.be/5UlVCZvIl1E">video tutorial by Marvin1099</a><br><br>

- **Optional:** If you have access to another PC and wish to control the Steam Deck remotely,  
consider using **[RustDesk](https://github.com/rustdesk/rustdesk/releases/latest)** for easier setup (the `.flatpak` is easiest).  

1. First `Python venv` and `TK` need to be installed  
   TK / Tkinter may have a other name in your repos  
   Search the internet for `install Tkinter for YOURDISTRO` (eg. Ubuntu)
2. Also Search for and install `ProtonUp-QT` in the store.
3. Download the latest `GE-Proton` in `ProtonUp-QT`  
   **NOTE:** After some testing it seams `Proton` also works  
   So you can try to run the launcher with `Proton` and without `GE-Proton`
4. Restart Steam/SteamOS
5. Run `git clone https://github.com/DaniAsh551/wemod-launcher.git` in the Konsole/Terminal
6. Run `sudo chmod -R ug+x /home/$USER/wemod-launcher` in the Konsole/Terminal
   **NOTE:** For use with the Steam Flatpak (not recomended) contiune [here](https://github.com/DaniAsh551/wemod-launcher/wiki/Steam-Flatpak-Usage)
7. In the WeMod chosen game, open the steam game settings  
   and in the `Compatibility` tab change the proton version to the downloaded one.
8. Also add the command `/home/$USER/wemod-launcher/wemod %command%`,  
   in the steam game settings under `Launch Options`
9. Start the game
10. Select no to the copy prefix question if it says it `might work`  
   If it says it `likely works` go to 12.
11. Select download
12. Select Yes/Ok until no more windows appear  
    All rundll32.exe errors can safely be ignored (click on `no` here)
13. WeMod will start with the game
14. Login and click play in WeMod for chosen game   
15. Set Mods and Switch to game or close the WeMod window,  
    it will keep running in the background
</div>

The wemod-launcher will automatically update if you installed it using step 5.  
**But:** This will only work if you have [launcher version 1.092 or older](https://github.com/DaniAsh551/wemod-launcher/wiki/The-Self-Update).

**Optionally:** Check out tutorials on how to use specific [WeMod Laucher features](https://github.com/DaniAsh551/wemod-launcher/wiki/Launcher-Tutorials)  
**Like:** Check how to [Use External Launchers](https://github.com/DaniAsh551/wemod-launcher/wiki/Using-External-Launchers) (Use The WeMod Launcher outside of Steam)  
**OR:** Check out how to [Edit The Config](https://github.com/DaniAsh551/wemod-launcher/wiki/Config-Usage)  

****
<h3><img src="https://cdn.discordapp.com/emojis/1113579886439833690.gif?size=20&quality=lossless" alt="Heart"/>&nbsp;Additional</h3>

<div><img src="https://cdn.discordapp.com/emojis/761419274945953842.webp?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>Video Tutorial:</b> <a href="https://youtu.be/5UlVCZvIl1E"> WeMod-launcher Setup Tutorial by Marvin1099</a></div> 

<div><img src="https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>Guide was written by Trippin and updated by Marvin1099.</b></div>  

<div><img src="https://cdn.discordapp.com/emojis/1113579884749529198.gif?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>WeMod Linux is developed by DaniAsh551 in recent support by Marvin1099.</b></div>  

<div><img src="https://cdn.discordapp.com/emojis/999743709677633536.gif?size=20&quality=lossless" alt="WeModApp"/>&nbsp;<b>If you find this guide helpful, we encourage you to star the project.</b></div><br> 

<a href="https://star-history.com/#DaniAsh551/wemod-launcher&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=DaniAsh551/wemod-launcher&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=DaniAsh551/wemod-launcher&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=DaniAsh551/wemod-launcher&type=Date" />
 </picture>
</a>
