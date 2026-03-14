# Setup wemod-launcher

1. Open your Terminal.
2. **Optionnal:** go into the directory you want to install wemod-launcher to (using `cd`).
3. Download the script: `curl -o "wemod-setup" https://raw.githubusercontent.com/DeckCheatz/wemod-launcher/refs/heads/main/setup`.
4. **Info:** Please review the script before running, you can use: `less wemod-setup` to see the content of the file.
5. Run the script: `bash wemod-setup`.

## Next:

1. Install 'ProtonPlus' (or 'ProtonUp-QT') and open the app
2. From the app, install 'Proton-GE' (or 'GE-Proton')
3. Restart Steam
4. Set this profile to all your games (using a Proton GUI or Steam directly (right-click on a game > Manage > Compatibility > Force Proton version))
5. If you did step 4 with a Proton GUI, restart Steam again
6. Here there are two ways, for a single game (a), or multiple at once (b). Both on Steam's Library:
  6.a. Right click at any game you want > Manage > General > Launch Options
  6.b. In the list of games (at the left, not the one with posters), select your with left click your first game then with CTRL+left click others (CTRL+A for all). Once all you want are selected, right click > Manage > General > Launch Options
7. Insert this command: `<REPO_PATH>/wemod %command%`
(launch command saved in `<REPO_PATH>/launch-command.txt`)

