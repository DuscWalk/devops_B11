"""Verify a live E12 job from the host or the other end of an SSH tunnel."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def exchange(url, body=None):
    req = Request(url, data=None if body is None else json.dumps(body).encode(),
                  headers={'Content-Type': 'application/json'})
    try:
        response = urlopen(req, timeout=20)
    except HTTPError as e:
        response = e
    with response:
        return response.status, response.headers, response.read()


def verify(base, request, key, out):
    out.mkdir(parents=True, exist_ok=False)
    def call(path, status, body=None):
        code, _, raw = exchange(base + path, body)
        if code != status:
            raise ValueError((code, raw[:400]))
        return json.loads(raw)
    body = {'idempotency_key':key, 'input':request}
    first = call('/v1/jobs', 202, body)
    jid = first['job_id']
    assert call('/v1/jobs', 202, body)['job_id'] == jid
    conflict = call('/v1/jobs', 409, {**body, 'input':{**request, 'target':request['base']}})
    assert conflict['error'] == 'IDEMPOTENCY_CONFLICT'
    route = '/v1/jobs/' + jid
    last = None
    with (out / 'poll.jsonl').open('w') as stream:
        while True:
            state = call(route, 200)
            if state['status'] != last:
                print(json.dumps(state), file=stream, flush=True)
                last = state['status']
            if last not in ('QUEUED', 'RUNNING'):
                break
            time.sleep(2)
    if last != 'SUCCEEDED':
        raise ValueError(state)
    result = call(route + '/artifacts', 200)
    assert [r['name'] for r in result['stages']] == ['draft','full-check','incremental-check','repair','recheck']
    assert (jid, state['trace_id'], request['target']) == (result['job_id'], result['trace_id'], result['target_commit'])
    ref, = (r for r in result['artifacts'] if r['uri'] == f'artifact://{jid}/candidate.patch')
    code, headers, patch = exchange(base + route + '/files/candidate.patch')
    digest = hashlib.sha256(patch).hexdigest()
    assert code == 200 and digest == ref['sha256'] == headers['X-Content-SHA256'] and len(patch) == ref['bytes']
    (out / 'candidate.patch').write_bytes(patch)
    for name, data in [('request',body),('result',result),('receipt',{'job_id':jid,'trace_id':state['trace_id'],
                          'target':request['target'],'duplicate_job':jid,'conflict':conflict,'download':ref})]:
        (out / (name+'.json')).write_text(json.dumps(data, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--key', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    verify(args.base.rstrip('/'), json.loads(args.request.read_text()), args.key, args.out)
