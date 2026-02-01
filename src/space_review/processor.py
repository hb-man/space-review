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
            "text": None,
            "suggested_edit": code_discussion.get("suggestedEdit"),
            "thread": [],
        })

    return discussions


SKIP_AUTHORS = {"Patronus"}


def extract_general_comments(feed_messages: list[dict], unbound_discussions: list[dict] | None = None) -> list[dict]:
    unbound_map = {}
    if unbound_discussions:
        for ud in unbound_discussions:
            item_id = ud.get("item", {}).get("id")
            if item_id:
                unbound_map[item_id] = ud

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

        msg_id = message["id"]
        unbound = unbound_map.get(msg_id, {})
        resolved = unbound.get("resolved")

        comments.append({
            "id": msg_id,
            "author": author,
            "text": message["text"],
            "time": message.get("time"),
            "resolved": resolved,
        })

    return comments


def filter_discussions(discussions: list[dict], unresolved_only: bool) -> list[dict]:
    if not unresolved_only:
        return discussions
    return [d for d in discussions if d["resolved"] is False]


def build_discussion_with_thread(discussion: dict, thread_messages: list[dict]) -> dict:
    if not thread_messages:
        return discussion

    first_msg = thread_messages[0]
    initial_text = first_msg["text"]
    initial_author = first_msg["author"]["name"]

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
