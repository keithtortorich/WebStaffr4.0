"""Test input validation schemas."""

import pytest
from pydantic import ValidationError
from github_mcp.server import (
    CodeSearchInput,
    IssueSearchInput,
    CommitInfoInput,
    FileSearchInput,
    ResponseFormat
)


def test_code_search_input_valid():
    """Valid code search input."""
    input_data = CodeSearchInput(
        query="tenant_id WHERE",
        limit=20,
        response_format=ResponseFormat.MARKDOWN
    )
    assert input_data.query == "tenant_id WHERE"
    assert input_data.limit == 20


def test_code_search_input_too_short():
    """Query too short."""
    with pytest.raises(ValidationError):
        CodeSearchInput(query="x")


def test_code_search_input_too_long():
    """Query too long."""
    with pytest.raises(ValidationError):
        CodeSearchInput(query="x" * 300)


def test_issue_search_input_valid():
    """Valid issue search input."""
    input_data = IssueSearchInput(
        state="open",
        labels="bug,urgent",
        limit=10
    )
    assert input_data.state == "open"
    assert input_data.labels == "bug,urgent"


def test_issue_search_input_invalid_state():
    """Invalid state."""
    with pytest.raises(ValidationError):
        IssueSearchInput(state="invalid")


def test_commit_info_input_valid():
    """Valid commit info input."""
    input_data = CommitInfoInput(
        branch="main",
        limit=5
    )
    assert input_data.branch == "main"
    assert input_data.limit == 5


def test_file_search_input_valid():
    """Valid file search input."""
    input_data = FileSearchInput(
        pattern="*.py"
    )
    assert input_data.pattern == "*.py"


def test_file_search_input_empty_pattern():
    """Empty pattern invalid."""
    with pytest.raises(ValidationError):
        FileSearchInput(pattern="")
