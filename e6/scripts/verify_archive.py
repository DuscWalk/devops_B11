"""Verify the selected historical artifacts without running Docker."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / "e6/source-manifest.json").read_text())
    package = ROOT / manifest["course_archive"]
    require(sha(package) == manifest["course_archive_sha256"], "Course ZIP hash mismatch")
    with zipfile.ZipFile(package) as archive:
        for item in manifest["course_files"]:
            data = (ROOT / item["path"]).read_bytes()
            require(data == archive.read(item["package_path"]), item["path"])
            require(hashlib.sha256(data).hexdigest() == item["sha256"], item["path"])
    custom = manifest["custom_test"]
    require(sha(ROOT / custom["path"]) == custom["sha256"], "Custom test changed")
    evidence = ROOT / manifest["evidence"]["destination"]
    checksums = json.loads((ROOT / manifest["evidence"]["manifest"]).read_text())
    for name, expected in checksums.items():
        path = (evidence / name).resolve()
        require(path.is_relative_to(evidence.resolve()), "Evidence path escapes archive")
        require(sha(path) == expected, f"Evidence hash mismatch: {name}")
    require(len(checksums) == manifest["evidence"]["files"], "Evidence count mismatch")
    actual = {p.relative_to(evidence).as_posix() for p in evidence.rglob("*") if p.is_file()}
    require(actual == set(checksums) | {"SHA256SUMS.json"}, "Evidence manifest coverage differs")
    spec = importlib.util.spec_from_file_location(
        "course_verify", ROOT / "e6/labs/B-draft/scripts/verify_e6_b_evidence.py"
    )
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    run = evidence / "e6-hubo-20261029-mirror/evidence"
    result = verifier.verify(run)
    report = json.loads((run / "result.json").read_text())
    require((run / "verify.log").read_bytes() == b"hello E3\n", "Output is not exact")
    command = report["verification"]["command"]
    require(command[command.index("--network") + 1] == "none", "Verification network enabled")
    require(sha(evidence / "candidate/Dockerfile") == result["candidate_sha256"], "Selected candidate differs")
    gate_root = evidence / "e7-hubo-20261029-customtest/gate"
    gate = json.loads((gate_root / "gate-result.json").read_text())
    require(gate["passed"] is True and all(c["passed"] for c in gate["cases"]), "Gate failed")
    require({c["case"] for c in gate["cases"]} == {
        "unit-tests", "success", "wrong-output", "invalid-candidate", "build-failed", "runtime-timeout"
    }, "Gate cases differ")
    verifier.verify(gate_root / "success/evidence")
    log = evidence / "build-hubo-20261029-customtest/unit-tests.log"
    require("25 passed" in log.read_text(), "Custom test build result missing")
    slides = json.loads((ROOT / "docs/e6/sources.json").read_text())
    require(sha(ROOT / "docs/e6" / slides["ppt"]["file"]) == slides["ppt"]["sha256"], "PPT hash mismatch")
    reproduction = json.loads((ROOT / "e6/reproduction.json").read_text())
    fresh_root = ROOT / reproduction["archive"]
    fresh_hashes = json.loads((fresh_root / "SHA256SUMS.json").read_text())
    for name, expected in fresh_hashes.items():
        path = (fresh_root / name).resolve()
        require(path.is_relative_to(fresh_root.resolve()), "Reproduction path escapes archive")
        require(sha(path) == expected, f"Reproduction hash mismatch: {name}")
    fresh_files = {p.relative_to(fresh_root).as_posix() for p in fresh_root.rglob("*") if p.is_file()}
    require(fresh_files == set(fresh_hashes) | {"SHA256SUMS.json"}, "Reproduction manifest coverage differs")
    fresh = fresh_root / reproduction["accepted_run"]
    executed = json.loads((fresh / "executed-source-sha256.json").read_text())
    for name, expected in executed.items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), "Executed source path escapes repository")
        require(sha(path) == expected, f"Executed source differs: {name}")
    fresh_result = verifier.verify(fresh / "e6/evidence")
    require((fresh / "e6/evidence/verify.log").read_bytes() == b"hello E3\n", "Fresh output is not exact")
    for step in ("environment", "service-build", "service-inspect", "unit-tests", "e6-driver", "e6-check", "gate-driver"):
        require((fresh / step / "exit-code.txt").read_text().strip() == "0", f"Fresh step failed: {step}")
    require("25 passed" in (fresh / "unit-tests/stdout.log").read_text(), "Fresh tests failed")
    service_id = json.loads((fresh / "service-inspect/stdout.log").read_text())[0]["Id"]
    for step in ("unit-tests", "e6-driver", "gate-driver"):
        command = shlex.split((fresh / step / "command.txt").read_text())
        require(service_id in command, f"Fresh service image differs: {step}")
    fresh_gate = json.loads((fresh / "gate/gate/gate-result.json").read_text())
    require(fresh_gate["passed"] is True and all(c["passed"] for c in fresh_gate["cases"]), "Fresh gate failed")
    require({c["case"] for c in fresh_gate["cases"]} == {c["case"] for c in gate["cases"]}, "Fresh gate cases differ")
    require(fresh_gate["image"] == service_id, "Fresh gate service image differs")
    verifier.verify(fresh / "gate/gate/success/evidence")
    print(json.dumps({
        "passed": True,
        "scope": "Archive hashes and saved result consistency; no Docker rerun",
        "course_files": len(manifest["course_files"]),
        "historical_evidence_files": len(checksums),
        "e6": result,
        "custom_service_tests": 25,
        "post_rebuild_gate": "passed (unit tests and five cases)",
        "reproduction_evidence_files": len(fresh_hashes),
        "executed_source_files": len(executed),
        "fresh_e6": fresh_result,
        "fresh_service_image": service_id,
        "fresh_service_tests": 25,
        "fresh_post_rebuild_gate": "passed (unit tests and five cases)",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    try:
        main()
    except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)
