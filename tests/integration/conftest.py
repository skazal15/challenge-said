"""
Shared fixtures for integration tests.

Provides a fully wired FastAPI TestClient backed by a Moto-mocked
DynamoDB table, enabling true end-to-end API testing without any
external infrastructure.
"""
import os
import pytest
import boto3
from moto import mock_aws
from fastapi.testclient import TestClient
from tests.conftest import SAMPLE_BOOK_DATA, SAMPLE_BOOK_DATA_SECOND


TABLE_NAME = "IntegrationBooksTable"


@pytest.fixture(scope="function")
def aws_environment(monkeypatch):
    """Configures fake AWS credentials and environment for Moto."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("BOOKS_TABLE", TABLE_NAME)
    # Ensure DYNAMODB_ENDPOINT is not set so Moto intercepts calls
    monkeypatch.delenv("DYNAMODB_ENDPOINT", raising=False)


@pytest.fixture(scope="function")
def dynamodb_table(aws_environment):
    """
    Creates and tears down a mocked DynamoDB table for each test.
    
    Using function scope ensures test isolation — each test starts
    with a clean, empty table.
    """
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


@pytest.fixture(scope="function")
def api_client(dynamodb_table) -> TestClient:
    """
    FastAPI TestClient with a real (mocked) DynamoDB backend.
    
    Note: The app must be imported INSIDE the mock_aws context
    to ensure Boto3 resource creation is intercepted by Moto.
    We re-import to avoid stale references from previous tests.
    """
    # mock_aws is already active from dynamodb_table fixture
    from src.app.main import app
    return TestClient(app)


@pytest.fixture
def seed_one_book(api_client) -> dict:
    """Seeds the database with one book and returns its data."""
    api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)
    return SAMPLE_BOOK_DATA.copy()


@pytest.fixture
def seed_two_books(api_client) -> list:
    """Seeds the database with two books and returns their data."""
    api_client.post("/api/books/", json=SAMPLE_BOOK_DATA)
    api_client.post("/api/books/", json=SAMPLE_BOOK_DATA_SECOND)
    return [SAMPLE_BOOK_DATA.copy(), SAMPLE_BOOK_DATA_SECOND.copy()]
