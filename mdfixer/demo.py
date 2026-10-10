#!/usr/bin/env python3
"""Reproduce a real local repair on the included manual source fixture."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from e2.contract import validate_job,validator
from e2.artifact_access import read_artifact


def run_demo(evidence_dir=None):
    fixture=ROOT/'fixtures/mdfixer-project'
    source=json.loads((fixture/'source.json').read_text())
    assert hashlib.sha256((fixture/'project.bundle').read_bytes()).hexdigest()==source['bundle_sha256']
    for name,digest in source['source_files'].items():
        assert hashlib.sha256((fixture/name).read_bytes()).hexdigest()==digest,name
    with tempfile.TemporaryDirectory(prefix='b11-md-demo-') as tmp:
        temp=Path(tmp); workspace=temp/'project';out=temp/'output'
        subprocess.run(['git','clone','-q',str(fixture/'project.bundle'),str(workspace)],check=True)
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=workspace,text=True).strip()==source['commit']
        original=(workspace/'Makefile').read_bytes()
        command=[sys.executable,str(ROOT/'mdfixer/mdfixer.py'),'--local','--request',str(ROOT/'mdfixer/examples/repair_request.json'),
                 '--workspace',str(workspace),'--artifact-root',str(fixture/'artifacts'),'--out-dir',str(out)]
        proc=subprocess.run(command,capture_output=True,text=True,timeout=90)
        if proc.returncode:
            raise RuntimeError(proc.stdout+proc.stderr)
        response=json.loads(proc.stdout)
        validate_job(response)
        assert response['output']['summary']['candidates_accepted']==1
        assert response['output']['summary']['recheck_performed'] is False
        assert (workspace/'Makefile').read_bytes()==original,'candidate verifier must restore source'
        for artifact in response['output']['artifacts']:
            read_artifact(out,artifact)
        patch=out/'b11'/response['job_id']/'fix.patch'
        subprocess.run(['git','apply','--check',str(patch)],cwd=workspace,check=True)
        subprocess.run(['git','apply',str(patch)],cwd=workspace,check=True)
        assert 'legacy.h' in (workspace/'Makefile').read_text(),'RD must remain untouched'
        verified=subprocess.run('make clean && make && make test',shell=True,cwd=workspace,capture_output=True,text=True,timeout=30)
        assert verified.returncode==0,verified.stdout+verified.stderr
        # The added prerequisite must cause recompilation after header content changes.
        header=workspace/'config.h';header.write_text('#define VALUE 9\n')
        import os,time
        stamp=time.time()+2
        os.utime(header,(stamp,stamp))
        rebuild=subprocess.run(['make','all'],cwd=workspace,capture_output=True,text=True,timeout=30)
        assert rebuild.returncode==0
        assert subprocess.check_output(['./app'],cwd=workspace,text=True).strip()=='9','header update did not trigger rebuilding'
        report={'result':'PASS','source_commit':source['commit'],'accepted_candidates':1,'artifact_reads':3,
                'patch_apply_check':True,'build_and_test_exit_code':verified.returncode,
                'header_change_rebuild_verified':True,'redundant_declaration_preserved':True,
                'detector_recheck':'NOT_RUN','execution_mode':'LOCAL_PROTOTYPE','image_used':False}
        if evidence_dir:
            dest=Path(evidence_dir);dest.mkdir(parents=True,exist_ok=True)
            (dest/'response.json').write_text(json.dumps(response,ensure_ascii=False,indent=2)+'\n')
            (dest/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            (dest/'build-test.txt').write_text(verified.stdout+verified.stderr)
            (dest/'header-rebuild.txt').write_text(rebuild.stdout+rebuild.stderr)
            shutil.copytree(out,dest/'artifacts',dirs_exist_ok=True)
        print('PASS: MDFixer local repair, 3 artifacts, git apply, build/test and header-change rebuild; detector recheck NOT_RUN')
        return response,report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir',type=Path)
    run_demo(parser.parse_args().evidence_dir)
