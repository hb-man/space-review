import pytest
from urllib.parse import unquote
from pytest_httpx import HTTPXMock

from space_review.api import SpaceClient


BASE_URL = "https://jetbrains.team/api/http"


class TestGetReviewByNumber:
    def test_get_review_by_number_returns_review_dict(
        self, httpx_mock: HTTPXMock, sample_review_data
    ):
        httpx_mock.add_response(json=sample_review_data)

        client = SpaceClient(token="test-token")
        result = client.get_review_by_number(project="IJ", number="174369")

        assert result["id"] == "2wBoBc4URsmM"
        assert result["title"] == "BAZEL-2284: don't export Kotlin stdlib to avoid red code"
        assert result["state"] == "Opened"

    def test_get_review_by_number_uses_correct_fields_parameter(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={"id": "test"})

        client = SpaceClient(token="test-token")
        client.get_review_by_number(project="IJ", number="174369")

        request = httpx_mock.get_request()
        url = unquote(str(request.url))
        assert "$fields=id,project,number,title,state,feedChannelId,branchPairs" in url
        assert "/projects/key:IJ/code-reviews/number:174369" in url

    def test_get_review_by_number_sends_auth_header(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={"id": "test"})

        client = SpaceClient(token="my-secret-token")
        client.get_review_by_number(project="IJ", number="174369")

        request = httpx_mock.get_request()
        assert request.headers["Authorization"] == "Bearer my-secret-token"


class TestGetFeedMessages:
    def test_get_feed_messages_returns_list(
        self, httpx_mock: HTTPXMock, sample_feed_message
    ):
        httpx_mock.add_response(json={
            "messages": [sample_feed_message],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        result = client.get_feed_messages(channel_id="feed-channel-123")

        assert len(result) == 1
        assert result[0]["id"] == "msg-1"
        assert result[0]["author"]["name"] == "Andrew.Kozlov"

    def test_get_feed_messages_uses_correct_url_and_fields(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "messages": [],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        client.get_feed_messages(channel_id="feed-channel-123")

        request = httpx_mock.get_request()
        url = str(request.url)
        assert "channel=id:feed-channel-123" in url
        assert "sorting=FromOldestToNewest" in url
        assert "batchSize=50" in url
        assert "$fields=nextStartFromDate,messages(id,text,author(name),time,details(className,codeDiscussion))" in url


class TestGetDiscussionThread:
    def test_get_discussion_thread_returns_messages(
        self, httpx_mock: HTTPXMock, sample_thread_message
    ):
        httpx_mock.add_response(json={
            "messages": [sample_thread_message],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        result = client.get_discussion_thread(channel_id="disc-channel-1")

        assert len(result) == 1
        assert result[0]["text"] == "`exported` is another thing that's set per dependency, not per library"

    def test_get_discussion_thread_uses_correct_parameters(
        self, httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(json={
            "messages": [],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        client.get_discussion_thread(channel_id="disc-channel-1")

        request = httpx_mock.get_request()
        url = str(request.url)
        assert "channel=id:disc-channel-1" in url
        assert "sorting=FromOldestToNewest" in url
        assert "batchSize=50" in url
        assert "$fields=nextStartFromDate,messages(id,text,author(name),time)" in url


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
        assert "$fields=data(id,resolved,archived,item(id))" in url


class TestPaginationBehavior:
    def test_single_page_no_pagination(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "messages": [
                {"id": "msg-1", "text": "First message"},
                {"id": "msg-2", "text": "Second message"}
            ],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        result = client.get_feed_messages(channel_id="test-channel")

        assert len(result) == 2
        assert result[0]["id"] == "msg-1"
        assert result[1]["id"] == "msg-2"
        assert len(httpx_mock.get_requests()) == 1

    def test_multiple_pages_concatenates_messages(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "messages": [
                {"id": "msg-1", "text": "Page 1 message 1"},
                {"id": "msg-2", "text": "Page 1 message 2"}
            ],
            "nextStartFromDate": "2024-01-15T10:00:00Z",
            "orgLimitReached": False
        })
        httpx_mock.add_response(json={
            "messages": [
                {"id": "msg-3", "text": "Page 2 message 1"},
                {"id": "msg-4", "text": "Page 2 message 2"}
            ],
            "nextStartFromDate": "2024-01-15T11:00:00Z",
            "orgLimitReached": False
        })
        httpx_mock.add_response(json={
            "messages": [
                {"id": "msg-5", "text": "Page 3 message 1"}
            ],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        result = client.get_feed_messages(channel_id="test-channel")

        assert len(result) == 5
        assert result[0]["id"] == "msg-1"
        assert result[2]["id"] == "msg-3"
        assert result[4]["id"] == "msg-5"
        assert len(httpx_mock.get_requests()) == 3

    def test_pagination_includes_startFromDate_parameter(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "messages": [{"id": "msg-1"}],
            "nextStartFromDate": "2024-01-15T10:00:00Z",
            "orgLimitReached": False
        })
        httpx_mock.add_response(json={
            "messages": [{"id": "msg-2"}],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        client.get_feed_messages(channel_id="test-channel")

        requests = httpx_mock.get_requests()
        assert len(requests) == 2

        first_url = str(requests[0].url)
        assert "startFromDate" not in first_url

        second_url = str(requests[1].url)
        assert "startFromDate=2024-01-15T10:00:00Z" in second_url

    def test_empty_channel_returns_empty_list(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "messages": [],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token")
        result = client.get_feed_messages(channel_id="empty-channel")

        assert result == []
        assert len(httpx_mock.get_requests()) == 1

    def test_http_error_during_pagination_raises_with_context(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "messages": [{"id": "msg-1"}],
            "nextStartFromDate": "2024-01-15T10:00:00Z",
            "orgLimitReached": False
        })
        httpx_mock.add_response(status_code=500)

        client = SpaceClient(token="test-token")

        with pytest.raises(ValueError, match=r"Failed to fetch page 2 from channel test-channel"):
            client.get_feed_messages(channel_id="test-channel")

    def test_custom_batch_size_is_used(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={
            "messages": [],
            "nextStartFromDate": None,
            "orgLimitReached": False
        })

        client = SpaceClient(token="test-token", batch_size=100)
        client.get_feed_messages(channel_id="test-channel")

        request = httpx_mock.get_request()
        url = str(request.url)
        assert "batchSize=100" in url

    @pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
    def test_max_pages_limit_protection(self, httpx_mock: HTTPXMock):
        for _ in range(101):
            httpx_mock.add_response(json={
                "messages": [{"id": f"msg-{_}"}],
                "nextStartFromDate": f"2024-01-15T10:{_:02d}:00Z",
                "orgLimitReached": False
            })

        client = SpaceClient(token="test-token")

        with pytest.raises(ValueError, match=r"Exceeded maximum page limit \(100\)"):
            client.get_feed_messages(channel_id="test-channel")
