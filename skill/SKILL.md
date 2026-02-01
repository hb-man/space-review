---
name: space-review
description: Use to fetch JetBrains Space code reviews with discussions
disable-model-invocation: true
argument-hint: <review-id> [--plain] [--unresolved] [--json]
allowed-tools: Bash(space-review:*)
---

# Space Review CLI

Fetch code review discussions from JetBrains Space.

## Quick Start

```bash
# Paste a review URL (colored output)
space-review "https://<SPACE>.jetbrains.space/p/PROJECT/reviews/123456/timeline"

# Or use review ID
space-review PROJECT-CR-123456

# Plain markdown for files
space-review $ARGUMENTS --plain -o review.md
```

## Options

- `--plain` - Plain markdown (default is colored terminal)
- `--json` - JSON output
- `--unresolved` - Only unresolved discussions
- `-o, --output PATH` - Export to file
- `--token TEXT` - Space API token

See [references/options.md](references/options.md) for details.
