#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any


class StepRunner:
    """Wraps the three core objects and provides guarded step execution.

    Every action phase runs through try_step() / try_step_code() —
    exceptions are caught, logged with the given topic, and shown to the
    user via the interface. The higher-level try_phase() / try_phase_code()
    add dependency gating and automatic result tracking on top.
    """

    def __init__(self, settings: Any, log: Any, interface: Any) -> None:
        self._settings = settings
        self._log = log
        self._interface = interface

    def try_step(self, topic: str, msg: str, fn) -> bool:
        """Execute *fn(settings, log, interface)*, return True if it failed.

        Exceptions are caught and reported — the phase is considered failed.
        """
        try:
            fn(self._settings, self._log, self._interface)
            return False
        except Exception as exc:
            self._log.error(topic, f"{msg}: {exc}")
            self._interface.error_msg_and_log(topic, msg)
            return True

    def try_step_code(self, topic: str, msg: str, fn) -> tuple[bool, int]:
        """Same as try_step but the phase returns an exit code.

        Returns (failed_flag, code). On exception: (True, 1).
        """
        try:
            code = fn(self._settings, self._log, self._interface)
            return (code != 0, code)
        except Exception as exc:
            self._log.error(topic, f"{msg}: {exc}")
            self._interface.error_msg_and_log(topic, msg)
            return (True, 1)

    def try_phase(
        self,
        topic: str,
        msg: str,
        fn,
        result: dict[str, str],
        *,
        requires: str | tuple[str, ...] | None = None,
    ) -> None:
        """try_step with optional dependency gating and result tracking.

        If *requires* is given, the phase is skipped unless every required
        phase has result["phase"] == "succeeded". The outcome is recorded
        in *result[topic]* as ``"succeeded"``, ``"failed"``, or ``"skipped"``.
        """
        if requires is not None:
            reqs = (requires,) if isinstance(requires, str) else requires
            if any(result.get(r) != "succeeded" for r in reqs):
                result[topic] = "skipped"
                return
        if self.try_step(topic, msg, fn):
            result[topic] = "failed"
        else:
            result[topic] = "succeeded"

    def try_phase_code(
        self,
        topic: str,
        msg: str,
        fn,
        result: dict[str, str],
        *,
        requires: str | tuple[str, ...] | None = None,
    ) -> int:
        """try_step_code with dependency gating and result tracking.

        Returns the exit code (1 if skipped, the phase's own code otherwise).
        """
        if requires is not None:
            reqs = (requires,) if isinstance(requires, str) else requires
            if any(result.get(r) != "succeeded" for r in reqs):
                result[topic] = "skipped"
                return 1
        failed, code = self.try_step_code(topic, msg, fn)
        result[topic] = "failed" if failed else "succeeded"
        return code
