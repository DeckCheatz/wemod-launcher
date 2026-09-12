# AGENTS.md — LLM context for Wand Launcher

## What This Is

Wand Launcher is a Linux tool that sets up and runs wand (a third-party application) inside a Wine/Proton prefix. It handles prefix management, app installation, data syncing, and process supervision from a single entry point. Distributed as an AppImage.

## Architecture

Sequential pipeline: bootstrap core services, run action phases, show troubleshooter if anything failed.

### Bootstrap Order

1. **SettingsManager** — bare container. Holds shared state and coordination. Created first, no dependencies.
2. **LogManager(settings)** — structured event-based logging. Takes settings reference. `settings.log_ready(log)` after creation so settings can log.
3. **InterfaceManager(settings, log)** — CLI or GUI (PyQt6). Takes settings and log. `settings.interface_ready(interface)` and `log.interface_ready(interface)` after creation so both can show messages.

After bootstrap, (settings, log, interface) are passed to each phase. The interface holds references to settings and log, so phases can access all three from the interface alone.

### How The Three Objects Wire Together

```python
settings = SettingsManager()
log = LogManager(settings)
settings.log_ready(log)            # settings can now log
interface = InterfaceManager(settings, log)
settings.interface_ready(interface) # settings can now show messages
log.interface_ready(interface)      # log can now show messages
```

Settings can report errors to log or show critical errors on interface and exit. Log can show errors on interface. Interface has log and settings on it, so phases only need to receive the interface.

### Main Flow Phases

Update → Migrations → App Install → Prefix Setup → Data Sync → Monitor Launch

Each phase is independent. A failure in one doesn't skip others. Monitor only launches if all prior phases succeeded (`flow` dict tracks `0` = success per phase).

```python
settings.local.main_flow = {}
flow = settings.local.main_flow

try:
    from .updater import update_if_needed
    update_if_needed(interface)
except Exception as e:
    interface.log_show.error(f"Update failed: {e}")
else:
    flow["update"] = 0
# ... same pattern for each phase
```

### Settings Namespaces

