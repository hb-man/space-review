import pytest
from space_review.processor import (
    extract_code_discussions,
    filter_discussions,
    build_discussion_with_thread,
)


class TestExtractCodeDiscussions:
    def test_extract_single_code_discussion(self, sample_feed_message):
        feed_messages = [sample_feed_message]

        result = extract_code_discussions(feed_messages)

        assert len(result) == 1
        discussion = result[0]
        assert discussion["id"] == "disc-1"
        assert discussion["filename"] == "/plugins/bazel/ModuleEntityUpdater.kt"
        assert discussion["line"] == 43
        assert discussion["resolved"] is False
        assert discussion["channel_id"] == "disc-channel-1"
        assert discussion["author"] == "Andrew.Kozlov"
        assert discussion["text"] is None
        assert discussion["suggested_edit"] is None
        assert discussion["thread"] == []

    def test_extract_code_discussion_snippet(self, sample_feed_message):
        feed_messages = [sample_feed_message]

        result = extract_code_discussions(feed_messages)

        discussion = result[0]
        assert discussion["snippet"] == [
            "val libraryDependency = libraries[dependency]",
            "if (libraryDependency != null) {",
            "  val exported = !libraryDependency.isLowPriority",
        ]

    def test_extract_skips_non_code_discussion_events(self, sample_feed_message):
        non_code_message = {
            "id": "msg-2",
            "text": "Some other message",
            "author": {"name": "Someone"},
            "details": {"className": "SomeOtherEvent"},
        }
        feed_messages = [sample_feed_message, non_code_message]

        result = extract_code_discussions(feed_messages)

        assert len(result) == 1
        assert result[0]["id"] == "disc-1"

    def test_extract_multiple_code_discussions(self, sample_feed_message):
        second_message = {
            "id": "msg-2",
            "text": "Another comment",
            "author": {"name": "Jane.Doe"},
            "details": {
                "className": "CodeDiscussionAddedFeedEvent",
                "codeDiscussion": {
                    "id": "disc-2",
                    "resolved": True,
                    "anchor": {"filename": "/src/Main.java", "line": 100},
                    "snippet": {"lines": [{"text": "public void main()"}]},
                    "channel": {"id": "disc-channel-2"},
                    "suggestedEdit": None,
                },
            },
        }
        feed_messages = [sample_feed_message, second_message]

        result = extract_code_discussions(feed_messages)

        assert len(result) == 2
        assert result[0]["id"] == "disc-1"
        assert result[1]["id"] == "disc-2"

    def test_extract_empty_feed_messages(self):
        result = extract_code_discussions([])

        assert result == []

    def test_extract_with_suggested_edit(self):
        message_with_edit = {
            "id": "msg-3",
            "text": "Rename this function",
            "author": {"name": "Reviewer"},
            "details": {
                "className": "CodeDiscussionAddedFeedEvent",
                "codeDiscussion": {
                    "id": "disc-3",
                    "resolved": False,
                    "anchor": {"filename": "/src/utils.kt", "line": 10},
                    "snippet": {"lines": [{"text": "fun oldName()"}]},
                    "channel": {"id": "disc-channel-3"},
                    "suggestedEdit": {
                        "original": "fun oldName()",
                        "suggested": "fun newName()",
                    },
                },
            },
        }

        result = extract_code_discussions([message_with_edit])

        assert len(result) == 1
        assert result[0]["suggested_edit"] == {
            "original": "fun oldName()",
            "suggested": "fun newName()",
        }

    def test_extract_handles_missing_details(self):
        message_without_details = {
            "id": "msg-4",
            "text": "Plain message",
            "author": {"name": "Someone"},
        }

        result = extract_code_discussions([message_without_details])

        assert result == []


class TestFilterDiscussions:
    def test_filter_unresolved_only(self):
        discussions = [
            {"id": "1", "resolved": False},
            {"id": "2", "resolved": True},
            {"id": "3", "resolved": False},
        ]

        result = filter_discussions(discussions, unresolved_only=True)

        assert len(result) == 2
        assert all(d["resolved"] is False for d in result)

    def test_filter_returns_all_when_not_filtering(self):
        discussions = [
            {"id": "1", "resolved": False},
            {"id": "2", "resolved": True},
            {"id": "3", "resolved": False},
        ]

        result = filter_discussions(discussions, unresolved_only=False)

        assert len(result) == 3

    def test_filter_empty_list(self):
        result = filter_discussions([], unresolved_only=True)

        assert result == []

    def test_filter_all_resolved(self):
        discussions = [
            {"id": "1", "resolved": True},
            {"id": "2", "resolved": True},
        ]

        result = filter_discussions(discussions, unresolved_only=True)

        assert result == []


