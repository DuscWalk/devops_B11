from __future__ import annotations
import difflib
import re
from mdfixer_engine import find_rule_for_target


def generate_patch_for_missing(makefile_content, rules, missing):
    rule=find_rule_for_target(rules,missing.target)
    dep=missing.dependency
    if rule is None or dep in rule.prerequisites or not re.fullmatch(r'[A-Za-z0-9_./-]+',dep):
        return None
    if any('$' in token or '%' in token for token in rule.prerequisites):
        return None
    lines=makefile_content.splitlines(keepends=True)
    idx=rule.line_no-1
    line=lines[idx]
    colon=line.index(':')
    # Insert before existing prerequisites, preserving continuations, comments and recipes.
    lines[idx]=line[:colon+1]+' '+dep+line[colon+1:]
    return ''.join(lines),'add missing dependency '+dep+' to '+missing.target


def make_unified_diff(original, patched, filename):
    return ''.join(difflib.unified_diff(
        original.splitlines(keepends=True),patched.splitlines(keepends=True),
        fromfile='a/'+filename,tofile='b/'+filename))
