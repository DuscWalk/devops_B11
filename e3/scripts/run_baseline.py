"""Run Hu Bo's B11 E3 acceptance fixtures without Docker or A11 services."""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT, EvidenceRun, file_sha256, write_json
from environment import capture_local

sys.path.insert(0, str(ROOT / "mdfixer"))
from mdfixer_verify import verify_candidate


FIXTURES = ROOT / "e3/fixtures"


def set_header(run, project, style, value):
    # Avoid future mtimes and coarse filesystem clocks. Only our disposable copy changes.
    time.sleep(1.1)
    header = project / "config.h"
    header.write_text(f"#define VALUE {value}\n", encoding="utf-8")
    run.check(f"{style}-header-{value}-newer-than-object",
              header.stat().st_mtime_ns > (project / "main.o").stat().st_mtime_ns,
              header_mtime_ns=header.stat().st_mtime_ns,
              object_mtime_ns=(project / "main.o").stat().st_mtime_ns)
    write_json(run.directory / f"header-edits/{style}-{value}.json",
               {"file": "config.h", "new_content": header.read_text(),
                "sha256": file_sha256(header), "operation": "controlled fixture edit"})


def build(run, project, label, clean=False):
    if clean:
        run.run(label + "-clean", ["make", "clean"], project)
    return run.run(label + "-build", ["make"], project)[1]


def output(run, project, label, expected):
    _, text = run.run(label + "-app", ["./app"], project)
    run.check(label + "-output", text == f"{expected}\n", expected=expected, stdout=text)


