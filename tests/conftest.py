import pytest
from typing import Any


@pytest.fixture
def sample_review_data() -> dict[str, Any]:
    return {
        "id": "2wBoBc4URsmM",
        "project": {"key": "IJ"},
        "number": 174369,
        "title": "BAZEL-2284: don't export Kotlin stdlib to avoid red code",
        "state": "Opened",
        "feedChannelId": "feed-channel-123",
    }


@pytest.fixture
def sample_feed_message() -> dict[str, Any]:
    return {
        "id": "msg-1",
        "text": "I'd suggest using `exported` word everywhere.",
        "author": {"name": "Andrew.Kozlov"},
        "time": "2024-01-15T10:30:00Z",
        "details": {
            "className": "CodeDiscussionAddedFeedEvent",
            "codeDiscussion": {
                "id": "disc-1",
                "resolved": False,
                "anchor": {
                    "filename": "/plugins/bazel/ModuleEntityUpdater.kt",
                    "line": 43,
                    "revision": "abc123",
                    "repository": "intellij",
                },
                "snippet": {
                    "lines": [
                        {"text": "val libraryDependency = libraries[dependency]"},
                        {"text": "if (libraryDependency != null) {"},
                        {"text": "  val exported = !libraryDependency.isLowPriority"},
                    ]
                },
                "channel": {"id": "disc-channel-1"},
                "suggestedEdit": None,
            },
        },
    }


@pytest.fixture
def sample_thread_message() -> dict[str, Any]:
    return {
        "id": "thread-msg-1",
        "text": "`exported` is another thing that's set per dependency, not per library",
        "author": {"name": "Lev.Leontev"},
        "time": "2024-01-15T11:00:00Z",
    }
