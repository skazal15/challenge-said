"""
Integration tests for Book API endpoints.

These tests exercise the FULL request lifecycle:
    HTTP Request → FastAPI Route → BookService → DynamoDBBookRepository → Moto DynamoDB

Every test uses a clean, isolated DynamoDB table (function-scoped fixtures).

Test naming: test_<endpoint>_<scenario>_should_<expected_behavior>
"""
import pytest
from moto import mock_aws
from tests.conftest import (
    SAMPLE_BOOK_DATA,
    SAMPLE_BOOK_DATA_WITHOUT_PREFIX,
    SAMPLE_BOOK_DATA_SECOND,
)


pytestmark = pytest.mark.integration


# ══════════════════════════════════════════════════════════════════════
# POST /api/books/ — Create Book
# ══════════════════════════════════════════════════════════════════════

class TestCreateBookEndpoint:
    """Integration tests for POST /api/books/."""

    @mock_aws
    def test_create_book_with_valid_data_should_return_201(self, api_client):
        """A valid book payload returns 201 Created with the book data."""
        response = api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)

        assert response.status_code == 201
        body = response.json()
        assert body["id"] == "/books/id1"
        assert body["name"] == "Fancy Tech"
        assert body["author"] == "/authors/id1"
        assert body["serial"] == "C040102"

    @mock_aws
    def test_create_book_without_prefix_should_normalize_id(self, api_client):
        """Book created without /books/ prefix gets auto-normalized."""
        response = api_client.post(
            "/api/books/", json=SAMPLE_BOOK_DATA_WITHOUT_PREFIX
        )

        assert response.status_code == 201
        body = response.json()
        assert body["id"] == "/books/id2"

    @mock_aws
    def test_create_duplicate_book_should_return_409(self, api_client):
        """Creating a book with an existing ID returns 409 Conflict."""
        api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)

        response = api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    @mock_aws
    def test_create_book_missing_fields_should_return_400(self, api_client):
        """Incomplete payload returns 400 Bad Request (Custom Validation)."""
        incomplete_data = {"id": "/books/id1", "name": "Incomplete Book"}

        response = api_client.post("/api/books/", json=incomplete_data)

        assert response.status_code == 400

    @mock_aws
    def test_create_book_empty_body_should_return_400(self, api_client):
        """Empty JSON body returns 400."""
        response = api_client.post("/api/books/", json={})
        assert response.status_code == 400

    @mock_aws
    def test_create_multiple_books_should_succeed(self, api_client):
        """Multiple distinct books can be created sequentially."""
        response1 = api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)
        response2 = api_client.post("/api/books/", json=SAMPLE_BOOK_DATA_SECOND)

        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["id"] != response2.json()["id"]

    @mock_aws
    def test_create_book_response_matches_request_fields(self, api_client):
        """All input fields are echoed back in the response body."""
        response = api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)
        body = response.json()

        assert body["note"] == SAMPLE_BOOK_DATA["note"]
        assert body["serial"] == SAMPLE_BOOK_DATA["serial"]
        assert body["author"] == SAMPLE_BOOK_DATA["author"]


# ══════════════════════════════════════════════════════════════════════
# GET /api/books/{id} — Get Book by ID
# ══════════════════════════════════════════════════════════════════════

class TestGetBookEndpoint:
    """Integration tests for GET /api/books/{id}."""

    @mock_aws
    def test_get_existing_book_should_return_200(self, api_client, seed_one_book):
        """Fetching an existing book by ID returns 200 with full data."""
        response = api_client.get("/api/books/id1")

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == "/books/id1"
        assert body["name"] == "Fancy Tech"

    @mock_aws
    def test_get_nonexistent_book_should_return_404(self, api_client):
        """Fetching a nonexistent book returns 404 Not Found."""
        response = api_client.get("/api/books/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @mock_aws
    def test_get_book_with_bare_id_resolves_via_smart_id_resolver(
        self, api_client, seed_one_book
    ):
        """GET /api/books/id1 resolves to /books/id1 via Smart ID Resolver.

        The service layer tries the bare ID first, then retries with
        the /books/ prefix — confirming the fallback lookup works.
        """
        response = api_client.get("/api/books/id1")

        assert response.status_code == 200
        assert response.json()["id"] == "/books/id1"

    @mock_aws
    def test_get_book_returns_all_fields(self, api_client, seed_one_book):
        """Response contains every field that was stored."""
        response = api_client.get("/api/books/id1")
        body = response.json()

        assert body["author"] == "/authors/id1"
        assert body["note"] == "Awesome book for beginners in Fancy."
        assert body["serial"] == "C040102"


# ══════════════════════════════════════════════════════════════════════
# System Endpoints
# ══════════════════════════════════════════════════════════════════════

class TestSystemEndpoints:
    """Integration tests for non-book system endpoints."""

    @mock_aws
    def test_health_check_should_return_healthy(self, api_client):
        """GET /health returns a healthy status and version."""
        response = api_client.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert "version" in body

    @mock_aws
    def test_root_endpoint_should_return_welcome_message(self, api_client):
        """GET / returns a welcome message directing to /docs."""
        response = api_client.get("/")

        assert response.status_code == 200
        body = response.json()
        assert "Welcome" in body["message"] or "welcome" in body["message"].lower()
        assert "/docs" in body["message"]


# ══════════════════════════════════════════════════════════════════════
# End-to-End Workflows
# ══════════════════════════════════════════════════════════════════════

class TestCreateThenRetrieveWorkflow:
    """Tests the full create → retrieve lifecycle."""

    @mock_aws
    def test_created_book_is_immediately_retrievable(self, api_client):
        """A book created via POST is immediately available via GET."""
        create_response = api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)
        assert create_response.status_code == 201

        get_response = api_client.get("/api/books/id1")
        assert get_response.status_code == 200

        assert create_response.json() == get_response.json()

    @mock_aws
    def test_create_without_prefix_then_retrieve_with_bare_id(self, api_client):
        """Book created with bare 'id2' is retrievable as 'id2'."""
        api_client.post("/api/books/", json=SAMPLE_BOOK_DATA_WITHOUT_PREFIX)

        response = api_client.get("/api/books/id2")

        assert response.status_code == 200
        assert response.json()["id"] == "/books/id2"

    @mock_aws
    def test_multiple_books_are_independently_retrievable(self, api_client):
        """Each created book can be fetched independently."""
        api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)
        api_client.post("/api/books/", json=SAMPLE_BOOK_DATA_SECOND)

        resp1 = api_client.get("/api/books/id1")
        resp3 = api_client.get("/api/books/id3")

        assert resp1.status_code == 200
        assert resp3.status_code == 200
        assert resp1.json()["name"] == "Fancy Tech"
        assert resp3.json()["name"] == "Clean Architecture"
