"""E9 personal exercise: measure the scope of a shared DEPS edit.

This is impact analysis of the course patch, not the core owner's repair policy.
GNU Make's expanded database supplies an oracle independent of lab.declarations.
"""
import argparse
import re
import subprocess
from pathlib import Path

from b11_handoff import prepare_candidate, source_hashes
from lab import commit, fixture, run, save, scan


def make_dependencies(project, out, label):
    args = ['make', '--no-print-directory', '-rR', '-qp']
    result = subprocess.run(args, cwd=project, text=True, capture_output=True)
    # -q returns 1 for an out-of-date target; -p prints the database without build.
    if result.returncode not in (0, 1):
        raise ValueError('MAKE_DATABASE_FAILED ' + result.stderr)
    (out / (label + '-make-db.txt')).write_text(result.stdout)
    (out / (label + '-make-stderr.txt')).write_text(result.stderr)
    save(out / (label + '-make-command.json'), {'argv': args, 'exit_code': result.returncode,
                                              'allowed_exit_codes': [0, 1]})
    expanded = {}
    for target in ('main.o', 'helper.o'):
        matches = re.findall(r'^' + re.escape(target) + r':([^\n]*)$', result.stdout, re.M)
        assert len(matches) == 1, (target, matches)
        expanded[target] = sorted(set(matches[0].split()))
    return expanded


def analyze(out, shared=True):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    project = out / 'project'
    fixture(project, 'macro')
    if shared:
        path = project / 'Makefile'
        path.write_text(path.read_text().replace('helper.o: helper.c\n', 'helper.o: helper.c $(DEPS)\n'))
        commit(project, 'E9 input: two object targets reference DEPS')
    before_hashes = source_hashes(project)
    report = scan(project)
    missing = [f for f in report['findings'] if f['type'] == 'MISSING']
    assert missing == [{'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'}]
    save(out / 'input.json', report)
    before = make_dependencies(project, out, 'before')
    run(['git', 'bundle', 'create', str(out / 'input.bundle'), '--all'], project)
    diff, plan, receipt = prepare_candidate(project, report)
    assert plan == [{'target': 'main.o', 'dependency': 'config.h', 'style': 'macro'}]
    patchfile = out / 'candidate.patch'
    patchfile.write_text(diff)
    save(out / 'plan.json', plan)
    save(out / 'source-receipt.json', receipt)
    run(['git', 'apply', '--check', str(patchfile)], project)
    copy = out / 'apply-demo'
    run(['git', 'clone', str(out / 'input.bundle'), str(copy)], out)
    run(['git', 'config', 'user.name', 'TeachingFixture'], copy)
    run(['git', 'config', 'user.email', 'fixture@localhost'], copy)
    run(['git', 'apply', str(patchfile)], copy)
    assert (copy / 'Makefile').read_bytes() == (project / 'Makefile').read_bytes().replace(
        b'DEPS = main.c unused.h\n', b'DEPS = main.c unused.h config.h\n')
    applied_commit = commit(copy, 'E9 analysis copy: apply course macro candidate')
    run(['git', 'bundle', 'create', str(out / 'applied.bundle'), '--all'], copy)
    after = make_dependencies(copy, out, 'after')
    after_report = scan(copy)
    save(out / 'after-report.json', after_report)
    added = {target: sorted(set(after[target]) - set(before[target])) for target in before}
    requested_targets = sorted({f['target'] for f in missing})
    unrequested_targets = sorted(t for t, dependencies in added.items()
                                if dependencies and t not in requested_targets)
    old_findings = {(f['type'], f['target'], f['dependency']) for f in report['findings']}
    new_findings = {(f['type'], f['target'], f['dependency']) for f in after_report['findings']}
    new_redundant = sorted(list(f) for f in new_findings - old_findings if f[0] == 'REDUNDANT')
    assert source_hashes(project) == before_hashes
    assert run(['git', 'status', '--porcelain'], project) == ''
    impact = {'shared': shared, 'sample_commit': report['commit'], 'applied_commit': applied_commit,
              'requested_targets': requested_targets, 'make_before': before, 'make_after': after,
              'added_dependencies': added, 'unrequested_targets': unrequested_targets,
              'new_redundant': new_redundant, 'source_unchanged': True,
              'analysis_only': True, 'e10_acceptance': 'not evaluated'}
    save(out / 'impact.json', impact)
    (out / '结论.txt').write_text(
        'DEPS 变量定义的修改会影响每一个引用它的目标。\n'
        + ('本例只报告 main.o 缺 config.h，但 helper.o 也增加了 config.h；GCC 显示 helper.c 不读取它，形成新增 RD。\n'
           if shared else '本对照中只有 main.o 引用 DEPS，helper.o 的依赖不变。\n')
        + '原输入未改，候选只应用于额外副本。共享变量场景应审查全部引用目标，再选择局部补丁或显式拒绝。\n')
    print('SHARED_IMPACT', impact)
    return impact


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--unshared', action='store_true')
    args = parser.parse_args()
    analyze(args.out, shared=not args.unshared)
