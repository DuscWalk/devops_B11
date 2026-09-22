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
import json
import sys
from pathlib import Path

from mdfixer_core import (
    SCHEMA_VERSION,
    BuildSpec,
    RepairInput,
    RepairResult,
    Repository,
)
from mdfixer_runner import run_repair


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
