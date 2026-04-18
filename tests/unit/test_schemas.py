"""
Unit tests for Pydantic book schemas.

Tests cover:
- Valid model construction
- Field presence and required validation
- Data serialization (model_dump)
"""
import pytest
from pydantic import ValidationError
from src.app.schemas.book import BookBase, BookCreate, BookRead


pytestmark = pytest.mark.unit


class TestBookCreateSchema:
    """Validates BookCreate schema construction and field requirements."""

    def test_create_with_valid_data_should_succeed(self, sample_book_create):
        """BookCreate accepts a complete, valid payload."""
        assert sample_book_create.id == "/books/id1"
        assert sample_book_create.author == "/authors/id1"
        assert sample_book_create.name == "Fancy Tech"
        assert sample_book_create.note == "Awesome book for beginners in Fancy."
        assert sample_book_create.serial == "C040102"

    def test_create_missing_required_field_should_raise_validation_error(self):
        """BookCreate rejects payloads missing mandatory fields."""
        with pytest.raises(ValidationError) as exc_info:
            BookCreate(
                id="/books/id1",
                author="/authors/id1",
                # missing: name, note, serial
            )
        errors = exc_info.value.errors()
        missing_fields = {e["loc"][0] for e in errors}
        assert {"name", "note", "serial"}.issubset(missing_fields)

    def test_create_with_empty_strings_should_fail(self):
        """Empty strings in required fields now fail (min_length=1 enforced)."""
        with pytest.raises(ValidationError):
            BookCreate(id="", author="", name="", note="", serial="")

    def test_create_with_invalid_characters_should_fail(self):
        """Fields like ID and Serial reject malicious characters (regex enforced)."""
        with pytest.raises(ValidationError) as exc_info:
            BookCreate(
                id="<script>alert(1)</script>",
                author="/authors/id1",
                name="Attack Book",
                note="Just a note",
                serial="OR 1=1"
            )
        errors = str(exc_info.value)
        assert "String should match pattern" in errors

    def test_model_dump_returns_complete_dictionary(self, sample_book_create):
        """model_dump() returns all fields as a plain dictionary."""
        data = sample_book_create.model_dump()
        assert isinstance(data, dict)
        assert set(data.keys()) == {"id", "author", "name", "note", "serial"}


class TestBookReadSchema:
    """Validates BookRead schema mirrors BookCreate structure."""

    def test_read_with_valid_data_should_succeed(self, sample_book_read):
        """BookRead accepts a complete, valid payload."""
        assert sample_book_read.id == "/books/id1"
        assert sample_book_read.name == "Fancy Tech"

    def test_read_from_dict_should_succeed(self, sample_book_dict):
        """BookRead can be constructed from a raw dictionary (DynamoDB item)."""
        book = BookRead(**sample_book_dict)
        assert book.id == sample_book_dict["id"]
        assert book.serial == sample_book_dict["serial"]

    def test_read_missing_field_should_raise_validation_error(self):
        """BookRead rejects incomplete data — same rules as BookCreate."""
        with pytest.raises(ValidationError):
            BookRead(id="/books/id1")


class TestBookBaseInheritance:
    """Ensures schema inheritance hierarchy is correct."""

    def test_book_create_inherits_from_book_base(self):
        assert issubclass(BookCreate, BookBase)

    def test_book_read_inherits_from_book_base(self):
        assert issubclass(BookRead, BookBase)
