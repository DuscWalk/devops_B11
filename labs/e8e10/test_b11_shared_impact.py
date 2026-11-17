"""Independent expectations for the E9 shared-variable task and its control."""
import tempfile
import unittest
from pathlib import Path

from b11_shared_impact import analyze


class SharedImpactTests(unittest.TestCase):
    def check_case(self, shared):
        with tempfile.TemporaryDirectory() as temporary:
            return analyze(Path(temporary) / 'case', shared=shared)

    def test_e9_shared_variable_changes_an_unreported_target(self):
        result = self.check_case(True)
        self.assertEqual(result['requested_targets'], ['main.o'])
        self.assertEqual(result['make_before'], {
            'main.o': ['main.c', 'unused.h'],
            'helper.o': ['helper.c', 'main.c', 'unused.h']})
        self.assertEqual(result['added_dependencies'], {'main.o': ['config.h'], 'helper.o': ['config.h']})
        self.assertEqual(result['unrequested_targets'], ['helper.o'])
        self.assertEqual(result['new_redundant'], [['REDUNDANT', 'helper.o', 'config.h']])
        self.assertTrue(result['source_unchanged'])

    def test_e9_unshared_control_only_changes_the_reported_target(self):
        result = self.check_case(False)
        self.assertEqual(result['make_before']['helper.o'], ['helper.c'])
        self.assertEqual(result['added_dependencies'], {'main.o': ['config.h'], 'helper.o': []})
        self.assertEqual(result['unrequested_targets'], [])
        self.assertEqual(result['new_redundant'], [])
        self.assertTrue(result['source_unchanged'])


if __name__ == '__main__':
    unittest.main()
