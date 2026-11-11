"""Review gate and durable audit output: patch generation never mutates source repos."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .workflow import execute

class ReviewService:
    def __init__(self):
        self.runs: dict[str, dict] = {}

    def start(self, issue: str = "Free shipping fails at exactly $50") -> dict:
        if len(issue) > 500:
            raise ValueError("Issue exceeds 500 characters")
        state = execute(issue)
        run_id = uuid.uuid4().hex
        record = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
                  **state, "human_approved": False, "artifact_released": False}
        self.runs[run_id] = record
        return record

    def approve(self, run_id: str, approved: bool, output_dir: Path) -> dict:
        record = self.runs.get(run_id)
        if record is None:
            raise KeyError("Unknown run ID")
        if approved and record["artifact_released"]:
            return record
        if record["decision"] != "AWAITING_HUMAN_APPROVAL":
            raise ValueError("Review gate is closed")
        if not approved:
            record["decision"] = "HUMAN_REJECTED"
            record["trace"].append({"agent": "human", "event": "rejected"})
            return record
        if record["artifact_released"]:
            return record
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{run_id}.patch"
        output_path.write_text(record["diff"], encoding="utf-8")
        record["human_approved"] = True
        record["artifact_released"] = True
        record["decision"] = "PATCH_RELEASED"
        record["patch_file"] = str(output_path)
        record["trace"].append({"agent": "human", "event": "approved_patch_export"})
        (output_dir / f"{run_id}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return record
