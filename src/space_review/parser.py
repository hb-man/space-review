import re
from dataclasses import dataclass


@dataclass
class ParsedReviewId:
    project: str
    number: str


_REVIEW_ID_PATTERN = re.compile(r"^([A-Z]+)-(CR|MR)-(\d+)$")
_URL_PATTERN = re.compile(
    r"https://jetbrains\.team/p/([a-zA-Z]+)/reviews/(\d+)(?:/\w+)?$"
)


def parse_review_id(input_str: str) -> ParsedReviewId:
    if match := _REVIEW_ID_PATTERN.match(input_str):
        return ParsedReviewId(project=match.group(1), number=match.group(3))

    if match := _URL_PATTERN.match(input_str):
        return ParsedReviewId(project=match.group(1).upper(), number=match.group(2))

    raise ValueError(f"Invalid review identifier: {input_str}")
