import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from space_review.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCliBasicInvocation:
    def test_cli_requires_review_id(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "REVIEW_ID" in result.output

    def test_cli_shows_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "REVIEW_ID" in result.output
        assert "--json" in result.output
        assert "--unresolved" in result.output
        assert "--token" in result.output


class TestCliTokenHandling:
    def test_cli_token_from_flag(self, runner):
        with patch("space_review.cli.fetch_review") as mock_fetch:
            mock_fetch.return_value = ("# Review", [])
            result = runner.invoke(main, ["IJ-CR-123", "--token", "my-token"])
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args
            assert call_args[1]["token"] == "my-token"

    def test_cli_token_from_env(self, runner):
        with patch("space_review.cli.fetch_review") as mock_fetch:
            mock_fetch.return_value = ("# Review", [])
            result = runner.invoke(
                main, ["IJ-CR-123"], env={"SPACE_TOKEN": "env-token"}
            )
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args
            assert call_args[1]["token"] == "env-token"

    def test_cli_token_flag_takes_precedence(self, runner):
        with patch("space_review.cli.fetch_review") as mock_fetch:
            mock_fetch.return_value = ("# Review", [])
            result = runner.invoke(
                main,
                ["IJ-CR-123", "--token", "flag-token"],
                env={"SPACE_TOKEN": "env-token"},
            )
            call_args = mock_fetch.call_args
            assert call_args[1]["token"] == "flag-token"

    def test_cli_missing_token_error(self, runner):
        with patch.dict(os.environ, {}, clear=True):
            with patch("space_review.cli.load_dotenv") as mock_dotenv:
                mock_dotenv.return_value = None
                result = runner.invoke(main, ["IJ-CR-123"], env={})
                assert result.exit_code != 0
                assert "token" in result.output.lower() or "SPACE_TOKEN" in result.output


class TestCliOutputFormat:
    def test_cli_default_markdown_output(self, runner):
        with patch("space_review.cli.fetch_review") as mock_fetch:
            mock_fetch.return_value = ("# Test Review\n**State:** Open", [])
            result = runner.invoke(
                main, ["IJ-CR-123"], env={"SPACE_TOKEN": "test-token"}
            )
            assert result.exit_code == 0
            assert "# Test Review" in result.output

    def test_cli_json_flag(self, runner):
        with patch("space_review.cli.fetch_review") as mock_fetch:
            mock_fetch.return_value = ('{"review": "test"}', [])
            result = runner.invoke(
                main, ["IJ-CR-123", "--json"], env={"SPACE_TOKEN": "test-token"}
            )
            assert result.exit_code == 0


class TestCliUnresolvedFlag:
    def test_cli_unresolved_flag_passed(self, runner):
        with patch("space_review.cli.fetch_review") as mock_fetch:
            mock_fetch.return_value = ("# Review", [])
            result = runner.invoke(
                main, ["IJ-CR-123", "--unresolved"], env={"SPACE_TOKEN": "test-token"}
            )
            call_args = mock_fetch.call_args
            assert call_args[1]["unresolved_only"] is True

    def test_cli_default_shows_all(self, runner):
        with patch("space_review.cli.fetch_review") as mock_fetch:
            mock_fetch.return_value = ("# Review", [])
            result = runner.invoke(
                main, ["IJ-CR-123"], env={"SPACE_TOKEN": "test-token"}
            )
            call_args = mock_fetch.call_args
            assert call_args[1]["unresolved_only"] is False
