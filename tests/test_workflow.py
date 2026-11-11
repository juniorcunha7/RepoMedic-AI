import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from repomedic.fixture import BUGGY, FIXED
from repomedic.security import bounded_patch, SecurityViolation
from repomedic.test_runner import run_tests
from repomedic.workflow import execute
from repomedic.service import ReviewService

class RepoMedicTests(unittest.TestCase):
    def test_baseline_fails(self):
        self.assertFalse(run_tests(False)["passed"])

    def test_repair_passes(self):
        result = run_tests(True)
        self.assertTrue(result["passed"], result["output"])
        self.assertIn("Ran 4 tests", result["output"])

    def test_exact_patch(self):
        self.assertEqual(bounded_patch(BUGGY), FIXED)

    def test_untrusted_source_denied(self):
        with self.assertRaises(SecurityViolation):
            bounded_patch("import os")

    def test_review_is_required(self):
        service = ReviewService()
        record = service.start()
        self.assertEqual(record["decision"], "AWAITING_HUMAN_APPROVAL")
        self.assertFalse(record["artifact_released"])
        self.assertEqual(len(record["trace"]), 4)

    def test_human_approval_exports_patch_and_audit(self):
        service = ReviewService()
        record = service.start()
        with TemporaryDirectory() as d:
            final = service.approve(record["run_id"], True, Path(d))
            self.assertTrue(Path(final["patch_file"]).exists())
            self.assertTrue((Path(d) / f"{record['run_id']}.json").exists())
            self.assertIn("+    return total >= threshold", Path(final["patch_file"]).read_text())

    def test_human_rejection_blocks_release(self):
        service = ReviewService()
        record = service.start()
        with TemporaryDirectory() as d:
            result = service.approve(record["run_id"], False, Path(d))
            self.assertEqual(result["decision"], "HUMAN_REJECTED")
            self.assertFalse(list(Path(d).iterdir()))

    def test_missing_run_denied(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(KeyError):
                ReviewService().approve("missing", True, Path(d))

    def test_trace_agent_order(self):
        state = execute(use_graph=False)
        self.assertEqual([e["agent"] for e in state["trace"]],
                         ["investigator", "developer", "tester", "auditor"])

    def test_diff_is_unified(self):
        self.assertIn("--- a/shipping.py", execute(use_graph=False)["diff"])

    def test_large_issue_rejected(self):
        with self.assertRaises(ValueError):
            ReviewService().start("x" * 501)

    def test_idempotent_approval(self):
        service = ReviewService()
        record = service.start()
        with TemporaryDirectory() as d:
            first = service.approve(record["run_id"], True, Path(d))
            second = service.approve(record["run_id"], True, Path(d))
            self.assertEqual(first["patch_file"], second["patch_file"])
