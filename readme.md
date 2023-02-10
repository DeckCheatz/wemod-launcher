# WeMod Launcher (For Linux)

## This is a small tool made to launch the popular Game Trainer / Cheat tool WeMod along with your game (made for steam-runtime version in Linux). I have tested this only on a handful of games and you are welcome to report your findings / suggestions.

## If this Helps you, please star the project.
<p align="center">
  <img src="https://www.wemod.com/static/images/wemod-logo-40777eae11.webp" alt="WeMod logo"/>
</p>


## Requirements
- Need a version of Wine/Proton which has the dotnet48 bug fixed (GE-Proton-3x should work) - set in the compatibility menu in gameoptions.
- Need the WINE_PREFIX to have dotnet48,allfonts,sdl installed (You need to install these using a version of Wine/Proton as stated in the point above).
  eg: `PATH="$HOME/.local/share/Steam/compatibilitytools.d/GE-Proton7-39/files/bin:$PATH" WINEPREFIX=$HOME/.local/share/Steam/steamapps/compatdata/409720/pfx winetricks allfonts dotnet48 sdl` should get you started.
- A clean WINE_PREFIX is *recommended* as a wrong version (such as GE-Proton-4x) may introduce some bugs which would cause WeMod to fail. If you have ever used a Wine/Proton version that is not compatible, your game's WINE_PREFIX may be dirty and thus make WeMod not run properly.

## Installation
- Download and unpack/install WeMod - In my testing, WeMod's installer has some issues running under wine (I believe it relates to UAC) and so may fail to run. A workaround would be to either copy the files from a Windows PC or with the steps in the next section.
- Clone or download this repository
- Copy "wemod.bat" and "wemod" files from this repo to WeMod's location
- Open Steam, select your desired game, go to Mnage->Properties->GENERAL->LAUNCH OPTIONS and add the full path to the "wemod" file (from this repo) just before " %command%".
    For example, if your LAUNCH OPTIONS looks like this `ENABLE_VKBASALT=1 WINE_FULLSCREEN_FSR=1 DXVK_ASYNC=1 PROTON_NO_ESYNC=1 DXVK_HUD=fps gamemoderun %command% +com_showLoadingScreen 0 +r_skipDOF 1`, once you apply the change(s) mentioned, your LAUNCH OPTIONS may look like this: `ENABLE_VKBASALT=1 WINE_FULLSCREEN_FSR=1 DXVK_ASYNC=1 PROTON_NO_ESYNC=1 DXVK_HUD=fps gamemoderun /home/user/WeMod/WeMod.sh %command% +com_showLoadingScreen 0 +r_skipDOF 1`
- You are all set, please verify that you have done all the steps correctly


## WeMod download / install / unpack
As stated earlier, installing WeMod has some challenges under linux (Due to *squirrel* and UAC presumably), so here I detail a way to obtain WeMod and unpack it all in linux.

- If "7zip FM" is available in your distro, install that, or go to [https://www.7-zip.org/download.html](https://www.7-zip.org/download.html), and download the 7zip installer for your platform. If unsure, select the very first one.
- Once downloaded, open the setup file in your regular system wine (or any other if you prefer), and complete the setup.
- Go to [https://api.wemod.com/client/download](https://api.wemod.com/client/download), which would trigger the download of the latest version of WeMod offline / full installer.
- Once downloaded, open "7-Zip File Manager" (for those whose distro does not ship "7zip FM" and installed this in wine, the installation is located in the "C:\Program Files\7-Zip" directory inside your WINE_PREFIX)
- In 7Zip FM, navigate your way to the path where you downloaded the WeMod installer and right click on it and select "Open Inside"
- Here you shall see a directory named "lib", go inside it and then there would be another directory named "net45", this folder contains the WeMod installation.
- Rightclick on "net45" and select "Copy To", then select where you want to extract / install WeMod to and click "OK"
- Once the copy / extraction / installation completes, you are done and you could start the actual installation of this utility as detailed in the **Installation** section above.


## Important Notes
- The `sdl` requirement is not confirmed
- The `allfonts` is not strictly required, you could get away with just the *needed* fonts, but I did not take my time to figure this out
- I did not test many versions of Wine / Proton, and so cannot guarantee that this would work for *any* other versions, but I ***highly recommend*** that you try other versions and share your experience
- I tested this on "steam-runtime" with a handful of games, so I cannot say how this would fare with the native and flatpak versions of steam or without steam at all. If you would like to support these, you are more than welcome to open a PR and contribute your efforts.
- ***If you have any suggestions / improvements / issues, please feel free to submit a pull request or create an issue***