| Namespace | Purpose | Source | Mutable? |
|---|---|---|---|
| `settings.chain` | Derived/resolved paths (e.g. `wand_bin_path`, `log_path`) | Computed at startup | No (computed) |
| `settings.global` | User-editable global config | `~/.config/wand/config.json` (see [Paths](#paths)) | Yes (user) |
| `settings.game` | Per-game overrides | `~/.config/wand/games.json` (see [Paths](#paths)) | Yes (user) |
| `settings.local` | This-run-only state (flow tracking, return code) | In-memory only | Yes (launcher) |
| `settings.private` | Internal launcher state (version tracking), not user-editable | `~/.local/share/wand/metadata.json` (see [Paths](#paths)) | Yes (launcher) |
| `settings.bundled` | Read-only bundled metadata (bundled version, URLs, checksums) | Compiled/source tree | No |
| `settings.source_order` | Config resolution order | Hardcoded or user-configurable | Configurable |

Tiered config: CLI args → env vars → config file → defaults. Game-specific overrides via `games.json`.

### Logger API

```python
log.info(msg)              # standard log levels
log.debug(msg)
log.warning(msg)
log.error(msg)
log.critical(msg)
log.command_cli(msg)       # Wine/Proton command output (noisy, separate category)
log.command_cli_on = True  # toggle command_cli verbosity (can be exposed as setting)
```

### Interface API

```python
interface.log_show.info(msg)      # info box
interface.log_show.warn(msg)      # warning box
interface.log_show.error(msg)     # error box
interface.log_show.critical(msg)  # critical error box (may exit)
interface.log.info(msg)           # show info box AND log
interface.log.error(msg)          # show error box AND log as error
interface.progress.start(total)   # start progress bar with total steps
interface.progress.update(n)      # advance by n steps
interface.progress.finish()       # close progress bar
```

### Troubleshooter

Runs by default after the main flow. Can be disabled via game config, settings, or env vars.

- **GUI (default):** PyQt6 window with status overview, log viewer, and recovery actions.
- **CLI:** Text-based prompts with same options. Skipped entirely with `--no-prompt` (logs and exits).

The troubleshooter is not just for launcher failures, wand is proprietary, we don't know what it does. It's always available for wand issues too.

### Process Monitor

Separate binary in its own repo. Launcher downloads it, sends config via TCP/JSON, reads exit code. Does not manage process lifecycle directly.

IPC protocol: gRPC contract between launcher and monitor. Queue-then-execute model. See full spec at `docs/gRPC-spec.md` (branch `marvin1099/rewrite-v2/project-docs-grpc-spec`, or on `rewrite/v2` if merged).

Key rules: `done` only in response to `exit`/`shutdown`. `idle` = "processes done, still listening." Fatal errors = monitor exits on its own. Error file fallback for dropped connections.

## Code Conventions

- **Formatter/Linter:** `ruff` format + check (line length 88 from `pyproject.toml`)
- **Import style:** `from __future__ import annotations`, relative imports for intra-package
- **Lazy imports:** Inside functions for startup modules (avoid circular imports, keep startup fast)
- **Naming:** PascalCase for classes (`SettingsManager`), snake_case for everything else. Use `*Manager` suffix for bootstrap objects.
- **License header:** `#!/usr/bin/env python3` + `# SPDX-License-Identifier: AGPL-3.0-only`
- **File header:** `"""Module docstring."""`
- **Commits:** Conventional commits (`fix:`, `feat:`, `docs:`, `chore:`, ...)
- **Type checking:** Astral `ty` (not mypy). Use `# ty: ignore[unresolved-import]` for stubs not yet implemented.
- **No bare `except Exception`** without `# noqa: BLE001` and a good reason.
- **No comments unless asked.** Code should be self-documenting.
- **Entry point:** `main()` function in `src/wand_launcher/entrypoint.py`, returns `int`. Always ends with `if __name__ == "__main__": sys.exit(main())`.

## Paths

| Path | Namespace | Purpose |
|---|---|---|
| `~/.config/wand/config.json` | `settings.global` | User-editable global config |
| `~/.config/wand/games.json` | `settings.game` | Per-game overrides |
| `~/.local/share/wand/metadata.json` | `settings.private` | Auto-generated manifest (version, URLs, checksums) |
| `~/.local/share/wand/bin/` | `settings.chain` | Installed app exe (shared across prefixes) |
| `~/.local/share/wand/login/` | `settings.chain` | Shared app data (symlinked into each prefix) |
| `~/.local/share/wand/prefixes.json` | `settings.chain` | Cached sibling prefix scan results |
| `~/.cache/wand/` | `settings.chain` | Downloads, logs, temp files |
| `~/.cache/wand/launcher.log` | `settings.chain` | Log file location |

## Project Priorities

### Must Have (MVP)
- Working launcher (bootstrap → install → prefix → monitor → exit)
- SettingsManager as coordination point
- CLI mode (`--cli` / `--no-prompt`)
- Structured logging
- XDG-compliant paths

### Should Have (Post-MVP)
- GUI mode (PyQt6)
- Tiered config (CLI > env > config > defaults)
- Binary updater
- Structured migrations
- Prefix management (scan, copy, download, build)

### Nice to Have
- Troubleshooter GUI
- User-Agent rotation for GitHub API
- Resume support for large downloads

## Current State

- **Exists:** `entrypoint.py` (on `marvin1099/rewrite-v2/entrypoint`), `CONTRIBUTING.md`, `pyproject.toml`, pre-commit hooks.
- **Docs (on feature branches, may be on `rewrite/v2` if merged):**
  - `docs/GOALS.md` — `marvin1099/rewrite-v2/project-docs-goals`
  - `docs/ARCHITECTURE.md` — `marvin1099/rewrite-v2/project-docs-architecture`
  - `docs/gRPC-spec.md` — `marvin1099/rewrite-v2/project-docs-grpc-spec`
- **Planned but not coded:** Everything in ARCHITECTURE.md (SettingsManager, LogManager, InterfaceManager, all phases, troubleshooter, monitor integration).
- **IPC protocol:** Designed and documented, monitor binary not yet implemented.

## Tooling

- **Python:** >=3.12, dev on 3.13
- **Build:** setuptools + setuptools-scm
- **Entry point:** `wand-launcher = "wand_launcher.entrypoint:main"`
- **Pre-commit:** ruff-check (--fix), ruff-format, ty, conventional-pre-commit, trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files

## PR Requirements

- Small and focused. One logical change per PR.
- Follow the architecture — don't bolt on parallel mechanisms.
- Meets tooling bar: `ruff` check + format, conventional commits, ty passes.
- Update docs if behavior changes.
- Explain why, not just what. Reference issues where possible.
- No merge conflicts, no unrelated whitespace churn.
