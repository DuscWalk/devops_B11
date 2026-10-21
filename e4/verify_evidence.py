#!/usr/bin/env python3
"""Validate the submitted E4 member records without running their experiments again."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "9765d5794fe43a0c5496be969004d3b84d5b740f"
RUNTIME = ["Makefile", "compose.yaml", ".dockerignore", ".env.example",
           "requirements-dev.in", "requirements-dev.lock", "scripts",
           "services", "fixtures/draft", "setup"]
MEMBERS = [
    ("胡博", "241276007", "hu-bo-20261016",
     "verification/scan-detected/secret-scan.txt", "verification/scan-cleaned/secret-scan.txt"),
    ("孙静怡", "241250112", "sun-jingyi-20261019",
     "verification/scan-detected/secret-scan.txt", "verification/scan-cleaned/secret-scan.txt"),
    ("王硕", "241250110", "241250110-20261021",
     "leak-test/scan-detected.txt", "leak-test/scan-after-cleanup.txt"),
]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def equivalent(left, right):
    p = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", left, right, "--", *RUNTIME])
    require(p.returncode in (0, 1), "Git comparison failed")
    return p.returncode == 0


def verify_submission():
    root = ROOT / "e4/evidence/submission-20261021"
    manifest = read_json(root / "SHA256SUMS.json")
    for relative, digest in manifest.items():
        path = (root / relative).resolve()
        require(path.is_relative_to(root.resolve()), "Submission path outside evidence")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                "Submission hash mismatch: " + relative)
    run = root / "integration-run/work/20261021T115501-607657048Z"
    source = (run / "source-sha.txt").read_text().strip()
    require(equivalent(source, "HEAD"), "Runtime differs from integration run")
    require((run / "source-status.txt").read_bytes() == b"", "Integration source was dirty")
    require(read_json(run / "env.json")["problems"] == [], "Integration doctor failed")
    require("4 passed" in (run / "test.log").read_text(), "Integration tests failed")
    smoke = read_json(run / "smoke.json")
    require(smoke["passed"] is True and smoke["build_exit_code"] == 1,
            "Integration smoke failed")
    require(smoke["build_log"] == (run / "smoke-build.log").read_text(),
            "Integration smoke log mismatch")
    require("未发现问题" in (run / "secret-scan.txt").read_text(), "Integration scan failed")
    require((root / "integration-run/work/submission-20261021-115501-command-exit-code.txt")
            .read_text().strip() == "0", "Integration make all failed")
    baseline = read_json(root / "e3-baseline/summary.json")
    require(baseline["result"] == "PASS" and baseline["checks_passed"] == baseline["checks_total"] == 67,
            "E3 baseline failed")
    peer = read_json(root / "peer-a11/review.json")
    require(peer["direction"] == "B11 -> A11", "Incorrect peer review direction")
    primary = root / "peer-a11/original-rerun"
    require(peer["source_sha"] == (primary / "logs/source-sha.txt").read_text().strip(),
            "Peer source SHA mismatch")
    code = int((primary / "logs/command-exit-code.txt").read_text().strip())
    require(peer["make_all_exit_code"] == code, "Peer exit code mismatch")
    require(peer["result"] == ("PASS" if code == 0 else "NOT_COMPLETED"), "Peer result mismatch")
    require((root / "peer-a11/logs/source-status-before.txt").read_bytes() == b"",
            "Peer checkout was initially dirty")
    for name in ("source-status-after.txt", "source-status-after-scan.txt"):
        status = (root / "peer-a11/logs" / name).read_text().splitlines()
        require(status == ["?? e4/work/20261021T200246+0800/"],
                "Unexpected peer changes beyond generated work evidence")
    for name in ("source-status-before.txt", "source-status-after.txt"):
        status = (primary / "logs" / name).read_text().splitlines()
        require(all(re.fullmatch(r"\?\? e4/work/\d{8}T\d{6}[+-]\d{4}/", line)
                    for line in status), "Unexpected peer changes in original-flow rerun")
    for name in ("repository-scan.txt", "cleaned-scan.txt"):
        require("[RESULT] findings=0" in (root / "peer-a11/logs" / name).read_text(),
                "Peer repository scan failed")
    require("[RESULT] findings=1" in (root / "peer-a11/logs/negative-scan.txt").read_text(),
            "Peer negative scan missing")
    diagnostic = root / "peer-a11/mirror-diagnostic"
    require((diagnostic / "logs/command-exit-code.txt").read_text().strip() == "0",
            "Peer mirror diagnostic failed")
    require("9 passed" in (diagnostic / "run/test.log").read_text(), "Peer diagnostic tests failed")
    require(read_json(diagnostic / "run/smoke.json")["status"] == "PASS",
            "Peer diagnostic smoke failed")
    require("[RESULT] findings=0" in (diagnostic / "run/secret-scan.txt").read_text(),
            "Peer diagnostic scan failed")
    require(peer["mirror_diagnostic"]["result"] == "PASS", "Peer diagnostic summary mismatch")
    return {"integration_source_sha": source, "integration_make_all": "PASS",
            "e3_local_baseline": "67/67", "supplementary_files_verified": len(manifest)}, peer


def audit():
    rows, toolchains, host_tools, hashes = [], [], [], {}
    for name, student, directory, negative, cleaned in MEMBERS:
        root = ROOT / "e4/evidence" / directory
        full = root / "full-run"
        source = (full / "source-sha.txt").read_text().strip()
        require(bool(re.fullmatch(r"[a-f0-9]{40}", source)), name + ": invalid SHA")
        git("cat-file", "-e", source + "^{commit}")
        require((full / "source-status.txt").read_bytes() == b"", name + ": dirty source")
        env, smoke, image = [read_json(full / f) for f in ("env.json", "smoke.json", "image.json")]
        require(env["problems"] == [], name + ": doctor failed")
        require(env["git"]["user.name"] == student, name + ": wrong identity")
        require(image["image"] == "e4-draft:" + student, name + ": wrong image")
        require("4 passed" in (full / "test.log").read_text(), name + ": tests missing")
        require(smoke["passed"] is True and smoke["build_exit_code"] == 1,
                name + ": unexpected smoke result")
        require("make: not found" in smoke["make_error_line"], name + ": missing expected failure")
        require(bool(smoke["docker_server"]), name + ": Docker server missing")
        require(smoke["build_log"] == (full / "smoke-build.log").read_text(), name + ": log mismatch")
        for path in (full / "secret-scan.txt", root / cleaned):
            text = path.read_text()
            require("未发现问题" in text and "FOUND  " not in text, name + ": scan failed")
        require("FOUND  " in (root / negative).read_text(), name + ": negative scan missing")
        require("Built" in (full / "build.log").read_text(), name + ": build log incomplete")
        require(equivalent(BASELINE, source), name + ": runtime differs from baseline")
        manifest = root / "SHA256SUMS.json"
        checked = 0
        if manifest.exists():
            for relative, digest in read_json(manifest).items():
                path = (root / relative).resolve()
                require(path.is_relative_to(root.resolve()), "Manifest path outside evidence")
                require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                        name + ": hash mismatch: " + relative)
                checked += 1
        for path in sorted(root.rglob("*")):
            if path.is_file():
                hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        toolchain = (full / "toolchain.lock").read_bytes()
        toolchains.append(toolchain)
        host_tools.append(env["tools"])
        rows.append({"name": name, "student_id": student, "source_sha": source,
                     "evidence_directory": root.relative_to(ROOT).as_posix(),
                     "run_time_utc": env["time"], "git_identity": env["git"],
                     "source_clean": True, "runtime_matches_baseline": True,
                     "tests_passed": 4, "smoke_passed": True, "complete_log_matches": True,
                     "scan_passed": True, "negative_scan_detected": True, "cleaned_scan_passed": True,
                     "existing_manifest_files_verified": checked, "image_id": image["id"],
                     "toolchain_sha256": hashlib.sha256(toolchain).hexdigest()})
    require(len(set(toolchains)) == 1, "Member toolchains differ")
    require(all(tools == host_tools[0] for tools in host_tools), "Host tool versions differ")
    require(equivalent(BASELINE, "HEAD"), "Current runtime differs from tested baseline")
    submission, peer = verify_submission()
    return {"result": "PASS", "baseline_sha": BASELINE, "members": rows,
            "all_toolchains_byte_identical": True, "all_host_tools_equal": True,
            "all_member_source_shas_identical": len({r["source_sha"] for r in rows}) == 1,
            "same_sha_pair": ["241276007", "241250112"],
            "current_runtime_matches_baseline": True,
            "comparison_scope": "Archived records; shared host/cache; no new member execution or human sign-off",
            "submission_validation": submission,
            "cross_group_reproduction": {"b11_reviews_a11": peer,
                                         "a11_reviews_b11": "NOT_PROVIDED"},
            "evidence_sha256": hashes}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    try:
        result = audit()
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        ap.exit(1, "E4 evidence verification FAILED: " + str(exc) + "\n")
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print("PASS: 3 member records; tests 4/4 each; smoke/scan/negative scans; matching toolchains")
    print("Source SHAs differ; runtime files match. Integration make all PASS; E3 local baseline 67/67.")
    print("B11 -> A11 original configuration:", result["cross_group_reproduction"]["b11_reviews_a11"]["result"],
          "; mirror diagnostic: PASS; A11 -> B11: NOT_PROVIDED.")
    print("SHA256 recorded for", len(result["evidence_sha256"]), "evidence files")


if __name__ == "__main__":
    main()
