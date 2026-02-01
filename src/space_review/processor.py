def extract_code_discussions(feed_messages: list[dict]) -> list[dict]:
    discussions = []
    for feed_index, message in enumerate(feed_messages):
        details = message.get("details")
        if not details:
            continue
        if details.get("className") != "CodeDiscussionAddedFeedEvent":
            continue

        code_discussion = details["codeDiscussion"]
        anchor = code_discussion["anchor"]
        end_anchor = code_discussion.get("endAnchor")
        snippet_data = code_discussion.get("snippet", {})
        snippet_lines = [
            {
                "text": line["text"],
                "type": line.get("type"),
                "old_line": line.get("oldLineNum"),
                "new_line": line.get("newLineNum"),
                "deletes": line.get("deletes"),
                "inserts": line.get("inserts"),
            }
            for line in snippet_data.get("lines", [])
        ]

        suggested_edit = code_discussion.get("suggestedEdit")
        is_suggestion = bool(suggested_edit and "suggestionCommitId" in suggested_edit)

        discussions.append({
            "id": code_discussion["id"],
            "feed_index": feed_index,
            "filename": anchor["filename"],
            "line": anchor["line"],
            "old_line": anchor.get("oldLine"),
            "end_line": end_anchor.get("line") if end_anchor else None,
            "old_end_line": end_anchor.get("oldLine") if end_anchor else None,
            "resolved": code_discussion["resolved"],
            "snippet": snippet_lines,
            "channel_id": code_discussion["channel"]["id"],
            "author": message["author"]["name"],
            "text": None,
            "suggested_edit": suggested_edit,
            "is_suggestion": is_suggestion,
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
    for feed_index, message in enumerate(feed_messages):
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
            "feed_index": feed_index,
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
