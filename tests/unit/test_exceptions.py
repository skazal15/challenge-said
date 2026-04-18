"""
Unit tests for custom domain exceptions.

Tests cover:
- Exception message formatting
- Exception hierarchy (inheritance from DomainError)
"""
import pytest
from src.app.core.exceptions import (
    DomainError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


pytestmark = pytest.mark.unit


class TestEntityAlreadyExistsError:
    """Tests for EntityAlreadyExistsError."""

    def test_message_includes_entity_name_and_id(self):
        """Error message contains both entity type and conflicting ID."""
        error = EntityAlreadyExistsError("Book", "/books/id1")
        assert "Book" in error.message
        assert "/books/id1" in error.message

    def test_inherits_from_domain_error(self):
        """Ensures proper exception hierarchy for catch-all handling."""
        error = EntityAlreadyExistsError("Book", "/books/id1")
        assert isinstance(error, DomainError)

    def test_str_representation_matches_message(self):
        """str(error) uses the formatted message."""
        error = EntityAlreadyExistsError("Book", "id99")
        assert "id99" in str(error)


class TestEntityNotFoundError:
    """Tests for EntityNotFoundError."""

    def test_message_includes_entity_name_and_id(self):
        """Error message contains both entity type and missing ID."""
        error = EntityNotFoundError("Book", "id42")
        assert "Book" in error.message
        assert "id42" in error.message

    def test_inherits_from_domain_error(self):
        """Ensures proper exception hierarchy for catch-all handling."""
        error = EntityNotFoundError("Book", "id42")
        assert isinstance(error, DomainError)

    def test_str_representation_matches_message(self):
        """str(error) uses the formatted message."""
        error = EntityNotFoundError("Book", "missing-id")
        assert "missing-id" in str(error)


class TestDomainErrorHierarchy:
    """Validates that all domain errors inherit from the base DomainError."""

    def test_entity_already_exists_is_catchable_as_domain_error(self):
        with pytest.raises(DomainError):
            raise EntityAlreadyExistsError("Book", "id1")

    def test_entity_not_found_is_catchable_as_domain_error(self):
        with pytest.raises(DomainError):
            raise EntityNotFoundError("Book", "id1")
