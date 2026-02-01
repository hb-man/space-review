# Space Review CLI - Detailed Options

## Input Formats

```bash
# Code Review ID
space-review IJ-CR-174369

# Merge Request ID
space-review IJ-MR-188658

# Space URL
space-review "https://jetbrains.team/p/ij/reviews/174369/timeline"
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
space-review IJ-CR-174369

# Plain markdown for piping/files
space-review IJ-CR-174369 --plain -o review.md

# Only unresolved discussions
space-review IJ-CR-174369 --unresolved

# JSON output for processing
space-review IJ-CR-174369 --json
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
