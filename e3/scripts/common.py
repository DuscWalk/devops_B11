"""Evidence helpers shared by the E3 acceptance commands (Python 3.10+)."""
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write_json(path, document):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_bytes(document):
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fingerprint(document):
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def source_snapshot():
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=ROOT, text=True)
    inventory = {}
    for directory in ("docs", "e3/fixtures", "e3/scripts", "e3/tests", "fixtures", "draft", "mdfixer", "e2"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and not {"__pycache__", "evidence"}.intersection(path.relative_to(ROOT).parts):
                inventory[path.relative_to(ROOT).as_posix()] = file_sha256(path)
    return {"repository_url": "https://git.nju.edu.cn/devops_b11/devops-project-b11",
            "repository_commit": revision, "working_tree_status": status,
            "input_files_sha256": inventory,
            "note": "When status is nonempty, file hashes describe actual input bytes; HEAD alone is not the complete source snapshot."}


class EvidenceRun:
    def __init__(self, directory, suite):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=False)
        (self.directory / "logs").mkdir()
        self.commands = []
        self.checks = []
        self.suite = suite
        self.started_at = datetime.now(timezone.utc).isoformat()
        write_json(self.directory / "source.json", source_snapshot())
        self.env = os.environ.copy()
        self.env.update({"LC_ALL": "C", "LANG": "C", "MAKEFLAGS": "", "MFLAGS": ""})
        # A caller's Make overrides must not silently change the documented fixtures.
        self.env.pop("GNUMAKEFLAGS", None)
        self.env.pop("MAKEFILES", None)

    def run(self, label, argv, cwd=None, timeout=120, allowed=(0,)):
        cwd = Path(cwd or ROOT).resolve()
        log = f"logs/{len(self.commands) + 1:03d}-{label}.txt"
        began = datetime.now(timezone.utc).isoformat()
        start = time.monotonic()
        code, output, timed_out = 127, "", False
        try:
            proc = subprocess.Popen([str(v) for v in argv], cwd=cwd, env=self.env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, errors="replace", start_new_session=True)
            try:
                output, _ = proc.communicate(timeout=timeout)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                if os.name == "nt":
                    # Terminate this run's process tree, then collect its captured output.
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   timeout=15, check=False)
                    if proc.poll() is None:
                        proc.kill()
                else:
                    os.killpg(proc.pid, signal.SIGKILL)
                output, _ = proc.communicate()
                code = 124
        except OSError as exc:
            output = str(exc) + "\n"
        (self.directory / log).write_text(output, encoding="utf-8")
        self.commands.append({"label": label, "argv": [str(v) for v in argv], "cwd": str(cwd),
                              "started_at_utc": began, "seconds": round(time.monotonic() - start, 4),
                              "exit_code": code, "timed_out": timed_out, "log": log,
                              "expected_exit_codes": None if allowed is None else list(allowed)})
        write_json(self.directory / "commands.json", self.commands)
        print(f"RUN {label}: exit={code}", flush=True)
        if allowed is not None and code not in allowed:
            raise RuntimeError(f"{label}: unexpected exit {code}; see {self.directory / log}")
        return code, output

    def check(self, name, condition, **observed):
        self.checks.append({"name": name, "passed": bool(condition), "observed": observed})
        write_json(self.directory / "observations.json", self.checks)
        if not condition:
            raise AssertionError(f"{name}: {observed}")

    def finish(self, error=None, **facts):
        write_json(self.directory / "commands.json", self.commands)
        write_json(self.directory / "observations.json", self.checks)
        summary = {"suite": self.suite, "result": "FAIL" if error else "PASS",
                   "started_at_utc": self.started_at, "ended_at_utc": datetime.now(timezone.utc).isoformat(),
                   "checks_passed": sum(c["passed"] for c in self.checks), "checks_total": len(self.checks),
                   "commands_recorded": len(self.commands), "error": error,
                   "cross_group_read_verified": False, "a11_detector_recheck": "NOT_RUN", **facts}
        write_json(self.directory / "summary.json", summary)
        checksums = {p.relative_to(self.directory).as_posix(): file_sha256(p)
                     for p in sorted(self.directory.rglob("*"))
                     if p.is_file() and "work" not in p.relative_to(self.directory).parts
                     and p.name != "checksums.json"}
        write_json(self.directory / "checksums.json", checksums)
        print(f"EVIDENCE_DIR={self.directory}", flush=True)
        print(f"{summary['result']}: {summary['checks_passed']}/{summary['checks_total']} checks", flush=True)
        return summary
