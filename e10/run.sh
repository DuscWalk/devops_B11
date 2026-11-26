#!/usr/bin/env bash
# Run from a clean checkout on the lab server, using the student's image.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
test -z "$(git status --porcelain)" || { echo 'Commit the source before collecting evidence.' >&2; exit 1; }
sid=$(git config --local user.name)
[[ $sid =~ ^[0-9]{6,16}$ ]]
image=${E10_IMAGE:-course-e8e10:$sid}
mkdir -p work
out=$(mktemp -d "work/e10-B-$sid.XXXXXXXX")
echo "OUT=$out"
git rev-parse HEAD > "$out/student-source-commit.txt"
git status --porcelain > "$out/student-source-status.txt"
docker image inspect "$image" --format '{{.Id}}' > "$out/environment-image-id.txt"
cli=(docker run --rm --network none --cap-add SYS_PTRACE --user "$(id -u):$(id -g)" -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD:/course" -w /course "$image")
"${cli[@]}" cat /opt/toolchain.lock > "$out/toolchain.lock"
step() {
  local name=$1; shift
  printf '%q ' "${cli[@]}" "$@" > "$out/$name.command.txt"
  if "${cli[@]}" "$@" > "$out/$name.log" 2>&1; then rc=0; else rc=$?; fi
  echo "$rc" > "$out/$name.exit-code.txt"
  if [[ $rc != 0 ]]; then cat "$out/$name.log" >&2; return "$rc"; fi
}
step tests python3 -m unittest discover -s labs/e8e10 -p 'test_*.py' -v
step matrix python3 labs/e8e10/b11_e10.py --out "$out/matrix"
cat "$out/matrix/results.csv"
printf '%s\n' "$out" > work/last-e10-B.path
