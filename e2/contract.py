"""The shared Schema plus cross-field rules for E2 submission validation."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker

SCHEMA=json.loads((Path(__file__).parent/'task.schema.json').read_text())


def validator(definition):
    return Draft202012Validator({'$schema':SCHEMA['$schema'],'$defs':SCHEMA['$defs'],'$ref':'#/$defs/'+definition},format_checker=FormatChecker())


def validate_request(doc):
    validator('CreateJobRequest').validate(doc)
    if doc['job_type']=='INCREMENTAL_CHECK':
        inp=doc['input']
        if inp['baseline']['commit']!=inp['base_commit']:
            raise ValueError('baseline.commit must equal base_commit')
        if inp['baseline']['configuration_id']!=inp['configuration_id']:
            raise ValueError('baseline configuration mismatch')


def validate_job(doc):
    validator('Job').validate(doc)
    validate_request({'schema_version':doc['schema_version'],'trace_id':doc['trace_id'],
                      'job_type':doc['job_type'],'idempotency_key':doc['execution'].get('idempotency_key','query-only'),
                      'input':doc['input']})
    out=doc['output']
    if doc['job_type']!='INCREMENTAL_CHECK' and ('delta' in out or 'current_graph_uri' in out):
        raise ValueError('delta/current_graph_uri require INCREMENTAL_CHECK')
    for f in out.get('findings',[]):
        if 'origin' in f and doc['job_type']!='INCREMENTAL_CHECK':raise ValueError('origin requires INCREMENTAL_CHECK')
        if f['type']=='MISSING' and f['evidence']!={'actual_read':True,'declared':False}:
            raise ValueError('MISSING evidence mismatch')
        if f['type']=='REDUNDANT' and f['evidence']!={'actual_read':False,'declared':True}:
            raise ValueError('REDUNDANT evidence mismatch')
    if out.get('delta') and out['delta']['baseline_commit']!=doc['input']['base_commit']:
        raise ValueError('delta baseline mismatch')
