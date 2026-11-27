import hashlib
import tempfile
import unittest
from pathlib import Path

from pipeline import Failure, repair_input, save


class ReportBinding(unittest.TestCase):
    def test_intact_artifact_must_still_match_the_consumer(self):
        target = 'a' * 40
        good = dict(schema_version='e11e12-1', kind='incremental-check', commit=target,
                    status='SUCCEEDED', job_id='j', trace_id='t', data={'commit': target})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.json'
            for change, expected in [({}, None), ({'trace_id':'other'}, 'TASK_MISMATCH'),
                    ({'job_id':'other'}, 'TASK_MISMATCH'), ({'kind':'fixed-md'}, 'ARTIFACT_TYPE_MISMATCH'),
                    ({'data':{'commit':'b'*40}}, 'STALE_REPORT')]:
                with self.subTest(change=change):
                    save(path, {**good, **change})
                    args = (path, hashlib.sha256(path.read_bytes()).hexdigest(), 'e12', target, 'j', 't')
                    if expected is None:
                        self.assertEqual(repair_input(*args), good['data'])
                    else:
                        with self.assertRaises(Failure) as exc:
                            repair_input(*args)
                        self.assertEqual(exc.exception.code, expected)
