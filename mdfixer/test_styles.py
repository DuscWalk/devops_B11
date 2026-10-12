"""Exercise generated E3 patches through REPAIR, git apply and real C builds."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mdfixer_core import BuildSpec, Finding, RepairInput, Repository
from mdfixer_runner import run_repair

FIXTURES = Path(__file__).resolve().parents[1] / "e3/fixtures/mdfixer"


class StyleRepairTests(unittest.TestCase):
    def check_style(self, style, cumulative=False):
        with tempfile.TemporaryDirectory(prefix="b11-style-") as tmp:
            root = Path(tmp)
            workspace = root / "project"
            shutil.copytree(FIXTURES / style, workspace)
            shutil.copyfile(workspace / "Makefile.before", workspace / "Makefile")

            if cumulative:
                extra = "\nextra.o: main.c unused.h{dependency}\n\t$(CC) $(CFLAGS) -c $< -o $@\n"
                for name, dependency in (("Makefile", ""), ("Makefile.reference", " config.h")):
                    path = workspace / name
                    path.write_text(path.read_text().replace("all: app", "all: app extra.o")
                                    + extra.format(dependency=dependency))

            def command(*args):
                return subprocess.check_output(
                    args, cwd=workspace, text=True, stderr=subprocess.STDOUT,
                    timeout=30,
                )

            command("git", "init", "-q")
            command("git", "add", ".")
            command("git", "-c", "user.name=duscwalk",
                    "-c", "user.email=241276007@smail.nju.edu.cn",
                    "-c", "commit.gpgsign=false", "commit", "-qm", "E3 manual fixture")
            commit = command("git", "rev-parse", "HEAD").strip()
            finding = Finding("MISSING", "main.o", "config.h", commit, "MANUAL",
                              {"file": "Makefile", "line": 1}, {})
            inputs = root / "inputs"
            report = inputs / "b11/job-md/report.json"
            report.parent.mkdir(parents=True)
            findings = [finding]
            if cumulative:
                findings.append(Finding("MISSING", "extra.o", "config.h", commit, "MANUAL",
                                        {"file": "Makefile", "line": 1}, {}))
            report.write_text(json.dumps({"findings": [asdict(item) for item in findings]}))
            request = RepairInput(
                Repository("https://example.invalid/b11-manual-fixture", commit),
                "artifact://b11/job-md/report.json", "repo://" + commit + "/Makefile",
                "unused-local-prototype", BuildSpec("make clean && make"), "./app",
                timeout_seconds=30,
            )
            before = (workspace / "Makefile").read_bytes()
            result = run_repair(request, root / "output", workspace=workspace,
                                artifact_root=inputs, job_id="job-style-" + style)
            self.assertIsNone(result.error)
            self.assertEqual(result.summary["candidates_accepted"], len(findings))
            self.assertFalse(result.summary["recheck_performed"])
            self.assertFalse(result.summary["image_used"])
            self.assertNotIn("recheck_missing_remaining", result.summary)
            self.assertEqual((workspace / "Makefile").read_bytes(), before)
            folder = root / "output/b11" / ("job-style-" + style)
            self.assertEqual(len(result.artifacts), 3)
            for artifact in result.artifacts:
                payload = (folder / artifact["uri"].rsplit("/", 1)[1]).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
            tests = json.loads((folder / "test_result.json").read_text())
            self.assertEqual(tests["candidates"][0]["verify_output"], "1\n")
            patch = folder / "fix.patch"
            command("git", "apply", "--check", str(patch))
            command("git", "apply", str(patch))
            self.assertEqual((workspace / "Makefile").read_bytes(),
                             (workspace / "Makefile.reference").read_bytes())
            command("make", "clean")
            command("make")
            self.assertEqual(command("./app"), "1\n")
            time.sleep(1.1)
            (workspace / "config.h").write_text("#define VALUE 2\n")
            rebuild = command("make")
            self.assertIn("main.c", rebuild)
            self.assertEqual(command("./app"), "2\n")
            if style == "implicit":
                self.assertIn("config.h", (workspace / "main.d").read_text())
            else:
                self.assertIn("unused.h", (workspace / "Makefile").read_text())
            print(f"PASS generated {style}: REPAIR, artifact hashes, git apply, oracle bytes, "
                  "build=1, header-change rebuild=2, source restored, recheck=NOT_RUN")

    def test_target(self):
        self.check_style("target")

    def test_macro(self):
        self.check_style("macro")

    def test_hybrid(self):
        self.check_style("hybrid")

    def test_implicit(self):
        self.check_style("implicit")

    def test_cumulative_after_implicit_insertion(self):
        self.check_style("implicit", cumulative=True)


if __name__ == "__main__":
    unittest.main()
