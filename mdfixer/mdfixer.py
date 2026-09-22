#!/usr/bin/env python3
"""MDFixer — 修复缺失依赖（MISSING）。

对应 A11-B11 E2 契约中的 REPAIR 任务类型。
输入：REPAIR 请求（含 md_report_uri、makefile_uri、image、build、verify_command）。
处理：
  1. 从 MD 报告中只提取 type=MISSING 的发现（REDUNDANT 不进入修复流程，见 ADR-004）。
  2. 解析 Makefile，推断声明风格（target: deps 形式、变量展开、续行符等）。
  3. 为每个 MISSING 生成候选补丁：把 dependency 追加到对应 target 的依赖列表。
  4. 对每个候选补丁执行 build + verify；通过则接受，失败则记录拒绝原因。
输出：PATCH（统一 diff）、STYLE_REPORT、TEST_RESULT 三类产物，以及 summary。

本脚本是 E2 阶段的本地可运行实现，不部署 HTTP API。
用法：
    python mdfixer.py --request examples/repair_request.json --out-dir out/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
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
    artifacts: list[dict] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    error: dict | None = None


def parse_artifact_uri(uri: str) -> tuple[str, str, str] | None:
    """解析 artifact://<group>/<job_id>/<name>，返回 (group, job_id, name)。"""
    m = re.match(r"^artifact://([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)/([A-Za-z0-9._/-]+)$", uri)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def resolve_artifact_path(uri: str) -> Path | None:
    """把 artifact:// URI 映射到本地共享目录 $ARTIFACT_ROOT/<group>/<job_id>/<name>。"""
    parsed = parse_artifact_uri(uri)
    if parsed is None:
        return None
    group, job_id, name = parsed
    if not ARTIFACT_ROOT:
        return None
    return Path(ARTIFACT_ROOT) / group / job_id / name


def parse_makefile_uri(uri: str) -> tuple[str, str] | None:
    """解析 repo://<sha>/<path>，返回 (sha, path)。"""
    m = re.match(r"^repo://([0-9a-f]{40})/(.+)$", uri)
    if not m:
        return None
    return m.group(1), m.group(2)


def load_md_report(md_report_uri: str) -> list[Finding]:
    """读取 MD 报告，返回 findings 列表。"""
    path = resolve_artifact_path(md_report_uri)
    if path is None or not path.exists():
        p = Path(md_report_uri)
        if p.exists():
            path = p
        else:
            raise FileNotFoundError(f"无法解析 md_report_uri: {md_report_uri}")
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
    """只保留 MISSING 类型发现；REDUNDANT 不进入修复流程（ADR-004）。"""
    return [f for f in findings if f.type == "MISSING"]


@dataclass
class MakefileRule:
    target: str
    prerequisites: list
    recipe: list
    line_no: int


def parse_makefile(content: str) -> list:
    """解析 Makefile，提取所有规则（target: prerequisites）。"""
    rules = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*[:?+]?=", line) and ":" not in line.split("=", 1)[0]:
            i += 1
            continue
        if not line.startswith("\t") and ":" in line:
            colon_idx = line.index(":")
            if colon_idx + 1 < len(line) and line[colon_idx + 1] == "=":
                i += 1
                continue
            target_part = line[:colon_idx].strip()
            prereq_part = line[colon_idx + 1:].strip()
            while prereq_part.endswith("\\"):
                prereq_part = prereq_part[:-1].rstrip()
                i += 1
                if i < len(lines):
                    prereq_part += " " + lines[i].strip()
            prerequisites = prereq_part.split() if prereq_part else []
            recipe = []
            rule_line = i + 1
            i += 1
            while i < len(lines) and (lines[i].startswith("\t") or lines[i].strip() == ""):
                if lines[i].startswith("\t"):
                    recipe.append(lines[i])
                i += 1
            rules.append(MakefileRule(
                target=target_part,
                prerequisites=prerequisites,
                recipe=recipe,
                line_no=rule_line,
            ))
        else:
            i += 1
    return rules


def detect_declaration_style(content, rules):
    """推断 Makefile 的声明风格。"""
    style = {
        "uses_tab_recipe": any(r.recipe for r in rules),
        "prereq_separator": " ",
        "has_continuation": "\\\\" in content,
        "variable_patterns": re.findall(r"\$\(([A-Za-z_][A-Za-z0-9_]*)\)", content),
    }
    return style


def find_rule_for_target(rules, target):
    for rule in rules:
        targets = rule.target.split()
        if target in targets:
            return rule
    return None