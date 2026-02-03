import httpx


class SpaceClient:
    BASE_URL = "https://jetbrains.team/api/http"
    DEFAULT_BATCH_SIZE = 50
    MAX_PAGES = 100

    def __init__(self, token: str, batch_size: int | None = None) -> None:
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        self._batch_size = batch_size or self.DEFAULT_BATCH_SIZE

    def get_review_by_number(self, project: str, number: str) -> dict:
        response = self._client.get(
            f"/projects/key:{project}/code-reviews/number:{number}",
            params={"$fields": "id,project,number,title,state,feedChannelId,branchPairs"},
        )
        response.raise_for_status()
        return response.json()

    def _paginate_messages(self, channel_id: str, fields: str) -> list[dict]:
        """
        Fetch all messages from a channel with automatic pagination.

        Args:
            channel_id: Channel identifier
            fields: Space API $fields parameter for response shaping (messages fields only)

        Returns:
            Complete list of messages across all pages
        """
        all_messages = []
        start_from_date = None
        page_num = 1

        while page_num <= self.MAX_PAGES:
            url = (
                f"/chats/messages"
                f"?channel=id:{channel_id}"
                f"&sorting=FromOldestToNewest"
                f"&batchSize={self._batch_size}"
                f"&$fields=nextStartFromDate,{fields}"
            )

            if start_from_date:
                url += f"&startFromDate={start_from_date}"

            try:
                response = self._client.get(url)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise ValueError(
                    f"Failed to fetch page {page_num} from channel {channel_id}: {e}"
                ) from e
            except httpx.RequestError as e:
                raise ValueError(
                    f"Network error fetching page {page_num} from channel {channel_id}: {e}"
                ) from e

            data = response.json()
            messages = data.get("messages", [])

            if not isinstance(messages, list):
                raise ValueError(
                    f"Unexpected response format: 'messages' is not a list "
                    f"(got {type(messages).__name__})"
                )

            all_messages.extend(messages)

            next_start = data.get("nextStartFromDate")
            if next_start is None or len(messages) == 0:
                break

            if isinstance(next_start, dict):
                start_from_date = next_start.get("iso")
            else:
                start_from_date = next_start
            page_num += 1

        if page_num > self.MAX_PAGES:
            raise ValueError(
                f"Exceeded maximum page limit ({self.MAX_PAGES}) "
                f"while fetching messages from channel {channel_id}"
            )

        return all_messages

    def get_feed_messages(self, channel_id: str) -> list[dict]:
        fields = "messages(id,text,author(name),time,details(className,codeDiscussion))"
        return self._paginate_messages(channel_id, fields)

    def get_discussion_thread(self, channel_id: str) -> list[dict]:
        fields = "messages(id,text,author(name),time)"
        return self._paginate_messages(channel_id, fields)

    def get_unbound_discussions(self, project: str, review_id: str) -> list[dict]:
        response = self._client.get(
            f"/projects/key:{project}/code-reviews/{review_id}/unbound-discussions",
            params={"$fields": "data(id,resolved,archived,item(id))"},
        )
        response.raise_for_status()
        return response.json()["data"]
