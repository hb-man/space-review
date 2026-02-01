---
name: space-review
description: Fetch JetBrains Space code reviews with discussions, suggestions, and inline diffs
disable-model-invocation: true
argument-hint: <review-id> [--unresolved] [--json] [--color]
allowed-tools: Bash(space-review:*)
---

# Space Review CLI

Fetch code review feedback from JetBrains Space in chronological order.

## Quick Start

```bash
# Paste a review URL (plain markdown by default)
space-review "https://<SPACE>.jetbrains.space/p/PROJECT/reviews/123456/timeline"

# Or use review ID
space-review PROJECT-CR-123456

# With colors for terminal
space-review $ARGUMENTS --color
```

## Output

- Comments, discussions, and suggestions in **chronological order**
- Inline diffs for modified lines: `[-deleted-][+inserted+]`
- Code suggestions marked with 💡
- Line markers: `+` added, `-` deleted, `*` modified, `>` selected

## Options

- `--color` - Colored terminal output (default is plain markdown)
- `--json` - JSON output
- `--unresolved` - Only unresolved feedback
- `-o, --output PATH` - Export to file
- `--token TEXT` - Space API token

See [references/options.md](references/options.md) for details.
