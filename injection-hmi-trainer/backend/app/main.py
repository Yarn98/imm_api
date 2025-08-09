from __future__ import annotations
import asyncio
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import InjectionRecipe
from .sim.engine import SimulationEngine

app = FastAPI(title="Injection HMI Trainer Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory current recipe
_current_recipe: InjectionRecipe = InjectionRecipe()


@app.get("/api/v1/recipe", response_model=InjectionRecipe)
async def get_recipe():
    return _current_recipe


@app.post("/api/v1/recipe", response_model=InjectionRecipe)
async def set_recipe(recipe: InjectionRecipe):
    global _current_recipe
    _current_recipe = recipe
    return _current_recipe


@app.post("/api/v1/sim/start")
async def sim_start():
    return JSONResponse({"status": "ok"})


@app.websocket("/ws/telemetry")
async def ws_telemetry(ws: WebSocket):
    await ws.accept()
    engine = SimulationEngine(_current_recipe)
    try:
        async for tel in engine.run_cycle():
            await ws.send_json(tel.model_dump())
    except WebSocketDisconnect:
        return
    finally:
        if not engine.is_running():
            await ws.close()