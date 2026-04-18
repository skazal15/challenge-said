# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-04-18

### Added
- **Comprehensive Test Suite**: Over 49 Pytest functions covering 100% of core operations.
  - Unit Tests for Pydantic validation, domain exceptions, repository abstraction, and service layers.
  - Integration Tests covering full HTTP lifecycle using `TestClient` and `Moto` for DynamoDB mocking.
- **Fixture Management**: Centralized test factories in `tests/conftest.py`.
- **Test Markers**: Implemented `-m unit` and `-m integration` in `pytest.ini` for selective execution.
- **Input Sanitization**: Added strict RegEx pattern enforcement to `BookCreate` Pydantic models to prevent NoSQL injection and XSS.
- **Length Constraints**: Defined `max_length` and `min_length` on endpoints to prevent Buffer/Payload bloat.
- **Custom Error Handler**: Overrode default FastAPI Pydantic `422 Unprocessable Entity` to instead emit standard `400 Bad Request` with streamlined JSON responses.

### Changed
- **Serverless IAM Overhaul**: Updated `serverless.yml` to adhere strictly to the Principle of Least Privilege (pruned `UpdateItem`, `DeleteItem` capabilities).
- **Function Context**: Renamed Serverless generic `api` function map to `bookApi` and bound timeout (`10s`) & memory (`256MB`) parameters.
- **Documentation**: Substantially updated `README.md` to reflect proper Python Venv test execution paths.

### Fixed
- **Pytest Dependencies Environment**: Mitigated global Python environment injection via `pytest.ini` overrides.
- URL double-slash proxy proxy testing bugs with FastAPI `TestClient`.
