"""Independent B-track checks for candidate scope and source preservation."""
import tempfile
import unittest
from pathlib import Path

from lab import fixture, patch, run, scan


class CrossReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name) / "project"

    def test_e8_redundant_only_report_does_not_delete_dependencies(self):
        fixture(self.project)
        report = scan(self.project)
        report["findings"] = [finding for finding in report["findings"]
                              if finding["type"] == "REDUNDANT"]
        self.assertEqual(len(report["findings"]), 1)
        before = (self.project / "Makefile").read_bytes()

        diff, plan = patch(self.project, report)

        self.assertEqual(diff, "")
        self.assertEqual(plan, [])
        self.assertEqual((self.project / "Makefile").read_bytes(), before)
        self.assertEqual(run(["git", "status", "--porcelain"], self.project), "")

    def test_e9_shared_macro_adds_unwanted_dependency_to_other_target(self):
        fixture(self.project, "macro")
        makefile = self.project / "Makefile"
        original = makefile.read_text()
        makefile.write_text(original.replace("helper.o: helper.c\n",
                                             "helper.o: helper.c $(DEPS)\n"))
        run(["git", "add", "Makefile"], self.project)
        run(["git", "commit", "-m", "share dependency variable"], self.project)
        before = makefile.read_bytes()
        report = scan(self.project)
        self.assertIn({"type": "MISSING", "target": "main.o", "dependency": "config.h"},
                      report["findings"])

        diff, plan = patch(self.project, report)
        self.assertEqual(plan, [{"target": "main.o", "dependency": "config.h", "style": "macro"}])
        self.assertIn("+DEPS = main.c unused.h config.h", diff)
        self.assertEqual(makefile.read_bytes(), before)
        self.assertEqual(run(["git", "status", "--porcelain"], self.project), "")

        candidate = makefile.with_name("candidate.patch")
        candidate.write_text(diff)
        run(["git", "apply", "--check", str(candidate)], self.project)
        run(["git", "apply", str(candidate)], self.project)
        after = scan(self.project)
        self.assertIn("config.h", after["declared"]["helper.o"])
        self.assertNotIn("config.h", after["actual"]["helper.o"])
        self.assertIn({"type": "REDUNDANT", "target": "helper.o", "dependency": "config.h"},
                      after["findings"])


if __name__ == "__main__":
    unittest.main()
