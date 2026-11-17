"""Personal E8/E9 checks: input binding and whole-file style preservation.

These supplement the seven unmodified instructor tests. Test oracles are
explicit expected Makefile bytes, not values calculated by patch().
"""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from b11_handoff import prepare_candidate, source_hashes
from lab import commit, fixture, patch, run, scan


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.p = self.root / 'project'
        fixture(self.p)

    def assert_rejected_without_writes(self, report, reason, project=None):
        project = project or self.p
        before = source_hashes(project)
        with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
            prepare_candidate(project, report)
        self.assertEqual(source_hashes(project), before)

    def test_e8_dirty_source_with_matching_head_rejected(self):
        report = scan(self.p)
        (self.p / 'config.h').write_text('#define VALUE 9\n')
        # Demonstrate the gap in the original HEAD-only check.
        self.assertTrue(patch(self.p, report)[0])
        self.assert_rejected_without_writes(report, 'DIRTY_PROJECT')

    def test_e8_stale_commit_rejected(self):
        report = scan(self.p)
        report['commit'] = '0' * 40
        self.assert_rejected_without_writes(report, 'STALE_REPORT')

    def test_e8_redundant_only_produces_no_deletion(self):
        report = scan(self.p)
        report['findings'] = [f for f in report['findings'] if f['type'] == 'REDUNDANT']
        before = source_hashes(self.p)
        diff, plan, receipt = prepare_candidate(self.p, report)
        self.assertEqual((diff, plan), ('', []))
        self.assertEqual(receipt['source_sha256'], before)
        self.assertEqual(source_hashes(self.p), before)

    def test_e8_symlink_outside_project_rejected(self):
        outside = self.root / 'outside.h'
        outside.write_text('/* outside */\n')
        (self.p / 'link.h').symlink_to(outside)
        commit(self.p, 'case: tracked link outside sample')
        report = scan(self.p)
        report['findings'] = [{'type': 'MISSING', 'target': 'main.o', 'dependency': 'link.h'}]
        self.assert_rejected_without_writes(report, 'UNSAFE_PATH')
        self.assertEqual(outside.read_bytes(), b'/* outside */\n')

    def test_e8_bad_report_contract_rejected(self):
        original = scan(self.p)
        for field, value, reason in [
            ('schema_version', 'unknown', 'INVALID_REPORT_SCHEMA'),
            ('profile', 'implicit', 'UNSUPPORTED_PROFILE'),
            ('commit', None, 'INVALID_REPORT_COMMIT'),
            ('findings', {}, 'INVALID_FINDINGS'),
            ('findings', [{'type': 'REMOVE'}], 'INVALID_FINDING'),
        ]:
            with self.subTest(field=field, value=value):
                report = copy.deepcopy(original)
                report[field] = value
                self.assert_rejected_without_writes(report, reason)

    def test_e8_ignored_untracked_dependency_rejected(self):
        with (self.p / '.gitignore').open('a') as stream:
            stream.write('generated.h\n')
        commit(self.p, 'case: ignored header')
        (self.p / 'generated.h').write_text('/* not bound to commit */\n')
        report = scan(self.p)
        report['findings'] = [{'type': 'MISSING', 'target': 'main.o', 'dependency': 'generated.h'}]
        self.assert_rejected_without_writes(report, 'UNTRACKED_DEPENDENCY')

    def test_e9_two_missing_edges_preserve_complete_file_for_all_styles(self):
        replacements = {
            'direct': ('main.o: main.c unused.h', 'main.o: main.c unused.h config.h extra.h'),
            'macro': ('DEPS = main.c unused.h', 'DEPS = main.c unused.h config.h extra.h'),
            'mixed': ('main.o: main.c $(HEADERS)', 'main.o: main.c $(HEADERS) config.h extra.h'),
        }
        for style, (old_line, new_line) in replacements.items():
            with self.subTest(style=style):
                p = self.root / style
                fixture(p, style)
                source = p / 'main.c'
                source.write_text('#include "extra.h"\n' + source.read_text())
                commit(p, 'case: two missing header edges')
                before = source_hashes(p)
                report = scan(p)
                self.assertEqual(
                    {(f['type'], f['dependency']) for f in report['findings']},
                    {('MISSING', 'config.h'), ('MISSING', 'extra.h'), ('REDUNDANT', 'unused.h')})
                diff, plan, _ = prepare_candidate(p, report)
                self.assertEqual(plan, [{'target': 'main.o', 'dependency': d, 'style': style}
                                        for d in ('config.h', 'extra.h')])
                candidate = self.root / (style + '.patch')
                candidate.write_text(diff)
                run(['git', 'apply', '--check', str(candidate)], p)
                dst = self.root / (style + '-copy')
                shutil.copytree(p, dst, ignore=shutil.ignore_patterns('.git'))
                run(['git', 'init', '-b', 'main'], dst)
                run(['git', 'apply', str(candidate)], dst)
                self.assertEqual((dst / 'Makefile').read_bytes(),
                                 (p / 'Makefile').read_bytes().replace(old_line.encode(), new_line.encode()))
                self.assertEqual(source_hashes(p), before)
                self.assertEqual(run(['git', 'status', '--porcelain'], p), '')

    def test_e9_invalid_second_target_does_not_partially_apply(self):
        for style in ('direct', 'macro', 'mixed'):
            with self.subTest(style=style):
                p = self.root / style
                fixture(p, style)
                report = scan(p)
                report['findings'].append({'type': 'MISSING', 'target': 'unknown.o', 'dependency': 'extra.h'})
                self.assert_rejected_without_writes(report, 'UNSUPPORTED_TARGET', p)
                self.assertEqual(run(['git', 'status', '--porcelain'], p), '')


if __name__ == '__main__':
    unittest.main()
