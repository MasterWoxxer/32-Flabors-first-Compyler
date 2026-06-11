"""FastAPI service for the 32 Flavors pipeline.

Run with:
    uvicorn src.service:app --reload --port 8000

The Next.js webapp's /api/pipeline route proxies POST /run to this service.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

# Import after dotenv so env vars are available
from src.flavors.config import PipelineConfig, config_from_settings  # noqa: E402
from src.flavors.pipeline import run_pipeline  # noqa: E402

app = FastAPI(title="32 Flavors Pipeline Service", version="0.1.0")

_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class RunRequest(BaseModel):
    message: str
    settings: dict = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run")
def run(req: RunRequest):
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")
    config: PipelineConfig = config_from_settings(req.settings)
    try:
        result = run_pipeline(req.message, config)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return result
