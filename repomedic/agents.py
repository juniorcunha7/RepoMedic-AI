"""Four separate, deterministic roles for a reviewable demo."""
import difflib
from typing import TypedDict
from .fixture import BUGGY
from .security import bounded_patch
from .test_runner import run_tests

class State(TypedDict, total=False):
    issue: str
    baseline: dict
    diagnosis: str
    proposed_source: str
    diff: str
    verification: dict
    decision: str
    trace: list[dict]

def investigator(state: State) -> dict:
    baseline = run_tests(False)
    diagnosis = ("Boundary comparison excludes equality at the free-shipping threshold."
                 if not baseline["passed"] else "No failing tests detected")
    return {"baseline": baseline, "diagnosis": diagnosis,
            "trace": [*state.get("trace", []), {"agent": "investigator", "event": "baseline_tests", "passed": baseline["passed"]}]}

def developer(state: State) -> dict:
    if state["baseline"]["passed"]:
        raise ValueError("Fixture unexpectedly passes: refusing patch")
    source = bounded_patch(BUGGY)
    diff = "".join(difflib.unified_diff(BUGGY.splitlines(keepends=True), source.splitlines(keepends=True),
                                        fromfile="a/shipping.py", tofile="b/shipping.py"))
    return {"proposed_source": source, "diff": diff,
            "trace": [*state.get("trace", []), {"agent": "developer", "event": "bounded_patch_proposed"}]}

def tester(state: State) -> dict:
    result = run_tests(True)
    return {"verification": result,
            "trace": [*state.get("trace", []), {"agent": "tester", "event": "patched_tests", "passed": result["passed"]}]}

def auditor(state: State) -> dict:
    approved_for_review = not state["baseline"]["passed"] and state["verification"]["passed"] and bool(state["diff"])
    decision = "AWAITING_HUMAN_APPROVAL" if approved_for_review else "REJECTED"
    return {"decision": decision,
            "trace": [*state.get("trace", []), {"agent": "auditor", "event": "policy_review", "decision": decision}]}
