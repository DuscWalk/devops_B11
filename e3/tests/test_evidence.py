"""Regression checks for evidence preservation, failures and environment keys."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "e3/scripts"))
from common import EvidenceRun, file_sha256, fingerprint


class EvidenceRegressionTests(unittest.TestCase):
    def test_identity_order_stable_and_configuration_change_visible(self):
        self.assertEqual(fingerprint({"compiler": "gcc", "cflags": ["-O0"]}),
                         fingerprint({"cflags": ["-O0"], "compiler": "gcc"}))
        self.assertNotEqual(fingerprint({"cflags": ["-O0"]}), fingerprint({"cflags": ["-O2"]}))

    def test_unexpected_exit_retains_log_and_failure_summary(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            run = EvidenceRun(Path(temp) / "run", "failure-regression")
            with self.assertRaises(RuntimeError):
                run.run("intentional-failure", [sys.executable, "-c", "print('failure marker');raise SystemExit(7)"])
            run.finish(error="intentional test failure")
            commands = json.loads((run.directory / "commands.json").read_text())
            self.assertEqual(commands[0]["exit_code"], 7)
            self.assertIn("failure marker", (run.directory / commands[0]["log"]).read_text())
            self.assertEqual(json.loads((run.directory / "summary.json").read_text())["result"], "FAIL")
            inventory = json.loads((run.directory / "checksums.json").read_text())
            for name, digest in inventory.items():
                self.assertEqual(file_sha256(run.directory / name), digest)

    def test_timeout_is_failure_and_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            run = EvidenceRun(Path(temp) / "run", "timeout-regression")
            code, output = run.run("timeout", [sys.executable, "-u", "-c",
                                   "import time;print('started');time.sleep(5)"], timeout=0.2, allowed=None)
            self.assertEqual(code, 124)
            self.assertIn("started", output)
            self.assertTrue(run.commands[0]["timed_out"])

    def test_existing_directory_and_exports_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            existing = Path(temp) / "existing"
            existing.mkdir()
            marker = existing / "keep.txt"
            marker.write_text("preserve me")
            for script in ("run_baseline.py", "verify_docker.py"):
                for flag in ("--out", "--export-evidence"):
                    args = [sys.executable, str(ROOT / "e3/scripts" / script), flag, str(existing)]
                    if flag == "--export-evidence":
                        args.extend(["--out", str(Path(temp) / (script + "-new"))])
                    proc = subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=10)
                    self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
                    self.assertEqual(marker.read_text(), "preserve me")
                    self.assertFalse((Path(temp) / (script + "-new")).exists())


if __name__ == "__main__":
    unittest.main()
