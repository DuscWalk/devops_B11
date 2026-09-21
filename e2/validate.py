#!/usr/bin/env python3
"""Validate the pinned A11 reference and B11's local E2 preparation."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    raise SystemExit(
        "Draft202012Validator is required; use the project virtual environment "
        "and install e2/requirements.txt. No checks have been run."
    )

E2 = Path(__file__).resolve().parent
ROOT = E2.parent
REFERENCE = E2 / "reference" / "a11"
SCHEMA = json.loads((REFERENCE / "task.schema.json").read_text(encoding="utf-8"))


def validator(definition):
    return Draft202012Validator({
        "$schema": SCHEMA["$schema"],
        "$defs": SCHEMA["$defs"],
        "$ref": f"#/$defs/{definition}",
    })


def validate_input_document(document, *, query=False):
    """Apply both the common envelope and the existing service input definition.

    A11's CreateJobRequest.input and Job.input are generic objects. Selecting the
    service definition here applies its declared rules without changing the
    reference schema. Cross-field rules remain covered by A11's validator.
    """
    validator("Job" if query else "CreateJobRequest").validate(document)
    definition = "".join(part.capitalize() for part in document["job_type"].split("_"))
    validator(definition + "Input").validate(document["input"])


def verify_reference():
    manifest = json.loads((E2 / "reference" / "a11-source.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    actual_names = {str(path.relative_to(REFERENCE)) for path in REFERENCE.rglob("*")
                    if path.is_file() and "__pycache__" not in path.parts}
    if actual_names != set(expected):
        raise ValueError("reference file set differs from the source manifest")
    for name, digest in expected.items():
        if hashlib.sha256((REFERENCE / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"reference file changed: {name}")
    Draft202012Validator.check_schema(SCHEMA)
    print(f"PASS: {len(expected)} A11 reference files match the recorded SHA-256 values.", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposed", action="store_true", help=(
        "validate the pending B11 correction for the incremental query example; "
        "this does not imply A11/B11 agreement"
    ))
    args = parser.parse_args(argv)
    try:
        verify_reference()
        print("\n[1] Original A11 validation (including Draft 2020-12 checks)", flush=True)
        result = subprocess.run([sys.executable, str(REFERENCE / "validate.py")], cwd=REFERENCE)
        if result.returncode:
            return result.returncode

        print("\n[2] Select the input definition for each request and query", flush=True)
        examples = json.loads((REFERENCE / "contract-examples.json").read_text(encoding="utf-8"))
        if args.proposed:
            proposal = E2 / "proposals/query_incremental_check.json"
            examples["responses"]["query_incremental_check"] = json.loads(
                proposal.read_text(encoding="utf-8")
            )
            print("PROPOSED: using the incremental query correction; agreement is pending.", flush=True)
        documents = [(f"request {name}", document, False)
                     for name, document in examples["requests"].items()]
        documents += [(f"response {name}", document, True)
                      for name, document in examples["responses"].items()
                      if name.startswith("query_")]
        failures = 0
        for name, document, query in documents:
            try:
                validate_input_document(document, query=query)
                print(f"PASS: {name}", flush=True)
            except Exception as exc:
                failures += 1
                print(f"FAIL: {name}: {getattr(exc, 'message', str(exc))}", flush=True)
        print(f"Service inputs: {len(documents) - failures}/{len(documents)} passed.", flush=True)
        if failures:
            print("Reference review is incomplete. See CONTRACT_REVIEW.md; --proposed checks the pending correction.")
            return 1

        print("\n[3] Input rejection and artifact access regression checks", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "e2/tests", "-v"], cwd=ROOT
        )
        if result.returncode:
            return result.returncode

        print("\n[4] Read the checked-in demonstration artifact", flush=True)
        metadata = ROOT / "fixtures/e2-handoff/artifact.json"
        validator("Artifact").validate(json.loads(metadata.read_text(encoding="utf-8")))
        result = subprocess.run([
            sys.executable, str(E2 / "artifact_access.py"),
            "--root", str(ROOT / "fixtures/e2-handoff/artifacts"),
            "--metadata", str(metadata),
        ], cwd=ROOT)
        if result.returncode:
            return result.returncode
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("\nPASS: local preparation checks completed. Team agreement and cross-group access remain pending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
