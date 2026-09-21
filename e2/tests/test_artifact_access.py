"""Verify actual file access, integrity failures and reference boundaries."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from e2.artifact_access import ArtifactAccessError, read_artifact


class ArtifactAccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="b11-artifact-test-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "artifacts"
        self.file = self.root / "b11/job-demo/handoff.txt"
        self.file.parent.mkdir(parents=True)
        self.payload = b"E2 handoff demonstration\n"
        self.file.write_bytes(self.payload)
        self.metadata = {
            "artifact_id": "demo", "type": "LOG",
            "uri": "artifact://b11/job-demo/handoff.txt",
            "media_type": "text/plain", "producer_job_id": "job-demo",
            "sha256": hashlib.sha256(self.payload).hexdigest(),
        }

    def test_file_bytes_and_checksum_are_read(self):
        path, payload, digest = read_artifact(self.root, self.metadata)
        self.assertEqual(path, self.file.resolve())
        self.assertEqual(payload, self.payload)
        self.assertEqual(digest, self.metadata["sha256"])

    def test_checksum_is_optional_in_current_reference(self):
        metadata = copy.deepcopy(self.metadata)
        del metadata["sha256"]
        self.assertEqual(read_artifact(self.root, metadata)[1], self.payload)

    def test_modified_file_is_rejected(self):
        self.file.write_bytes(b"changed")
        with self.assertRaisesRegex(ArtifactAccessError, "sha256 mismatch"):
            read_artifact(self.root, self.metadata)

    def test_missing_file_is_rejected(self):
        self.file.unlink()
        with self.assertRaises(ArtifactAccessError):
            read_artifact(self.root, self.metadata)

    def test_path_escape_is_rejected(self):
        self.metadata["uri"] = "artifact://b11/job-demo/../../../outside.txt"
        with self.assertRaises(ArtifactAccessError):
            read_artifact(self.root, self.metadata)

    def test_symlink_outside_root_is_rejected(self):
        outside = self.base / "outside.txt"
        outside.write_bytes(self.payload)
        self.file.unlink()
        self.file.symlink_to(outside)
        with self.assertRaisesRegex(ArtifactAccessError, "outside"):
            read_artifact(self.root, self.metadata)

    def test_local_path_is_not_an_artifact_uri(self):
        self.metadata["uri"] = str(self.file)
        with self.assertRaises(ArtifactAccessError):
            read_artifact(self.root, self.metadata)

    def test_media_type_is_required(self):
        del self.metadata["media_type"]
        with self.assertRaisesRegex(ArtifactAccessError, "media_type"):
            read_artifact(self.root, self.metadata)

    def test_invalid_checksum_format_is_rejected(self):
        self.metadata["sha256"] = "abc"
        with self.assertRaisesRegex(ArtifactAccessError, "64 lowercase"):
            read_artifact(self.root, self.metadata)


if __name__ == "__main__":
    unittest.main()
