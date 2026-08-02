# GitHub MCP Server for WebStaffr

MCP server for GitHub API integration focused on WebStaffr development workflow.

## Features

- **Code Search** — Find patterns, validate tenant scoping, locate functions
- **Issue & PR Tracking** — List active work, filter by state/labels
- **Commit Inspection** — Recent commits, branch state, push readiness
- **File Search** — Locate files by name or glob pattern

## Installation

```bash
cd github-mcp-server
pip install -e .
```

## Configuration

Set environment variables:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
export GITHUB_REPO_OWNER=keithtortorich
export GITHUB_REPO_NAME=WebStaffr4.0
```

**Token Requirements:**
- Must have `read:repo` scope (read repository code, issues, PRs)
- Must have `read:user` scope (read user profile)
- Create at: https://github.com/settings/tokens

## Usage

### Local (stdio)

```bash
python -m github_mcp.server
```

### In Claude

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "github-webstaffr": {
      "command": "python",
      "args": ["-m", "github_mcp.server"],
      "env": {
        "GITHUB_TOKEN": "your_token_here",
        "GITHUB_REPO_OWNER": "keithtortorich",
        "GITHUB_REPO_NAME": "WebStaffr4.0"
      }
    }
  }
}
```

## Tools

### `github_search_code`
Search repository code by pattern.

```
query: "tenant_id WHERE"  # Find all SQL queries mentioning tenant
limit: 20                  # Max results
response_format: "markdown" or "json"
```

### `github_list_issues`
List issues and PRs with optional filtering.

```
state: "open" or "closed" or "all"  # Filter by state
labels: "bug,urgent"                 # Optional comma-separated labels
limit: 20                            # Max results
response_format: "markdown" or "json"
```

### `github_get_commit_info`
Get recent commits on a branch.

```
branch: "main"                       # Branch name
limit: 10                            # Number of commits
response_format: "markdown" or "json"
```

### `github_search_files`
Find files by name or pattern.

```
pattern: "*.py" or "site_renderer" or "test_*"
response_format: "markdown" or "json"
```

## Development

Run tests:

```bash
pytest tests/
```

## Architecture

- **FastMCP** — High-level framework for MCP servers
- **PyGithub** — GitHub API wrapper
- **Pydantic** — Input validation
- **stdio transport** — Local subprocess communication

## Future Enhancements

- HTTP transport for remote access
- Workflow status checks
- Release info
- PR review integration
- Branch protection status
