# Root-level entrypoint for Render deployment.
# Render runs: uvicorn main:app --host 0.0.0.0 --port $PORT
# The actual app lives in app/main.py, so we re-export it here.
from app.main import app  # noqa: F401
