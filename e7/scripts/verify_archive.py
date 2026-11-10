"""Verify saved E7 evidence offline; never rerun Docker or rewrite original logs."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def located(name):
    path = (ROOT / name).resolve()
    require(path.is_relative_to(ROOT), "Path escapes repository")
    return path


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_gate(artifact, expected, tests, oracle):
    gate = artifact / "gate"
    result = read(gate / "gate-result.json")
    require(result["passed"] is (expected == "success"), "Gate conclusion mismatch")
    rows = result["cases"]
    with (gate / "results.csv").open(newline="") as stream:
        actual = list(csv.DictReader(stream))
    fields = ("case", "passed", "exit_code", "workflow_status", "trace_id", "error")
    require(actual == [{key: str(row.get(key, "")) for key in fields} for row in rows],
            "CSV and JSON differ")
    require(result["intentional_failure"] is False, "Unexpected injected oracle")
    unit_log = (gate / "unit-tests/stdout.log").read_text()
    if expected == "failure":
        require([row["case"] for row in rows] == ["unit-tests", "runner"], "Unexpected failed cases")
        require(rows[0]["exit_code"] == 1 and rows[0]["passed"] is False, "Unit failure missing")
        require("assert 0 == 1" in unit_log and "1 failed, 25 passed" in unit_log,
                "Expected wrong-version oracle did not fail")
        return {"passed": True, "expected_ci": "failure", "unit_tests": "1 failed, 25 passed"}
    require([row["case"] for row in rows] == ["unit-tests", "success", "wrong-output",
            "invalid-candidate", "build-failed", "runtime-timeout"], "Missing or duplicate gate case")
    require(all(row["passed"] is True for row in rows), "A case failed")
    require(rows[0]["exit_code"] == 0 and f"{tests} passed" in unit_log, "Unit tests differ")
    for row in rows[1:]:
        case = gate / row["case"]
        name = row["case"]
        report = read(case / "stdout.log")
        oracle.evaluate(name, row["exit_code"], report)
        require(row["workflow_status"] == report["status"], "Tool status mismatch")
        command = read(case / "command.json")
        require(command[command.index("--network") + 1] == "bridge", "Service network differs")
        require((case / "stderr.log").is_file(), "Missing stderr")
        evidence = case / "evidence"
        if name == "invalid-candidate":
            oracle.check_artifacts(name, evidence, report)
            require(not (evidence / "iter-01").exists(), "Invalid candidate started a build")
            continue
        require(read(evidence / "result.json") == report, "CLI and saved report differ")
        for path, digest in report["input_sha256"].items():
            source = (evidence / "project" / path).resolve()
            require(source.is_relative_to((evidence / "project").resolve()), "Input path escapes")
            require(hashlib.sha256(source.read_bytes()).hexdigest() == digest, "Input hash differs")
        require(hashlib.sha256((evidence / "iter-02/Dockerfile").read_bytes()).hexdigest()
                == report["candidate_sha256"], "Candidate hash differs")
        if name == "runtime-timeout":
            # The course checker calls Docker here. Validate its saved observation instead.
            baseline = (evidence / "iter-01/build-stderr.log").read_text()
            require(re.search(r"/bin/sh:.*\bmake: not found", baseline), "Baseline failure missing")
            cid = (evidence / "verify-container-id.txt").read_text().strip()
            require(re.fullmatch(r"[0-9a-f]{64}", cid), "Invalid runtime container ID")
            cleanup = evidence / "cleanup-check"
            require(read(cleanup / "command.json") == ["docker", "container", "inspect", cid],
                    "Cleanup command differs")
            require("no such" in (cleanup / "stderr.log").read_text().lower(), "Removal not observed")
            fault = read(case / "fault-injection.json")
            require(fault["delay_seconds"] == 10 and fault["verify_timeout_seconds"] == 1,
                    "Timeout injection differs")
            require(fault["source_files_changed"] == [], "Unexpected source mutation")
            delayed = 'CMD ["sh", "-c", "sleep 10; exec ./hello"]'
            require(delayed in (case / "fixture/Dockerfile.broken").read_text()
                    and delayed in (case / "candidate.Dockerfile").read_text(), "Delayed CMD differs")
        else:
            oracle.check_artifacts(name, evidence, report)
        if name in ("success", "wrong-output"):
            verify = report["verification"]["command"]
            require(verify[verify.index("--network") + 1] == "none", "Program has network")
            require((evidence / "verify.log").read_bytes() == b"hello E3\n", "Output bytes differ")
    return {"passed": True, "expected_ci": "success", "unit_tests": tests, "gate_cases": 6}


def main():
    manifest = read(ROOT / "e7/evidence-manifest.json")
    for item in manifest["files"]:
        require(hashlib.sha256(located(item["path"]).read_bytes()).hexdigest() == item["sha256"],
                f"Hash differs: {item['path']}")
    oracle = load_module("course_e7_gate", ROOT / "e5/labs/B-draft/scripts/run_e7_b_gate.py")
    snapshot = located(manifest["verification_snapshot"])
    protection = read(snapshot / "main-protection.json")
    required = protection["required_status_checks"]
    require(required["strict"] is True and protection["enforce_admins"]["enabled"] is True,
            "Strict/admin protection disabled")
    require({"context": "e7-b-quality-gate", "app_id": 15368} in required["checks"],
            "Required check/App differs")
    require(protection["required_pull_request_reviews"]["required_approving_review_count"] == 0,
            "Review count differs")
    current = read(snapshot / "main-ref.json")["object"]["sha"]
    checks = read(snapshot / "main-check-runs.json")["check_runs"]
    require(any(c["head_sha"] == current and c["name"] == "e7-b-quality-gate"
                and c["conclusion"] == "success" and c["app"]["id"] == 15368 for c in checks),
            "Current main check missing")
    verified = []
    for run in manifest["runs"]:
        metadata = read(snapshot / f"run-{run['id']}.json")
        artifact = located(run["artifact"])
        checked_out = (artifact / "commit.txt").read_text().strip()
        require(metadata["conclusion"] == run["conclusion"], "Run conclusion differs")
        require(metadata["head_sha"] == run["head_sha"], "Head SHA differs")
        if metadata["event"] == "pull_request":
            commit = read(snapshot / f"commit-{checked_out}.json")
            require(commit["sha"] == checked_out and
                    run["head_sha"] in [p["sha"] for p in commit["parents"]], "PR merge SHA mismatch")
        else:
            require(checked_out == run["head_sha"], "Push commit mismatch")
        jobs = read(snapshot / f"jobs-{run['id']}.json")["jobs"]
        require(any(j["name"] == "e7-b-quality-gate" and j["conclusion"] == run["conclusion"]
                    for j in jobs), "Required job conclusion differs")
        outcome = verify_gate(artifact, run["conclusion"], run["unit_tests"], oracle)
        verified.append({"id": run["id"], "head_sha": run["head_sha"],
                         "checked_out_sha": checked_out, **outcome})
    historical = ROOT / "e5/evidence/hu-bo-20261029/ci"
    rejected = read(historical / "rejection-pr2/PR.json")
    require(rejected["state"] == "OPEN" and rejected["mergeStateStatus"] == "BLOCKED",
            "Rejected PR state missing")
    refusal = (historical / "rejection-pr2/merge-rejection.log").read_text()
    require("base branch policy prohibits the merge" in refusal
            and "MERGE_ATTEMPT_EXIT_CODE=1" in refusal, "Merge refusal missing")
    before = read(historical / "recovery-pr2/PR-before-merge.json")
    merged = read(historical / "recovery-pr2/PR-merged.json")
    require(before["mergeStateStatus"] == "CLEAN" and merged["state"] == "MERGED", "Recovery missing")
    require(rejected["url"] == before["url"] == merged["url"], "Not the same PR")
    live = read(snapshot / "pr-2.json")
    require(live["merged"] is True and live["merge_commit_sha"] == merged["mergeCommit"]["oid"]
            and live["merged_at"] == merged["mergedAt"], "Live/historical merge records differ")
    print(json.dumps({"passed": True, "scope": "Saved artifacts and API snapshot; no Docker rerun",
                      "hashes_verified": len(manifest["files"]), "runs": verified,
                      "main_protection": "passed", "same_pr_rejection_and_recovery": 2}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}))
        raise SystemExit(1)
