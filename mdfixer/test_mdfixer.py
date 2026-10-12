import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mdfixer_core import Finding, filter_missing, parse_artifact_uri
from mdfixer_engine import parse_makefile
from mdfixer_patch import generate_patch_for_missing
from mdfixer_verify import run_command, verify_candidate


def finding(dep='config.h', kind='MISSING', origin=''):
    return Finding(kind, 'app.o', dep, 'a' * 40, 'MANUAL', {'file': 'Makefile', 'line': 1}, {}, origin=origin)


class RepairRegressionTests(unittest.TestCase):
    def test_ignore_redundant_and_resolved(self):
        a = finding()
        self.assertEqual(filter_missing([a, finding(kind='REDUNDANT'), finding(origin='RESOLVED')]), [a])

    def test_artifact_uri_and_traversal(self):
        self.assertEqual(parse_artifact_uri('artifact://b11/job-md/report.json'), ('b11', 'job-md', 'report.json'))
        self.assertIsNone(parse_artifact_uri('artifact://b11/job-md/../../file'))

    def test_cumulative_additions_preserve_continuation(self):
        content = 'app.o: app.c \\\n  legacy.h\n\tcc -c app.c\n'
        for dep in ['config.h', 'value.h']:
            rules, variables = parse_makefile(content)
            result = generate_patch_for_missing(content, rules, variables, finding(dep))
            self.assertIsNotNone(result)
            content = result[0]
        rules, _ = parse_makefile(content)
        self.assertEqual(set(rules[0].prerequisites), {'app.c', 'config.h', 'value.h', 'legacy.h'})
        self.assertIn('\\\n', content)

    def test_rejected_candidate_restores_makefile(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'Makefile'
            p.write_text('original\n')
            result = verify_candidate('candidate\n', p, 'exit 3', 'true', tmp, timeout=2)
            self.assertFalse(result.accepted)
            self.assertEqual(result.build_exit_code, 3)
            self.assertEqual(p.read_text(), 'original\n')

    def test_timeout_enforced(self):
        before = time.monotonic()
        code, _, _ = run_command('sleep 5', timeout=0.05)
        self.assertEqual(code, 124)
        self.assertLess(time.monotonic() - before, 2)

    def test_variable_rule_is_not_guessed(self):
        content = 'app.o: $(SOURCES)\n\tcc -c app.c\n'
        rules, variables = parse_makefile(content)
        self.assertIsNone(generate_patch_for_missing(content, rules, variables, finding()))


class ParsingAndPatchRegressionTests(unittest.TestCase):
    def patch(self, content, dep='config.h', target='app.o'):
        item = finding(dep)
        item.target = target
        rules, variables = parse_makefile(content)
        return generate_patch_for_missing(content, rules, variables, item)

    def test_variable_continuation_uses_first_line_and_keeps_recipe(self):
        content = 'DEPS := app.c \\\n  legacy.h\napp.o: $(DEPS)\n\tcc -c app.c\n'
        rules, variables = parse_makefile(content)
        self.assertEqual(variables[0].line_no, 1)
        self.assertEqual(rules[0].line_no, 3)
        for dep in ('config.h', 'value.h'):
            content = self.patch(content, dep)[0]
        self.assertIn('DEPS := app.c config.h value.h \\\n  legacy.h\n', content)
        self.assertTrue(content.endswith('\tcc -c app.c\n'))

    def test_inline_comment_does_not_hide_dependency(self):
        content = 'app.o: app.c # retain comment\n\tcc -c app.c\n'
        patched = self.patch(content)[0]
        rules, _ = parse_makefile(patched)
        self.assertIn('config.h', rules[0].prerequisites)
        self.assertIn('# retain comment', patched)

    def test_ambiguous_and_unevaluated_make_syntax_is_rejected(self):
        for content in (
            'app.o: $(A) $(B)\nA = a.h\nB = b.h\n',
            'app.o: $(A)\nA = a.h\nA += b.h\n',
            'app.o: $(A)\nA = $(B)\n',
            'app.o other.o: app.c\n',
            'app.o: app.c\napp.o: extra.h\n',
            'ifeq (x,y)\napp.o: app.c\nendif\n',
            'app.o: app.c | build-dir\n',
            '-include config.mk\napp.o: app.c\n',
            '-include $(DEPS)\napp.o: app.c\n',
        ):
            with self.subTest(content=content):
                self.assertIsNone(self.patch(content))
        self.assertIsNone(self.patch('app.o: app.c\n', dep='$(shell touch BAD)'))

    def test_pattern_match_is_anchored_and_ambiguity_is_rejected(self):
        from mdfixer_engine import find_rule_for_target
        rules, _ = parse_makefile('%.o: %.c\n\tcc -c $< -o $@\n')
        self.assertIsNotNone(find_rule_for_target(rules, 'app.o'))
        self.assertIsNone(find_rule_for_target(rules, 'app.o.backup'))
        rules, _ = parse_makefile('%.o: %.c\na%.o: a%.c\n')
        self.assertIsNone(find_rule_for_target(rules, 'app.o'))

    def test_implicit_flags_are_completed_once(self):
        for flag in ('-MMD', '-MP'):
            content = '%.o: %.c\n\t$(CC) ' + flag + ' -c $< -o $@\n\nclean:\n\trm -f *.o\n'
            patched = self.patch(content)[0]
            self.assertEqual(patched.count('-MMD'), 1)
            self.assertEqual(patched.count('-MP'), 1)
            self.assertEqual(patched.count('-include app.d'), 1)
            self.assertIsNone(self.patch(patched))

    def test_artifact_symlink_escape_and_local_path_are_rejected(self):
        from mdfixer_core import load_md_report
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_root = root / 'artifacts'
            folder = artifact_root / 'b11/job-md'
            folder.mkdir(parents=True)
            outside = root / 'outside.json'
            outside.write_text('{"findings": []}')
            (folder / 'report.json').symlink_to(outside)
            with self.assertRaises(ValueError):
                load_md_report('artifact://b11/job-md/report.json', artifact_root)
            with self.assertRaises(ValueError):
                load_md_report(str(outside), artifact_root)


if __name__ == '__main__':
    unittest.main()
