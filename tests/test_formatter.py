import json
import pytest
from space_review.formatter import (
    format_markdown,
    format_json,
    format_suggested_edit_diff,
)


@pytest.fixture
def sample_review() -> dict:
    return {
        "project": {"key": "IJ"},
        "number": 174369,
        "title": "BAZEL-2284: don't export Kotlin stdlib to avoid red code",
        "state": "Opened",
    }


@pytest.fixture
def sample_discussion() -> dict:
    return {
        "id": "disc-1",
        "filename": "/plugins/bazel/ModuleEntityUpdater.kt",
        "line": 43,
        "resolved": False,
        "snippet": [
            "val libraryDependency = libraries[dependency]",
            "if (libraryDependency != null) {",
            "  val exported = !libraryDependency.isLowPriority",
        ],
        "author": "Andrew.Kozlov",
        "text": "I'd suggest using `exported` word everywhere.",
        "thread": [
            {"author": "Lev.Leontev", "text": "`exported` is another thing"},
            {"author": "Andrew.Kozlov", "text": "Good point, let me fix it"},
        ],
        "suggested_edit": None,
    }


@pytest.fixture
def discussion_with_suggested_edit() -> dict:
    return {
        "id": "disc-2",
        "filename": "/plugins/bazel/Utils.kt",
        "line": 10,
        "resolved": False,
        "snippet": ["fun oldName() {", "  return 42", "}"],
        "author": "Reviewer",
        "text": "Rename this function",
        "thread": [],
        "suggested_edit": {
            "original": "fun oldName() {\n  return 42\n}",
            "suggested": "fun newName(): Int {\n  return 42\n}",
        },
    }


class TestFormatMarkdownReviewHeader:
    def test_format_markdown_review_header(self, sample_review):
        result = format_markdown(sample_review, [])

        assert "# BAZEL-2284: don't export Kotlin stdlib to avoid red code" in result
        assert "`IJ-CR-174369`" in result
        assert "🟢 Opened" in result

    def test_format_markdown_meta_line_format(self, sample_review):
        result = format_markdown(sample_review, [])

        assert "**Review:** `IJ-CR-174369` | **State:** 🟢 Opened" in result


class TestFormatMarkdownCodeDiscussion:
    def test_format_markdown_code_discussion(self, sample_review, sample_discussion):
        result = format_markdown(sample_review, [sample_discussion])

        assert "## Feedback" in result
        # Line 43 (0-indexed) displays as 44 (1-indexed)
        assert "### 💬 `/plugins/bazel/ModuleEntityUpdater.kt:44`" in result

    def test_format_markdown_discussion_metadata(self, sample_review, sample_discussion):
        result = format_markdown(sample_review, [sample_discussion])

        assert "Andrew.Kozlov" in result
        assert "1 unresolved" in result

    def test_format_markdown_resolved_discussion(self, sample_review, sample_discussion):
        sample_discussion["resolved"] = True
        result = format_markdown(sample_review, [sample_discussion])

        assert "✅" in result
        assert "1 resolved" in result


class TestFormatMarkdownSnippet:
    def test_format_markdown_snippet_with_kotlin(self, sample_review, sample_discussion):
        result = format_markdown(sample_review, [sample_discussion])

        assert "```kotlin" in result
        assert "val libraryDependency = libraries[dependency]" in result
        assert "```" in result

    def test_format_markdown_snippet_with_python(self, sample_review, sample_discussion):
        sample_discussion["filename"] = "/src/main.py"
        sample_discussion["snippet"] = ["def hello():", "    return 'world'"]

        result = format_markdown(sample_review, [sample_discussion])

        assert "```python" in result

    def test_format_markdown_snippet_with_java(self, sample_review, sample_discussion):
        sample_discussion["filename"] = "/src/Main.java"
        sample_discussion["snippet"] = ["public class Main {", "}"]

        result = format_markdown(sample_review, [sample_discussion])

        assert "```java" in result

    def test_format_markdown_snippet_unknown_extension(
        self, sample_review, sample_discussion
    ):
        sample_discussion["filename"] = "/config/settings.xyz"
        sample_discussion["snippet"] = ["some content"]

        result = format_markdown(sample_review, [sample_discussion])

        assert "```\n" in result or "```xyz" in result


class TestFormatMarkdownThread:
    def test_format_markdown_thread(self, sample_review, sample_discussion):
        result = format_markdown(sample_review, [sample_discussion])

        assert "> **Lev.Leontev:**" in result
        assert "> `exported` is another thing" in result
        assert "> **Andrew.Kozlov:**" in result
        assert "> Good point, let me fix it" in result

    def test_format_markdown_initial_comment(self, sample_review, sample_discussion):
        result = format_markdown(sample_review, [sample_discussion])

        assert "**Andrew.Kozlov**" in result
        assert "I'd suggest using `exported` word everywhere." in result


class TestFormatMarkdownSuggestedEdit:
    def test_format_markdown_suggested_edit_as_diff(
        self, sample_review, discussion_with_suggested_edit
    ):
        result = format_markdown(sample_review, [discussion_with_suggested_edit])

        assert "**Suggested Edit:**" in result
        assert "```diff" in result
        assert "-fun oldName() {" in result
        assert "+fun newName(): Int {" in result


