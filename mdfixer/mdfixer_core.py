from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = "1.1.0"


@dataclass
class Repository:
    url: str
    commit: str


@dataclass
class BuildSpec:
    command: str


@dataclass
class RepairInput:
    repository: Repository
    md_report_uri: str
    makefile_uri: str
    image: str
    build: BuildSpec
    verify_command: str
    max_iterations: int = 1
    timeout_seconds: int = 1200


@dataclass
class Finding:
    type: str
    target: str
    dependency: str
    commit: str
    detector: str
    location: dict
    evidence: dict
    suggested_fix: str = ""
    origin: str = ""


@dataclass
class RepairResult:
    patch_uri: str = ""
    patch_sha256: str = ""
    artifacts: list[dict] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    error: dict | None = None


@dataclass
class MakefileRule:
    target: str
    prerequisites: list[str]
    recipe: list[str]
    line_no: int


@dataclass
class CandidateResult:
    accepted: bool
    reason: str = ""
    patch: str = ""
    description: str = ""
    build_exit_code: int = -1
    verify_exit_code: int = -1
    build_output: str = ""
    verify_output: str = ""


def parse_artifact_uri(uri):
    m = re.fullmatch(r"artifact://([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)/([A-Za-z0-9._/-]+)", uri)
    if not m or any(x in ("", ".", "..") for x in '/'.join(m.groups()).split('/')):
        return None
    return m.groups()


def resolve_artifact_path(uri, artifact_root=None):
    parsed = parse_artifact_uri(uri)
    base = artifact_root or os.environ.get("ARTIFACT_ROOT")
    if parsed is None or not base:
        raise ValueError("artifact:// URI and explicit artifact root are required")
    root = Path(base).resolve(strict=True)
    path = root.joinpath(*parsed).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("artifact is not a file inside artifact root")
    return path


def parse_makefile_uri(uri):
    m = re.fullmatch(r"repo://([0-9a-f]{40})/([A-Za-z0-9._/-]+)", uri)
    if not m or any(x in ("", ".", "..") for x in m[2].split('/')):
        return None
    return m.groups()


def load_md_report(md_report_uri, artifact_root=None):
    data = json.loads(resolve_artifact_path(md_report_uri, artifact_root).read_text(encoding="utf-8"))
    # Both a complete detector Job and a standalone report use a findings array.
    node = data.get("output", data) if isinstance(data, dict) else {}
    raw = node.get("findings")
    if not isinstance(raw, list):
        raise ValueError("MD report must contain a findings array")
    findings = []
    for item in raw:
        if not isinstance(item, dict) or not all(k in item for k in (
                "type", "target", "dependency", "commit", "detector", "location", "evidence")):
            raise ValueError("finding lacks required fields")
        if item['type'] not in ('MISSING', 'REDUNDANT'):
            raise ValueError("unknown finding type")
        if not isinstance(item['location'],dict) or not isinstance(item['evidence'],dict):
            raise ValueError("location and evidence must be objects")
        findings.append(Finding(**{k:item[k] for k in Finding.__dataclass_fields__ if k in item}))
    return findings


def filter_missing(findings):
    return [f for f in findings if f.type == "MISSING" and f.origin != "RESOLVED"]
