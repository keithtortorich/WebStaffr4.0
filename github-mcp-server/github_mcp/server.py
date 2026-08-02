#!/usr/bin/env python3
"""
MCP Server for GitHub API integration.

Focused on WebStaffr development workflow: code search, issue tracking,
commit inspection, and push readiness checks.

Uses MCP 2.0 SDK with stdio transport.
"""

import os
import json
import asyncio
from typing import Optional

from mcp.server import Server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field, ConfigDict
from github import Github, GithubException, Repository
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("github_mcp")


# GitHub client initialization
def _get_github_client():
    """Initialize GitHub client from GITHUB_TOKEN env var."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN environment variable is required. "
            "Provide a GitHub Personal Access Token with read:repo and read:user scopes."
        )
    return Github(token)


def _get_repo() -> Repository.Repository:
    """Get WebStaffr repository."""
    client = _get_github_client()
    owner = os.getenv("GITHUB_REPO_OWNER", "keithtortorich")
    name = os.getenv("GITHUB_REPO_NAME", "WebStaffr4.0")
    return client.get_user(owner).get_repo(name)


# Input validation models
class CodeSearchInput(BaseModel):
    """Input model for code search operations."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    query: str = Field(
        ...,
        description="Search query (e.g., 'tenant_id WHERE', 'def create_app')",
        min_length=2,
        max_length=200
    )
    limit: Optional[int] = Field(
        default=20,
        description="Maximum results to return",
        ge=1,
        le=100
    )
    response_format: str = Field(
        default="markdown",
        description="Output format: 'markdown' or 'json'"
    )


# Tool handlers
async def handle_code_search(query: str, limit: int = 20, response_format: str = "markdown") -> str:
    """Search for code patterns in WebStaffr repository."""
    try:
        repo = _get_repo()
        results = repo.search_code(query)

        matches = []
        for idx, item in enumerate(results):
            if idx >= limit:
                break
            matches.append({
                "file": item.path,
                "url": item.html_url,
            })

        if not matches:
            return f"No code matches found for '{query}'"

        if response_format == "markdown":
            lines = [f"# Code Search: '{query}'", ""]
            lines.append(f"Found {len(matches)} matches:\n")
            for match in matches:
                lines.append(f"- `{match['file']}`")
                lines.append(f"  {match['url']}")
            return "\n".join(lines)
        else:
            return json.dumps({
                "query": query,
                "count": len(matches),
                "matches": matches
            }, indent=2)

    except GithubException as e:
        if e.status == 422:
            return "Error: Invalid query syntax"
        elif e.status == 403:
            return "Error: GitHub API rate limit exceeded"
        return f"Error: GitHub API error {e.status}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Code search error: {e}")
        return f"Error: {str(e)}"


async def handle_list_issues(state: str = "open", labels: Optional[str] = None, limit: int = 20, response_format: str = "markdown") -> str:
    """List issues and pull requests."""
    try:
        repo = _get_repo()
        label_list = [l.strip() for l in labels.split(",")] if labels else None

        issues = repo.get_issues(state=state, labels=label_list)

        items = []
        for issue in issues:
            if len(items) >= limit:
                break
            item_type = "PR" if issue.pull_request else "Issue"
            items.append({
                "number": issue.number,
                "title": issue.title,
                "type": item_type,
                "state": issue.state,
                "url": issue.html_url,
            })

        if not items:
            return f"No {state} issues found"

        if response_format == "markdown":
            lines = [f"# {state.capitalize()} Issues & PRs", ""]
            lines.append(f"Found {len(items)} items\n")
            for item in items:
                lines.append(f"## [{item['type']}] {item['title']} (#{item['number']})")
                lines.append(f"- State: {item['state']}")
                lines.append(f"- {item['url']}")
                lines.append("")
            return "\n".join(lines)
        else:
            return json.dumps({
                "state": state,
                "count": len(items),
                "items": items
            }, indent=2)

    except GithubException as e:
        return f"Error: GitHub API error {e.status}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"List issues error: {e}")
        return f"Error: {str(e)}"


async def handle_get_commits(branch: str = "main", limit: int = 10, response_format: str = "markdown") -> str:
    """Get recent commits on a branch."""
    try:
        repo = _get_repo()
        commits = repo.get_commits(sha=branch)

        commit_list = []
        for commit in commits:
            if len(commit_list) >= limit:
                break
            commit_list.append({
                "sha": commit.sha[:8],
                "message": commit.commit.message.split("\n")[0],
                "author": commit.commit.author.name if commit.commit.author else "Unknown",
                "url": commit.html_url
            })

        if not commit_list:
            return f"No commits found on branch '{branch}'"

        if response_format == "markdown":
            lines = [f"# Recent Commits: '{branch}'", ""]
            for commit in commit_list:
                lines.append(f"## {commit['sha']} - {commit['message']}")
                lines.append(f"- Author: {commit['author']}")
                lines.append(f"- {commit['url']}")
                lines.append("")
            return "\n".join(lines)
        else:
            return json.dumps({
                "branch": branch,
                "count": len(commit_list),
                "commits": commit_list
            }, indent=2)

    except GithubException as e:
        if e.status == 404:
            return f"Error: Branch '{branch}' not found"
        return f"Error: GitHub API error {e.status}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Get commits error: {e}")
        return f"Error: {str(e)}"


