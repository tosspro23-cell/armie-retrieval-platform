import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WorkbenchStartupTests(unittest.TestCase):
    def test_launcher_contains_startup_safety_contract(self):
        script = (ROOT / "scripts" / "start_workbench.sh").read_text(encoding="utf-8")
        for marker in ("PYTHONPATH", "armie_retrieval", "health_url", "kill -0", "Frontend:", "cleanup", "node_modules/vite"):
            self.assertIn(marker, script)

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
