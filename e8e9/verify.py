"""Verify a retrieved run, including sample commit provenance, without Docker."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


def command(args, cwd):
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def verify_shared(out):
    for shared, label in ((True, 'e9-shared'), (False, 'e9-unshared')):
        folder = out / label
        assert (out / (label + '.exit-code.txt')).read_text().strip() == '0'
        impact = json.loads((folder / 'impact.json').read_text())
        assert impact['shared'] is shared and impact['source_unchanged'] is True
        expected_before = {'main.o': ['main.c', 'unused.h'],
                           'helper.o': ['helper.c', 'main.c', 'unused.h'] if shared else ['helper.c']}
        expected_after = {'main.o': ['config.h', 'main.c', 'unused.h'],
                          'helper.o': ['config.h', 'helper.c', 'main.c', 'unused.h'] if shared else ['helper.c']}
        assert impact['make_before'] == expected_before
        assert impact['make_after'] == expected_after
        assert impact['requested_targets'] == ['main.o']
        assert impact['unrequested_targets'] == (['helper.o'] if shared else [])
        assert impact['new_redundant'] == ([['REDUNDANT', 'helper.o', 'config.h']] if shared else [])
        for phase, expected in (('before', expected_before), ('after', expected_after)):
            raw = (folder / (phase + '-make-db.txt')).read_text()
            for target, dependencies in expected.items():
                matches = re.findall(r'^' + re.escape(target) + r':([^\n]*)$', raw, re.M)
                assert len(matches) == 1 and sorted(set(matches[0].split())) == dependencies
            cmd = json.loads((folder / (phase + '-make-command.json')).read_text())
            assert cmd['argv'] == ['make', '--no-print-directory', '-rR', '-qp']
            assert cmd['exit_code'] in (0, 1)
        receipt = json.loads((folder / 'source-receipt.json').read_text())
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / 'sample'
            command(['git', 'clone', str((folder / 'input.bundle').resolve()), str(clone)], folder)
            assert command(['git', 'rev-parse', 'HEAD'], clone) == impact['sample_commit']
            assert receipt['sample_commit'] == impact['sample_commit']
            for name, digest in receipt['source_sha256'].items():
                data = (clone / name).read_bytes()
                assert data == (folder / 'project' / name).read_bytes()
                assert hashlib.sha256(data).hexdigest() == digest
            before = (clone / 'Makefile').read_bytes()
            command(['git', 'apply', str((folder / 'candidate.patch').resolve())], clone)
            expected = before.replace(b'DEPS = main.c unused.h\n', b'DEPS = main.c unused.h config.h\n')
            assert (clone / 'Makefile').read_bytes() == expected
            applied = Path(temporary) / 'applied'
            command(['git', 'clone', str((folder / 'applied.bundle').resolve()), str(applied)], folder)
            assert command(['git', 'rev-parse', 'HEAD'], applied) == impact['applied_commit']
            assert (applied / 'Makefile').read_bytes() == expected == (folder / 'apply-demo/Makefile').read_bytes()
        original = json.loads((folder / 'input.json').read_text())
        after = json.loads((folder / 'after-report.json').read_text())
        assert original['commit'] == impact['sample_commit'] and after['commit'] == impact['applied_commit']
        assert [f for f in original['findings'] if f['type'] == 'MISSING'] == [
            {'type': 'MISSING', 'target': 'main.o', 'dependency': 'config.h'}]
        assert not any(f['type'] == 'MISSING' for f in after['findings'])
        added = {(f['type'], f['target'], f['dependency']) for f in after['findings']} - {
            (f['type'], f['target'], f['dependency']) for f in original['findings']}
        assert added == ({('REDUNDANT', 'helper.o', 'config.h')} if shared else set())


def verify(out, legacy=False):
    checksums = json.loads((out / 'sha256.json').read_text())
    actual_files = {p.relative_to(out).as_posix() for p in out.rglob('*')
                    if p.is_file() and '.git' not in p.relative_to(out).parts and p.name != 'sha256.json'}
    assert actual_files == set(checksums), 'missing or additional archived files'
    for name, expected in checksums.items():
        path = out / name
        assert path.resolve().is_relative_to(out.resolve()), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
    assert (out / 'student-source-status.txt').read_text() == ''
    assert len((out / 'student-source-commit.txt').read_text().strip()) == 40
    image = json.loads((out / 'environment-image-inspect.json').read_text())
    assert image[0]['Id'] == (out / 'environment-image-id.txt').read_text().strip()
    for step in ('tests', 'baseline-e8', 'personal-e8', 'baseline-e9', 'personal-e9'):
        assert (out / (step + '.exit-code.txt')).read_text().strip() == '0', step
    assert '\nOK\n' in (out / 'tests.log').read_text()
    assert 'test_e8_dirty_source_with_matching_head_rejected' in (out / 'tests.log').read_text()
    assert 'test_e9_two_missing_edges_preserve_complete_file_for_all_styles' in (out / 'tests.log').read_text()
    for mode in ('baseline', 'personal'):
        for stage in ('e8', 'e9'):
            folder = out / (mode + '-' + stage)
            gate = json.loads((folder / 'gate.json').read_text())
            assert gate['passed'] is True and gate['stage'] == stage and gate['track'] == 'B'
            for style in (['direct'] if stage == 'e8' else ['direct', 'macro', 'mixed']):
                label = 'project' if stage == 'e8' else style
                report = json.loads((folder / ('fixed-md-report.json' if stage == 'e8' else style + '-input.json')).read_text())
                assert {(f['type'], f['target'], f['dependency']) for f in report['findings']} == {
                    ('MISSING', 'main.o', 'config.h'), ('REDUNDANT', 'main.o', 'unused.h')}
                receipt = json.loads((folder / (label + '-receipt.json')).read_text())
                assert receipt['sample_commit'] == report['commit'] and receipt['source_unchanged'] is True
                patchfile = folder / ('candidate.patch' if stage == 'e8' else style + '.patch')
                plan = json.loads((folder / ('patch-plan.json' if stage == 'e8' else style + '-plan.json')).read_text())
                assert plan == [{'target': 'main.o', 'dependency': 'config.h', 'style': style}]
                with tempfile.TemporaryDirectory() as temporary:
                    clone = Path(temporary) / 'sample'
                    command(['git', 'clone', str((folder / (label + '.bundle')).resolve()), str(clone)], folder)
                    assert command(['git', 'rev-parse', 'HEAD'], clone) == report['commit']
                    for name, digest in receipt['source_sha256'].items():
                        data = (folder / label / name).read_bytes()
                        assert (clone / name).read_bytes() == data
                        assert hashlib.sha256(data).hexdigest() == digest
                    before = (clone / 'Makefile').read_bytes()
                    command(['git', 'apply', '--check', str(patchfile.resolve())], clone)
                    command(['git', 'apply', str(patchfile.resolve())], clone)
                    old = {'direct': b'main.o: main.c unused.h', 'macro': b'DEPS = main.c unused.h',
                           'mixed': b'main.o: main.c $(HEADERS)'}[style]
                    expected = before.replace(old + b'\n', old + b' config.h\n')
                    assert (clone / 'Makefile').read_bytes() == expected
                    if stage == 'e9' and style == 'macro':
                        assert (folder / 'apply-demo/Makefile').read_bytes() == expected
            if stage == 'e8':
                rejection = json.loads((folder / 'expected-failure.json').read_text())
                assert rejection == {'error': 'STALE_REPORT', 'source_unchanged': True}
                assert json.loads((folder / 'stale-input.json').read_text())['commit'] == '0' * 40
    if not legacy:
        verify_shared(out)
        print('E9_SHARED_VARIABLE_EXERCISE_VERIFIED')
    print('VERIFIED', out, 'files=', len(checksums))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--legacy', action='store_true', help='verify the older archive without the E9 shared-variable exercise')
    args = parser.parse_args()
    verify(args.run.resolve(), legacy=args.legacy)
