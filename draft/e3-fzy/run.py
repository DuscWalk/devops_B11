"""Execute a fixed manual fzy broken/reference baseline, not an automatic fixer."""
import argparse
import difflib
import json
import shutil
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "e3/scripts"))
from common import EvidenceRun, file_sha256, write_json
from verify_docker import IMAGE_FORMAT, is_expected_toolchain_failure

COMMIT = "28195b3a709995354b6c33cec9bb7c9f81532eb6"


def execute(run, source):
    context = run.directory / "work/context"
    exported = context / "source"
    exported.mkdir(parents=True)
    _, commit = run.run("source-commit", ["git", "-C", source, "rev-parse", COMMIT + "^{commit}"])
    run.check("fixed-source-commit", commit.strip() == COMMIT)
    archive = run.directory / "work/source.tar"
    run.run("source-archive", ["git", "-C", source, "archive", "--format=tar", "--output", archive, COMMIT])
    run.run("source-extract", ["tar", "-xf", archive, "-C", exported])
    write_json(run.directory / "fzy-source.json", {
        "repository": "https://github.com/jhawthorn/fzy", "commit": COMMIT,
        "files": {p.relative_to(exported).as_posix(): file_sha256(p)
                  for p in sorted(exported.rglob("*")) if p.is_file()}})
    inputs = Path(__file__).resolve().parent
    for name in ("Dockerfile.broken", "Dockerfile.reference"):
        shutil.copyfile(inputs / name, context / name)
        shutil.copyfile(inputs / name, run.directory / name)
    (run.directory / "reference.diff").write_text("".join(difflib.unified_diff(
        (inputs / "Dockerfile.broken").read_text().splitlines(True),
        (inputs / "Dockerfile.reference").read_text().splitlines(True),
        fromfile="Dockerfile.broken", tofile="Dockerfile.reference")), encoding="utf-8")
    _, base = run.run("base-image", ["docker", "image", "inspect", "ubuntu:24.04", "--format", IMAGE_FORMAT])
    write_json(run.directory / "base-image.json", json.loads(base))
    tag = "b11/e3-fzy-reference:" + uuid.uuid4().hex[:12]
    code, log = run.run("broken-build", ["docker", "build", "--progress=plain", "-f", "Dockerfile.broken", "."], context, timeout=900, allowed=None)
    expected = is_expected_toolchain_failure(code, log)
    write_json(run.directory / "broken-result.json", {"exit_code": code, "expected_missing_toolchain": expected})
    run.check("missing-toolchain-failure", expected)
    run.run("reference-build", ["docker", "build", "--progress=plain", "-t", tag, "-f", "Dockerfile.reference", "."], context, timeout=900)
    _, identity = run.run("reference-image", ["docker", "image", "inspect", tag, "--format", IMAGE_FORMAT])
    image = json.loads(identity)
    # Use immutable ID for subsequent checks, even if another process changes the tag.
    container = ["docker", "run", "--rm", "--network", "none", "--cpus", "2", "--memory", "1g", image["id"]]
    _, log = run.run("offline-build-and-tests", container + ["sh", "-lc", "make clean && make && test -x fzy && make check && ./fzy --help"], timeout=120)
    run.check("upstream-tests", "Pass: 31, fail: 0, skip: 0." in log)
    _, result = run.run("functional-filter", container + ["sh", "-lc", "printf 'alpha\\nbeta\\n' | ./fzy -e alp"])
    run.check("functional-output", result == "alpha\n", expected="alpha\n", stdout=result)
    run.run("toolchain", container + ["sh", "-lc", "gcc --version && make --version && cat /etc/os-release"])
    _, packages = run.run("packages", container + ["dpkg-query", "-W"])
    (run.directory / "packages.txt").write_text(packages, encoding="utf-8")
    write_json(run.directory / "image-reference.json", {"image": tag, **image,
        "source_commit": COMMIT, "example_only": False, "availability": "LOCAL_DOCKER_ENGINE_ONLY",
        "automatic_draft_service": False, "registry_published": False, "a11_received": False})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--export-evidence", required=True, type=Path)
    args = parser.parse_args()
    destination = args.export_evidence.resolve()
    if destination.exists():
        parser.error("Evidence destination exists; choose a new path")
    run = EvidenceRun(ROOT / "e3/work" / ("fzy-" + uuid.uuid4().hex), "b11-e3-draft-fzy")
    error = None
    try:
        execute(run, args.source.resolve())
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        print(error, file=sys.stderr)
    finally:
        run.finish(error=error, reference_dockerfile_is_manual=True, automatic_draft_service=False)
        shutil.copytree(run.directory, destination, ignore=shutil.ignore_patterns("work"))
    return 1 if error else 0


if __name__ == "__main__":
    sys.exit(main())
