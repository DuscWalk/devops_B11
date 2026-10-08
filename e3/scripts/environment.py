"""Capture a local environment and a B11-only proposed build fingerprint."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from common import fingerprint, write_json


def version(argv):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=10,
                                env={**os.environ, "LC_ALL": "C", "LANG": "C"})
        return {"argv": argv, "exit_code": result.returncode,
                "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"argv": argv, "exit_code": None, "error": str(exc)}


def capture_local():
    distro = platform.freedesktop_os_release() if Path("/etc/os-release").exists() else {}
    tools = {name: version(argv) for name, argv in {
        "cc": ["cc", "--version"], "cc_target": ["cc", "-dumpmachine"],
        "make": ["make", "--version"], "git": ["git", "--version"],
        "python": [sys.executable, "--version"], "strace": ["strace", "--version"],
        "docker_client": ["docker", "--version"],
    }.items()}
    identity = {"spec": "b11-build-environment-proposal-v1", "execution_mode": "LOCAL_HOST",
                "os": platform.system(), "architecture": platform.machine(),
                "distro": {key: distro.get(key) for key in ("ID", "VERSION_ID")},
                "kernel": platform.release(), "compiler": tools["cc"],
                "compiler_target": tools["cc_target"], "make": tools["make"],
                "cflags": ["-O0", "-Wall", "-Wextra"], "working_directory": "project-root"}
    return {"captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "configuration_id": "b11-e3-tiny-local-v1", "agreement_status": "PROPOSED_B11_ONLY",
            "identity": identity, "build_environment_hash": fingerprint(identity), "tools": tools,
            "paths": {name: shutil.which(name) for name in ("cc", "make", "git", "docker", "strace")},
            "not_a_fzy_gcc13_environment": True,
            "limitations": "Host package/library inventory is not included; this fingerprint is a local comparison key, not proof of complete reproducibility or an A11-approved protocol."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    document = capture_local()
    if args.output:
        if args.output.exists():
            parser.error("output already exists; preserve earlier evidence")
        write_json(args.output, document)
    print(json.dumps(document, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
