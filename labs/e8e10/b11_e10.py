"""Run the three B-track transactions and an independent recheck failure."""
import argparse
import csv
import difflib
import json
from pathlib import Path

from b11_handoff import prepare_candidate, source_hashes
from lab import buildchecker, fixture, run, save, scan, validate


CHECKS = dict.fromkeys(('patch_applies', 'build', 'test', 'header_change', 'no_missing'), True)


def recheck_failure(out):
    out.mkdir()
    project = out / 'project'
    fixture(project)
    source = project / 'Makefile'
    before = source.read_text()
    # Fix main.o but drop helper.c from helper.o's declared prerequisites.
    # A clean build and a config.h change still give the expected outputs.
    proposed = before.replace('main.c unused.h\n', 'main.c unused.h config.h\n').replace(
        'helper.o: helper.c\n', 'helper.o: unused.h\n')
    candidate = out / 'candidate.patch'
    candidate.write_text(''.join(difflib.unified_diff(before.splitlines(True), proposed.splitlines(True),
                                                     'a/Makefile', 'b/Makefile')))
    (out / 'source-before.Makefile').write_bytes(source.read_bytes())
    original = source_hashes(project)
    save(out / 'input.json', scan(project))
    result = validate(project, candidate, out / 'reject-md')
    observed = json.loads((out / 'reject-md/recheck.json').read_text())
    assert [f for f in observed['findings'] if f['type'] == 'MISSING'] == [
        {'target': 'helper.o', 'dependency': 'helper.c', 'type': 'MISSING'}]
    assert result['checks'] == {**CHECKS, 'no_missing': False}
    assert not result['accepted'] and result['rollback'] and result['source_unchanged']
    assert source_hashes(project) == original
    save(out / 'tracked-hashes.json', {'before': original, 'after': source_hashes(project)})
    return result


def matrix(out):
    out.mkdir(parents=True, exist_ok=False)
    p = out / 'project'
    fixture(p)
    src = p / 'Makefile'
    before = src.read_bytes()
    (out / 'source-before.Makefile').write_bytes(before)
    report = scan(p)
    diff, plan, receipt = prepare_candidate(p, report)
    save(out / 'fixed-md-report.json', report)
    save(out / 'patch-plan.json', plan)
    save(out / 'source-receipt.json', receipt)
    run(['git', 'bundle', 'create', str(out / 'input.bundle'), '--all'], p)
    candidate = out / 'candidate.patch'
    candidate.write_text(diff)
    rejected = validate(p, candidate, out / 'reject-test', fail_test=True)
    assert rejected['checks'] == {**CHECKS, 'test': False}
    assert rejected['rollback'] and rejected['source_unchanged'] and not rejected['accepted']
    assert source_hashes(p) == receipt['source_sha256']
    accepted = validate(p, candidate, out / 'accept')
    after = src.read_bytes()
    assert accepted['accepted'] and accepted['checks'] == CHECKS
    assert not accepted['rollback'] and not accepted['source_unchanged']
    assert after != before and after == before.replace(b'main.c unused.h\n', b'main.c unused.h config.h\n')
    assert (p / 'config.h').read_bytes() == b'#define VALUE 1\n'
    assert (out / 'accept/sandbox/config.h').read_bytes() == b'#define VALUE 2\n'
    (out / 'source-after-accept.Makefile').write_bytes(after)
    accepted_hashes = source_hashes(p)
    assert [k for k in accepted_hashes if accepted_hashes[k] != receipt['source_sha256'][k]] == ['Makefile']
    broken = out / 'broken.patch'
    broken.write_text('invalid patch\n')
    bad = validate(p, broken, out / 'reject-patch')
    assert bad['rollback'] and bad['source_unchanged'] and not bad['accepted']
    assert not bad['checks'] and 'COMMAND_FAILED' in bad['error']
    assert source_hashes(p) == accepted_hashes
    dynamic = buildchecker(p, out / 'recheck-buildchecker')
    assert not any(f['type'] == 'MISSING' for f in dynamic['findings'])
    assert any((f['type'], f['target'], f['dependency']) == ('REDUNDANT', 'main.o', 'unused.h')
               for f in dynamic['findings'])
    recheck_failure(out / 'personal')
    with (out / 'results.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('case', 'passed'))
        writer.writerows((case, True) for case in ('test-rejection', 'accepted', 'patch-rejection'))
    save(out / 'gate.json', {'track': 'B', 'rows': 3, 'passed': True, 'personal_rejection': 'no_missing'})
    (out / '结论.txt').write_text('功能测试失败时保持初始字节；正常候选只写回 Makefile；坏补丁保留已接受版本。\n'
                              '自主反例中构建、功能和头文件变化均通过，重检发现 helper.o 缺 helper.c，拒绝写回。\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    matrix(parser.parse_args().out.resolve())
