"""Run a known-safe unit test fixture in an isolated temporary working directory."""
import subprocess
import sys
import tempfile
from pathlib import Path
from .fixture import install_fixture
from .security import bounded_patch


def run_tests(patched: bool = False) -> dict:
    with tempfile.TemporaryDirectory(prefix="repomedic-") as temp:
        workspace = Path(temp)
        install_fixture(workspace)
        if patched:
            shipping = workspace / "shipping.py"
            shipping.write_text(bounded_patch(shipping.read_text(encoding="utf-8")), encoding="utf-8")
        # Fixed command and fixed test files only. Not a general-purpose secure sandbox.
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-m", "unittest", "discover", "-s", str(workspace), "-p", "test_shipping.py", "-v"],
                cwd=str(workspace), capture_output=True, text=True, timeout=15,
                env={"PATH": "", "PYTHONIOENCODING": "utf-8"},
            )
        except subprocess.TimeoutExpired:
            return {"passed": False, "returncode": -1, "output": "Test execution timed out"}
        output = (proc.stdout + "\n" + proc.stderr)[-5000:]
        return {"passed": proc.returncode == 0, "returncode": proc.returncode, "output": output}
