import pytest

from space_review.parser import ParsedReviewId, parse_review_id


def test_parse_review_id_cr_format():
    result = parse_review_id("IJ-CR-174369")
    assert result == ParsedReviewId(project="IJ", number="174369")


def test_parse_review_id_mr_format():
    result = parse_review_id("IJ-MR-188658")
    assert result == ParsedReviewId(project="IJ", number="188658")


def test_parse_url_timeline():
    result = parse_review_id("https://jetbrains.team/p/ij/reviews/174369/timeline")
    assert result == ParsedReviewId(project="IJ", number="174369")


def test_parse_url_files():
    result = parse_review_id("https://jetbrains.team/p/ij/reviews/174369/files")
    assert result == ParsedReviewId(project="IJ", number="174369")


def test_parse_invalid_format():
    with pytest.raises(ValueError):
        parse_review_id("invalid-format")
