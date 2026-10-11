import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mdfixer_core import Finding, filter_missing, parse_artifact_uri
from mdfixer_engine import parse_makefile
from mdfixer_patch import generate_patch_for_missing
from mdfixer_verify import run_command, verify_candidate


def finding(dep='config.h', kind='MISSING', origin=''):
    return Finding(kind, 'app.o', dep, 'a' * 40, 'MANUAL', {'file': 'Makefile', 'line': 1}, {}, origin=origin)


class RepairRegressionTests(unittest.TestCase):
    def test_ignore_redundant_and_resolved(self):
        a = finding()
        self.assertEqual(filter_missing([a, finding(kind='REDUNDANT'), finding(origin='RESOLVED')]), [a])

    def test_artifact_uri_and_traversal(self):
        self.assertEqual(parse_artifact_uri('artifact://b11/job-md/report.json'), ('b11', 'job-md', 'report.json'))
        self.assertIsNone(parse_artifact_uri('artifact://b11/job-md/../../file'))

    def test_cumulative_additions_preserve_continuation(self):
        content = 'app.o: app.c \\\n  legacy.h\n\tcc -c app.c\n'
        for dep in ['config.h', 'value.h']:
            rules, variables = parse_makefile(content)
            result = generate_patch_for_missing(content, rules, variables, finding(dep))
            self.assertIsNotNone(result)
            content = result[0]
        rules, _ = parse_makefile(content)
        self.assertEqual(set(rules[0].prerequisites), {'app.c', 'config.h', 'value.h', 'legacy.hg})
        self.assertIn('\\\n', content)

    def test_rejected_candidate_restores_makefile(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'Makefile'
            p.write_text('original\n')
            result = verify_candidate('candidate\n', p, 'exit 3', 'true', tmp, timeout=2)
            self.assertFalse(result.accepted)
            self.assertEqual(result.build_exit_code, 3)
            self.assertEqual(p.read_text(), 'original\n')

    def test_timeout_enforced(self):
        before = time.monotonic()
        code, _, _ = run_command('sleep 5', timeout=0.05)
        self.assertEqual(code, 124)
        self.assertLess(time.monotonic() - before, 2)

    def test_variable_rule_is_not_guessed(self):
        content = 'app.o: $(SOURCES)\n\tcc -c app.c\n'
        rules, variables = parse_makefile(content)
        self.assertIsNone(generate_patch_for_missing(content, rules, variables, finding()))


if __name__ == '__main__':
    unittest.main()