def reference_style(run, style):
    fixture = FIXTURES / "mdfixer" / style
    project = run.directory / "work" / style
    shutil.copytree(fixture, project)
    oracle = json.loads((fixture / "oracle.json").read_text())
    run.check(style + "-oracle-source", oracle["provenance"] == "B11_REFERENCE_ORACLE"
              and oracle["detector_result"] is False, provenance=oracle["provenance"])
    shutil.copyfile(project / "Makefile.before", project / "Makefile")
    run.run(style + "-git-init", ["git", "init", "-q"], project)
    build(run, project, style + "-before", clean=True)
    output(run, project, style + "-initial", 1)
    set_header(run, project, style, 2)
    build(run, project, style + "-unfixed-incremental")
    output(run, project, style + "-unfixed-incremental", 1)
    build(run, project, style + "-unfixed-clean", clean=True)
    output(run, project, style + "-unfixed-clean", 2)
    run.run(style + "-patch-check", ["git", "apply", "--check", "reference.patch"], project)
    run.run(style + "-patch-apply", ["git", "apply", "reference.patch"], project)
    run.check(style + "-reference-bytes", (project / "Makefile").read_bytes()
              == (fixture / "Makefile.reference").read_bytes())
    build(run, project, style + "-fixed-clean", clean=True)
    output(run, project, style + "-fixed-clean", 2)
    set_header(run, project, style, 3)
    rebuild_log = build(run, project, style + "-fixed-incremental")
    output(run, project, style + "-fixed-incremental", 3)
    run.check(style + "-recompiled", "main.c" in rebuild_log, build_output=rebuild_log)
    if style == "implicit":
        depfile = (project / "main.d").read_text()
        (run.directory / "implicit-main.d.txt").write_text(depfile, encoding="utf-8")
        run.check("implicit-generated-dependency", "config.h" in depfile, depfile=depfile)
    else:
        run.check(style + "-redundant-declaration-preserved", "unused.h" in (project / "Makefile").read_text())
    # Exercise the existing verifier, with a genuinely failing Make recipe.
    original = (project / "Makefile").read_bytes()
    candidate = original.decode() + "\n.PHONY: reject-me\nall: reject-me\nreject-me:\n\t@echo E3_INVALID_CANDIDATE >&2\n\t@false\n"
    candidate_dir = run.directory / "rejected" / style
    candidate_dir.mkdir(parents=True)
    (candidate_dir / "Makefile.candidate").write_text(candidate, encoding="utf-8")
    result = verify_candidate(candidate, project / "Makefile", "make clean && make",
                              "./app", project, timeout=30)
    (candidate_dir / "build.txt").write_text(result.build_output, encoding="utf-8")
    write_json(candidate_dir / "result.json", {"accepted": result.accepted,
               "build_exit_code": result.build_exit_code, "reason": result.reason,
               "build_command": "make clean && make", "verify_command": "./app",
               "source_restored_sha256": file_sha256(project / "Makefile"),
               "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest()})
    run.check(style + "-invalid-candidate-rejected", not result.accepted
              and result.build_exit_code not in (None, 0) and "E3_INVALID_CANDIDATE" in result.build_output,
              accepted=result.accepted, build_exit_code=result.build_exit_code)
    run.check(style + "-original-restored", (project / "Makefile").read_bytes() == original)
    build(run, project, style + "-restored", clean=True)
    output(run, project, style + "-restored", 3)


def run_suite(run):
    environment = capture_local()
    write_json(run.directory / "environment.json", environment)
    for tool in ("cc", "make", "git"):
        run.check(tool + "-available", environment["tools"][tool]["exit_code"] == 0)
    run.check("gnu-make", "GNU Make" in environment["tools"]["make"]["stdout"])
    run.env["CC"] = environment["paths"]["cc"]
    # The existing in-process candidate verifier inherits the same documented environment.
    os.environ.update({key: run.env[key] for key in ("CC", "LC_ALL", "LANG", "MAKEFLAGS", "MFLAGS")})
    os.environ.pop("GNUMAKEFLAGS", None)
    os.environ.pop("MAKEFILES", None)
    slide_sources = json.loads((ROOT / "docs/sources.json").read_text())
    for slide in slide_sources["files"]:
        run.check(slide["stage"] + "-slides-integrity", file_sha256(ROOT / "docs" / slide["file"]) == slide["sha256"])
    run.run("e3-evidence-regressions", [sys.executable, "-m", "unittest", "discover", "-s", "e3/tests", "-v"])
    # Preserve E2 and exercise existing code through its official entry point.
    run.run("e2-validation", [sys.executable, ROOT / "e2/validate.py"], timeout=180)
    draft = run.directory / "work/tiny-greeting"
    shutil.copytree(FIXTURES / "draft/tiny-greeting", draft)
    run.run("draft-local-clean", ["make", "clean"], draft)
    run.run("draft-local-build", ["make"], draft)
    run.check("draft-executable-created", (draft / "hello").is_file()
              and os.access(draft / "hello", os.X_OK))
    _, text = run.run("draft-local-verify", ["./hello"], draft)
    oracle = json.loads((draft / "oracle.json").read_text())
    run.check("draft-local-function", text == oracle["expected_stdout"], stdout=text)
    for style in ("target", "macro", "hybrid", "implicit"):
        reference_style(run, style)
    run.run("mdfixer-real-local-prototype", [sys.executable, ROOT / "mdfixer/demo.py",
            "--evidence-dir", run.directory / "mdfixer-prototype"], timeout=120)
    report = json.loads((run.directory / "mdfixer-prototype/result.json").read_text())
    run.check("prototype-repair-and-honest-scope", report["result"] == "PASS"
              and report["header_change_rebuild_verified"] and report["detector_recheck"] == "NOT_RUN"
              and report["image_used"] is False, report=report)
    # Consume fresh artifacts from a separate root, like a receiving workspace.
    sys.path.insert(0, str(ROOT))
    from e2.artifact_access import ArtifactAccessError, read_artifact
    response = json.loads((run.directory / "mdfixer-prototype/response.json").read_text())
    producer = run.directory / "mdfixer-prototype/artifacts"
    consumer = run.directory / "work/consumer-artifacts"
    shutil.copytree(producer, consumer)
    receipts = []
    for metadata in response["output"]["artifacts"]:
        _, payload, digest = read_artifact(consumer, metadata)
        receipts.append({"uri": metadata["uri"], "bytes": len(payload), "sha256": digest})
    run.check("fresh-artifacts-read-from-separate-root", len(receipts) == 3, receipts=receipts)
    write_json(run.directory / "artifact-receipt.json", {"consumer": "B11_LOCAL_INTEGRATION_CHECK",
               "a11_received": False, "files": receipts})
    first = response["output"]["artifacts"][0]
    path, payload, _ = read_artifact(consumer, first)
    path.write_bytes(payload + b"corrupt")
    try:
        read_artifact(consumer, first)
    except ArtifactAccessError as exc:
        run.check("corrupted-artifact-rejected", "sha256 mismatch" in str(exc), error=str(exc))
    else:
        run.check("corrupted-artifact-rejected", False)
    finally:
        path.write_bytes(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new run directory; never overwrite an earlier run")
    parser.add_argument("--export-evidence", type=Path, help="copy logs/metadata to a new reviewable directory; exclude work")
    args = parser.parse_args()
    destination = args.out or ROOT / "e3/work" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    destination = destination.resolve()
    if destination.exists():
        parser.error("--out already exists; choose a new directory")
    if args.export_evidence:
        export = args.export_evidence.resolve()
        if export.exists() or export == destination or export.is_relative_to(destination) or destination.is_relative_to(export):
            parser.error("export must be a new directory outside the run directory")
    run = EvidenceRun(destination, "b11-e3-hubo-local-baseline")
    error = None
    try:
        run_suite(run)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        print(error, file=sys.stderr)
    finally:
        run.finish(error=error, reference_styles=["target", "macro", "hybrid", "implicit"],
                   reference_patches_are_manual=True, prototype_supported_styles=["simple-explicit-target", "single-variable-macro",
                                               "single-variable-hybrid", "simple-c-object-pattern"],
                   prototype_scope="limited fixtures; see mdfixer/README.md",
                   docker_validation="NOT_RUN_BY_THIS_COMMAND", environment_hash_status="PROPOSED_B11_ONLY")
        if args.export_evidence:
            shutil.copytree(run.directory, export, ignore=shutil.ignore_patterns("work"))
            print(f"EXPORTED_EVIDENCE={export}")
    return 1 if error else 0


if __name__ == "__main__":
    sys.exit(main())
