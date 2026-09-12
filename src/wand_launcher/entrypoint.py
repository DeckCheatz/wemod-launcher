#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

"""Main entry point for the Wand Launcher."""

from __future__ import annotations

import sys


def main() -> int:
    """Run the Wand Launcher startup sequence."""
    from .core.settings import SettingsManager  # ty: ignore[unresolved-import]

    settings = SettingsManager()

    from .logging.logger import LogManager  # ty: ignore[unresolved-import]

    log = LogManager(settings)
    log.info("Launcher started")
    settings.log_ready(log)

    from .ui.detect import InterfaceManager  # ty: ignore[unresolved-import]

    interface = InterfaceManager(settings, log)
    settings.interface_ready(interface)
    log.interface_ready(interface)

    flow = getattr(settings.local, "main_flow", None)
    if flow is None:
        flow = {}
        settings.local.main_flow = flow

    return_code = getattr(settings.local, "return_code", None)
    if return_code is None:
        return_code = 0
        settings.local.return_code = return_code

    try:
        from .updater import update_if_needed  # ty: ignore[unresolved-import]

        update_if_needed(interface)
    except Exception as e:  # noqa: BLE001
        interface.show.error(f"Update failed: {e}")
    else:
        flow["update"] = 0

    try:
        if settings.private.version < settings.bundled.version:
            from .migrations import apply_migrations  # ty: ignore[unresolved-import]

            apply_migrations(interface)
    except Exception as e:  # noqa: BLE001
        interface.show.error(f"Migration failed: {e}")
    else:
        flow["migrations"] = 0

    try:
        from .app_installer import ensure_app  # ty: ignore[unresolved-import]

        ensure_app(interface)
    except Exception as e:  # noqa: BLE001
        interface.show.error(f"App installation failed: {e}")
    else:
        flow["installed"] = 0

    try:
        from .prefix_manager import setup_prefix  # ty: ignore[unresolved-import]

        setup_prefix(interface)
    except Exception as e:  # noqa: BLE001
        interface.show.error(f"Prefix setup failed: {e}")
    else:
        flow["prefix"] = 0

    try:
        from .data_sync import sync_app_data  # ty: ignore[unresolved-import]

        sync_app_data(interface)
    except Exception as e:  # noqa: BLE001
        interface.show.error(f"Data sync failed: {e}")
    else:
        flow["sync"] = 0

    try:
        required = ["update", "migrations", "installed", "prefix", "sync"]
        if all(flow.get(k, 1) <= 0 for k in required):
            from .monitor import launch_monitor  # ty: ignore[unresolved-import]

            launch_monitor(interface)
        else:
            msg = "Not all required startup steps completed"
            raise RuntimeError(msg)
    except Exception as e:  # noqa: BLE001
        interface.show.error(f"Monitor launch failed: {e}")
    else:
        flow["monitor"] = 0

    try:
        from .troubleshooter import run_troubleshooter  # ty: ignore[unresolved-import]

        run_troubleshooter(interface)
    except Exception as e:  # noqa: BLE001
        interface.show.error(f"Troubleshooter failed: {e}")

    return return_code


if __name__ == "__main__":
    sys.exit(main())
