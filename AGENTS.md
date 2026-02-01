# Agent Instructions

This file contains instructions for AI agents working with this codebase.

## Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest -v

# Run the CLI
uv run space-review IJ-CR-174369
```

## Project Structure

```
src/space_review/
├── api.py          # Space API client (HTTP requests, auth)
├── cli.py          # CLI entry point (click commands)
├── formatter.py    # Markdown/JSON output formatting
├── parser.py       # Review ID/URL parsing
└── processor.py    # Data transformation (API response → output model)
```

## Testing

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=space_review --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_parser.py -v
```

## Space API Reference

The repository includes JetBrains Space API OpenAPI specification files.

### File Readability

| File | Size | Can Read Fully | Use Case |
|------|------|----------------|----------|
| `openapi-endpoints.txt` | 46KB | ✅ Yes | Browse all 626 API endpoints |
| `openapi-schema-names.txt` | 51KB | ✅ Yes | Browse all 2108 schema type names |
| `openapi.min.json` | 1.2MB | ❌ No (use rg/jq) | Look up full endpoint/schema details |
| `openapi.json` | 2.4MB | ❌ No | Original spec (keep for reference) |

### Workflow

1. **Read** `openapi-endpoints.txt` to find relevant API paths
2. **Read** `openapi-schema-names.txt` to find relevant data types
3. **Use rg/jq** on `openapi.min.json` for full details when needed

### Index File Formats

**`openapi-endpoints.txt`** - One line per endpoint:
```
METHOD /path - [tags]
```

Example:
```
GET /projects/{project}/code-reviews/{reviewId} - []
POST /projects/{project}/code-reviews/merge-requests - []
```

**`openapi-schema-names.txt`** - One schema type name per line:
```
CodeReviewRecord
MergeRequestRecord
TD_MemberProfile
```

### Searching the API

```bash
# Find code review endpoints
rg -i "code-review" openapi-endpoints.txt

# Find schema names containing "Review"
rg -i "review" openapi-schema-names.txt

# Get full schema definition
jq '.components.schemas.CodeReviewRecord' openapi.min.json

# Get full endpoint definition
jq '.paths["/projects/{project}/code-reviews/{reviewId}"]' openapi.min.json

# Get all properties of a schema
jq '.components.schemas.CodeReviewRecord.properties | keys' openapi.min.json
```

## Code Style

- Python 3.10+
- Type hints required
- Use `httpx` for HTTP requests
- Use `click` for CLI
- Prefer dataclasses for data models

## Environment

Requires `SPACE_TOKEN` environment variable or `--token` flag for API access.

## Claude Code Skill

This repo includes a Claude Code skill in the `skill/` directory. **Ask the user if they want it installed.**

### Installing the Skill

```bash
# Copy skill to Claude skills directory
cp -r skill ~/.claude/skills/space-review
```

After installation, users can invoke it via `/space-review IJ-CR-174369` in Claude Code.

### Skill Features

- Fetch reviews by ID or URL
- Colored terminal output with diff-style snippets
- Line numbers with add/delete/selection markers
- Options: `--plain`, `--json`, `--unresolved`, `-o file.md`
