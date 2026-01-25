import os
import sys

import click
from dotenv import load_dotenv

load_dotenv()

from .api import SpaceClient
from .parser import parse_review_id
from .formatter import format_markdown, format_json
from .processor import extract_code_discussions, filter_discussions, build_discussion_with_thread


def fetch_review(
    review_id: str,
    token: str,
    unresolved_only: bool = False,
    output_json: bool = False,
) -> tuple[str, list]:
    parsed = parse_review_id(review_id)
    client = SpaceClient(token=token)

    internal_id = client.search_review(parsed.project, parsed.number)
    review = client.get_review(parsed.project, internal_id)

    feed_messages = client.get_feed_messages(review["feedChannelId"])
    discussions = extract_code_discussions(feed_messages)
    discussions = filter_discussions(discussions, unresolved_only)

    for discussion in discussions:
        thread_messages = client.get_discussion_thread(discussion["channel_id"])
        discussion.update(build_discussion_with_thread(discussion, thread_messages))

    if output_json:
        return format_json(review, discussions), discussions
    else:
        return format_markdown(review, discussions), discussions


@click.command()
@click.argument("review_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--unresolved", "unresolved_only", is_flag=True, help="Show only unresolved discussions")
@click.option("--token", envvar="SPACE_TOKEN", help="Space API token")
def main(review_id: str, output_json: bool, unresolved_only: bool, token: str | None):
    """Fetch code review discussions from JetBrains Space.

    REVIEW_ID can be in format: IJ-CR-174369, IJ-MR-188658, or a Space URL.
    """
    if token is None:
        token = os.environ.get("SPACE_TOKEN")

    if not token:
        click.echo("Error: No token provided. Use --token flag, SPACE_TOKEN env var, or .env file.", err=True)
        sys.exit(1)

    try:
        output, _ = fetch_review(
            review_id=review_id,
            token=token,
            unresolved_only=unresolved_only,
            output_json=output_json,
        )
        click.echo(output)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error fetching review: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