async def handle_search_files(pattern: str, response_format: str = "markdown") -> str:
    """Search for files by name pattern."""
    try:
        repo = _get_repo()
        files = []

        def search_tree(contents):
            for item in contents:
                if item.type == "dir":
                    try:
                        search_tree(repo.get_contents(item.path))
                    except GithubException:
                        pass
                elif item.type == "file":
                    if _matches_pattern(item.name, pattern):
                        files.append({
                            "name": item.name,
                            "path": item.path,
                            "url": item.html_url,
                        })

        try:
            root_contents = repo.get_contents("")
            search_tree(root_contents)
        except GithubException as e:
            if e.status == 404:
                return "Error: Repository root not accessible"

        if not files:
            return f"No files matching pattern '{pattern}' found"

        if response_format == "markdown":
            lines = [f"# File Search: '{pattern}'", ""]
            lines.append(f"Found {len(files)} files:\n")
            for file in files[:50]:
                lines.append(f"- {file['path']}")
            if len(files) > 50:
                lines.append(f"\n... and {len(files) - 50} more")
            return "\n".join(lines)
        else:
            return json.dumps({
                "pattern": pattern,
                "count": len(files),
                "files": files[:50]
            }, indent=2)

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Search files error: {e}")
        return f"Error: {str(e)}"


def _matches_pattern(filename: str, pattern: str) -> bool:
    """Simple glob-like pattern matching."""
    if pattern == "*" or pattern == "":
        return True
    if "*" not in pattern:
        return pattern in filename
    parts = pattern.split("*")
    if len(parts) == 2:
        return filename.startswith(parts[0]) and filename.endswith(parts[1])
    return pattern in filename


# Tool definitions
TOOLS = [
        Tool(
            name="github_search_code",
            description="Search for code patterns in WebStaffr repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'tenant_id WHERE')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (1-100)",
                        "default": 20
                    },
                    "response_format": {
                        "type": "string",
                        "description": "Output format: 'markdown' or 'json'",
                        "default": "markdown"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="github_list_issues",
            description="List issues and PRs",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "'open', 'closed', or 'all'",
                        "default": "open"
                    },
                    "labels": {
                        "type": "string",
                        "description": "Comma-separated labels"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results",
                        "default": 20
                    },
                    "response_format": {
                        "type": "string",
                        "default": "markdown"
                    }
                }
            }
        ),
        Tool(
            name="github_get_commit_info",
            description="Get recent commits on a branch",
            inputSchema={
                "type": "object",
                "properties": {
                    "branch": {
                        "type": "string",
                        "default": "main"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10
                    },
                    "response_format": {
                        "type": "string",
                        "default": "markdown"
                    }
                }
            }
        ),
        Tool(
            name="github_search_files",
            description="Search for files by pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., '*.py', 'test_*')"
                    },
                    "response_format": {
                        "type": "string",
                        "default": "markdown"
                    }
                },
                "required": ["pattern"]
            }
        )
]


async def call_tool(name: str, arguments: dict) -> str:
    """Handle tool calls."""
    if name == "github_search_code":
        return await handle_code_search(
            arguments.get("query", ""),
            arguments.get("limit", 20),
            arguments.get("response_format", "markdown")
        )
    elif name == "github_list_issues":
        return await handle_list_issues(
            arguments.get("state", "open"),
            arguments.get("labels"),
            arguments.get("limit", 20),
            arguments.get("response_format", "markdown")
        )
    elif name == "github_get_commit_info":
        return await handle_get_commits(
            arguments.get("branch", "main"),
            arguments.get("limit", 10),
            arguments.get("response_format", "markdown")
        )
    elif name == "github_search_files":
        return await handle_search_files(
            arguments.get("pattern", ""),
            arguments.get("response_format", "markdown")
        )
    else:
        return f"Error: Unknown tool {name}"


# Register handlers
from mcp.types import ListToolsResult, CallToolResult

@server.request_handler("tools/list")
async def handle_list_tools() -> ListToolsResult:
    return ListToolsResult(tools=TOOLS)


@server.request_handler("tools/call")
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    result = await call_tool(name, arguments)
    return CallToolResult(content=[TextContent(type="text", text=result)])


async def main():
    """Run MCP server over stdio."""
    from mcp.server.stdio import stdio_server
    async with stdio_server(server):
        pass


if __name__ == "__main__":
    asyncio.run(main())
