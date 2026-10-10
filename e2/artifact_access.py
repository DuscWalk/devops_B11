#!/usr/bin/env python3
"""Read a local artifact using the proposed A11/B11 directory mapping."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


class ArtifactAccessError(ValueError):
    """The reference cannot be read or its integrity check failed."""


def resolve_artifact(root, uri):
    if not isinstance(uri, str):
        raise ArtifactAccessError("artifact uri must be a string")
    parsed = urlsplit(uri)
    parts = [parsed.netloc, *parsed.path.removeprefix("/").split("/")]
    if (parsed.scheme != "artifact" or parsed.query or parsed.fragment
            or len(parts) < 3 or any(
                part in (".", "..") or not re.fullmatch(r"[A-Za-z0-9._-]+", part)
                for part in parts)):
        raise ArtifactAccessError("expected artifact://<group>/<job_id>/<name>")
    try:
        base = Path(root).resolve(strict=True)
        if not base.is_dir():
            raise ArtifactAccessError("artifact root must be a directory")
        path = base.joinpath(*parts).resolve(strict=True)
        if not path.is_relative_to(base):
            raise ArtifactAccessError("artifact resolves outside the artifact root")
        if not path.is_file():
            raise ArtifactAccessError("artifact must be a regular file")
        return path
    except OSError as exc:
        raise ArtifactAccessError(f"artifact unavailable: {exc}") from exc


def read_artifact(root, metadata):
    if not isinstance(metadata, dict):
        raise ArtifactAccessError("artifact metadata must be an object")
    for field in ("artifact_id", "type", "uri", "media_type", "producer_job_id"):
        if not isinstance(metadata.get(field), str) or not metadata[field]:
            raise ArtifactAccessError(f"artifact metadata requires {field}")
    expected = metadata.get("sha256")
    if "sha256" in metadata and (
            not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)):
        raise ArtifactAccessError("sha256 must contain 64 lowercase hexadecimal digits")
    path = resolve_artifact(root, metadata["uri"])
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise ArtifactAccessError(f"artifact unreadable: {exc}") from exc
    actual = hashlib.sha256(payload).hexdigest()
    if expected is not None and actual != expected:
        raise ArtifactAccessError("artifact sha256 mismatch")
    return path, payload, actual


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
        path, payload, digest = read_artifact(args.root, metadata)
    except (ArtifactAccessError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "uri": metadata["uri"], "path": str(path),
        "media_type": metadata["media_type"], "bytes_read": len(payload),
        "sha256": digest, "checksum_verified": "sha256" in metadata,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