class TestBuildDiscussionWithThread:
    def test_build_with_thread_messages(self, sample_thread_message):
        discussion = {
            "id": "disc-1",
            "filename": "/src/file.kt",
            "line": 10,
            "resolved": False,
            "snippet": ["code line"],
            "channel_id": "channel-1",
            "author": "Author",
            "text": "Initial comment",
            "suggested_edit": None,
            "thread": [],
        }
        initial_message = {
            "id": "initial-msg",
            "text": "Initial comment",
            "author": {"name": "Author"},
        }
        thread_messages = [initial_message, sample_thread_message]

        result = build_discussion_with_thread(discussion, thread_messages)

        assert len(result["thread"]) == 1
        assert result["thread"][0]["author"] == "Lev.Leontev"
        assert (
            result["thread"][0]["text"]
            == "`exported` is another thing that's set per dependency, not per library"
        )

    def test_build_with_multiple_replies(self):
        discussion = {
            "id": "disc-1",
            "filename": "/src/file.kt",
            "line": 10,
            "resolved": False,
            "snippet": ["code"],
            "channel_id": "channel-1",
            "author": "Author",
            "text": "Initial comment",
            "suggested_edit": None,
            "thread": [],
        }
        thread_messages = [
            {"id": "msg-0", "text": "Initial comment", "author": {"name": "Author"}},
            {"id": "msg-1", "text": "Reply 1", "author": {"name": "User1"}},
            {"id": "msg-2", "text": "Reply 2", "author": {"name": "User2"}},
            {"id": "msg-3", "text": "Reply 3", "author": {"name": "User1"}},
        ]

        result = build_discussion_with_thread(discussion, thread_messages)

        assert len(result["thread"]) == 3
        assert result["thread"][0] == {"author": "User1", "text": "Reply 1"}
        assert result["thread"][1] == {"author": "User2", "text": "Reply 2"}
        assert result["thread"][2] == {"author": "User1", "text": "Reply 3"}

    def test_build_with_empty_thread(self):
        discussion = {
            "id": "disc-1",
            "filename": "/src/file.kt",
            "line": 10,
            "resolved": False,
            "snippet": ["code"],
            "channel_id": "channel-1",
            "author": "Author",
            "text": "Initial comment",
            "suggested_edit": None,
            "thread": [],
        }
        thread_messages = []

        result = build_discussion_with_thread(discussion, thread_messages)

        assert result["thread"] == []

    def test_build_with_only_initial_message(self):
        discussion = {
            "id": "disc-1",
            "filename": "/src/file.kt",
            "line": 10,
            "resolved": False,
            "snippet": ["code"],
            "channel_id": "channel-1",
            "author": "Author",
            "text": "Initial comment",
            "suggested_edit": None,
            "thread": [],
        }
        thread_messages = [
            {"id": "msg-0", "text": "Initial comment", "author": {"name": "Author"}},
        ]

        result = build_discussion_with_thread(discussion, thread_messages)

        assert result["thread"] == []

    def test_build_preserves_discussion_fields(self):
        discussion = {
            "id": "disc-1",
            "filename": "/src/file.kt",
            "line": 42,
            "resolved": True,
            "snippet": ["line1", "line2"],
            "channel_id": "channel-1",
            "author": "Author",
            "text": "Initial comment",
            "suggested_edit": {"original": "old", "suggested": "new"},
            "thread": [],
        }
        thread_messages = []

        result = build_discussion_with_thread(discussion, thread_messages)

        assert result["id"] == "disc-1"
        assert result["filename"] == "/src/file.kt"
        assert result["line"] == 42
        assert result["resolved"] is True
        assert result["snippet"] == ["line1", "line2"]
        assert result["channel_id"] == "channel-1"
        assert result["author"] == "Author"
        assert result["text"] == "Initial comment"
        assert result["suggested_edit"] == {"original": "old", "suggested": "new"}
