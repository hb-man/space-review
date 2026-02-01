import httpx


class SpaceClient:
    BASE_URL = "https://jetbrains.team/api/http"

    def __init__(self, token: str) -> None:
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

    def get_review_by_number(self, project: str, number: str) -> dict:
        response = self._client.get(
            f"/projects/key:{project}/code-reviews/number:{number}",
            params={"$fields": "id,project,number,title,state,feedChannelId,branchPairs"},
        )
        response.raise_for_status()
        return response.json()

    def get_feed_messages(self, channel_id: str) -> list[dict]:
        fields = "messages(id,text,author(name),time,details(className,codeDiscussion))"
        url = f"/chats/messages?channel=id:{channel_id}&sorting=FromOldestToNewest&batchSize=50&$fields={fields}"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()["messages"]

    def get_discussion_thread(self, channel_id: str) -> list[dict]:
        fields = "messages(id,text,author(name),time)"
        url = f"/chats/messages?channel=id:{channel_id}&sorting=FromOldestToNewest&batchSize=50&$fields={fields}"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()["messages"]

    def get_unbound_discussions(self, project: str, review_id: str) -> list[dict]:
        response = self._client.get(
            f"/projects/key:{project}/code-reviews/{review_id}/unbound-discussions",
            params={"$fields": "data(id,resolved,item(id))"},
        )
        response.raise_for_status()
        return response.json()["data"]
