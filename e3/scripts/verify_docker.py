"""Record a real broken/reference DRAFT Docker acceptance run, separately from host checks."""
import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT, EvidenceRun, file_sha256, fingerprint, write_json


IMAGE_FORMAT = '{"id":{{json .Id}},"repo_digests":{{json .RepoDigests}},"os":{{json .Os}},"architecture":{{json .Architecture}}}'


def docker_suite(run):
    run.run("docker-server", ["docker", "version", "--format", "{{json .Server}}"], timeout=30)
    fixture = ROOT / "e3/fixtures/draft/tiny-greeting"
    project = run.directory / "work/tiny-greeting"
    shutil.copytree(fixture, project)
    buildx_code, _ = run.run("docker-buildx-probe", ["docker", "buildx", "version"], timeout=30, allowed=None)
    build_options = ["--progress=plain"] if buildx_code == 0 else ["--force-rm"]
    if buildx_code != 0:
        # Process-local fallback; do not install plugins or change Docker configuration.
        run.env["DOCKER_BUILDKIT"] = "0"
    write_json(run.directory / "builder.json", {"builder": "buildkit" if buildx_code == 0 else "legacy",
               "buildx_probe_exit_code": buildx_code, "global_configuration_changed": False})
    suffix = uuid.uuid4().hex[:12]
    broken = "b11/e3-tiny-broken:" + suffix
    reference = "b11/e3-tiny-reference:" + suffix
    _, context = run.run("docker-context", ["docker", "context", "show"], timeout=30)
    code, text = run.run("draft-broken-build", ["docker", "build", *build_options, "--no-cache",
                            "-t", broken, "-f", "Dockerfile.broken", "."], project, timeout=300, allowed=None)
    expected_failure = code not in (0, 124, 127) and ("make: not found" in text or "make: command not found" in text)
    write_json(run.directory / "broken-result.json", {
        "exit_code": code, "expected_toolchain_failure_observed": expected_failure,
        "classification": "EXPECTED_MISSING_TOOLCHAIN" if expected_failure else "UNEXPECTED_FAILURE_OR_SUCCESS",
        "note": "A registry/network/timeout failure is not the expected missing-make result."})
    run.check("draft-broken-missing-toolchain", expected_failure, exit_code=code)
    _, base_text = run.run("docker-base-identity", ["docker", "image", "inspect", "python:3.13-slim",
                          "--format", IMAGE_FORMAT], timeout=30)
    base = json.loads(base_text)
    run.run("draft-reference-build", ["docker", "build", *build_options, "--no-cache",
            "-t", reference, "-f", "Dockerfile.reference", "."], project, timeout=300)
    _, image_text = run.run("docker-reference-identity", ["docker", "image", "inspect", reference,
                           "--format", IMAGE_FORMAT], timeout=30)
    image = json.loads(image_text)
    container = ["docker", "run", "--rm", "--network", "none", "--cpus", "2", "--memory", "1g", reference]
    _, function = run.run("draft-reference-function", container + ["./hello"], timeout=30)
    run.check("draft-container-function", function == "hello E3\n", stdout=function)
    _, rebuilt = run.run("draft-container-offline-rebuild", container + ["sh", "-c",
                         "make clean && make && test -x hello && ./hello"], timeout=60)
    run.check("draft-container-offline-rebuild-function", rebuilt.splitlines()[-1:] == ["hello E3"], stdout=rebuilt)
    _, compiler = run.run("container-compiler", container + ["cc", "--version"], timeout=30)
    _, make = run.run("container-make", container + ["make", "--version"], timeout=30)
    _, packages = run.run("container-packages", container + ["dpkg-query", "-W", "-f", "${Package}=${Version}\n"], timeout=30)
    package_file = run.directory / "packages.txt"
    package_file.write_text(packages, encoding="utf-8")
    identity = {"spec": "b11-build-environment-proposal-v1", "execution_mode": "DOCKER",
                "image_id": image["id"], "os": image["os"], "architecture": image["architecture"],
                "compiler_version": compiler.strip(), "make_version": make.strip(),
                "package_inventory_sha256": file_sha256(package_file),
                "cflags": ["-O0", "-Wall", "-Wextra"], "working_directory": "/work"}
    write_json(run.directory / "environment.json", {"agreement_status": "PROPOSED_B11_ONLY",
        "configuration_id": "b11-e3-tiny-container-v1", "identity": identity,
        "build_environment_hash": fingerprint(identity), "base_image": base,
        "docker_context": context.strip(), "resource_limits": {"cpus": 2, "memory": "1g", "network": "none"}})
    write_json(run.directory / "image-reference.json", {"example_only": False, "image": reference,
        **image, "availability": "LOCAL_DOCKER_ENGINE_ONLY", "registry_published": False,
        "archive_exported": False, "a11_received": False,
        "dockerfile_sha256": file_sha256(project / "Dockerfile.reference"),
        "note": "Only the generated image tag belongs to this run. Base tags and package repositories are not pinned; use the resolved image ID for this observation."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--export-evidence", type=Path)
    args = parser.parse_args()
    directory = (args.out or ROOT / "e3/work" / ("docker-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])).resolve()
    if directory.exists():
        parser.error("--out exists; preserve previous runs")
    if args.export_evidence:
        export = args.export_evidence.resolve()
        if export.exists() or export == directory or export.is_relative_to(directory) or directory.is_relative_to(export):
            parser.error("export must be new and outside the run directory")
    run = EvidenceRun(directory, "b11-e3-draft-docker-reference")
    error = None
    try:
        docker_suite(run)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        print(error, file=sys.stderr)
    finally:
        run.finish(error=error, reference_dockerfile_is_manual=True, automatic_draft_service=False,
                   environment_hash_status="PROPOSED_B11_ONLY")
        if args.export_evidence:
            shutil.copytree(run.directory, export, ignore=shutil.ignore_patterns("work"))
            print(f"EXPORTED_EVIDENCE={export}")
    return 1 if error else 0


if __name__ == "__main__":
    sys.exit(main())
