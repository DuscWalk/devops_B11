from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from mdfixer_core import (
    CandidateResult,
    RepairInput,
    RepairResult,
    filter_missing,
    load_md_report,
    parse_makefile_uri,
)
from mdfixer_engine import detect_declaration_style, detect_rule_style, parse_makefile
from mdfixer_patch import generate_patch_for_missing, make_unified_diff
from mdfixer_verify import verify_candidate


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_summary(total: int, accepted: int, fixed: int) -> dict:
    return {
        "candidates_total": total,
        "candidates_accepted": accepted,
        "candidates_rejected": total - accepted,
        "missing_fixed": fixed,
        "recheck_missing_remaining": total - fixed,
    }


def run_repair(rep_input, out_dir, *, workspace, artifact_root, job_id=None):
    result = RepairResult()
    job_id = job_id or "job-repair-" + uuid.uuid4().hex
    try:
        workspace = Path(workspace).resolve(strict=True)
        info = parse_makefile_uri(rep_input.makefile_uri)
        if not info or info[0] != rep_input.repository.commit:
            raise ValueError("Makefile URI commit differs from requested repository commit")
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=workspace, text=True
        ).strip()
        if head != rep_input.repository.commit:
            raise ValueError("workspace HEAD differs from requested repository commit")
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=workspace,
            text=True,
        )
        if dirty:
            raise ValueError("workspace tracked files must be clean")
        makefile = workspace.joinpath(info[1]).resolve(strict=True)
        if not makefile.is_relative_to(workspace):
            raise ValueError("Makefile escapes workspace")
        findings = load_md_report(rep_input.md_report_uri, artifact_root)
        if any(f.commit != rep_input.repository.commit for f in findings):
            raise ValueError("report commit differs from source commit")
        missing = filter_missing(findings)
        if any(f.location.get("file") != info[1] for f in missing):
            raise ValueError("finding location differs from requested Makefile")
        original = makefile.read_text(encoding="utf-8")
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        result.error = {
            "code": "VALIDATION_4001",
            "message": "REPAIR input/workspace validation failed",
            "detail": str(exc),
        }
        return result

    rules, variables = parse_makefile(original)
    style = detect_declaration_style(original, rules)
    current = original
    candidates: list[CandidateResult] = []
    fixed_count = 0
    for finding in missing:
        generated = generate_patch_for_missing(current, rules, variables, finding)
        if generated is None:
            candidates.append(
                CandidateResult(
                    accepted=False,
                    reason="unsupported, ambiguous or already declared rule",
                    description=finding.target + ": " + finding.dependency,
                )
            )
            continue
        patched, description = generated
        candidate = verify_candidate(
            patched,
            makefile,
            rep_input.build.command,
            rep_input.verify_command,
            workspace,
            timeout=rep_input.timeout_seconds,
        )
        candidate.patch = make_unified_diff(current, patched, info[1])
        candidate.description = description
        if candidate.accepted:
            current = patched
            fixed_count += 1
        candidates.append(candidate)

    accepted = sum(c.accepted for c in candidates)
    rejected = [c for c in candidates if not c.accepted]
    patch = make_unified_diff(original, current, info[1])
    patch_bytes = patch.encode("utf-8")
    patch_sha = sha256_hex(patch_bytes)

    style_report = {
        "declaration_style": style,
        "targets_found": [r.target for r in rules],
        "rule_styles": [
            {"target": r.target, "style": detect_rule_style(r, variables)}
            for r in rules
        ],
        "variables": [
            {"name": v.name, "value": v.value, "line": v.line_no}
            for v in variables
        ],
        "scope": "simple explicit Makefile rules",
        "missing_fixed": fixed_count,
        "missing_total": len(missing),
        "rejected_reasons": [
            {"target": c.description, "reason": c.reason} for c in rejected
        ],
        "summary": build_summary(
            total=len(candidates),
            accepted=accepted,
            fixed=fixed_count,
        ),
    }

    test_result = {
        "candidates_total": len(candidates),
        "candidates_accepted": accepted,
        "candidates_rejected": len(rejected),
        "accepted_details": [
            {
                "description": c.description,
                "build_exit_code": c.build_exit_code,
                "verify_exit_code": c.verify_exit_code,
            }
            for c in candidates
            if c.accepted
        ],
        "rejected_details": [
            {"description": c.description, "reason": c.reason}
            for c in rejected
        ],
        "recheck": {
            "status": "NOT_RUN",
            "reason": "BuildChecker/EChecker integration belongs to E3",
        },
        "command_timeout_seconds": rep_input.timeout_seconds,
        "max_iterations_note": "one candidate per finding; iterative search not implemented",
    }

    folder = Path(out_dir) / "b11" / job_id
    folder.mkdir(parents=True, exist_ok=False)
    for name, kind, media, data in [
        ("fix.patch", "PATCH", "text/x-diff", patch_bytes),
        (
            "declaration_style.json",
            "STYLE_REPORT",
            "application/json",
            (json.dumps(style_report, ensure_ascii=False, indent=2) + "\n").encode(),
        ),
        (
            "test_result.json",
            "TEST_RESULT",
            "application/json",
            (json.dumps(test_result, ensure_ascii=False, indent=2) + "\n").encode(),
        ),
    ]:
        (folder / name).write_bytes(data)
        result.artifacts.append(
            {
                "artifact_id": job_id + "-" + kind.lower(),
                "type": kind,
                "uri": "artifact://b11/" + job_id + "/" + name,
                "media_type": media,
                "producer_job_id": job_id,
                "commit": rep_input.repository.commit,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    result.patch_uri = result.artifacts[0]["uri"]
    result.patch_sha256 = result.artifacts[0]["sha256"]
    result.summary = builld_summary(
        total= len(candidates),
        accepted=accepted,
        fixed=fixed_count,
    )
    result.patch_bytes = patch.encode("utf-8")
    result.patch_sha256 = hashlib.sha256(patch.encode("utf-8")).hexdigest()
    return result
