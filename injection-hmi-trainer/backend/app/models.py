from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Literal


class SpeedSegment(BaseModel):
    position_from_mm: float = Field(ge=0)
    position_to_mm: float = Field(gt=0)
    velocity_mm_s: float = Field(ge=0)


class PackStep(BaseModel):
    pressure_bar: float = Field(ge=0)
    duration_s: float = Field(ge=0)


class InjectionRecipe(BaseModel):
    name: str = "default"
    screw_profile: List[SpeedSegment] = Field(default_factory=list)
    v2p_transfer_by: Literal["position", "pressure", "time"] = "position"
    v2p_transfer_threshold: float = 12.0
    pack_hold: List[PackStep] = Field(default_factory=list)
    cooling_s: float = 14.0
    back_pressure_bar: float = 80.0
    barrel_zones_c: List[float] = Field(default_factory=lambda: [160, 170, 178, 180])
    mold_temp_c: float = 35.0
    screw_rpm: float = 100.0
    screw_diameter_mm: float = 35.0
    shot_volume_cc: float = 18.0
    pressure_limit_bar: float = 1100.0


class Telemetry(BaseModel):
    t_ms: int
    phase: Literal["Clamp", "Injection", "PackHold", "Cooling", "Eject", "Idle"]
    screw_pos_mm: float
    screw_vel_mm_s: float
    cavity_pressure_bar: float
    motor_current_a: float
    mold_temp_c: float
    events: List[str] = Field(default_factory=list)