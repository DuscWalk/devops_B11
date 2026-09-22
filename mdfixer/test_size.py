#!/usr/bin/env python3
"""MDFixer — 修复缺失依赖（MISSING）。
对应 A11-B11 E2 契约中的 REPAIR 任务类型。"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
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
    artifacts: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    error: Any = None
def parse_artifact_uri(uri):
    m = re.match(r"^artifact://([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)/([A-Za-z0-9._/-]+)$", uri)
    if not m: return None
    return m.group(1), m.group(2), m.group(3)
def resolve_artifact_path(uri):
    parsed = parse_artifact_uri(uri)
    if parsed is None: return None
    group, job_id, name = parsed
    if not ARTIFACT_ROOT: return None
    return Path(ARTIFACT_ROOT) / group / job_id / name
def parse_makefile_uri(uri):
    m = re.match(r"^repo://([0-9a-f]{40})/(.+)$", uri)
    if not m: return None
    return m.group(1), m.group(2)
def load_md_report(md_report_uri):
    path = resolve_artifact_path(md_report_uri)
    if path is None or not path.exists():
        p = Path(md_report_uri)
        if p.exists(): path = p
        else: raise FileNotFoundError(f"无法解析 md_report_uri: {md_report_uri}")
    with open(path, "r", encoding="utf-8") as f: data = json.load(f)
    findings_raw = data
    if isinstance(data, dict):
        if "output" in data and isinstance(data["output"], dict): findings_raw = data["output"].get("findings", [])
        elif "findings" in data: findings_raw = data["findings"]
        else: findings_raw = []
    findings = []
    for item in findings_raw:
        findings.append(Finding(type=item.get("type",""), target=item.get("target",""), dependency=item.get("dependency",""), commit=item.get("commit",""), detector=item.get("detector",""), location=item.get("location",{}), evidence=item.get("evidence",{}), suggested_fix=item.get("suggested_fix","")))
    return findings
def filter_missing(findings):
    return [f for f in findings if f.type == "MISSING"]
@dataclass
class MakefileRule:
    target: str
    prerequisites: list
    recipe: list
    line_no: int
def parse_makefile(content):
    rules = []
    lines = content.split("
")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"): i += 1; continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*s*[:?+]?=", line) and ":" not in line.split("=",1)[0]: i += 1; continue
        if not line.startswith("	") and ":" in line:
            colon_idx = line.index(":")
            if colon_idx+1 < len(line) and line[colon_idx+1] == "=": i += 1; continue
            target_part = line[:colon_idx].strip()
            prereq_part = line[colon_idx+1:].strip()
            while prereq_part.endswith("\"):
                prereq_part = prereq_part[:-1].rstrip()
                i += 1
                if i < len(lines): prereq_part += " " + lines[i].strip()
            prerequisites = prereq_part.split() if prereq_part else []
            recipe = []
            rule_line = i + 1
            i += 1
            while i < len(lines) and (lines[i].startswith("	") or lines[i].strip() == ""):
                if lines[i].startswith("	"): recipe.append(lines[i])
                i += 1
            rules.append(MakefileRule(target=target_part, prerequisites=prerequisites, recipe=recipe, line_no=rule_line))
        else: i += 1
    return rules
def detect_declaration_style(content, rules):
    return {"uses_tab_recipe": any(r.recipe for r in rules), "prereq_separator": " ", "has_continuation": "\\" in content, "variable_patterns": re.findall(r"$(([A-Za-z_][A-Za-z0-9_]*))", content)}
def find_rule_for_target(rules, target):
    for rule in rules:
        if target in rule.target.split(): return rule
    return None
def generate_patch_for_missing(makefile_content, rules, missing):
    rule = find_rule_for_target(rules, missing.target)
    if rule is None: return None
    dep = missing.dependency
    if dep in rule.prerequisites: return None
    lines = makefile_content.split("
")
    rule_idx = rule.line_no - 1
    line = lines[rule_idx]
    colon_idx = line.index(":")
    target_part = line[:colon_idx]
    prereq_part = line[colon_idx+1:]
    new_prereq = prereq_part.rstrip()
    if new_prereq and not new_prereq.endswith("\"): new_prereq = new_prereq + " " + dep
    elif new_prereq.endswith("\"): new_prereq = new_prereq + "
	" + dep + " \"
    else: new_prereq = " " + dep
    lines[rule_idx] = target_part + ":" + new_prereq
    patched = "
".join(lines)
    return patched, f"为 {missing.target} 补充缺失依赖 {missing.dependency}"
def make_unified_diff(original, patched, filename):
    import difflib
    diff = difflib.unified_diff(original.splitlines(keepends=True), patched.splitlines(keepends=True), fromfile=f"a/{filename}", tofile=f"b/{filename}", lineterm="")
    return "".join(diff)
@dataclass
class CandidateResult:
    accepted: bool
    reason: str = ""
    patch: str = ""
    description: str = ""
    build_exit_code: int = -1
    verify_exit_code: int = -1
def run_command(cmd, cwd=None, timeout=1200):
    try:
        proc = subprocess.run(cmd, shell=True, c