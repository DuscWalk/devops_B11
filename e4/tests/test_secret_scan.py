"""Regressions for scanning the existing E2/E3 history without losing detections."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCANNER = Path(__file__).resolve().parents[2] / 'scripts' / 'secret_scan.py'


class HistoryScanTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git('init', '-q')
        self.git('config', 'user.name', '241276007')
        self.git('config', 'user.email', '241276007@smail.nju.edu.cn')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args],
                              check=True, capture_output=True)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'disposable regression fixture')

    def scan(self):
        return subprocess.run([sys.executable, str(SCANNER), str(self.root), '--history'],
                              capture_output=True, text=True)

    def test_legacy_non_utf8_text_scans_successfully(self):
        (self.root / 'legacy.txt').write_bytes(b'legacy text \x99\xff\n')
        self.commit()
        result = self.scan()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn('未发现问题', result.stdout)

    def test_removed_key_in_non_utf8_history_is_still_detected(self):
        # Synthetic key exists only in a disposable temporary repository.
        (self.root / 'legacy.txt').write_bytes(b'legacy \x99\xff\n' + b'sk-' + b'a' * 24 + b'\n')
        self.commit()
        (self.root / 'legacy.txt').write_text('cleaned\n')
        self.commit()
        result = self.scan()
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertIn('git-history', result.stdout)
        self.assertNotIn('sk-' + 'a' * 24, result.stdout)


if __name__ == '__main__':
    unittest.main()
