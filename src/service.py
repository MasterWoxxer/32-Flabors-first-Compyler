"""FastAPI service for the 32 Flavors pipeline.

Run with:
    uvicorn src.service:app --reload --port 8000

The Next.js webapp's /api/pipeline route proxies POST /run to this service.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

# Import after dotenv so env vars are available
from src.flavors.config import PipelineConfig, config_from_settings  # noqa: E402
from src.flavors.pipeline import (  # noqa: E402
    compyle,
    execute,
    orchestrate,
    run_pipeline,
    split_labor_output,
)

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

# On Vercel the Python function is publicly reachable at /api/py/*, bypassing
# the Next.js routes' access-code check. When PIPELINE_INTERNAL_SECRET is set
# (production), only requests carrying it — i.e. the Next.js proxies — pass.
# Unset locally, so direct uvicorn use keeps working.
_INTERNAL_SECRET = os.getenv("PIPELINE_INTERNAL_SECRET", "")


@app.middleware("http")
async def _require_internal_secret(request: Request, call_next):
    if (
        _INTERNAL_SECRET
        and not request.url.path.endswith("/health")
        and request.headers.get("x-internal-secret") != _INTERNAL_SECRET
    ):
        return JSONResponse({"detail": "forbidden"}, status_code=403)
    return await call_next(request)


class RunRequest(BaseModel):
    message: str
    settings: dict = {}
    history: list[dict] = []


class ExecuteRequest(BaseModel):
    message: str
    instruction: str
    settings: dict = {}


class CompyleRequest(BaseModel):
    message: str
    instruction: str
    output: str
    check_voice: bool = False
    settings: dict = {}


def _require_message(message: str) -> None:
    if not message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run")
def run(req: RunRequest):
    _require_message(req.message)
    config: PipelineConfig = config_from_settings(req.settings)
    try:
        result = run_pipeline(req.message, config, history=req.history or None)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return result


# ── Staged endpoints — one LLM call each, driven sequentially by the UI ──────


@app.post("/orchestrate")
def orchestrate_stage(req: RunRequest):
    _require_message(req.message)
    config = config_from_settings(req.settings)
    try:
        instruction, orchestrator_thinking = orchestrate(
            req.message, config, history=req.history or None
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"instruction": instruction, "orchestrator_thinking": orchestrator_thinking}


@app.post("/execute")
def execute_stage(req: ExecuteRequest):
    _require_message(req.message)
    config = config_from_settings(req.settings)
    try:
        raw_output, labor_thinking = execute(req.instruction, req.message, config)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    labor_output, direct_response = split_labor_output(raw_output)
    return {
        "labor_output": labor_output,
        "labor_thinking": labor_thinking,
        "direct_response": direct_response,
    }


@app.post("/compyle")
def compyle_stage(req: CompyleRequest):
    _require_message(req.message)
    config = config_from_settings(req.settings)
    try:
        verdict = compyle(
            req.message,
            req.instruction,
            req.output,
            config,
            check_voice=req.check_voice,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return verdict