class TestFormatJson:
    def test_format_json_output(self, sample_review, sample_discussion):
        result = format_json(sample_review, [sample_discussion])

        parsed = json.loads(result)
        assert parsed["review"]["title"] == sample_review["title"]
        assert parsed["review"]["project"] == "IJ"
        assert parsed["review"]["number"] == 174369
        assert parsed["review"]["state"] == "Opened"
        assert len(parsed["discussions"]) == 1
        assert parsed["discussions"][0]["filename"] == sample_discussion["filename"]

    def test_format_json_pretty_printed(self, sample_review, sample_discussion):
        result = format_json(sample_review, [sample_discussion])

        assert "\n" in result
        assert "  " in result

    def test_format_json_empty_discussions(self, sample_review):
        result = format_json(sample_review, [])

        parsed = json.loads(result)
        assert parsed["discussions"] == []


class TestFormatSuggestedEditDiff:
    def test_format_suggested_edit_diff(self):
        original = "fun oldName() {\n  return 42\n}"
        suggested = "fun newName(): Int {\n  return 42\n}"

        result = format_suggested_edit_diff(original, suggested)

        assert "-fun oldName() {" in result
        assert "+fun newName(): Int {" in result
        assert " " in result

    def test_format_suggested_edit_diff_single_line(self):
        original = "val x = 1"
        suggested = "val x = 2"

        result = format_suggested_edit_diff(original, suggested)

        assert "-val x = 1" in result
        assert "+val x = 2" in result


class TestFormatMarkdownGeneralComments:
    def test_format_general_comments_section(self, sample_review):
        general_comments = [
            {"id": "gc-1", "author": "Reviewer", "text": "LGTM!", "resolved": None}
        ]

        result = format_markdown(sample_review, [], general_comments)

        assert "## Feedback" in result
        assert "**Reviewer**" in result
        assert "> LGTM!" in result

    def test_format_general_comments_with_resolved_status(self, sample_review):
        general_comments = [
            {"id": "gc-1", "author": "Dev", "text": "Fixed", "resolved": True},
            {"id": "gc-2", "author": "Dev2", "text": "Pending", "resolved": False},
        ]

        result = format_markdown(sample_review, [], general_comments)

        assert "1 unresolved, 1 resolved" in result
        assert "✅" in result
        assert "💬" in result

    def test_format_general_comments_multiline_text(self, sample_review):
        general_comments = [
            {"id": "gc-1", "author": "Reviewer", "text": "Line 1\nLine 2\nLine 3", "resolved": None}
        ]

        result = format_markdown(sample_review, [], general_comments)

        assert "> Line 1" in result
        assert "> Line 2" in result
        assert "> Line 3" in result

    def test_format_general_comments_unknown_resolved_status(self, sample_review):
        general_comments = [
            {"id": "gc-1", "author": "Reviewer", "text": "Comment", "resolved": None}
        ]

        result = format_markdown(sample_review, [], general_comments)

        assert "💭" in result

    def test_format_no_general_comments_section_when_empty(self, sample_review):
        result = format_markdown(sample_review, [], [])

        assert "General Comments" not in result

    def test_format_json_includes_general_comments(self, sample_review):
        general_comments = [
            {"id": "gc-1", "author": "Reviewer", "text": "Comment", "resolved": True}
        ]

        result = format_json(sample_review, [], general_comments)

        parsed = json.loads(result)
        assert len(parsed["general_comments"]) == 1
        assert parsed["general_comments"][0]["author"] == "Reviewer"


class TestFormatInlineDiff:
    def test_apply_inline_diff_plain(self):
        from space_review.formatter import _apply_inline_diff_plain

        text = "consoleOutput.contains(consoleOutputconsoleText)"
        deletes = [{"start": 23, "length": 13}]
        inserts = [{"start": 36, "length": 11}]

        result = _apply_inline_diff_plain(text, deletes, inserts)

        assert "[-consoleOutput-]" in result
        assert "[+consoleText+]" in result
        assert "consoleOutput.contains(" in result

    def test_apply_inline_diff_plain_no_changes(self):
        from space_review.formatter import _apply_inline_diff_plain

        text = "unchanged line"

        result = _apply_inline_diff_plain(text, None, None)

        assert result == "unchanged line"

    def test_apply_inline_diff_color(self):
        from space_review.formatter import _apply_inline_diff_color, Colors

        text = "consoleOutput.contains(consoleOutputconsoleText)"
        deletes = [{"start": 23, "length": 13}]
        inserts = [{"start": 36, "length": 11}]

        result = _apply_inline_diff_color(text, deletes, inserts)

        assert Colors.RED in result
        assert Colors.STRIKETHROUGH in result
        assert Colors.GREEN in result
        assert "consoleOutput" in result
        assert "consoleText" in result

    def test_format_snippet_line_modified(self):
        from space_review.formatter import _format_snippet_line

        line = {
            "text": "foo(oldValuenewValue)",
            "type": "MODIFIED",
            "old_line": 10,
            "new_line": 10,
            "deletes": [{"start": 4, "length": 8}],
            "inserts": [{"start": 12, "length": 8}],
        }

        result = _format_snippet_line(line, False)

        assert "*" in result
        assert "[-oldValue-]" in result
        assert "[+newValue+]" in result
