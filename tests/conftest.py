"""
Shared fixtures for the Book API test suite.

This module provides reusable fixtures for both unit and integration tests,
following the Arrange-Act-Assert pattern with descriptive fixture names.
"""
import pytest
from src.app.schemas.book import BookCreate, BookRead


# ──────────────────────────────────────────────────────────────────────
# Book Data Factories
# ──────────────────────────────────────────────────────────────────────

SAMPLE_BOOK_DATA = {
    "id": "/books/id1",
    "author": "/authors/id1",
    "name": "Fancy Tech",
    "note": "Awesome book for beginners in Fancy.",
    "serial": "C040102",
}

SAMPLE_BOOK_DATA_WITHOUT_PREFIX = {
    "id": "id2",
    "author": "/authors/id2",
    "name": "Advanced Python",
    "note": "Deep dive into Python internals.",
    "serial": "P090301",
}

SAMPLE_BOOK_DATA_SECOND = {
    "id": "/books/id3",
    "author": "/authors/id3",
    "name": "Clean Architecture",
    "note": "Guide to building maintainable systems.",
    "serial": "A010501",
}


@pytest.fixture
def sample_book_create() -> BookCreate:
    """A valid BookCreate instance with the /books/ prefix."""
    return BookCreate(**SAMPLE_BOOK_DATA)


@pytest.fixture
def sample_book_create_without_prefix() -> BookCreate:
    """A valid BookCreate instance WITHOUT the /books/ prefix.
    Used to test ID normalization logic."""
    return BookCreate(**SAMPLE_BOOK_DATA_WITHOUT_PREFIX)


@pytest.fixture
def sample_book_read() -> BookRead:
    """A valid BookRead instance matching sample_book_create."""
    return BookRead(**SAMPLE_BOOK_DATA)


@pytest.fixture
def sample_book_dict() -> dict:
    """Raw dictionary representation of a book (as stored in DynamoDB)."""
    return SAMPLE_BOOK_DATA.copy()
