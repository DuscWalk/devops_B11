from __future__ import annotations
import os
import signal
import subprocess
from mdfixer_core import CandidateResult


def run_command(cmd, cwd=None, timeout=1200):
    proc=subprocess.Popen(cmd,shell=True,cwd=cwd,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,text=True,start_new_session=True)
    try:
        output,_=proc.communicate(timeout=timeout)
        return proc.returncode,output,''
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid,signal.SIGKILL)
        output,_=proc.communicate()
        return 124,output,'command timeout'


def verify_candidate(patch, makefile_path, build_cmd, verify_cmd, workdir, timeout=1200):
    original=makefile_path.read_bytes()
    try:
        makefile_path.write_text(patch,encoding='utf-8')
        brc,bout,berr=run_command(build_cmd,cwd=workdir,timeout=timeout)
        if brc:
            return CandidateResult(False,reason=f'build failed (exit={brc}): {berr or bout[-500:]}',build_exit_code=brc,build_output=bout)
        vrc,vout,verr=run_command(verify_cmd,cwd=workdir,timeout=timeout)
        return CandidateResult(vrc==0,reason='' if vrc==0 else f'verify failed (exit={vrc}): {verr or vout[-500:]}',
                               build_exit_code=brc,verify_exit_code=vrc,build_output=bout,verify_output=vout)
    finally:
        makefile_path.write_bytes(original)
