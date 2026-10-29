"""Deliberately wrong oracle for a protected-branch rejection demonstration.

Use on the demonstration branch. After capturing the failed PR and merge-block
evidence, repair the expected return code from 1 to 0.
"""
from draft.cli import main


def test_version_returns_success_exit_code():
    assert main(["version"]) == 0
