from __future__ import annotations

import re

from mdfixer_core import MakefileRule, VariableDef

VAR_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*([:?+]?=)\s*(.*)$")
VAR_REF_RE = re.compile(r"\$\(([A-Za-z_]\w*)\)")


def parse_makefile(content):
    """Index simple rules/variables without evaluating Make expressions.

    Keep the first physical line of continuations so a patch changes the
    declaration, never the last continuation or the following recipe.
    """
    rules, variables = [], []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or line.startswith("\t"):
            i += 1
            continue
        start = i
        logical = line
        while logical.rstrip().endswith("\\") and i + 1 < len(lines):
            i += 1
            logical = logical.rstrip()[:-1] + " " + lines[i].strip()
        logical = logical.split("#", 1)[0].strip()
        match = VAR_RE.fullmatch(logical)
        if match:
            variables.append(VariableDef(
                name=match[1], value=match[3].strip(),
                operator=match[2], line_no=start + 1,
            ))
            i += 1
            continue
        if ":" not in logical:
            i += 1
            continue
        target, prereqs = logical.split(":", 1)
        # Double-colon/static-pattern rules are outside this local subset.
        if ":" in prereqs:
            i += 1
            continue
        recipe = []
        i += 1
        while i < len(lines) and (
            lines[i].startswith("\t") or not lines[i].strip()
            or lines[i].lstrip().startswith("#")
        ):
            if lines[i].startswith("\t"):
                recipe.append(lines[i])
            i += 1
        rules.append(MakefileRule(
            target=target.strip(), prerequisites=prereqs.split(),
            recipe=recipe, line_no=start + 1,
        ))
    return rules, variables


def detect_declaration_style(content, rules):
    return {
        "uses_tab_recipe": any(r.recipe for r in rules),
        "prereq_separator": " ",
        "has_continuation": "\\\n" in content,
        "variable_patterns": re.findall(r"\$\(([A-Za-z_]\w*)\)", content),
    }


def detect_rule_style(rule, variables):
    if "%" in rule.target:
        return "implicit"
    refs = [p for p in rule.prerequisites if VAR_REF_RE.fullmatch(p)]
    if refs:
        return "macro" if len(refs) == len(rule.prerequisites) else "hybrid"
    return "target"


def find_rule_for_target(rules, target):
    exact = [r for r in rules if target in r.target.split()]
    if exact:
        # Multiple declarations/multiple targets require Make semantics.
        return exact[0] if len(exact) == 1 and exact[0].target == target else None
    patterns = [
        r for r in rules
        if r.target.count("%") == 1 and len(r.target.split()) == 1
        and re.fullmatch(re.escape(r.target).replace("%", ".+"), target)
    ]
    return patterns[0] if len(patterns) == 1 else None


def find_variable(variables, name):
    matches = [v for v in variables if v.name == name]
    return matches[0] if len(matches) == 1 else None
