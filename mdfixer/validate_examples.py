#!/usr/bin/env python3
"""契约验证脚本 — 校验 MDFixer 的输入/输出是否符合 A11-B11 E2 契约。

本脚本不依赖 jsonschema 库，使用内置 dict 校验逻辑，确保在 CI 环境下零依赖运行。

校验对象：
  1. REPAIR 请求（RepairInput）字段完整性与类型
  2. REPAIR 响应（RepairResult）字段完整性与类型
  3. 产物（artifacts）结构：PATCH / STYLE_REPORT / TEST_RESULT
  4. artifact:// URI 格式
  5. repo:// URI 格式

用法：
    python validate_examples.py --request examples/repair_request.json
    python validate_examples.py --response out/response.json
    python validate_examples.py --request examples/repair_request.json --response out/response.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# A11 契约版本（与 task.schema.json 中 schema_version 对齐）
EXPECTED_SCHEMA_VERSION = "1.1.0"

# artifact://<group>/<job_id>/<name>
ARTIFACT_URI_RE = re.compile(r"^artifact://([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)/([A-Za-z0-9._/-]+)$")
# repo://<sha40>/<path>
REPO_URI_RE = re.compile(r"^repo://([0-9a-f]{40})/(.+)$")


class ValidationError(Exception):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValidationError(msg)


def is_nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and len(v) > 0


# ---------------------------------------------------------------------------
# RepairInput 校验
# ---------------------------------------------------------------------------

REQUIRED_REPAIR_INPUT_FIELDS = {
    "repository": dict,
    "md_report_uri": str,
    "makefile_uri": str,
    "image": str,
    "build": dict,
    "verify_command": str,
}

OPTIONAL_REPAIR_INPUT_FIELDS = {
    "max_iterations": int,
    "timeout_seconds": int,
}


def validate_repair_input(inp: dict) -> list[str]:
    errors: list[str] = []

    for field, typ in REQUIRED_REPAIR_INPUT_FIELDS.items():
        if field not in inp:
            errors.append(f"RepairInput 缺少必填字段: {field}")
        elif not isinstance(inp[field], typ):
            errors.append(f"RepairInput.{field} 类型错误: 期望 {typ.__name__}, 实际 {type(inp[field]).__name__}")

    for field, typ in OPTIONAL_REPAIR_INPUT_FIELDS.items():
        if field in inp and not isinstance(inp[field], typ):
            errors.append(f"RepairInput.{field} 类型错误: 期望 {typ.__name__}, 实际 {type(inp[field]).__name__}")

    # repository 子字段
    repo = inp.get("repository")
    if isinstance(repo, dict):
        for f in ("url", "commit"):
            if f not in repo:
                errors.append(f"RepairInput.repository 缺少字段: {f}")
            elif not is_nonempty_str(repo[f]):
                errors.append(f"RepairInput.repository.{f} 必须是非空字符串")

    # build 子字段
    build = inp.get("build")
    if isinstance(build, dict):
        if "command" not in build:
            errors.append("RepairInput.build 缺少字段: command")
        elif not is_nonempty_str(build["command"]):
            errors.append("RepairInput.build.command 必须是非空字符串")

    # URI 格式
    md_uri = inp.get("md_report_uri", "")
    if is_nonempty_str(md_uri) and not ARTIFACT_URI_RE.match(md_uri):
        errors.append(f"md_report_uri 格式不符合 artifact:// 协议: {md_uri}")

    mk_uri = inp.get("makefile_uri", "")
    if is_nonempty_str(mk_uri) and not REPO_URI_RE.match(mk_uri):
        errors.append(f"makefile_uri 格式不符合 repo:// 协议: {mk_uri}")

    return errors


# ---------------------------------------------------------------------------
# RepairResult 校验
# ---------------------------------------------------------------------------

REQUIRED_OUTPUT_FIELDS = {
    "patch_uri": str,
    "patch_sha256": str,
    "artifacts": list,
    "summary": dict,
}

REQUIRED_ARTIFACT_FIELDS = {
    "artifact_id": str,
    "type": str,
    "uri": str,
    "media_type": str,
    "producer_job_id": str,
    "commit": str,
}

VALID_ARTIFACT_TYPES = {"PATCH", "STYLE_REPORT", "TEST_RESULT"}

REQUIRED_SUMMARY_FIELDS = {
    "candidates_total": int,
    "candidates_accepted": int,
    "candidates_rejected": int,
    "missing_fixed": int,
    "recheck_missing_remaining": int,
}


def validate_repair_result(resp: dict) -> list[str]:
    errors: list[str] = []

    # 顶层字段
    if resp.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append(f"schema_version 不匹配: 期望 {EXPECTED_SCHEMA_VERSION}, 实际 {resp.get('schema_version')}")

    if resp.get("job_type") != "REPAIR":
        errors.append(f"job_type 必须为 REPAIR, 实际 {resp.get('job_type')}")

    status = resp.get("status")
    if status not in ("SUCCEEDED", "FAILED"):
        errors.append(f"status 必须为 SUCCEEDED 或 FAILED, 实际 {status}")

    output = resp.get("output")
    if status == "SUCCEEDED":
        if not isinstance(output, dict):
            errors.append("SUCCEEDED 状态下 output 必须是对象")
            return errors

        for field, typ in REQUIRED_OUTPUT_FIELDS.items():
            if field not in output:
                errors.append(f"output 缺少字段: {field}")
            elif not isinstance(output[field], typ):
                errors.append(f"output.{field} 类型错误: 期望 {typ.__name__}")

        # patch_uri 格式
        patch_uri = output.get("patch_uri", "")
        if is_nonempty_str(patch_uri) and not ARTIFACT_URI_RE.match(patch_uri):
            errors.append(f"patch_uri 格式不符合 artifact:// 协议: {patch_uri}")

        # patch_sha256 应为 64 位十六进制
        sha = output.get("patch_sha256", "")
        if is_nonempty_str(sha) and not re.match(r"^[0-9a-f]{64}$", sha):
            errors.append(f"patch_sha256 应为 64 位十六进制字符串: {sha}")

        # artifacts 校验
        artifacts = output.get("artifacts", [])
        if isinstance(artifacts, list):
            seen_types = set()
            for idx, art in enumerate(artifacts):
                if not isinstance(art, dict):
                    errors.append(f"artifacts[{idx}] 必须是对象")
                    continue
                for f, typ in REQUIRED_ARTIFACT_FIELDS.items():
                    if f not in art:
                        errors.append(f"artifacts[{idx}] 缺少字段: {f}")
                    elif not isinstance(art[f], typ):
                        errors.append(f"artifacts[{idx}].{f} 类型错误")
                atype = art.get("type")
                if atype and atype not in VALID_ARTIFACT_TYPES:
                    errors.append(f"artifacts[{idx}].type 非法: {atype}")
                if atype:
                    seen_types.add(atype)
                uri = art.get("uri", "")
                if is_nonempty_str(uri) and not ARTIFACT_URI_RE.match(uri):
                    errors.append(f"artifacts[{idx}].uri 格式错误: {uri}")

            # PATCH 产物必须存在
            if "PATCH" not in seen_types:
                errors.append("artifacts 中必须包含 type=PATCH 的产物")

        # summary 校验
        summary = output.get("summary", {})
        if isinstance(summary, dict):
            for field, typ in REQUIRED_SUMMARY_FIELDS.items():
                if field not in summary:
                    errors.append(f"summary 缺少字段: {field}")
                elif not isinstance(summary[field], typ):
                    errors.append(f"summary.{field} 类型错误: 期望 {typ.__name__}")

    elif status == "FAILED":
        err = resp.get("error")
        if not isinstance(err, dict):
            errors.append("FAILED 状态下必须包含 error 对象")
        elif "code" not in err or "message" not in err:
            errors.append("error 对象必须包含 code 和 message 字段")

    return errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] 文件不存在: {path}", file=sys.stderr)
        sys.exit(2)
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 MDFixer 输入/输出是否符合 A11-B11 E2 契约")
    parser.add_argument("--request", help="REPAIR 请求 JSON 文件")
    parser.add_argument("--response", help="REPAIR 响应 JSON 文件")
    args = parser.parse_args()

    if not args.request and not args.response:
        parser.print_help()
        return 1

    all_errors: list[str] = []

    if args.request:
        data = load_json(args.request)
        # 请求可能是裸 RepairInput，也可能包在 {"input": {...}} 中
        inp = data.get("input", data) if isinstance(data, dict) else data
        if not isinstance(inp, dict):
            all_errors.append("请求文件根必须是对象")
        else:
            errs = validate_repair_input(inp)
            if errs:
                all_errors.extend([f"[Request] {e}" for e in errs])
            else:
                print(f"[OK] 请求契约校验通过: {args.request}")

    if args.response:
        data = load_json(args.response)
        if not isinstance(data, dict):
            all_errors.append("响应文件根必须是对象")
        else:
            errs = validate_repair_result(data)
            if errs:
                all_errors.extend([f"[Response] {e}" for e in errs])
            else:
                print(f"[OK] 响应契约校验通过: {args.response}")

    if all_errors:
        print("\n[FAIL] 契约校验失败:", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\n[PASS] 所有契约校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
