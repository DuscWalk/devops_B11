from __future__ import annotations

import re
from mdfixer_core import MakefileRule


def parse_makefile(content):
    """Index simple explicit rules; keep the first physical line of continuations.

    This local prototype does not evaluate make variables, includes or patterns.
    Unsupported rules are left for manual repair.
    """
    rules = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith('#') or line.startswith('\t'):
            i += 1
            continue
        if re.match(r'^\s*[A-Za-z_]\w*\s*[:?+]?=', line) or ':' not in line:
            i += 1
            continue
        start = i
        logical = line
        while logical.rstrip().endswith('\\'):
            logical = logical.rstrip()[:-1] + ' '
            i += 1
            if i >= len(lines):
                break
            logical += lines[i].strip()
        target, prereq = logical.split(':',1)
        if any(c in target for c in '$%=') or prereq.startswith(':') or ';' in prereq or ':' in prereq:
            i += 1
            continue
        prereq = prereq.split('#',1)[0].split('|',1)[0]
        i += 1
        recipe = []
        while i < len(lines) and (lines[i].startswith('\t') or not lines[i].strip()):
            if lines[i].startswith('\t'):
                recipe.append(lines[i])
            i += 1
        rules.append(MakefileRule(target.strip(),prereq.split(),recipe,start+1))
    return rules


def detect_declaration_style(content, rules):
    return {
        "uses_tab_recipe":any(r.recipe for r in rules),
        "prereq_separator":" ",
        "has_continuation":'\\\n' in content,
        "variable_patterns":re.findall(r'\$\(([A-Za-z_]\w*)\)',content),
        "supported_scope":"simple explicit rules; no variable expansion or pattern repair",
    }


def find_rule_for_target(rules, target):
    matches=[r for r in rules if target in r.target.split()]
    return matches[0] if len(matches)==1 else None
