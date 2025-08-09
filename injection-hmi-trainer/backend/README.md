# Backend (FastAPI)

## Quick start

```bash
cd /workspace/injection-hmi-trainer/backend
python3 -m pip install --break-system-packages -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If `pip` refuses due to externally-managed environment and you prefer isolation, install `python3-venv` and use a virtualenv.

## Endpoints
- GET /api/v1/recipe
- POST /api/v1/recipe
- WS  /ws/telemetry  (streams telemetry ~20 Hz for one cycle)

CORS is open during development.