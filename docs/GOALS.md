# Project Goals

## What This Is

Wand Launcher is a Linux tool that sets up and runs wand (a third-party application) inside a Wine/Proton prefix. It handles prefix management, app installation, data syncing, and process supervision, all from a single entry point.

## Priorities

### Must Have (MVP)

- **Working launcher.** Bootstrap, install app, set up prefix, launch monitor, exit. The happy path must work end-to-end before anything else.
- **SettingsManager as coordination point.** A shared container that other components wire into via `*_ready()` methods. Holds shared state (flow tracking, return code) and provides a single place for components to find each other. No scattered `os.environ` reads or ad-hoc state management.
- **CLI mode.** Full non-interactive operation via `--cli` / `--no-prompt`. The launcher must be scriptable.
- **Structured logging.** Standard log levels, file output, contextual messages. Debuggability from day one.
- **XDG-compliant paths.** `~/.config/wand/`, `~/.local/share/wand/`, `~/.cache/wand/` — no dotfiles in `$HOME`.

### Should Have (Post-MVP)

- **GUI mode.** PyQt6 interface as the default when no CLI flags are set. Same functionality, different presentation.
- **Tiered config.** CLI args > env vars > config file > hardcoded defaults. Game-specific overrides via `games.json`.
- **Binary updater.** Self-update via GitHub Releases (AppImage swap for production, git pull for source installs).
- **Structured migrations.** Schema versioning in `metadata.json` with ordered migration scripts for breaking changes.
- **Prefix management.** Scan sibling prefixes, match by version/arch, copy or download pre-built prefixes, winetricks-based build as fallback.

### Nice to Have

- **Troubleshooter GUI.** PyQt6 window with log viewer, status overview, and recovery actions. Always runs unless disabled.
- **User-Agent rotation** for GitHub API calls.
- **Resume support** for large downloads.

## Architecture Principles

- **Code grouped by responsibility.** Settings, logging, UI, steps — each in its own module with clean internal APIs.
- **Platform-correct.** Consistent Wine/Proton prefix handling. `pfx/` normalization, `steamuser` → `$USER` symlinks.
- **Predictable and debuggable.** Structured logging, guard-wrapped phases, clear error paths.
- **Quality over speed.** Reviewed, maintainable code beats quick-and-dirty fixes.

## Platform

- Distributed as an AppImage (bundled Python + all dependencies, no sandbox issues).
- The process monitor is a separate binary in its own repository, the launcher builds a config and readsthe result, the monitor handles process lifecycle inside Wine/Proton.
- Container-compatible via AppImage bundling.
