# Space Code Review CLI

A command-line tool to fetch code reviews from JetBrains Space (jetbrains.team) with full discussion details including code snippets and threaded replies.

## Installation

### Development (requires uv)

```bash
cd space-review
uv sync --all-extras
```

### Standalone executable (Unix)

Build a self-contained executable that only requires Python:

```bash
./scripts/build-executable.sh
```

This creates `dist/space-review` (~700KB) which you can copy anywhere in your PATH.

## Configuration

The tool requires a JetBrains Space API token. Configure it via:

1. `--token` flag (highest priority)
2. `SPACE_TOKEN` environment variable
3. `.env` file in the project root

To get a token: JetBrains Space → Your Profile → Personal Tokens → Create new token.

## Usage

### Basic Usage

```bash
# By review ID
space-review IJ-CR-174369
space-review IJ-MR-188658

# By URL
space-review "https://jetbrains.team/p/ij/reviews/174369/timeline"
```

### Output Options

```bash
# Default: Markdown to stdout
space-review IJ-CR-174369

# Export to markdown file
space-review IJ-CR-174369 -o review.md
space-review IJ-CR-174369 --output review.md

# JSON output
space-review IJ-CR-174369 --json
```

### Filtering

```bash
# Only unresolved discussions
space-review IJ-CR-174369 --unresolved
```

### Combined Options

```bash
# Unresolved discussions exported to file
space-review IJ-CR-174369 --unresolved -o unresolved.md

# JSON with unresolved only
space-review IJ-CR-174369 --unresolved --json
```

## Output Format

The markdown output includes:

- **Review header** with title, ID, and status (🔴 Closed / 🟢 Opened)
- **General comments** (non-code review comments) with quoted text
- **Code discussions** grouped by file with:
  - Status icon (✅ resolved / 💬 unresolved)
  - Code snippet with syntax highlighting
  - Initial comment
  - Collapsible thread replies

### Example Output

```markdown
# BAZEL-2843 [bazel]: make unit tests runnable with Bazel

**Review:** `IJ-CR-189586` | **State:** 🔴 Closed

## 💬 General Comments

**Andrzej.Gluszak:**

> >     Add hermetic_cc_toolchain for rules_kotlin 2.0.0 compatibility
>
> sounds suspicious...

---

## 📝 Code Discussions (0 unresolved, 4 resolved)

### ✅ `/plugins/bazel/src/BazelGlobalFunctions.kt:68`

\`\`\`kotlin
val globalFunctions: Map<String, BazelGlobalFunction>
  get() = StarlarkGlobalFunctionProvider.extensionPoint.extensionList
\`\`\`

**Andrzej.Gluszak**

I think it's not the only place where we have such caching

<details>
<summary>💬 5 replies</summary>

> **pasynkov:**
> Any reason to hold it on static?
...
</details>
```

## CLI Reference

```
Usage: space-review [OPTIONS] REVIEW_ID

  Fetch code review discussions from JetBrains Space.

  REVIEW_ID can be in format: IJ-CR-174369, IJ-MR-188658, or a Space URL.

Options:
  --json              Output as JSON
  --unresolved        Show only unresolved discussions
  --token TEXT        Space API token
  -o, --output PATH   Export to markdown file
  --help              Show this message and exit.
```

## Development

### Running Tests

```bash
uv run pytest -v
```

### Project Structure

```
space-review/
├── src/space_review/
│   ├── api.py          # Space API client
│   ├── cli.py          # CLI entry point
│   ├── formatter.py    # Markdown/JSON formatting
│   ├── parser.py       # Review ID/URL parsing
│   └── processor.py    # Data transformation
├── tests/
└── pyproject.toml
```

## Features

- Parses review IDs (`IJ-CR-*`, `IJ-MR-*`) and Space URLs
- Fetches general comments and code discussions
- Gets actual comment text from thread channels (not just "posted a comment")
- Filters out bot comments (Patronus)
- Supports resolved/unresolved filtering
- Syntax highlighting for code snippets (Kotlin, Python, Java, Starlark, etc.)
- Collapsible thread replies in markdown output
