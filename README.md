# Space Code Review CLI

A command-line tool to fetch code reviews from JetBrains Space (jetbrains.team) with full discussion details including code snippets and threaded replies.

## Installation

```bash
# Clone the repository
cd space-review

# Install dependencies with uv
uv sync --all-extras
```

## Configuration

The tool requires a JetBrains Space API token. You can provide it in three ways (in order of precedence):

### 1. Command-line flag
```bash
space-review IJ-CR-174369 --token "eyJ..."
```

### 2. Environment variable
```bash
export SPACE_TOKEN="eyJ..."
space-review IJ-CR-174369
```

### 3. `.env` file
Create a `.env` file in the project root:
```
SPACE_TOKEN=eyJ...
```

To get a token, go to JetBrains Space → Your Profile → Personal Tokens → Create a new token with appropriate permissions.

## Usage

### Basic Usage

Fetch a code review by ID:
```bash
# Code Review format
uv run space-review IJ-CR-174369

# Merge Request format
uv run space-review IJ-MR-188658
```

### URL Input

You can also pass a Space review URL directly:
```bash
uv run space-review "https://jetbrains.team/p/ij/reviews/174369/timeline"
uv run space-review "https://jetbrains.team/p/ij/reviews/174369/files"
```

### Output Formats

#### Markdown (default)
```bash
uv run space-review IJ-CR-174369
```

#### JSON
```bash
uv run space-review IJ-CR-174369 --json
```

### Filtering

Show only unresolved discussions:
```bash
uv run space-review IJ-CR-174369 --unresolved
```

### Combining Options

```bash
# Unresolved discussions in JSON format
uv run space-review IJ-CR-174369 --unresolved --json

# URL with unresolved filter
uv run space-review "https://jetbrains.team/p/ij/reviews/174369/timeline" --unresolved
```

## Output Examples

### Markdown Output

```markdown
# BAZEL-2284: don't export Kotlin stdlib to avoid red code

**Review:** IJ-CR-174369 | **State:** Opened

## Code Discussions

### /plugins/bazel/ModuleEntityUpdater.kt:43

```kotlin
val libraryDependency = libraries[dependency]
if (libraryDependency != null) {
  val exported = !libraryDependency.isLowPriority
```

**Andrew.Kozlov:** (Unresolved)

I'd suggest using `exported` word everywhere.

> **Lev.Leontev:**
> `exported` is another thing that's set per dependency, not per library

> **Andrew.Kozlov:**
> Right now this looks like a hack...
```

### JSON Output

```json
{
  "review": {
    "title": "BAZEL-2284: don't export Kotlin stdlib to avoid red code",
    "project": "IJ",
    "number": 174369,
    "state": "Opened"
  },
  "discussions": [
    {
      "id": "disc-1",
      "filename": "/plugins/bazel/ModuleEntityUpdater.kt",
      "line": 43,
      "resolved": false,
      "snippet": [
        "val libraryDependency = libraries[dependency]",
        "if (libraryDependency != null) {",
        "  val exported = !libraryDependency.isLowPriority"
      ],
      "author": "Andrew.Kozlov",
      "text": "I'd suggest using `exported` word everywhere.",
      "thread": [
        {
          "author": "Lev.Leontev",
          "text": "`exported` is another thing..."
        }
      ]
    }
  ]
}
```

## CLI Reference

```
Usage: space-review [OPTIONS] REVIEW_ID

  Fetch code review discussions from JetBrains Space.

  REVIEW_ID can be in format: IJ-CR-174369, IJ-MR-188658, or a Space URL.

Options:
  --json        Output as JSON
  --unresolved  Show only unresolved discussions
  --token TEXT  Space API token
  --help        Show this message and exit.
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/test_api.py -v

# Run with coverage
uv run pytest --cov=space_review
```

### Project Structure

```
space-review/
├── src/space_review/
│   ├── __init__.py
│   ├── api.py          # Space API client
│   ├── cli.py          # CLI entry point
│   ├── formatter.py    # Markdown/JSON formatting
│   ├── parser.py       # Review ID/URL parsing
│   └── processor.py    # Data transformation
├── tests/
│   ├── conftest.py     # Shared fixtures
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_formatter.py
│   ├── test_parser.py
│   └── test_processor.py
├── .env                # Token configuration
└── pyproject.toml
```

## Dependencies

- **httpx** - HTTP client for API requests
- **click** - CLI framework
- **python-dotenv** - .env file loading
- **pytest** - Testing framework
- **pytest-httpx** - httpx mocking for tests
