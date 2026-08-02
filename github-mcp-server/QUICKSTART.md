# Quick Start

## 1. Install

```bash
cd github-mcp-server
pip install -e .
```

## 2. Configure

```bash
cp .env.example .env
# Edit .env with your GitHub token and repo info
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export GITHUB_REPO_OWNER="keithtortorich"
export GITHUB_REPO_NAME="WebStaffr4.0"
```

Get a token: https://github.com/settings/tokens/new
- Scopes needed: `read:repo`, `read:user`

## 3. Run Locally

```bash
python -m github_mcp.server
```

Will start listening on stdio. Connect via Claude or MCP client.

## 4. Test Tools

From Claude or MCP inspector:

```
Tool: github_search_code
Query: "tenant_id WHERE"
Limit: 20
Response Format: markdown
```

```
Tool: github_list_issues
State: open
Limit: 10
```

```
Tool: github_get_commit_info
Branch: main
Limit: 5
```

```
Tool: github_search_files
Pattern: "*.py"
```

## Deployment to HTTP

To run as a web service:

```python
from github_mcp.server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable_http", port=8000)
```

Then configure in Claude:
```json
{
  "mcpServers": {
    "github": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Next Steps

- Run `pytest tests/` to validate schemas
- Add more tools (branch protection, workflow status)
- Integrate with CI/CD (GitHub Actions)
- Test tenant_id code search validation

## Architecture

- **FastMCP** — Handles MCP protocol
- **PyGithub** — GitHub API client
- **Pydantic** — Input validation
- **stdio** — Local subprocess transport

Tools follow WebStaffr's validation patterns: strict input schemas, error messages with actionable guidance, read-only operations by default.
