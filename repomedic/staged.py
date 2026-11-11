"""Stepwise orchestration for the dashboard; real work runs on every step."""
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
from .agents import investigator, developer, tester, auditor

STAGES = (investigator, developer, tester, auditor)

class StagedRuns:
    def __init__(self, review_service):
        self.review_service = review_service
        self.lock = RLock()

    def create(self, issue: str):
        if not issue or len(issue) > 500:
            raise ValueError("Issue must contain 1 to 500 characters")
        with self.lock:
            run_id = uuid4().hex
            record = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
                      "issue": issue, "trace": [], "step": 0, "decision": "NOT_STARTED",
                      "human_approved": False, "artifact_released": False,
                      "mode": "deterministic_fixture_demo"}
            self.review_service.runs[run_id] = record
            return record

    def advance(self, run_id):
        with self.lock:
            record = self.review_service.runs.get(run_id)
            if record is None:
                raise KeyError("Unknown run ID")
            if "step" not in record:
                raise ValueError("This run was created in immediate mode")
            step = record["step"]
            if step >= len(STAGES):
                raise ValueError("Workflow already complete")
            try:
                updates = STAGES[step](record)
            except Exception:
                record["decision"] = "EXECUTION_FAILED"
                record["trace"].append({"agent": STAGES[step].__name__, "event": "stage_failed"})
                raise
            record.update(updates)
            record["step"] = step + 1
            if record["step"] < len(STAGES):
                record["decision"] = "RUNNING"
            return record
