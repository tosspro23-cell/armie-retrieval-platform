import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _armie_retrieval_resolves_without_pythonpath() -> bool:
    """True when `armie_retrieval` is importable without PYTHONPATH=src injection
    (e.g. after `pip install .`). In that case the diagnostic below has no
    failure to observe, by construction."""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    probe = subprocess.run(
        [sys.executable, "-c", "import armie_retrieval"],
        cwd=ROOT, env=env, capture_output=True,
    )
    return probe.returncode == 0


class WorkbenchStartupTests(unittest.TestCase):
    def test_launcher_contains_startup_safety_contract(self):
        script = (ROOT / "scripts" / "start_workbench.sh").read_text(encoding="utf-8")
        for marker in ("PYTHONPATH", "armie_retrieval", "health_url", "kill -0", "Frontend:", "cleanup", "node_modules/vite"):
            self.assertIn(marker, script)

    @unittest.skipIf(
        _armie_retrieval_resolves_without_pythonpath(),
        "armie_retrieval already resolves without PYTHONPATH (e.g. `pip install .` "
        "ran first, as CI does): the no-path-injection failure this test checks for "
        "cannot occur in this environment. Run in a source-only checkout "
        "(no `pip install .`) to exercise this diagnostic.",
    )
    def test_direct_backend_diagnostic_from_repository_root_without_path_injection(self):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        process = subprocess.Popen(
            ["python3", "-m", "uvicorn", "services.api.app:app", "--host", "127.0.0.1", "--port", "8777"],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            process.wait(timeout=2)
            self.assertNotEqual(process.returncode, 0)
            stderr = process.stderr.read().decode("utf-8", errors="replace")
            self.assertIn("armie_retrieval", stderr)
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
