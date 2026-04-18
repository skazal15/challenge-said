"""
Unit tests for DynamoDBBookRepository.

Uses Moto to mock DynamoDB at the Boto3 level, keeping tests fast and
deterministic. These tests verify repository-level concerns:
- DynamoDB read/write behavior
- ConditionalCheckFailed → EntityAlreadyExistsError mapping
- Return types

Test naming: test_<method>_<scenario>_<expected_result>
"""
import os
import pytest
import boto3
from moto import mock_aws
from src.app.repositories.book_repo import DynamoDBBookRepository
from src.app.schemas.book import BookCreate
from src.app.core.exceptions import EntityAlreadyExistsError
from tests.conftest import SAMPLE_BOOK_DATA


pytestmark = pytest.mark.unit

TABLE_NAME = "TestBooksTable"


@pytest.fixture
def aws_environment(monkeypatch):
    """Sets up fake AWS environment variables for Moto."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT", "")
    monkeypatch.delenv("DYNAMODB_ENDPOINT", raising=False)


@pytest.fixture
def dynamodb_table(aws_environment):
    """Creates a mocked DynamoDB table and tears it down after the test."""
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


@pytest.fixture
def book_repository(dynamodb_table) -> DynamoDBBookRepository:
    """A DynamoDBBookRepository instance connected to the mocked table."""
    return DynamoDBBookRepository(table_name=TABLE_NAME)


# ──────────────────────────────────────────────────────────────────────
# get_by_id
# ──────────────────────────────────────────────────────────────────────

class TestGetById:
    """Tests for DynamoDBBookRepository.get_by_id()."""

    @mock_aws
    def test_get_by_id_existing_item_should_return_dict(self, book_repository):
        """Returns a dictionary for an existing book."""
        book = BookCreate(**SAMPLE_BOOK_DATA)
        book_repository.create(book)

        result = book_repository.get_by_id("/books/id1")

        assert result is not None
        assert result["id"] == "/books/id1"
        assert result["name"] == "Fancy Tech"

    @mock_aws
    def test_get_by_id_nonexistent_item_should_return_none(self, book_repository):
        """Returns None when the book ID does not exist."""
        result = book_repository.get_by_id("nonexistent-id")
        assert result is None

    @mock_aws
    def test_get_by_id_returns_all_stored_fields(self, book_repository):
        """Verifies all fields are persisted and returned correctly."""
        book = BookCreate(**SAMPLE_BOOK_DATA)
        book_repository.create(book)

        result = book_repository.get_by_id("/books/id1")

        assert result["author"] == "/authors/id1"
        assert result["note"] == "Awesome book for beginners in Fancy."
        assert result["serial"] == "C040102"


# ──────────────────────────────────────────────────────────────────────
# create
# ──────────────────────────────────────────────────────────────────────

class TestCreate:
    """Tests for DynamoDBBookRepository.create()."""

    @mock_aws
    def test_create_new_book_should_return_true(self, book_repository):
        """Successfully creates a new book and returns True."""
        book = BookCreate(**SAMPLE_BOOK_DATA)
        result = book_repository.create(book)
        assert result is True

    @mock_aws
    def test_create_duplicate_id_should_raise_entity_already_exists(
        self, book_repository
    ):
        """Raises EntityAlreadyExistsError on duplicate ID (ConditionExpression)."""
        book = BookCreate(**SAMPLE_BOOK_DATA)
        book_repository.create(book)

        with pytest.raises(EntityAlreadyExistsError) as exc_info:
            book_repository.create(book)

        assert "/books/id1" in exc_info.value.message

    @mock_aws
    def test_create_book_is_retrievable_after_insert(self, book_repository):
        """Created book can be immediately read back (write consistency)."""
        book = BookCreate(**SAMPLE_BOOK_DATA)
        book_repository.create(book)

        stored = book_repository.get_by_id("/books/id1")
        assert stored is not None
        assert stored["name"] == "Fancy Tech"
