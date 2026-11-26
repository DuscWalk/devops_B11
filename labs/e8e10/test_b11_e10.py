import tempfile
import unittest
from pathlib import Path

from b11_e10 import recheck_failure


class E10GateTests(unittest.TestCase):
    def test_new_md_blocks_an_otherwise_working_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'case'
            result = recheck_failure(root)
            self.assertIsNone(result['error'])
            self.assertFalse(result['accepted'])
            self.assertEqual((root / 'project/Makefile').read_bytes(), (root / 'source-before.Makefile').read_bytes())
            self.assertIn(b'helper.o: unused.h\n', (root / 'reject-md/sandbox/Makefile').read_bytes())
