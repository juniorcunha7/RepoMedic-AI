"""Optional FastAPI façade. Local use only; no auth or production hardening."""
import os
from pathlib import Path
from .service import ReviewService

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:
    raise RuntimeError("Install the API extra: pip install -e '.[api]'") from exc

app = FastAPI(title="RepoMedic AI", version="1.0.0", description="Demo-only multi-agent repair API")
service = ReviewService()

class StartRequest(BaseModel):
    issue: str = Field(default="Free shipping fails at exactly $50", max_length=500)

class ApprovalRequest(BaseModel):
    approved: bool

@app.get("/health")
def health():
    return {"status": "ok", "mode": "demo"}

@app.post("/runs")
def start(request: StartRequest):
    return service.start(request.issue)

@app.get("/runs/{run_id}")
def get_run(run_id: str):
    if run_id not in service.runs:
        raise HTTPException(status_code=404, detail="Unknown run ID")
    return service.runs[run_id]

@app.post("/runs/{run_id}/review")
def review(run_id: str, request: ApprovalRequest):
    try:
        return service.approve(run_id, request.approved, Path(os.environ.get("REPOMEDIC_ARTIFACTS", "artifacts")))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
