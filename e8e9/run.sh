#!/usr/bin/env bash
# Run from a clean outer repository. Runtime output stays outside tracked sources.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
IMAGE="${E8_IMAGE:-course-e8e10:241276007}"
test -z "$(git status --porcelain)" || { echo 'Commit source changes before collecting evidence.' >&2; exit 1; }
mkdir -p work
OUT=$(mktemp -d work/e8e9-B.XXXXXXXX)
printf '%s\n' "$OUT" > work/last-e8e9-B.path
git rev-parse HEAD > "$OUT/student-source-commit.txt"
git status --porcelain > "$OUT/student-source-status.txt"
git log -1 --format='%an <%ae>' > "$OUT/source-author.txt"
date -u +%FT%TZ > "$OUT/start.txt"
docker image inspect "$IMAGE" > "$OUT/environment-image-inspect.json"
docker image inspect "$IMAGE" --format '{{.Id}}' > "$OUT/environment-image-id.txt"
(uname -a; id; free -h; docker version) > "$OUT/host.txt"
RUN=(docker run --rm --network none --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD:/course" -w /course "$IMAGE")
"${RUN[@]}" cat /opt/toolchain.lock > "$OUT/toolchain.lock"

step() {
  local name="$1"
  shift
  printf '%q ' "${RUN[@]}" "$@" > "$OUT/$name.command.txt"
  printf '\n' >> "$OUT/$name.command.txt"
  set +e
  "${RUN[@]}" "$@" 2>&1 | tee "$OUT/$name.log"
  local codes=("${PIPESTATUS[@]}")
  set -e
  printf '%s\n' "${codes[0]}" > "$OUT/$name.exit-code.txt"
  if [[ "${codes[0]}" != 0 ]]; then exit "${codes[0]}"; fi
  if [[ "${codes[1]}" != 0 ]]; then exit "${codes[1]}"; fi
}
step tests python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v
for stage in e8 e9; do
  step "baseline-$stage" python3 labs/e8e10/run_b11_evidence.py "$stage" --baseline --out "$OUT/baseline-$stage"
  step "personal-$stage" python3 labs/e8e10/run_b11_evidence.py "$stage" --out "$OUT/personal-$stage"
done
step e9-shared python3 labs/e8e10/b11_shared_impact.py --out "$OUT/e9-shared"
step e9-unshared python3 labs/e8e10/b11_shared_impact.py --unshared --out "$OUT/e9-unshared"
date -u +%FT%TZ > "$OUT/end.txt"
python3 - "$OUT" <<'PY'
import hashlib, json, sys
from pathlib import Path
out = Path(sys.argv[1])
files = {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(out.rglob('*')) if p.is_file() and '.git' not in p.relative_to(out).parts}
(out / 'sha256.json').write_text(json.dumps(files, ensure_ascii=False, indent=2) + '\n')
PY
printf 'E8_E9_COMPLETE OUT=%s\n' "$OUT"
