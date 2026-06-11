"""Vercel serverless entrypoint.

Mounts the FastAPI service under /api/py so the same app serves both:
  - locally:  `uvicorn src.service:app --port 8000` (unprefixed routes)
  - Vercel:   requests to /api/py/* are routed here via vercel.json
"""

from fastapi import FastAPI

from src.service import app as service_app

app = FastAPI()
app.mount("/api/py", service_app)
