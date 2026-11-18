"""B11 integration boundary for the restricted classroom MDfixer.

The reference patch algorithm stays in lab.py. This wrapper checks report
identity and committed input before delegating; it never applies a patch.
It is a sequential local experiment interface, not a hostile-repository sandbox.
"""
import hashlib
import re
from pathlib import Path

from lab import patch, run


def source_hashes(project):
    """Hash tracked files, including the link text for symlinks, without writes."""
    project = Path(project)
    names = run(['git', 'ls-files', '-z'], project).split('\0')
    result = {}
    for name in filter(None, names):
        path = project / name
        data = str(path.readlink()).encode() if path.is_symlink() else path.read_bytes()
        result[name] = hashlib.sha256(data).hexdigest()
    return result


def prepare_candidate(project, report):
    """Return (unified diff, plan, receipt) for a clean, matching sample commit.

    Exact schema/profile names refer to the course adapter contract, not a
    claim of interoperability with A11's service or arbitrary Make projects.
    """
    project = Path(project).resolve()
    if not isinstance(report, dict) or report.get('schema_version') != 'e8e10-1':
        raise ValueError('INVALID_REPORT_SCHEMA')
    if report.get('profile') != 'GCC_LOCAL_HEADERS_EXPLICIT_MAKE':
        raise ValueError('UNSUPPORTED_PROFILE')
    revision = report.get('commit')
    if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('INVALID_REPORT_COMMIT')
    if revision != run(['git', 'rev-parse', 'HEAD'], project).strip():
        raise ValueError('STALE_REPORT')
    # HEAD alone does not bind an edited working tree to its old report.
    if run(['git', 'status', '--porcelain', '--untracked-files=all'], project):
        raise ValueError('DIRTY_PROJECT')
    if (project / 'Makefile').is_symlink():
        raise ValueError('UNSAFE_MAKEFILE')
    findings = report.get('findings')
    if not isinstance(findings, list):
        raise ValueError('INVALID_FINDINGS')
    tracked = set(filter(None, run(['git', 'ls-files', '-z'], project).split('\0')))
    unique_missing = {}
    for finding in findings:
        if (not isinstance(finding, dict)
                or finding.get('type') not in ('MISSING', 'REDUNDANT')
                or not isinstance(finding.get('target'), str)
                or not isinstance(finding.get('dependency'), str)):
            raise ValueError('INVALID_FINDING')
        if finding['type'] != 'MISSING':
            continue
        dep = finding['dependency']
        if (not re.fullmatch(r'[\w./-]+', dep) or Path(dep).is_absolute()
                or '..' in Path(dep).parts
                or not (project / dep).resolve().is_relative_to(project)):
            raise ValueError('UNSAFE_PATH')
        if not (project / dep).is_file():
            raise ValueError('MISSING_INPUT')
        # A tracked symlink can still point to an ignored, uncommitted file.
        # Bind both its link text and its resolved content to this commit.
        resolved_name = (project / dep).resolve().relative_to(project).as_posix()
        if dep not in tracked or resolved_name not in tracked:
            raise ValueError('UNTRACKED_DEPENDENCY')
        unique_missing.setdefault((finding['target'], dep), finding)
    before = source_hashes(project)
    diff, plan = patch(project, {**report, 'findings': list(unique_missing.values())})
    # In the course profile a macro-style edit appends to a single NAME = line.
    # Reject another reference anywhere, including an alias in a variable value.
    makefile = (project / 'Makefile').read_text()
    for name in re.findall(r'^\+(\w+) = ', diff, re.M):
        references = makefile.count('$(' + name + ')') + makefile.count('${' + name + '}')
        if references > 1:
            raise ValueError('SHARED_VARIABLE')
    if source_hashes(project) != before:
        raise RuntimeError('SOURCE_CHANGED')
    return diff, plan, {'sample_commit': revision, 'source_sha256': before,
                        'source_unchanged': True, 'candidate_only': True}
