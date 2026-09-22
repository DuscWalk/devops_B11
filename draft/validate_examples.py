"""Validate this fixed DRAFT proposal bundle; not a service request validator."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "draft/examples"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, help="Exact reference Schema file")
    args = parser.parse_args()
    source = read_json(EXAMPLES / "source.json")
    if args.schema:
        raw = args.schema.read_bytes()
    else:
        raw = subprocess.check_output(
            ["git", "show", source["reference_commit"] + ":" + source["schema_path"]],
            cwd=ROOT,
        )
    # A checked-out Windows copy may have CRLF; source hash is for Git LF bytes.
    raw = raw.replace(b"\r\n", b"\n")
    require(hashlib.sha256(raw).hexdigest() == source["schema_sha256"],
            "Reference Schema changed; review and update provenance explicitly")
    schema = json.loads(raw)
    Draft202012Validator.check_schema(schema)

    def validator(name):
        return Draft202012Validator({"$ref": "#/$defs/" + name, "$defs": schema["$defs"]})

    request = read_json(EXAMPLES / "request.json")
    validator("CreateJobRequest").validate(request)
    validator("DraftInput").validate(request["input"])
    invalid = read_json(EXAMPLES / "request-missing-verify.invalid.json")
    validator("CreateJobRequest").validate(invalid)
    require(list(validator("DraftInput").iter_errors(invalid["input"])),
            "Missing verify_command was not rejected")
    print("PASS: DRAFT request and missing-verify negative example")

    accepted = read_json(EXAMPLES / "accepted.example.json")
    validator("DraftResponse").validate(accepted)
    require(accepted["status"] == "QUEUED", "202 must be QUEUED in this proposal")
    success = read_json(EXAMPLES / "query-succeeded.example.json")
    failed = read_json(EXAMPLES / "query-failed.example.json")
    for job in (success, failed):
        validator("Job").validate(job)
        validator("DraftInput").validate(job["input"])
        require(job["input"] == request["input"], "Query input differs from request")
        require(job["job_id"] == accepted["job_id"] and job["job_type"] == "DRAFT",
                "Job identity mismatch")
    require(success["status"] == "SUCCEEDED" and success["error"] is None,
            "Inconsistent success sample")
    require(success["output"]["summary"]["example_only"] is True,
            "Synthetic success must be marked as an example")
    require(failed["status"] == "FAILED" and failed["output"] == {}
            and failed["error"]["code"] == "ENV_3002", "Inconsistent failure sample")
    print("PASS: accepted, success and complete failure Job samples")

    artifact_root = (ROOT / "fixtures/draft-handoff/artifacts").resolve()
    require(len(success["output"]["artifacts"]) == 5, "Expected five handoff artifacts")
    require({art["uri"].rsplit("/", 1)[-1] for art in success["output"]["artifacts"]}
            == {"Dockerfile", "image_ref.json", "iterations.json", "iteration-01.txt", "verify.json"},
            "Handoff artifact list is incomplete or duplicated")
    for art in success["output"]["artifacts"]:
        validator("Artifact").validate(art)
        prefix = "artifact://b11/" + success["job_id"] + "/"
        require(art["uri"].startswith(prefix), "Unexpected artifact owner")
        path = (artifact_root / art["uri"][len("artifact://"):]).resolve()
        require(artifact_root in path.parents, "Artifact path escapes bundle")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == art["sha256"],
                "Artifact checksum mismatch: " + str(path))
        require(art["commit"] == request["input"]["repository"]["commit"],
                "Artifact commit mismatch")
    folder = artifact_root / "b11" / success["job_id"]
    image = read_json(folder / "image_ref.json")
    require(image["example_only"] and image["availability"] == "NOT_BUILT"
            and image["image_id"] is None and image["repo_digest"] is None,
            "Unbuilt image must not be presented as available")
    require(image["repository"] == request["input"]["repository"], "Image source mismatch")
    require(image["clean_build_command"] == request["input"]["build"]["command"]
            and image["verify_command"] == request["input"]["verify_command"],
            "Image handoff commands differ from request")
    iterations = read_json(folder / "iterations.json")
    verify = read_json(folder / "verify.json")
    require(iterations["example_only"] and verify["example_only"], "Missing synthetic labels")
    require(verify["command"] == request["input"]["verify_command"]
            and verify["repository"] == request["input"]["repository"],
            "Verification sample does not match request")
    require((folder / "Dockerfile").read_bytes() == (ROOT / "draft/Dockerfile").read_bytes(),
            "Candidate Dockerfile copies differ")
    print("PASS: 5 artifact files, checksums, source identity and example labels")
    print("This checks local proposal data only; no image build or cross-group acceptance.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("FAIL:", error, file=sys.stderr)
        sys.exit(1)
