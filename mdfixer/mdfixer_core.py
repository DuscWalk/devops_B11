from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = "1.1.0"
ARTIFACT_ROOT = os.environ.get("ARTIFACT_ROOT", "")


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
                                                                                                                class VariableDef:
                                                                                                                    name: str
                                                                                                                        value: str
                                                                                                                            operator: str
                                                                                                                                line_no: int
                                                                                                                                
                                                                                                                                
                                                                                                                                @dataclass
                                                                                                                                class CandidateResult:
                                                                                                                                    accepted: bool
                                                                                                                                        reason: str = ""
                                                                                                                                            patch: str = ""
                                                                                                                                                description: str = ""
                                                                                                                                                    build_exit_code: int = -1
                                                                                                                                                        verify_exit_code: int = -1
                                                                                                                                                        
                                                                                                                                                        
                                                                                                                                                        def parse_artifact_uri(uri):
                                                                                                                                                            m = re.match(r"^artifact://([\w.-]+)/([\w.-]+)/([\w./-]+)$", uri)
                                                                                                                                                                if not m:
                                                                                                                                                                        return None
                                                                                                                                                                            return m.group(1), m.group(2), m.group(3)
                                                                                                                                                                            
                                                                                                                                                                            
                                                                                                                                                                            def resolve_artifact_path(uri):
                                                                                                                                                                                parsed = parse_artifact_uri(uri)
                                                                                                                                                                                    if parsed is None:
                                                                                                                                                                                            return None
                                                                                                                                                                                                group, job_id, name = parsed
                                                                                                                                                                                                    if not ARTIFACT_ROOT:        return None
                                                                                                                                                                                                        return Path(ARTIFACT_ROOT) / group / job_id / name
                                                                                                                                                                                                        
                                                                                                                                                                                                        
                                                                                                                                                                                                        def parse_makefile_uri(uri):
                                                                                                                                                                                                            m = re.match(r"^repo://([0-9a-f]{40})/,++)$", uri)
                                                                                                                                                                                                                if not m:
                                                                                                                                                                                                                        return None
                                                                                                                                                                                                                            return m.group(1), m.group(2)
                                                                                                                                                                                                                            
                                                                                                                                                                                                                            
                                                                                                                                                                                                                            def load_md_report(md_report_uri):
                                                                                                                                                                                                                                path = resolve_artifact_path(md_report_uri)
                                                                                                                                                                                                                                    if path is None or not path.exists():
                                                                                                                                                                                                                                            p = Path(md_report_uri)
                                                                                                                                                                                                                                                    if p.exists():
                                                                                                                                                                                                                                                                path = p
                                                                                                                                                                                                                                                                        else:
                                                                                                                                                                                                                                                                                    raise FileNotFoundError(f"cannot resolve md_report_uri: {md_report_uri}")
                                                                                                                                                                                                                                                                                        with open(path, "r", encoding="utf-8") as f:
                                                                                                                                                                                                                                                                                                data = json.load(f)
                                                                                                                                                                                                                                                                                                    findings_raw = data
                                                                                                                                                                                                                                                                                                        if isinstance(data, dict):
                                                                                                                                                                                                                                                                                                                if "output" in data and isinstance(data["output"], dict):
                                                                                                                                                                                                                                                                                                                            findings_raw = data["output"].get("findings", [])
                                                                                                                                                                                                                                                                                                                                    elif "findings" in data:
                                                                                                                                                                                                                                                                                                                                                findings_raw = data["findings"]
                                                                                                                                                                                                                                                                                                                                                        else:
                                                                                                                                                                                                                                                                                                                                                                    findings_raw = []
                                                                                                                                                                                                                                                                                                                                                                        findings = []
                                                                                                                                                                                                                                                                                                                                                                            for item in findings_raw:
                                                                                                                                                                                                                                                                                                                                                                                    findings.append(Finding(
                                                                                                                                                                                                                                                                                                                                                                                                type=item.get("type", ""),
                                                                                                                                                                                                                                                                                                                                                                                                            target=item.get("target", ""),
                                                                                                                                                                                                                                                                                                                                                                                                                        dependency=item.get("dependency", ""),
                                                                                                                                                                                                                                                                                                                                                                                                                                    commit=item.get("commit", ""),
                                                                                                                                                                                                                                                                                                                                                                                                                                                detector=item.get("detector", ""),
                                                                                                                                                                                                                                                                                                                                                                                                                                                            location=item.get("location", {}),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        evidence=item.get("evidence", {}),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    suggested_fix=item.get("suggested_fix", ""),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ))
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                return findings
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                def filter_missing(findings):
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    return [f for f in findings if f.type == "MISSING"]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    def parse_artifact_uri(uri):
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = "1.1.0"
ARTIFACT_ROOT = os.environ.get("ARTIFACT_ROOT", "")


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
class VariableDef:
    name: str
    value: str
    operator: str
    line_no: int


@dataclass
class CandidateResult:
    accepted: bool
    reason: str = ""
    patch: str = ""
    description: str = ""
    build_exit_code: int = -1
    verify_exit_code: int = -1


def parse_artifact_uri(uri):
    m = re.match(r"^artifact://([w.-]+)/([w.-]+)/([w./-]+)$", uri)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def resolve_artifact_path(uri):
    parsed = parse_artifact_uri(uri)
    if parsed is None:
        return None
    group, job_id, name = parsed
    if not ARTIFACT_ROOT:
        return None
    return Path(ARTIFACT_ROOT) / group / job_id / name


def parse_makefile_uri(uri):
    m = re.match(r"^repo://([0-9a-f]{40})/(.+)$", uri)
    if not m:
        return None
    return m.group(1), m.group(2)


def load_md_report(md_report_uri):
    path = resolve_artifact_path(md_report_uri)
    if path is None or not path.exists():
        p = Path(md_report_uri)
        if p.exists():
            path = p
        else:
            raise FileNotFoundError(f"cannot resolve md_report_uri: ${md_report_uri}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    findings_raw = data
    if isinstance(data, dict):
        if "output" in data and isinstance(data["output"], dict):
            findings_raw = data["output"].get("findings", [])
        elif "findings" in data:
            findings_raw = data["findings"]
        else:
            findings_raw = []
    findings = []
    for item in findings_raw:
        findings.append(Finding(
            type=item.get("type", ""),
            target=item.get("target", ""),
            dependency=item.get("dependency", ""),
            commit=item.get("commit", ""),
            detector=item.get("detector", ""),
            location=item.get("location", {}),
            evidence=item.get("evidence", {}),
            suggested_fix=item.get("suggested_fix", ""),
        ))
    return findings


def filter_missing(findings):
    return [f for f in findings if f.type == "MISSING"]
