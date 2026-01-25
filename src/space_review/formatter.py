import json
import difflib
from pathlib import Path

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".scala": "scala",
    ".groovy": "groovy",
    ".xml": "xml",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".sql": "sql",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
}


def _detect_language(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext, "")


def _format_discussion(discussion: dict) -> str:
    lines = []

    filename = discussion["filename"]
    line_num = discussion["line"]
    lines.append(f"### {filename}:{line_num}")
    lines.append("")

    language = _detect_language(filename)
    snippet = discussion.get("snippet", [])
    if snippet:
        lines.append(f"```{language}")
        for snippet_line in snippet:
            lines.append(snippet_line)
        lines.append("```")
        lines.append("")

    author = discussion["author"]
    resolved = discussion.get("resolved", False)
    status = "Resolved" if resolved else "Unresolved"
    lines.append(f"**{author}:** ({status})")
    lines.append("")
    lines.append(discussion["text"])
    lines.append("")

    suggested_edit = discussion.get("suggested_edit")
    if suggested_edit:
        lines.append("**Suggested Edit:**")
        lines.append("")
        diff = format_suggested_edit_diff(
            suggested_edit["original"], suggested_edit["suggested"]
        )
        lines.append("```diff")
        lines.append(diff)
        lines.append("```")
        lines.append("")

    thread = discussion.get("thread", [])
    for message in thread:
        lines.append(f"> **{message['author']}:**")
        lines.append(f"> {message['text']}")
        lines.append("")

    return "\n".join(lines)


def format_markdown(review: dict, discussions: list[dict]) -> str:
    lines = []

    title = review["title"]
    lines.append(f"# {title}")
    lines.append("")

    project_key = review["project"]["key"]
    number = review["number"]
    state = review["state"]
    lines.append(f"**Review:** {project_key}-CR-{number} | **State:** {state}")
    lines.append("")

    if discussions:
        lines.append("## Code Discussions")
        lines.append("")

        for discussion in discussions:
            lines.append(_format_discussion(discussion))

    return "\n".join(lines)


def format_json(review: dict, discussions: list[dict]) -> str:
    output = {
        "review": {
            "title": review["title"],
            "project": review["project"]["key"],
            "number": review["number"],
            "state": review["state"],
        },
        "discussions": discussions,
    }
    return json.dumps(output, indent=2)


def format_suggested_edit_diff(original: str, suggested: str) -> str:
    original_lines = original.splitlines(keepends=True)
    suggested_lines = suggested.splitlines(keepends=True)

    if original_lines and not original_lines[-1].endswith("\n"):
        original_lines[-1] += "\n"
    if suggested_lines and not suggested_lines[-1].endswith("\n"):
        suggested_lines[-1] += "\n"

    diff = difflib.unified_diff(
        original_lines,
        suggested_lines,
        fromfile="original",
        tofile="suggested",
        lineterm="",
    )

    diff_lines = list(diff)
    if len(diff_lines) > 2:
        diff_lines = diff_lines[2:]

    return "".join(diff_lines).rstrip("\n")
