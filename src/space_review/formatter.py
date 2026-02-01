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
    ".bazel": "starlark",
    ".bzl": "starlark",
}


def _detect_language(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext, "")


def _indent_text(text: str, indent: str = "    ") -> str:
    return "\n".join(indent + line if line else "" for line in text.split("\n"))


def _format_discussion(discussion: dict) -> str:
    lines = []

    filename = discussion["filename"]
    line_num = discussion["line"]
    resolved = discussion.get("resolved", False)
    status_icon = "✅" if resolved else "💬"

    lines.append(f"### {status_icon} `{filename}:{line_num}`")
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
    lines.append(f"**{author}**")
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
    if thread:
        lines.append("<details>")
        lines.append(f"<summary>💬 {len(thread)} replies</summary>")
        lines.append("")
        for message in thread:
            lines.append(f"> **{message['author']}:**")
            for msg_line in message['text'].split('\n'):
                lines.append(f"> {msg_line}")
            lines.append(">")
        lines.append("</details>")
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def format_markdown(review: dict, discussions: list[dict], general_comments: list[dict] | None = None) -> str:
    lines = []

    title = review["title"]
    lines.append(f"# {title}")
    lines.append("")

    project_key = review["project"]["key"]
    number = review["number"]
    state = review["state"]
    state_icon = "🟢" if state == "Opened" else "🔴" if state == "Closed" else "⚪"
    lines.append(f"**Review:** `{project_key}-CR-{number}` | **State:** {state_icon} {state}")
    lines.append("")

    if general_comments:
        resolved_gc = sum(1 for c in general_comments if c.get("resolved"))
        unresolved_gc = len(general_comments) - resolved_gc
        lines.append(f"## 💬 General Comments ({unresolved_gc} unresolved, {resolved_gc} resolved)")
        lines.append("")
        for comment in general_comments:
            resolved = comment.get("resolved")
            status_icon = "✅" if resolved else "💬" if resolved is False else "💭"
            lines.append(f"### {status_icon} **{comment['author']}**")
            lines.append("")
            for text_line in comment["text"].split('\n'):
                lines.append(f"> {text_line}")
            lines.append("")
            lines.append("---")
            lines.append("")

    if discussions:
        resolved_count = sum(1 for d in discussions if d.get("resolved"))
        unresolved_count = len(discussions) - resolved_count
        lines.append(f"## 📝 Code Discussions ({unresolved_count} unresolved, {resolved_count} resolved)")
        lines.append("")

        for discussion in discussions:
            lines.append(_format_discussion(discussion))

    return "\n".join(lines)


def format_json(review: dict, discussions: list[dict], general_comments: list[dict] | None = None) -> str:
    output = {
        "review": {
            "title": review["title"],
            "project": review["project"]["key"],
            "number": review["number"],
            "state": review["state"],
        },
        "general_comments": general_comments or [],
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
