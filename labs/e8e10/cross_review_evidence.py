"""Produce independent B-track input and patch evidence for E8/E9."""

import argparse
import hashlib
import shutil
from pathlib import Path

from lab import commit, fixture, patch, run, save, scan


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_case(root, style):
    project = root / style
    fixture(project, style)
    source = project / "Makefile"
    before = digest(source)
    report = scan(project)
    diff, plan = patch(project, report)
    save(root / f"{style}-input.json", report)
    save(root / f"{style}-plan.json", plan)
    candidate = root / f"{style}.patch"
    candidate.write_text(diff)
    run(["git", "apply", "--check", str(candidate)], project)
    assert digest(source) == before
    assert run(["git", "status", "--porcelain"], project) == ""
    return {"style": style, "sample_commit": report["commit"],
            "makefile_sha256_before_after": before, "source_clean": True,
            "patch_applies": True, "plan": plan}


def shared_impact(root):
    project = root / "shared-input"
    fixture(project, "macro")
    source = project / "Makefile"
    source.write_text(source.read_text().replace(
        "helper.o: helper.c\n", "helper.o: helper.c $(DEPS)\n"))
    commit(project, "E9 shared dependency input")
    before = digest(source)
    report = scan(project)
    diff, plan = patch(project, report)
    save(root / "shared-input.json", report)
    save(root / "shared-plan.json", plan)
    candidate = root / "shared.patch"
    candidate.write_text(diff)
    run(["git", "apply", "--check", str(candidate)], project)
    assert digest(source) == before
    assert run(["git", "status", "--porcelain"], project) == ""

    copy = root / "shared-apply-demo"
    shutil.copytree(project, copy, ignore=shutil.ignore_patterns(".git"))
    run(["git", "init", "-b", "main"], copy)
    run(["git", "config", "user.name", "TeachingFixture"], copy)
    run(["git", "config", "user.email", "fixture@localhost"], copy)
    run(["git", "add", "."], copy)
    run(["git", "commit", "-m", "independent apply copy"], copy)
    run(["git", "apply", str(candidate)], copy)
    after = scan(copy)
    assert "config.h" in after["declared"]["helper.o"]
    assert "config.h" not in after["actual"]["helper.o"]
    finding = {"type": "REDUNDANT", "target": "helper.o",
               "dependency": "config.h"}
    assert finding in after["findings"]
    save(root / "shared-after.json", after)
    save(root / "shared-impact.json", {
        "sample_commit": report["commit"], "input_makefile_sha256": before,
        "source_clean": True, "requested_target": "main.o",
        "affected_unrequested_target": "helper.o", "new_finding": finding,
        "analysis_only": True,
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    save(root / "e9-cases.json", [record_case(root, style)
                                  for style in ("direct", "macro", "mixed")])
    shared_impact(root)
    print("CROSS_REVIEW_EVIDENCE", root)


if __name__ == "__main__":
    main()
