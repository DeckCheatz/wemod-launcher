# Architecture

> All paths use their default locations.
> If the corresponding XDG environment variable is set (`XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`), paths resolve accordingly.

## Overview

The launcher is a sequential pipeline: bootstrap core services, run action phases, show the troubleshooter if anything failed. Each phase is wrapped in a guard that catches exceptions, logs them, and notifies the user. Non-fatal errors in one phase don't prevent later phases from running.

The process monitor is a separate binary in its own repository. The launcher downloads it, sends a config via TCP/JSON, and reads the exit code. It does not manage process lifecycle directly.

## Bootstrap

The bootstrap creates objects in order, then wires them together. SettingsManager is a container and coordination point — it does not create other components itself.

1. **SettingsManager** — created bare. Holds shared state (`local` namespace for flow tracking, return code, etc.) and any flags/paths the launcher needs. Does not load config files or parse args at this stage — that happens later or is delegated.

2. **LogManager(settings)** — takes a reference to settings. Writes the log file header (launcher version, Python version, platform, timestamp). Emits structured events to subscribed handlers (file, console, UI). After creation, `settings.log_ready(log)` gives settings a reference back to the logger.

3. **InterfaceManager(settings, log)** — creates either a `CLIInterface` or `GUIInterface` (PyQt6) based on settings flags. The interface is the single point of user interaction, no scattered `input()` or `print()` calls elsewhere. After creation, both `settings.interface_ready(interface)` and `log.interface_ready(interface)` are called so the other components can reach the interface.

After bootstrap, the three objects (settings, log, interface) are passed to each phase. Phase functions access state through settings, emit events through log, and show messages or progress via the interface.

## Main Flow

After bootstrap, the launcher runs these phases in order. Each phase is independent — a failure in one doesn't skip the others.

### Update

Checks for launcher self-updates. In production (AppImage), compares the running version against GitHub Releases and swaps the binary atomically if newer. From source, runs `git pull`. Network failures are logged and silently skipped — a failed update is not fatal.

### Migrations

Compares the stored schema version in `metadata.json` against the version bundled with the launcher. If they differ, pending migrations run in order. Migrations can restructure files, update config formats, or transform the prefix database. After success, `metadata.json` is updated with the current schema version.

### App Install

Ensures the app exe exists at `~/.local/share/wand/bin/`. If missing, downloads the archive from the URL in `metadata.json`, verifies its checksum, extracts to `~/.cache/wand/`, and copies the exe to `bin/`. The app exe is shared across all prefixes.

### Prefix Setup

The most complex phase. Ensures the Wine prefix has the app installed and ready.

1. **Normalize** — move `pfx/` contents up one level, symlink `pfx` → `.`. Move `drive_c/users/steamuser/` to `drive_c/users/$USER/`, symlink `steamuser` → `USER`. Handles differences between Proton and standalone Wine prefixes.

2. **Check marker** — look for `.wand_installer` next to `drive_c`. If found, the prefix is ready.

3. **Scan siblings** — walk the parent directory for other prefixes with `.wand_installer`. Cache results in `~/.local/share/wand/prefixes.json`, remove stale entries.

4. **Present options** — user chooses based on how many valid prefixes exist:
   - **Closest match** — copy the best sibling prefix (1+ valid prefixes)
   - **Second closest** — auto-pick next best (exactly 2 valid prefixes)
   - **Download** — fetch a pre-built prefix from GitHub Releases
   - **List all** — pick from all valid prefixes (3+)
   - **Build** — download winetricks, run `winetricks -q sdl cjkfonts vkd3d dxvk2030 dotnet48`, write `.wand_installer`
   - **Exit** — cancel

5. **Post-setup** — write `.wand_installer` marker if not already present.

### Data Sync

Links app data to shared storage so all games share the same login/settings.

1. Create `~/.local/share/wand/login/` if it doesn't exist.
2. Copy the app data folder from inside the prefix to `login/`.
3. Replace the prefix data folder with a symlink to `login/`.
4. If both sides already have data, prompt the user to pick which copy wins.

### Monitor Launch

Downloads `monitor.exe` from the monitor's GitHub releases (separate repo). Sends a `LaunchConfig` via TCP/JSON (game exe, wand exe, lifecycle instructions). Waits for `session_complete` with the game's exit code. Returns that exit code as the launcher's own.

If the monitor can't start (missing binary, port in use), the phase reports failure.

## Troubleshooter

Runs by default after the main flow, regardless of whether phases succeeded or failed. Can be disabled via game config, settings, or environment variables.

**GUI (default):** PyQt6 window with status overview, log viewer, and recovery actions (retry prefix setup, redownload app, delete prefix and start fresh).

**CLI:** Text-based prompts with the same options, line-overwrite progress. Skipped entirely with `--no-prompt` — in that mode it only logs and exits.

The troubleshooter subscribes to error-level log events during the flow, so it already knows what went wrong when it opens.

## Paths

| Path | Purpose |
|---|---|
| `~/.config/wand/config.json` | User-editable global config |
| `~/.config/wand/games.json` | Per-game overrides |
| `~/.local/share/wand/metadata.json` | Auto-generated manifest (version, URLs, checksums) |
| `~/.local/share/wand/bin/` | Installed app exe (shared across prefixes) |
| `~/.local/share/wand/login/` | Shared app data (symlinked into each prefix) |
| `~/.local/share/wand/prefixes.json` | Cached sibling prefix scan results |
| `~/.cache/wand/` | Downloads, temp extraction, log file |
