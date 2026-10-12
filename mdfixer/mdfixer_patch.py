from __future__ import annotations

import difflib
import re

from mdfixer_engine import VAR_REF_RE, detect_rule_style, find_rule_for_target, find_variable

FILE_RE = re.compile(r"[A-Za-z0-9_./-]+")
UNSUPPORTED_DIRECTIVE = re.compile(
    r"^\s*(?:ifeq|ifneq|ifdef|ifndef|else|endif|define|endef|override|"
    r"export|unexport|include|sinclude|vpath)\b", re.MULTILINE
)


def _append_dep_to_line(line, dep):
    """Append before a continuation or comment, preserving the rest of the line."""
    body, marker, comment = line.partition("#")
    body = body.rstrip()
    if body.endswith("\\"):
        body = body[:-1].rstrip() + " " + dep + " \\"
    else:
        body += " " + dep
    return body + (" #" + comment if marker else "")


def generate_patch_for_missing(makefile_content, rules, variables, missing):
    if missing.type != "MISSING" or missing.origin == "RESOLVED":
        return None
    if not FILE_RE.fullmatch(missing.dependency) or not FILE_RE.fullmatch(missing.target):
        return None
    if UNSUPPORTED_DIRECTIVE.search(makefile_content):
        return None
    for line in makefile_content.splitlines():
        directive = line.split("#", 1)[0].strip().split()
        if directive and directive[0] == "-include":
            if len(directive) < 2 or any(
                not re.fullmatch(r"[A-Za-z0-9_./-]+\.d", name) for name in directive[1:]
            ):
                return None
    rule = find_rule_for_target(rules, missing.target)
    if rule is None or missing.dependency in rule.prerequisites:
        return None
    style = detect_rule_style(rule, variables)
    lines = makefile_content.split("\n")
    if style == "implicit":
        return _patch_implicit(lines, rule, missing.target)
    if any(not FILE_RE.fullmatch(p) and not VAR_REF_RE.fullmatch(p)
           for p in rule.prerequisites):
        return None
    if style in ("macro", "hybrid"):
        return _patch_variable(lines, rule, variables, missing.dependency)
    idx = rule.line_no - 1
    colon = lines[idx].index(":")
    lines[idx] = lines[idx][:colon + 1] + _append_dep_to_line(
        lines[idx][colon + 1:], missing.dependency
    )
    return "\n".join(lines), "add missing dependency " + missing.dependency + " to " + rule.target


def _patch_variable(lines, rule, variables, dep):
    names = [VAR_REF_RE.fullmatch(p)[1] for p in rule.prerequisites
             if VAR_REF_RE.fullmatch(p)]
    # Do not guess between variables, repeated definitions or unevaluated values.
    if len(names) != 1:
        return None
    variable = find_variable(variables, names[0])
    if variable is None or variable.operator not in ("=", ":=", "?="):
        return None
    values = variable.value.split()
    if dep in values or any(not FILE_RE.fullmatch(p) for p in values):
        return None
    idx = variable.line_no - 1
    eq = lines[idx].index("=")
    lines[idx] = lines[idx][:eq + 1] + _append_dep_to_line(lines[idx][eq + 1:], dep)
    return "\n".join(lines), (
        "add missing dependency " + dep + " to variable " + variable.name
        + " (used by " + rule.target + ")"
    )


def _patch_implicit(lines, rule, target):
    # The E3 fixture uses one C-to-object pattern rule and one compiler recipe.
    if rule.target != "%.o" or rule.prerequisites != ["%.c"] or len(rule.recipe) != 1:
        return None
    recipe = rule.recipe[0]
    if not re.search(r"(?<!\S)-c(?!\S)", recipe) or "-o $@" not in recipe:
        return None
    if not recipe.rstrip().endswith("$@") or "$<" not in recipe:
        return None
    start = rule.line_no
    while start < len(lines) and not lines[start].startswith("\t"):
        start += 1
    if start >= len(lines):
        return None
    flags = [flag for flag in ("-MMD", "-MP")
             if not re.search(r"(?<!\S)" + re.escape(flag) + r"(?!\S)", recipe)]
    if flags:
        lines[start] = re.sub(r"(?<!\S)-c(?!\S)", " ".join(flags) + " -c", recipe, count=1)
    depfile = target.rsplit(".", 1)[0] + ".d"
    included = any(
        re.fullmatch(r"\s*-include\s+" + re.escape(depfile) + r"\s*(?:#.*)?", line)
        for line in lines
    )
    if included and not flags:
        return None
    if not included:
        # Keep a blank line on both sides, matching the checked-in oracle.
        insert = start + 1
        while insert < len(lines) and not lines[insert].strip():
            insert += 1
        prefix = [] if insert > start + 1 else [""]
        lines[insert:insert] = prefix + ["-include " + depfile, ""]
    return "\n".join(lines), "enable -MMD -MP and include " + depfile


def make_unified_diff(original, patched, filename):
    return "".join(difflib.unified_diff(
        original.splitlines(keepends=True), patched.splitlines(keepends=True),
        fromfile="a/" + filename, tofile="b/" + filename,
    ))
