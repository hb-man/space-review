import pytest
from urllib.parse import unquote
from pytest_httpx import HTTPXMock

from space_review.api import SpaceClient


BASE_URL = "https://jetbrains.team/api/http"


class TestSearchReview:
    def test_search_review_returns_internal_id(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/projects/key:IJ/code-reviews?text=174369&$top=1",
            json={"data": [{"review": {"id": "2wBoBc4URsmM"}}]},
        )

        client = SpaceClient(token="test-token")
        result = client.search_review(project="IJ", number="174369")

        assert result == "2wBoBc4URsmM"

    def test_search_review_sends_auth_header(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/projects/key:IJ/code-reviews?text=174369&$top=1",
            json={"data": [{"review": {"id": "abc123"}}]},
        )

        client = SpaceClient(token="my-secret-token")
        client.search_review(project="IJ", number="174369")

        request = httpx_mock.get_request()
        assert request.headers["Authorization"] == "Bearer my-secret-token"


class TestGetReview:
    def test_get_review_returns_review_dict(
        self, httpx_mock: HTTPXMock, sample_review_data
    ):
        httpx_mock.add_response(json=sample_review_data)

        client = SpaceClient(token="test-token")
        result = client.get_review(project="IJ", internal_id="2wBoBc4URsmM")

        assert result["id"] == "2wBoBc4URsmM"
        assert result["title"] == "BAZEL-2284: don't export Kotlin stdlib to avoid red code"
        assert result["state"] == "Opened"

    def test_get_review_uses_correct_fields_parameter(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={"id": "test"})

        client = SpaceClient(token="test-token")
        client.get_review(project="IJ", internal_id="2wBoBc4URsmM")

        request = httpx_mock.get_request()
        url = unquote(str(request.url))
        assert "$fields=id,project,number,title,state,feedChannelId,branchPairs" in url
        assert "/projects/key:IJ/code-reviews/2wBoBc4URsmM" in url


class TestGetFeedMessages:
    def test_get_feed_messages_returns_list(
        self, httpx_mock: HTTPXMock, sample_feed_message
    ):
        httpx_mock.add_response(json={"messages": [sample_feed_message]})

        client = SpaceClient(token="test-token")
        result = client.get_feed_messages(channel_id="feed-channel-123")

        assert len(result) == 1
        assert result[0]["id"] == "msg-1"
        assert result[0]["author"]["name"] == "Andrew.Kozlov"

    def test_get_feed_messages_uses_correct_url_and_fields(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={"messages": []})

        client = SpaceClient(token="test-token")
        client.get_feed_messages(channel_id="feed-channel-123")

        request = httpx_mock.get_request()
        url = str(request.url)
        assert "channel=id:feed-channel-123" in url
        assert "sorting=FromOldestToNewest" in url
        assert "batchSize=50" in url
        assert "$fields=messages(id,text,author(name),time,details(className,codeDiscussion))" in url


class TestGetDiscussionThread:
    def test_get_discussion_thread_returns_messages(
        self, httpx_mock: HTTPXMock, sample_thread_message
    ):
        httpx_mock.add_response(json={"messages": [sample_thread_message]})

        client = SpaceClient(token="test-token")
        result = client.get_discussion_thread(channel_id="disc-channel-1")

        assert len(result) == 1
        assert result[0]["text"] == "`exported` is another thing that's set per dependency, not per library"

    def test_get_discussion_thread_uses_correct_parameters(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(json={"messages": []})

        client = SpaceClient(token="test-token")
        client.get_discussion_thread(channel_id="disc-channel-1")

        request = httpx_mock.get_request()
        url = str(request.url)
        assert "channel=id:disc-channel-1" in url
        assert "sorting=FromOldestToNewest" in url
        assert "batchSize=50" in url
        assert "$fields=messages(id,text,author(name),time)" in url


class TestGetUnboundDiscussions:
    def test_get_unbound_discussions_returns_list(self, httpx_mock: HTTPXMock):
        response_data = {
            "data": [
                {"id": "unbound-1", "resolved": False, "item": {"id": "item-1"}},
                {"id": "unbound-2", "resolved": True, "item": {"id": "item-2"}},
            ]
        }
        httpx_mock.add_response(json=response_data)

        client = SpaceClient(token="test-token")
        result = client.get_unbound_discussions(project="IJ", review_id="2wBoBc4URsmM")

        assert len(result) == 2
        assert result[0]["id"] == "unbound-1"
        assert result[1]["resolved"] is True

    def test_get_unbound_discussions_uses_correct_url_and_fields(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(json={"data": []})

        client = SpaceClient(token="test-token")
        client.get_unbound_discussions(project="IJ", review_id="2wBoBc4URsmM")

        request = httpx_mock.get_request()
        url = unquote(str(request.url))
        assert "/projects/key:IJ/code-reviews/2wBoBc4URsmM/unbound-discussions" in url
        assert "$fields=data(id,resolved,item(id))" in url
