#!/usr/bin/env python3
"""Validate MDFixer examples against the shared submission Schema."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from e2.contract import validate_request,validate_job,validator


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path)
    parser.add_argument('--response',type=Path)
    args=parser.parse_args()
    req=args.request or ROOT/'mdfixer/examples/repair_request.json'
    response=args.response or ROOT/'mdfixer/examples/repair_response_sample.json'
    request=json.loads(req.read_text());validate_request(request)
    if request['job_type']!='REPAIR':raise ValueError('expected REPAIR')
    job=json.loads(response.read_text());validate_job(job)
    report=json.loads((ROOT/'mdfixer/examples/md_report.json').read_text())
    validator('ErrorReport').validate(report)
    if report['repository']!=request['input']['repository']:raise ValueError('report repository mismatch')
    if any(f['commit']!=report['repository']['commit'] for f in report['findings']):raise ValueError('finding commit mismatch')
    print('PASS: REPAIR request, full Job response and MANUAL MD/RD report')


if __name__=='__main__':
    main()
