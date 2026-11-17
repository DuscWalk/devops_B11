"""Replay the B manuals with independent assertions and preserved sample Git bundles."""
import argparse
import json
import shutil
from pathlib import Path

from b11_handoff import prepare_candidate, source_hashes
from lab import fixture, patch, run, save, scan


def candidate(project, report, extended):
    if extended:
        return prepare_candidate(project, report)
    before = source_hashes(project)
    diff, plan = patch(project, report)
    assert source_hashes(project) == before
    return diff, plan, {'sample_commit': report['commit'], 'source_sha256': before,
                        'source_unchanged': True, 'candidate_only': True}


def inspect_sample(project, report, label, out):
    assert report['commit'] == run(['git', 'rev-parse', 'HEAD'], project).strip()
    assert {(f['type'], f['target'], f['dependency']) for f in report['findings']} == {
        ('MISSING', 'main.o', 'config.h'), ('REDUNDANT', 'main.o', 'unused.h')}
    assert report['actual'] == {'main.o': ['config.h', 'main.c'], 'helper.o': ['helper.c']}
    run(['git', 'bundle', 'create', str((out / (label + '.bundle')).resolve()), '--all'], project)
    print('COMMIT_MATCH', label, report['commit'])


def verify_patch(project, patchfile, receipt):
    run(['git', 'apply', '--check', str(patchfile.resolve())], project)
    assert source_hashes(project) == receipt['source_sha256']
    assert run(['git', 'status', '--porcelain'], project) == ''
    print('APPLY_CHECK_PASS_SOURCE_CLEAN', project.name)


def execute(stage, out, extended):
    out.mkdir(parents=True, exist_ok=False)
    expected = {'direct': '+main.o: main.c unused.h config.h',
                'macro': '+DEPS = main.c unused.h config.h',
                'mixed': '+main.o: main.c $(HEADERS) config.h'}
    for style in (['direct'] if stage == 'e8' else ['direct', 'macro', 'mixed']):
        label = 'project' if stage == 'e8' else style
        project = out / label
        fixture(project, style)
        report = scan(project)
        reportfile = 'fixed-md-report.json' if stage == 'e8' else style + '-input.json'
        save(out / reportfile, report)
        inspect_sample(project, report, label, out)
        diff, plan, receipt = candidate(project, report, extended)
        assert plan == [{'target': 'main.o', 'dependency': 'config.h', 'style': style}]
        assert [line for line in diff.splitlines() if line.startswith('+') and not line.startswith('+++')] == [expected[style]]
        assert not any(line.startswith(('+\t', '-\t')) for line in diff.splitlines())
        patchfile = out / ('candidate.patch' if stage == 'e8' else style + '.patch')
        patchfile.write_text(diff)
        save(out / ('patch-plan.json' if stage == 'e8' else style + '-plan.json'), plan)
        save(out / (label + '-receipt.json'), receipt)
        verify_patch(project, patchfile, receipt)
        print(diff, 'PLAN', json.dumps(plan))
    if stage == 'e8':
        stale = dict(report, commit='0' * 40)
        save(out / 'stale-input.json', stale)
        before = source_hashes(project)
        try:
            candidate(project, stale, extended)
        except ValueError as error:
            assert str(error) == 'STALE_REPORT'
            save(out / 'expected-failure.json', {'error': str(error), 'source_unchanged': source_hashes(project) == before})
        else:
            raise AssertionError('stale report was accepted')
        assert source_hashes(project) == before
        print('EXPECTED_REJECTION STALE_REPORT SOURCE_BYTES_UNCHANGED')
    else:
        src, dst = out / 'macro', out / 'apply-demo'
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.git'))
        run(['git', 'init', '-b', 'main'], dst)
        run(['git', 'apply', '--check', str((out / 'macro.patch').resolve())], dst)
        run(['git', 'apply', str((out / 'macro.patch').resolve())], dst)
        original = (src / 'Makefile').read_bytes()
        assert (dst / 'Makefile').read_bytes() == original.replace(
            b'DEPS = main.c unused.h\n', b'DEPS = main.c unused.h config.h\n')
        assert b'config.h' not in original
        print('APPLY_TO_COPY_PASS')
    save(out / 'gate.json', {'stage': stage, 'track': 'B', 'passed': True,
                             'mode': 'b11-interface' if extended else 'course-baseline',
                             'e10_quality_validation': 'not performed'})
    (out / '结论.txt').write_text(
        '候选只增加缺失依赖，保留冗余依赖和配方；原输入保持不变。\n'
        + ('旧报告被拒绝。\n' if stage == 'e8' else 'direct 修改目标行，macro 修改 DEPS，mixed 保留变量引用；只在额外副本应用。\n')
        + 'git apply --check 通过不等于 E10 构建、测试、重检、回滚已完成。\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['e8', 'e9'])
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    execute(args.stage, args.out.resolve(), not args.baseline)
