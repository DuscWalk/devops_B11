from __future__ import annotations

import difflib

from mdfixer_engine import find_rule_for_target


def generate_patch_for_missing(makefile_content, rules, missing):
    rule = find_rule_for_target(rules, missing.target)
    if rule is None:
        return None
    dep = missing.dependency
    if dep in rule.prerequisites:
        return None
    lines = makefile_content.split("
")
    rule_idx = rule.line_no - 1
    line = lines[rule_idx]
    colon_idx = line.index(":")
    target_part = line[:colon_idx]
    prereq_part = line[colon_idx + 1:]
    new_prereq = prereq_part.rstrip()
    backslash = chr(92)
    if new_prereq and not new_prereq.endswith(backslash):
        new_prereq = new_prereq + " " + dep
    elif new_prereq.endswith(backslash):
        new_prereq = new_prereq + "
	" + dep + " " + backslash
    else:
        new_prereq = " " + dep
    lines[rule_idx] = target_part + ":" + new_prereq
    patched = "
".join(lines)
    desc = "add missing dependency " + dep + " to " + missing.target
    return patched, desc


def make_unified_diff(original, patched, filename):
    orig_lines = original.splitlines(keepends=True)
    patched_lines = patched.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        patched_lines,
        fromfile="a/" + filename,
        tofile="b/" + filename,
        lineterm="",
    )
    return "".join(diff)
