# Space Code Review CLI

CLI to fetch code reviews from JetBrains Space with discussion threads and code snippets.

## Installation

### Quick Install (macOS/Linux)

```bash
./scripts/install.sh           # Install
./scripts/install.sh update    # Update to latest
./scripts/install.sh uninstall # Remove
```

Installs `uv` if needed, copies the tool to `~/.local/share/uv/tools/`, and adds `space-review` to `~/.local/bin`. The repo can be deleted after install.

### Standalone Executable

Build a self-contained executable (~700KB) that only requires Python:

```bash
./scripts/build-executable.sh
```

Creates `dist/space-review` which you can copy anywhere.

### Without Installing

Run directly from the source directory:

```bash
uv sync
uv run space-review IJ-CR-174369
```

## Configuration

The tool requires a JetBrains Space API token.

### Creating a Token

1. Go to `https://<YOUR-SPACE>.jetbrains.space/m/User.Name/authentication?tab=ApplicationPasswords`
2. Click **New application password**
3. Select the projects you need access to
4. Enable these permissions:
   - **Code Reviews** → Read
   - **Chats** → View messages
5. Copy the generated token

### Setting the Token

Configure via (in priority order):
1. `--token` flag
2. `SPACE_TOKEN` environment variable
3. `.env` file with `SPACE_TOKEN=your_token`

## Usage

### Basic Usage

```bash
# By URL (paste from browser)
space-review "https://<YOUR-SPACE>.jetbrains.space/p/PROJECT/reviews/123456/timeline"

# By review ID
space-review PROJECT-CR-123456
space-review PROJECT-MR-123456
```

### Output Options

```bash
# Default: Colored terminal output
space-review IJ-CR-174369

# Plain markdown (no colors, for piping/files)
space-review IJ-CR-174369 --plain

# Export to markdown file
space-review IJ-CR-174369 --plain -o review.md

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

Code snippets show diff-style formatting with line numbers and selection markers:

```
Legend: + added | - deleted | > selected

   182  182       }
>       184 +     // Ensure HOME is set (Bazelisk requires it)
>       185 +     val userHome = System.getProperty("user.home")
>       186 +     if (commandLine.environment["HOME"] == null) {
>       187 +       commandLine.withEnvironment("HOME", userHome)
>       188 +     }
   184  192       commandLine.withRedirectErrorStream(false)
```

- **Two columns**: old line number, new line number
- **`+`**: Added line (green in color mode)
- **`-`**: Deleted line (red in color mode)
- **`>`**: Selected lines being discussed (yellow marker)

## CLI Reference

```
Usage: space-review [OPTIONS] REVIEW_ID

  Fetch code review discussions from JetBrains Space.

  REVIEW_ID can be in format: IJ-CR-174369, IJ-MR-188658, or a Space URL.

Options:
  --json              Output as JSON
  --plain             Output as plain markdown (no colors)
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
├── AGENTS.md                # Instructions for AI agents
├── openapi.json             # Full Space API spec (2.4MB)
├── openapi.min.json         # Minified spec (1.2MB)
├── openapi-endpoints.txt    # Endpoint index (46KB)
├── openapi-schema-names.txt # Schema names (51KB)
└── pyproject.toml
```

## For AI Agents

See [AGENTS.md](AGENTS.md).

## Features

- Accepts review IDs (`IJ-CR-*`, `IJ-MR-*`) or Space URLs
- Fetches general comments and code discussions with full thread content
- Diff-style code snippets with line numbers, add/delete markers, and selection highlighting
- Colored terminal output (default) or plain markdown
- Filters bot comments (Patronus) and supports `--unresolved` filtering
- JSON output for programmatic use
