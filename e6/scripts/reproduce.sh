#!/usr/bin/env bash
# Run the E6 course workflow in a fresh directory on the Linux Docker host.
set -euo pipefail

if [[ ${1:-} == --help ]]; then
  printf 'Usage: bash e6/scripts/reproduce.sh\nRequires Linux, Python 3, and access to the local Docker daemon.\n'
  exit 0
fi
if (( $# )); then
  printf 'Unexpected arguments; use --help.\n' >&2
  exit 2
fi

stage=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
lab="$stage/labs/B-draft"
archive="$stage/evidence/hu-bo-20261029"
cd "$lab"
mkdir -p work
run=$(mktemp -d "$lab/work/e6-reproduce-XXXXXXXX")
run_id=$(basename "$run" | tr '[:upper:]' '[:lower:]')
printf 'E6_RUN_DIR=%s\n' "$run"

record() {
  local name=$1
  shift
  local folder="$run/$name" code
  mkdir -p "$folder"
  printf '%q ' "$@" > "$folder/command.txt"
  printf '\n' >> "$folder/command.txt"
  date -u +%FT%TZ > "$folder/start-utc.txt"
  printf 'Running %s; logs: %s\n' "$name" "$folder"
  if "$@" > "$folder/stdout.log" 2> "$folder/stderr.log"; then
    code=0
  else
    code=$?
  fi
  date -u +%FT%TZ > "$folder/end-utc.txt"
  printf '%s\n' "$code" > "$folder/exit-code.txt"
  if (( code != 0 )); then
    tail -n 40 "$folder/stdout.log" "$folder/stderr.log" >&2
  fi
  return "$code"
}

# Apply the archived mirror settings only to a generated build recipe.
# Keeping the original fixed base avoids registry lookup of a local base tag.
python3 - "$lab/services/draft/Dockerfile" \
  "$archive/service-base-mirror.Dockerfile" "$run" <<'PY'
import hashlib
import json
from pathlib import Path
import re
import sys

original, mirror, output = map(Path, sys.argv[1:])
source = original.read_text()
adaptation = mirror.read_text().splitlines()
base = re.search(r"^ARG BASE_IMAGE=(.+)$", source, re.MULTILINE).group(1)
if adaptation[0] != "FROM " + base or source.count("FROM ${BASE_IMAGE}\n") != 1:
    raise SystemExit("Review changed course base before adapting mirrors")
generated = source.replace("FROM ${BASE_IMAGE}\n", "FROM ${BASE_IMAGE}\n\n" + "\n".join(adaptation[1:]) + "\n")
target = output / "service.Dockerfile"
target.write_text(generated)
(output / "build-source.json").write_text(json.dumps({
    "course_dockerfile_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
    "mirror_adapter_sha256": hashlib.sha256(mirror.read_bytes()).hexdigest(),
    "generated_dockerfile_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    "change": "Insert archived RUN/ENV mirror settings after final-stage FROM; keep fixed course base and dependency lock.",
}, indent=2) + "\n")
PY
record environment docker info
record service-build docker build --progress=plain \
  -f "$run/service.Dockerfile" \
  -t "b11-e6-draft:$run_id" .
record service-inspect docker image inspect "b11-e6-draft:$run_id"
service_id=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[0]["Id"])' "$run/service-inspect/stdout.log")
record unit-tests docker run --rm --network none "$service_id" pytest
record e6-driver python3 scripts/lab_cloud.py e6 --image "$service_id" \
  --candidate "$archive/candidate/Dockerfile" --out "$run/e6" --build-timeout 600
record e6-check python3 scripts/verify_e6_b_evidence.py --run-dir "$run/e6/evidence"
# E6 slides 16–17 ask for a new test, service rebuild, and gate execution.
record gate-driver python3 scripts/lab_cloud.py gate --image "$service_id" \
  --candidate "$archive/candidate/Dockerfile" --out "$run/gate" --build-timeout 600
printf 'E6_REPRODUCE=PASS\nE6_RUN_DIR=%s\n' "$run"
