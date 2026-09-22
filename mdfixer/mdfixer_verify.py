from __future__ import annotations

import os

from mdfixer_core import CandidateResult


def run_command(cmd, cwd=None, timeout=1200):
    try:
        if cwd:
            old_cwd = os.getcwd()
            os.chdir(cwd)
            try:
                pipe = os.popen(cmd + " 2>&1")
                output = pipe.read()
                rc = pipe.close()
            finally:
                os.chdir(old_cwd)
        else:
            pipe = os.popen(cmd + " 2>&1")
            output = pipe.read()
            rc = pipe.close()
        return rc if rc else 0, output, ""
    except Exception as e:
        return -1, "", str(e)


def verify_candidate(patch, makefile_path, build_cmd, verify_cmd, workdir):
    original = makefile_path.read_text(encoding="utf-8")
    try:
        makefile_path.write_text(patch, encoding="utf-8")
        build_rc, build_out, build_err = run_command(build_cmd, cwd=str(workdir))
        if build_rc != 0:
            return CandidateResult(
                accepted=False,
                reason="build failed (exit=" + str(build_rc) + "): " + build_out[:200],
                patch=patch,
                build_exit_code=build_rc,
            )
        verify_rc, verify_out, verify_err = run_command(verify_cmd, cwd=str(workdir))
        if verify_rc != 0:
            return CandidateResult(
                accepted=False,
                reason="verify failed (exit=" + str(verify_rc) + "): " + verify_out[:200],
                patch=patch,
                build_exit_code=build_rc,
                verify_exit_code=verify_rc,
            )
        return CandidateResult(
            accepted=True,
            patch=patch,
            build_exit_code=build_rc,
            verify_exit_code=verify_rc,
        )
    finally:
        makefile_path.write_text(original, encoding="utf-8")
