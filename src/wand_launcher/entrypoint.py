#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.runner import StepRunner
    from .core.settings import SettingsManager  # ty: ignore[unresolved-import]


def main() -> int:
    # ── Bootstrap ──────────────────────────────────────────────────────────
    # 1. SettingsManager: parse argv, compute XDG paths. No config files yet.
    from .core.settings import SettingsManager  # ty: ignore[unresolved-import]

    settings = SettingsManager()

    # 2. LogManager: open log file at settings.log_path
    from .logging.event_bus import LogManager  # ty: ignore[unresolved-import]

    log = LogManager(settings)
    log.info("launcher.start", "Launcher started")

    # 3. Interface detection: PyQt6 GUI or CLI based on --cli / --no-prompt
    from .ui.detect import detect_interface  # ty: ignore[unresolved-import]

    interface = detect_interface(settings, log)

    # ── Main execution ────────────────────────────────────────────────────
    # Wrap the three core objects in a StepRunner so every action phase gets
    # consistent exception handling and user-facing error reporting.
    #   runner.try_step(ErrorLogTopic, ErrorMSG, fn)        -> bool  (True = failed)
    #   runner.try_step_code(ErrorLogTopic, ErrorMSG, fn)   -> (bool, int)
    from .core.runner import StepRunner

    runner = StepRunner(settings, log, interface)

    # Run action phases through _run_flow. Each phase only runs when its
    # declared prerequisites have succeeded — the runner handles gating.
    return _run_flow(runner, settings)


def _run_flow(runner: "StepRunner", settings: "SettingsManager") -> int:
    from types import SimpleNamespace

    result: dict[str, str] = {}
    if not hasattr(settings, "internal"):
        settings.internal = SimpleNamespace()
    settings.internal.main_flow_results = result

    # 1. Self-update — check GitHub Releases for a newer launcher version
    from .updater import update_if_needed  # ty: ignore[unresolved-import]

    runner.try_phase(
        "updater", "Could not check for updates.", update_if_needed, result
    )

    # 2. Data migrations — apply pending schema changes
    from .migrations import apply_migrations  # ty: ignore[unresolved-import]

    runner.try_phase(
        "apply_migrations", "Failed to apply data migrations.", apply_migrations, result
    )

    # 3. App install — download and verify the app exe if missing
    from .app_installer import ensure_app  # ty: ignore[unresolved-import]

    runner.try_phase(
        "download_app",
        "Could not download the app.",
        ensure_app,
        result,
        requires="apply_migrations",
    )

    # 4. Prefix setup — normalise, scan siblings, copy/download/build prefix
    from .prefix_manager import setup_prefix  # ty: ignore[unresolved-import]

    runner.try_phase(
        "prefix_setup", "Could not set up the Wine prefix.", setup_prefix, result
    )

    # 5. Data sync — link prefix app data to the shared login directory
    from .data_sync import sync_app_data  # ty: ignore[unresolved-import]

    runner.try_phase(
        "data_sync",
        "Could not sync app data.",
        sync_app_data,
        result,
        requires="prefix_setup",
    )

    # 6. Monitor launch — start the game via the monitor binary (TCP/JSON IPC)
    from .monitor import launch_monitor  # ty: ignore[unresolved-import]

    code = runner.try_phase_code(
        "monitor_launch",
        "Cannot launch the monitor.",
        launch_monitor,
        result,
        requires=("data_sync", "download_app"),
    )

    # 7. Troubleshooter — show recovery options (always runs)
    from .troubleshooter import run_troubleshooter  # ty: ignore[unresolved-import]

    runner.try_phase(
        "troubleshooter",
        "Could not run the troubleshooter.",
        run_troubleshooter,
        result,
    )

    return code


if __name__ == "__main__":
    sys.exit(main())
