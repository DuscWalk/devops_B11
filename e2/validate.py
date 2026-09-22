#!/usr/bin/env python3
"""Single validation entry point for the B11 E2 submission."""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

E2=Path(__file__).resolve().parent
ROOT=E2.parent
sys.path.insert(0,str(ROOT))
from e2.contract import SCHEMA,validator,validate_request,validate_job
from jsonschema import Draft202012Validator, ValidationError

# Retained public helper for the original input regression tests.
REFERENCE=E2


def validate_input_document(document, *, query=False):
    (validate_job if query else validate_request)(document)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proposed',action='store_true',help='legacy alias; the corrected submission is now the default')
    parser.add_argument('--reference',action='store_true',help='run only the archived A11 validator')
    args=parser.parse_args()
    if args.reference:
        return subprocess.run([sys.executable,str(E2/'reference/a11/validate.py')]).returncode
    Draft202012Validator.check_schema(SCHEMA)
    manifest=json.loads((E2/'reference/a11-source.json').read_text())
    for name,digest in manifest['files'].items():
        assert hashlib.sha256((E2/'reference/a11'/name).read_bytes()).hexdigest()==digest,name
    print('PASS: submission Schema and 13 unchanged historical reference files',flush=True)
    examples=json.loads((E2/'contract-examples.json').read_text())
    for request in examples['requests'].values():validate_request(request)
    for name,response in examples['responses'].items():
        (validator('DraftResponse').validate if name=='accepted_202' else validate_job)(response)
    for error in examples['errors']:validate_job(error)
    print('PASS: 4 requests, 202, 4 query responses, 3 complete failed Jobs',flush=True)
    rejected=0
    for case in examples['invalid']:
        try:
            doc=case['data']
            (validate_job if 'status' in doc else validate_request)(doc)
        except (ValidationError, ValueError):
            rejected+=1
        else:raise AssertionError('invalid example accepted: '+case['case'])
    print(f'PASS: {rejected} invalid examples rejected',flush=True)
    for cmd in [
        [sys.executable,'-m','unittest','discover','-s','e2/tests','-v'],
        [sys.executable,'-m','unittest','discover','-s','mdfixer','-p','test_*.py','-v'],
        [sys.executable,'draft/validate_examples.py'],
        [sys.executable,'mdfixer/validate_examples.py'],
        [sys.executable,'mdfixer/demo.py'],
    ]:
        print('\nRUN: '+' '.join(cmd[1:]),flush=True)
        result=subprocess.run(cmd,cwd=ROOT)
        if result.returncode:return result.returncode
    from e2.artifact_access import read_artifact
    for jobfile,artifact_root in [
        (ROOT/'draft/examples/query-succeeded.example.json',ROOT/'fixtures/draft-handoff/artifacts'),
        (ROOT/'mdfixer/examples/repair_response_sample.json',E2/'evidence/mdfixer-2026-09-22/artifacts'),
    ]:
        job=json.loads(jobfile.read_text());validate_job(job)
        for artifact in job['output']['artifacts']:read_artifact(artifact_root,artifact)
    print('\nPASS: 8 DRAFT/REPAIR artifact files readable with valid checksums',flush=True)
    print('PASS: E2 submission validation completed; no API deployment or detector recheck claimed',flush=True)
    return 0


if __name__=='__main__':
    sys.exit(main())
