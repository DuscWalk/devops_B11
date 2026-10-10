#!/usr/bin/env python3
"""Local MDFixer prototype. Explicit --local mode runs commands in a supplied checkout."""
from __future__ import annotations
import argparse
import json
import sys
import uuid
from datetime import datetime,timezone
from pathlib import Path

from mdfixer_core import BuildSpec,RepairInput,Repository
from mdfixer_runner import run_repair


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--artifact-root',type=Path,required=True)
    parser.add_argument('--out-dir',type=Path,required=True,help='output ARTIFACT_ROOT')
    parser.add_argument('--local',action='store_true',required=True,help='explicit host execution; input.image is not used')
    args=parser.parse_args()
    try:
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        from e2.contract import validate_request
        request=json.loads(args.request.read_text())
        validate_request(request)
        if request['job_type']!='REPAIR':
            raise ValueError('job_type must be REPAIR')
        inp=request['input']
        spec=RepairInput(Repository(**inp['repository']),inp['md_report_uri'],inp['makefile_uri'],
                         inp['image'],BuildSpec(**inp['build']),inp['verify_command'],
                         inp.get('max_iterations',1),inp.get('timeout_seconds',1200))
    except Exception as exc:
        print(json.dumps({'code':'VALIDATION_4001','message':str(exc)},ensure_ascii=False))
        return 2
    job_id='job-repair-'+uuid.uuid4().hex
    started=datetime.now(timezone.utc).isoformat()
    result=run_repair(spec,args.out_dir,workspace=args.workspace,artifact_root=args.artifact_root,job_id=job_id)
    response={'schema_version':request['schema_version'],'job_id':job_id,'trace_id':request['trace_id'],
              'job_type':'REPAIR','status':'FAILED' if result.error else 'SUCCEEDED',
              'execution':{'submitted_at':started,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
                           'timeout_seconds':spec.timeout_seconds,'idempotency_key':request['idempotency_key']},
              'input':inp,'output':{} if result.error else {'patch_uri':result.patch_uri,'patch_sha256':result.patch_sha256,
                        'artifacts':result.artifacts,'summary':result.summary},'error':result.error}
    print(json.dumps(response,ensure_ascii=False,indent=2))
    return 1 if result.error else 0


if __name__=='__main__':
    sys.exit(main())
