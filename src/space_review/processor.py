def extract_code_discussions(feed_messages: list[dict]) -> list[dict]:
    discussions = []
    for message in feed_messages:
        details = message.get("details")
        if not details:
            continue
        if details.get("className") != "CodeDiscussionAddedFeedEvent":
            continue

        code_discussion = details["codeDiscussion"]
        anchor = code_discussion["anchor"]
        snippet_data = code_discussion.get("snippet", {})
        snippet_lines = [line["text"] for line in snippet_data.get("lines", [])]

        discussions.append({
            "id": code_discussion["id"],
            "filename": anchor["filename"],
            "line": anchor["line"],
            "resolved": code_discussion["resolved"],
            "snippet": snippet_lines,
            "channel_id": code_discussion["channel"]["id"],
            "author": message["author"]["name"],
            "text": None,  # Will be filled from thread's first message
            "suggested_edit": code_discussion.get("suggestedEdit"),
            "thread": [],
        })

    return discussions


SKIP_AUTHORS = {"Patronus"}


def extract_general_comments(feed_messages: list[dict]) -> list[dict]:
    comments = []
    for message in feed_messages:
        details = message.get("details")
        if not details:
            continue
        if details.get("className") != "M2TextItemContent":
            continue

        author = message["author"]["name"]
        if author in SKIP_AUTHORS:
            continue

        comments.append({
            "id": message["id"],
            "author": author,
            "text": message["text"],
            "time": message.get("time"),
        })

    return comments


def filter_discussions(discussions: list[dict], unresolved_only: bool) -> list[dict]:
    if not unresolved_only:
        return discussions
    return [d for d in discussions if d["resolved"] is False]


def build_discussion_with_thread(discussion: dict, thread_messages: list[dict]) -> dict:
    if not thread_messages:
        return discussion

    # First message is the initial comment
    first_msg = thread_messages[0]
    initial_text = first_msg["text"]
    initial_author = first_msg["author"]["name"]

    # Rest are replies
    replies = []
    for msg in thread_messages[1:]:
        replies.append({
            "author": msg["author"]["name"],
            "text": msg["text"],
        })

    return {
        **discussion,
        "text": initial_text,
        "author": initial_author,
        "thread": replies,
    }
