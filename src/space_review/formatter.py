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


def _find_selected_indices(
    snippet: list[dict],
    anchor_line: int | None,
    anchor_old_line: int | None,
    end_line: int | None,
    old_end_line: int | None,
) -> set[int]:
    selected = set()
    for i, line in enumerate(snippet):
        new_num = line.get("new_line")
        old_num = line.get("old_line")

        in_new_range = (
            anchor_line is not None and new_num is not None and
            anchor_line <= new_num <= (end_line if end_line is not None else anchor_line)
        )
        in_old_range = (
            anchor_old_line is not None and old_num is not None and
            anchor_old_line <= old_num <= (old_end_line if old_end_line is not None else anchor_old_line)
        )

        if in_new_range or in_old_range:
            selected.add(i)

    return selected


def _format_snippet_line(line: dict, is_selected: bool) -> str:
    old_num = line.get("old_line")
    new_num = line.get("new_line")
    line_type = line.get("type")
    text = line.get("text", "")

    old_str = str(old_num + 1) if old_num is not None else ""
    new_str = str(new_num + 1) if new_num is not None else ""

    if line_type == "ADDED":
        marker = "+"
    elif line_type == "DELETED":
        marker = "-"
    else:
        marker = " "

    select_marker = ">" if is_selected else " "

    return f"{select_marker} {old_str:>4} {new_str:>4} {marker} {text}"


def _format_discussion(discussion: dict) -> str:
    lines = []

    filename = discussion["filename"]
    line_num = discussion["line"]
    display_line = line_num + 1 if line_num is not None else 0
    resolved = discussion.get("resolved", False)
    status_icon = "✅" if resolved else "💬"

    lines.append(f"### {status_icon} `{filename}:{display_line}`")
    lines.append("")

    language = _detect_language(filename)
    snippet = discussion.get("snippet", [])
    anchor_line = discussion.get("line")
    anchor_old_line = discussion.get("old_line")
    end_line = discussion.get("end_line")
    old_end_line = discussion.get("old_end_line")

    if snippet:
        if isinstance(snippet[0], dict):
            selected_indices = _find_selected_indices(
                snippet, anchor_line, anchor_old_line, end_line, old_end_line
            )
            lines.append("```")
            for i, snippet_line in enumerate(snippet):
                lines.append(_format_snippet_line(snippet_line, i in selected_indices))
            lines.append("```")
        else:
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

    lines.append("```")
    lines.append("Legend: + added | - deleted | > selected lines")
    lines.append("```")
    lines.append("")

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


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


def _color_snippet_line(line: dict, is_selected: bool) -> str:
    old_num = line.get("old_line")
    new_num = line.get("new_line")
    line_type = line.get("type")
    text = line.get("text", "")

    old_str = str(old_num + 1) if old_num is not None else ""
    new_str = str(new_num + 1) if new_num is not None else ""

    if line_type == "ADDED":
        marker = "+"
        line_color = Colors.GREEN
    elif line_type == "DELETED":
        marker = "-"
        line_color = Colors.RED
    else:
        marker = " "
        line_color = ""

    if is_selected:
        select_marker = f"{Colors.YELLOW}{Colors.BOLD}>{Colors.RESET}"
        content = f"{line_color}{old_str:>4} {new_str:>4} {marker} {text}{Colors.RESET if line_color else ''}"
    else:
        select_marker = " "
        if line_color:
            content = f"{line_color}{old_str:>4} {new_str:>4} {marker} {text}{Colors.RESET}"
        else:
            content = f"{old_str:>4} {new_str:>4} {marker} {text}"

    return f"{select_marker} {content}"


