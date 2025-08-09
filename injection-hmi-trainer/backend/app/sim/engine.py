from __future__ import annotations
import asyncio
import math
from typing import AsyncGenerator, Optional
from ..models import InjectionRecipe, Telemetry


class SimulationEngine:
    def __init__(self, recipe: InjectionRecipe):
        self.recipe = recipe
        self._running = False
        self._t_ms = 0

    async def run_cycle(self) -> AsyncGenerator[Telemetry, None]:
        self._running = True
        self._t_ms = 0

        # Phases durations (ms) — coarse placeholders
        t_inj = 1200
        t_pack = 2500
        t_cool = int(self.recipe.cooling_s * 1000)
        t_eject = 600
        phases = [
            ("Injection", t_inj),
            ("PackHold", t_pack),
            ("Cooling", t_cool),
            ("Eject", t_eject),
        ]

        screw_stroke_mm = max(10.0, min(30.0, self.recipe.shot_volume_cc / (math.pi * (self.recipe.screw_diameter_mm/2/10)**2) * 10))
        pos_mm = screw_stroke_mm

        for phase, dur in phases:
            elapsed = 0
            while elapsed < dur:
                dt = 50  # 50 ms
                self._t_ms += dt
                elapsed += dt

                # very rough signals
                if phase == "Injection":
                    screw_vel = max(5.0, min(220.0, 80.0))
                    pos_mm = max(0.0, pos_mm - screw_vel * (dt/1000))
                    cav_p = min(self.recipe.pressure_limit_bar, 300 + 600 * (1 - pos_mm / max(1.0, screw_stroke_mm)))
                elif phase == "PackHold":
                    screw_vel = 5.0
                    cav_p = max(150.0, 500.0 * (1 - (elapsed / dur)))
                elif phase == "Cooling":
                    screw_vel = 0.0
                    cav_p = 80.0
                else:  # Eject
                    screw_vel = 0.0
                    cav_p = 50.0

                motor_a = 10.0 + cav_p / 80.0

                yield Telemetry(
                    t_ms=self._t_ms,
                    phase=phase,  # type: ignore[arg-type]
                    screw_pos_mm=round(pos_mm, 2),
                    screw_vel_mm_s=round(screw_vel, 2),
                    cavity_pressure_bar=round(cav_p, 1),
                    motor_current_a=round(motor_a, 2),
                    mold_temp_c=self.recipe.mold_temp_c,
                    events=[],
                )
                await asyncio.sleep(dt / 1000)

        self._running = False

    def is_running(self) -> bool:
        return self._running