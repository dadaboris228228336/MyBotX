#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCENARIO/scenario_01_runner.py
Выполняет шаги сценария последовательно.
"""

import time
from .scenario_02_steps import STEP_KEY_LABELS
from .scenario_04_adb_actions import (
    do_tap, do_swipe, do_key, do_text,
    do_launch, do_stop, do_pinch, do_pinch_swipe, do_find_and_tap
)


class ScenarioRunner:

    def __init__(self, steps: list[dict], device: str, log=None):
        self.steps  = steps
        self.device = device
        self.log    = log or (lambda msg, tag="info": print(msg))

    def run(self):
        total = len(self.steps)
        for i, step in enumerate(self.steps, 1):
            t = step.get("type", "")
            p = step.get("params", {})
            label = STEP_KEY_LABELS.get(t, t)
            self.log(f"▶ Шаг {i}/{total}: {label}", "info")
            try:
                self._execute(t, p)
            except Exception as e:
                self.log(f"❌ Ошибка на шаге {i}: {e}", "error")
                return
        self.log("✅ Сценарий завершён", "success")

    def _execute(self, t: str, p: dict):
        d = self.device
        if t == "find_and_tap":
            do_find_and_tap(
                d,
                pattern=p.get("pattern", ""),
                threshold=float(p.get("threshold", 0.8)),
                retries=int(p.get("retries", 3)),
                retry_delay=float(p.get("retry_delay", 2.0)),
                log=self.log
            )
        elif t == "tap_coords":
            do_tap(d, int(p.get("x", 0)), int(p.get("y", 0)))
            self.log(f"  👆 tap ({p.get('x')}, {p.get('y')})", "dim")
        elif t == "swipe":
            do_swipe(d, int(p.get("x1", 0)), int(p.get("y1", 0)),
                     int(p.get("x2", 0)), int(p.get("y2", 0)),
                     int(p.get("duration", 300)))
            self.log(f"  👆 swipe", "dim")
        elif t == "pinch_out":
            do_pinch_swipe(d, zoom_in=False, times=int(p.get("times", 1)), log=self.log)
        elif t == "pinch_in":
            do_pinch_swipe(d, zoom_in=True, times=int(p.get("times", 1)), log=self.log)
        elif t == "key_home":
            do_key(d, 3)
            self.log("  🏠 HOME", "dim")
        elif t == "key_back":
            do_key(d, 4)
            self.log("  ↩ BACK", "dim")
        elif t == "input_text":
            do_text(d, p.get("text", ""))
            self.log(f"  ⌨ text: {p.get('text', '')}", "dim")
        elif t == "launch_app":
            do_launch(d, p.get("package", ""))
            self.log(f"  🚀 launch: {p.get('package', '')}", "dim")
        elif t == "stop_app":
            do_stop(d, p.get("package", ""))
            self.log(f"  🛑 stop: {p.get('package', '')}", "dim")
        elif t == "wait":
            secs = float(p.get("seconds", 1))
            self.log(f"  ⏳ ждём {secs}с", "dim")
            time.sleep(secs)
