# Python Coding Challenge: REST API on FastAPI

A production-ready REST API implemented with **FastAPI**, **AWS DynamoDB**, and **AWS Lambda**. This project demonstrates the application of **SOLID principles**, **Clean Architecture**, and **High Resilience** standards.

## Tech Stack
- **Framework:** FastAPI
- **Database:** AWS DynamoDB (NoSQL)
- **Compute:** AWS Lambda & API Gateway
- **Infrastructure as Code:** Serverless Framework
- **CI/CD:** GitHub Actions
- **Testing:** Pytest & Moto (AWS Mocking)

## Architecture & Key Features

### 1. Clean Architecture (SOLID)
The project is divided into three distinct layers to ensure separation of concerns:
- **API Layer:** Handles HTTP requests, Pydantic validation, and response mapping.
- **Service Layer:** Contains core business logic. It is decoupled from the data source.
- **Repository Layer:** Abstracts data access. Using the Repository Pattern allows switching the database (e.g., to PostgreSQL) without touching the business logic.

### 2. Enterprise Resilience
- **Exponential Backoff & Retries:** Integrated `tenacity` to handle transient AWS failures.
- **Circuit Breaker Logic:** Prevents cascade failures by limiting retry attempts.
- **Explicit Timeouts:** Configured Boto3 timeouts to prevent hanging requests.
- **Health Checks:** `/health` endpoint for orchestrator monitoring.
- **Structured Logging:** Integrated logging for production observability.
- **Smart ID Resolver:** Handles both `/books/id1` and `id1` formats to ensure a seamless user experience.

---

## How to Run the Project

### Option A: Local Testing (Zero AWS Required)
The easiest way to test the API locally is using Docker. It will spin up a local DynamoDB instance.

1. **Start the environment:**
   \`\`\`bash
   docker-compose up --build
   \`\`\`
2. **Access the API:**
   - Swagger UI: `http://localhost:8080/docs`
   - Root: `http://localhost:8080/`
   - Health: `http://localhost:8080/health`

### Option B: Run Tests Locally
To ensure everything is working correctly, you can run the test suite. It is highly recommended to use a virtual environment.

1. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run tests:**
   We use markers to separate unit and integration tests.
   ```bash
   # Run all tests (both unit and integration tests using Moto to mock AWS)
   pytest

   # Run ONLY Unit Tests (Fast, no mocked infrastructure)
   pytest -m unit

   # Run ONLY Integration Tests (Exercises full HTTP lifecycle with mocked DynamoDB)
   pytest -m integration
   ```

### Option C: Manual AWS Deployment
If you have the Serverless Framework installed:
1. Configure AWS CLI: `aws configure`
2. Install plugins: `npm install --save-dev serverless-python-requirements`
3. Deploy: `sls deploy`

---

## CI/CD Pipeline
This project uses **GitHub Actions** for fully automated deployment.

**Workflow Process:**
`Push to main` &rarr; `Run Unit Tests` &rarr; `Run Integration Tests` &rarr; `Deploy to AWS Lambda`

**GitHub Secrets required:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

---

## API Specification

### 1. Create Book
`POST /api/books`
- **Request Body:**
  \`\`\`json
  {
    "id": "/books/id1",
    "author": "/authors/id1",
    "name": "Fancy Tech",
    "note": "Awesome book for beginners in Fancy.",
    "serial": "C040102"
  }
  \`\`\`
- **Responses:**
  - `201 Created`: Success.
  - `409 Conflict`: ID already exists.
  - `400 Bad Request`: Missing or invalid fields.

### 2. Get Book by ID
`GET /api/books/{id}`
- **Example:** `/api/books/id1` or `/api/books//books/id1`
- **Responses:**
  - `200 OK`: Returns the book object.
  - `404 Not Found`: Book not found.