def _format_discussion_color(discussion: dict) -> str:
    lines = []

    filename = discussion["filename"]
    line_num = discussion["line"]
    display_line = line_num + 1 if line_num is not None else 0
    resolved = discussion.get("resolved", False)
    status = f"{Colors.GREEN}✓ Resolved{Colors.RESET}" if resolved else f"{Colors.YELLOW}○ Open{Colors.RESET}"

    lines.append(f"{Colors.BOLD}{Colors.BLUE}{filename}:{display_line}{Colors.RESET}  {status}")
    lines.append("")

    snippet = discussion.get("snippet", [])
    anchor_line = discussion.get("line")
    anchor_old_line = discussion.get("old_line")
    end_line = discussion.get("end_line")
    old_end_line = discussion.get("old_end_line")

    if snippet:
        if isinstance(snippet[0], dict):
            selected_indices = _find_selected_indices(
                snippet, anchor_line, anchor_old_line, end_line, old_end_line
            )
            for i, snippet_line in enumerate(snippet):
                lines.append(_color_snippet_line(snippet_line, i in selected_indices))
        else:
            for snippet_line in snippet:
                lines.append(f"  {snippet_line}")
        lines.append("")

    author = discussion["author"]
    text = discussion["text"]
    lines.append(f"{Colors.CYAN}{Colors.BOLD}{author}:{Colors.RESET}")
    for text_line in text.split('\n'):
        lines.append(f"  {text_line}")
    lines.append("")

    suggested_edit = discussion.get("suggested_edit")
    if suggested_edit:
        lines.append(f"{Colors.MAGENTA}Suggested Edit:{Colors.RESET}")
        diff = format_suggested_edit_diff(
            suggested_edit["original"], suggested_edit["suggested"]
        )
        for diff_line in diff.split('\n'):
            if diff_line.startswith('+'):
                lines.append(f"  {Colors.GREEN}{diff_line}{Colors.RESET}")
            elif diff_line.startswith('-'):
                lines.append(f"  {Colors.RED}{diff_line}{Colors.RESET}")
            else:
                lines.append(f"  {diff_line}")
        lines.append("")

    thread = discussion.get("thread", [])
    if thread:
        lines.append(f"{Colors.DIM}─── {len(thread)} replies ───{Colors.RESET}")
        for message in thread:
            lines.append(f"  {Colors.CYAN}{message['author']}:{Colors.RESET}")
            for msg_line in message['text'].split('\n'):
                lines.append(f"    {msg_line}")
        lines.append("")

    lines.append(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
    lines.append("")

    return "\n".join(lines)


def format_color(review: dict, discussions: list[dict], general_comments: list[dict] | None = None) -> str:
    lines = []

    lines.append(f"{Colors.DIM}Legend:{Colors.RESET} {Colors.GREEN}+ added{Colors.RESET} | {Colors.RED}- deleted{Colors.RESET} | {Colors.YELLOW}{Colors.BOLD}>{Colors.RESET} selected")
    lines.append("")

    title = review["title"]
    lines.append(f"{Colors.BOLD}{Colors.WHITE}{title}{Colors.RESET}")
    lines.append("")

    project_key = review["project"]["key"]
    number = review["number"]
    state = review["state"]
    state_color = Colors.GREEN if state == "Opened" else Colors.RED if state == "Closed" else Colors.WHITE
    lines.append(f"{Colors.DIM}Review:{Colors.RESET} {project_key}-CR-{number}  {Colors.DIM}State:{Colors.RESET} {state_color}{state}{Colors.RESET}")
    lines.append("")

    if general_comments:
        resolved_gc = sum(1 for c in general_comments if c.get("resolved"))
        unresolved_gc = len(general_comments) - resolved_gc
        lines.append(f"{Colors.BOLD}General Comments{Colors.RESET} ({Colors.YELLOW}{unresolved_gc} open{Colors.RESET}, {Colors.GREEN}{resolved_gc} resolved{Colors.RESET})")
        lines.append(f"{Colors.DIM}{'═' * 60}{Colors.RESET}")
        lines.append("")
        for comment in general_comments:
            resolved = comment.get("resolved")
            status = f"{Colors.GREEN}✓{Colors.RESET}" if resolved else f"{Colors.YELLOW}○{Colors.RESET}" if resolved is False else f"{Colors.DIM}?{Colors.RESET}"
            lines.append(f"{status} {Colors.CYAN}{Colors.BOLD}{comment['author']}:{Colors.RESET}")
            for text_line in comment["text"].split('\n'):
                lines.append(f"    {text_line}")
            lines.append("")
            lines.append(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
            lines.append("")

    if discussions:
        resolved_count = sum(1 for d in discussions if d.get("resolved"))
        unresolved_count = len(discussions) - resolved_count
        lines.append(f"{Colors.BOLD}Code Discussions{Colors.RESET} ({Colors.YELLOW}{unresolved_count} open{Colors.RESET}, {Colors.GREEN}{resolved_count} resolved{Colors.RESET})")
        lines.append(f"{Colors.DIM}{'═' * 60}{Colors.RESET}")
        lines.append("")

        for discussion in discussions:
            lines.append(_format_discussion_color(discussion))

    return "\n".join(lines)
