"""
Unit tests for BookService.

The service layer is tested in ISOLATION by injecting a mock repository.
This verifies business logic (ID normalization, error propagation) without
any dependency on DynamoDB or Boto3.

Test naming: test_<method>_<scenario>_<expected_result>
"""
import pytest
from unittest.mock import MagicMock, patch
from src.app.services.book_service import BookService
from src.app.schemas.book import BookCreate, BookRead
from src.app.core.exceptions import EntityNotFoundError, EntityAlreadyExistsError
from tests.conftest import SAMPLE_BOOK_DATA, SAMPLE_BOOK_DATA_WITHOUT_PREFIX


pytestmark = pytest.mark.unit


@pytest.fixture
def mock_repository():
    """Creates a mock IBookRepository for dependency injection."""
    return MagicMock()


@pytest.fixture
def book_service(mock_repository) -> BookService:
    """BookService wired with a mock repository."""
    return BookService(repository=mock_repository)


# ──────────────────────────────────────────────────────────────────────
# get_book
# ──────────────────────────────────────────────────────────────────────

class TestGetBook:
    """Tests for BookService.get_book()."""

    def test_get_book_with_existing_id_should_return_book_read(
        self, book_service, mock_repository
    ):
        """When a book exists, it returns a BookRead instance."""
        mock_repository.get_by_id.return_value = SAMPLE_BOOK_DATA
        result = book_service.get_book("id1")

        assert isinstance(result, BookRead)
        assert result.name == "Fancy Tech"

    def test_get_book_with_prefix_id_should_find_directly(
        self, book_service, mock_repository
    ):
        """When ID already has /books/ prefix, searches directly without retry."""
        mock_repository.get_by_id.return_value = SAMPLE_BOOK_DATA
        result = book_service.get_book("/books/id1")

        mock_repository.get_by_id.assert_called_once_with("/books/id1")
        assert result.id == "/books/id1"

    def test_get_book_without_prefix_should_try_prefixed_fallback(
        self, book_service, mock_repository
    ):
        """When bare ID 'id1' is not found, tries '/books/id1' as fallback."""
        # First call with 'id1' returns None; second with '/books/id1' succeeds
        mock_repository.get_by_id.side_effect = [None, SAMPLE_BOOK_DATA]

        result = book_service.get_book("id1")

        assert mock_repository.get_by_id.call_count == 2
        mock_repository.get_by_id.assert_any_call("id1")
        mock_repository.get_by_id.assert_any_call("/books/id1")
        assert result.id == "/books/id1"

    def test_get_book_nonexistent_should_raise_entity_not_found(
        self, book_service, mock_repository
    ):
        """When book doesn't exist under any ID variation, raises EntityNotFoundError."""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError) as exc_info:
            book_service.get_book("nonexistent")

        assert "nonexistent" in str(exc_info.value)

    def test_get_book_with_prefix_nonexistent_should_not_try_fallback(
        self, book_service, mock_repository
    ):
        """When ID starts with /books/ and not found, does NOT add another prefix."""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(EntityNotFoundError):
            book_service.get_book("/books/missing")

        # Should only call once — no double-prefix attempt
        mock_repository.get_by_id.assert_called_once_with("/books/missing")


# ──────────────────────────────────────────────────────────────────────
# create_book
# ──────────────────────────────────────────────────────────────────────

class TestCreateBook:
    """Tests for BookService.create_book()."""

    def test_create_book_with_prefix_should_preserve_id(
        self, book_service, mock_repository, sample_book_create
    ):
        """When ID already has /books/ prefix, it is preserved as-is."""
        mock_repository.create.return_value = True

        result = book_service.create_book(sample_book_create)

        assert isinstance(result, BookRead)
        assert result.id == "/books/id1"

    def test_create_book_without_prefix_should_normalize_id(
        self, book_service, mock_repository, sample_book_create_without_prefix
    ):
        """When ID lacks /books/ prefix, service normalizes it automatically."""
        mock_repository.create.return_value = True

        result = book_service.create_book(sample_book_create_without_prefix)

        assert result.id == "/books/id2"
        # Verify the normalized book was passed to repository
        created_book = mock_repository.create.call_args[0][0]
        assert created_book.id == "/books/id2"

    def test_create_book_duplicate_should_propagate_conflict_error(
        self, book_service, mock_repository, sample_book_create
    ):
        """When repository raises EntityAlreadyExistsError, it propagates up."""
        mock_repository.create.side_effect = EntityAlreadyExistsError(
            "Book", "/books/id1"
        )

        with pytest.raises(EntityAlreadyExistsError) as exc_info:
            book_service.create_book(sample_book_create)

        assert "/books/id1" in exc_info.value.message

    def test_create_book_returns_all_fields(
        self, book_service, mock_repository, sample_book_create
    ):
        """The returned BookRead contains all fields from the input."""
        mock_repository.create.return_value = True
        result = book_service.create_book(sample_book_create)

        assert result.author == "/authors/id1"
        assert result.name == "Fancy Tech"
        assert result.note == "Awesome book for beginners in Fancy."
        assert result.serial == "C040102"
