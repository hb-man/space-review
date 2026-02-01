# Space Review CLI - Detailed Options

## Input Formats

```bash
# Space URL (most common - paste from browser)
space-review "https://<SPACE>.jetbrains.space/p/PROJECT/reviews/123456/timeline"

# Code Review ID
space-review PROJECT-CR-123456

# Merge Request ID
space-review PROJECT-MR-123456
```

## Output Options

| Flag | Description |
|------|-------------|
| `--plain` | Plain markdown output (default is colored terminal) |
| `--json` | Output as JSON |
| `--unresolved` | Show only unresolved discussions |
| `--token TEXT` | Space API token (or use SPACE_TOKEN env var) |
| `-o, --output PATH` | Export to file |

## Examples

```bash
# View review in terminal (colored)
space-review "https://<SPACE>.jetbrains.space/p/PROJECT/reviews/123456/timeline"

# Plain markdown for files
space-review "https://<SPACE>.jetbrains.space/p/PROJECT/reviews/123456/timeline" --plain -o review.md

# Only unresolved discussions
space-review "https://<SPACE>.jetbrains.space/p/PROJECT/reviews/123456/timeline" --unresolved

# JSON output for processing
space-review PROJECT-CR-123456 --json
```

## Output Features

- **Colored terminal output** (default) with diff-style code snippets
- **Diff markers**: `+` added, `-` deleted, `>` selected lines
- **Line numbers**: old/new columns for context
- **General comments** with quoted citations
- **Code discussions** with threaded replies
- **Summary** showing unresolved/resolved counts

## Notes

- Bot comments (Patronus) are automatically filtered out
- Supports both Code Reviews (CR) and Merge Requests (MR)
- Works with closed/merged reviews
- Token from `--token` flag > `SPACE_TOKEN` env var > `.env` file
