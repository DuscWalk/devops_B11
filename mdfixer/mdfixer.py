undefined#!/usr/bin/env python3
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
import sys
from datetime import datetime
from pathlib import Path

from mdfixer_core import (
    SCHEMA_VERSION,
    BuildSpec,
    CandidateResult,
    Finding,
    MakefileRule,
    RepairInput,
    RepairResult,
    Repository,
    detect_declaration_style,
    filter_missing,
    generate_patch_for_missing,
    load_md_report,
    make_unified_diff,
    parse_makefile,
    parse_makefile_uri,
    verify_candidate,
)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_summary(total: int, accepted: int, fixed: int) -> dict:
    """构造 REPAIR 结果的 summary 字段。"""
    return {
        "candidates_total": total,
        "candidates_accepted": accepted,
        "candidates_rejected": total - accepted,
        "missing_fixed": fixed,
        "recheck_missing_remaining": total - fixed,
    }


def run_repair(rep_input: RepairInput, out_dir: Path) -> RepairResult:
    """执行 REPAIR 任务，返回 RepairResult。"""
    result = RepairResult()

    # 1. 读取 MD 报告并提取 MISSING
    try:
        findings = load_md_report(rep_input.md_report_uri)
    except Exception as e:
        result.error = {
            "code": "ANALYSIS_5001",
            "message": "读取 MD 报告失败",
            "detail": str(e),
        }
        return result

    missing_findings = filter_missing(findings)
    if not missing_findings:
        result.summary = build_summary(total=0, accepted=0, fixed=0)
        return result

    # 2. 解析 Makefile
    makefile_info = parse_makefile_uri(rep_input.makefile_uri)
    if makefile_info is None:
        result.error = {
            "code": "VALIDATION_4001",
            "message": "makefile_uri 格式不正确",
            "detail": f"期望 repo://<sha>/<path>，实际: {rep_input.makefile_uri}",
        }
        return result

    # 定位 Makefile：优先从仓库检出，否则按 makefile_uri 的 path 在工作目录查找
    makefile_path = out_dir / "workspace" / makefile_info[1]
    if not makefile_path.exists():
        # E2 降级：直接用 uri 的路径
        makefile_path = Path(makefile_info[1])
    if not makefile_path.exists():
        result.error = {
            "code": "ENV_3002",
            "message": "找不到 Makefile",
            "detail": f"makefile_uri={rep_input.makefile_uri}",
        }
        return result

    original_content = makefile_path.read_text(encoding="utf-8")
    rules = parse_makefile(original_content)
    style = detect_declaration_style(original_content, rules)

    # 3. 生成候选补丁并逐一验证
    candidates: list[CandidateResult] = []
    current_patched = original_content
    fixed_count = 0

    for finding in missing_findings:
        gen = generate_patch_for_missing(current_patched, rules, finding)
        if gen is None:
            candidates.append(CandidateResult(
                accepted=False,
                reason=f"无法为 target={finding.target} 生成补丁（目标不在 Makefile 中或已声明）",
            ))
            continue

        patched_content, desc = gen
        diff = make_unified_diff(original_content, patched_content, makefile_info[1])

        cand = verify_candidate(
            patch=patched_content,
            makefile_path=makefile_path,
            build_cmd=rep_input.build.command,
            verify_cmd=rep_input.verify_command,
            workdir=makefile_path.parent,
        )
        cand.patch = diff
        cand.description = desc
        if cand.accepted:
            current_patched = patched_content
            fixed_count += 1
        candidates.append(cand)

    accepted = [c for c in candidates if c.accepted]
    rejected = [c for c in candidates if not c.accepted]

    # 4. 写出产物
    out_dir.mkdir(parents=True, exist_ok=True)
    job_id = f"job-repair-{int(datetime.now().timestamp())}"

    # PATCH 产物
    final_patch = make_unified_diff(original_content, current_patched, makefile_info[1])
    patch_bytes = final_patch.encode("utf-8")
    patch_sha = sha256_hex(patch_bytes)
    patch_path = out_dir / "fix.patch"
    patch_path.write_bytes(patch_bytes)

    patch_uri = f"artifact://b11/{job_id}/fix.patch"
    result.patch_uri = patch_uri
    result.patch_sha256 = patch_sha

    # STYLE_REPORT 产物
    style_report = {
        "declaration_style": style,
        "targets_found": [r.target for r in rules],
        "missing_fixed": fixed_count,
        "missing_total": len(missing_findings),
        "rejected_reasons": [{"target": c.description, "reason": c.reason} for c in rejected],
    }
    style_path = out_dir / "declaration_style.json"
    style_path.write_text(json.dumps(style_report, ensure_ascii=False, indent=2), encoding="utf-8")

    # TEST_RESULT 产物
    test_result = {
        "candidates_total": len(candidates),
        "candidates_accepted": len(accepted),
        "candidates_rejected": len(rejected),
        "accepted_details": [
            {"description": c.description, "build_exit_code": c.build_exit_code, "verify_exit_code": c.verify_exit_code}
            for c in accepted
        ],
        "rejected_details": [
            {"description": c.description, "reason": c.reason}
            for c in rejected
        ],
    }
    test_path = out_dir / "test_result.json"
    test_path.write_text(json.dumps(test_result, ensure_ascii=False, indent=2), encoding="utf-8")

    result.artifacts = [
        {
            "artifact_id": f"{job_id}-patch",
            "type": "PATCH",
            "uri": patch_uri,
            "media_type": "text/x-diff",
            "producer_job_id": job_id,
            "commit": rep_input.repository.commit,
            "sha256": patch_sha,
        },
        {
            "artifact_id": f"{job_id}-style",
            "type": "STYLE_REPORT",
            "uri": f"artifact://b11/{job_id}/declaration_style.json",
            "media_type": "application/json",
            "producer_job_id": job_id,
            "commit": rep_input.repository.commit,
        },
        {
            "artifact_id": f"{job_id}-test",
            "type": "TEST_RESULT",
            "uri": f"artifact://b11/{job_id}/test_result.json",
            "media_type": "application/json",
            "producer_job_id": job_id,
            "commit": rep_input.repository.commit,
        },
    ]
    result.summary = build_summary(
        total=len(candidates),
        accepted=len(accepted),
        fixed=fixed_count,
    )
    return result


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def load_request(path: str) -> RepairInput:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    inp = data["input"]
    return RepairInput(
        repository=Repository(url=inp["repository"]["url"], commit=inp["repository"]["commit"]),
        md_report_uri=inp["md_report_uri"],
        makefile_uri=inp["makefile_uri"],
        image=inp["image"],
        build=BuildSpec(command=inp["build"]["command"]),
        verify_command=inp["verify_command"],
        max_iterations=inp.get("max_iterations", 1),
        timeout_seconds=inp.get("timeout_seconds", 1200),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="MDFixer — 修复缺失依赖（MISSING）")
    parser.add_argument("--request", required=True, help="REPAIR 请求 JSON 文件路径")
    parser.add_argument("--out-dir", default="out", help="输出目录")
    args = parser.parse_args()

    rep_input = load_request(args.request)
    out_dir = Path(args.out_dir)
    result = run_repair(rep_input, out_dir)

    output = {
        "schema_version": SCHEMA_VERSION,
        "job_type": "REPAIR",
        "status": "SUCCEEDED" if result.error is None else "FAILED",
        "output": {
            "patch_uri": result.patch_uri,
            "patch_sha256": result.patch_sha256,
            "artifacts": result.artifacts,
            "summary": result.summary,
        },
        "error": result.error,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if result.error is None else 1


if __name__ == "__main__":
    sys.exit(main())
