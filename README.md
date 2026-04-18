# Python Coding Challenge: REST API on FastAPI

This is a production-ready implementation of a Book Management API, following SOLID principles, Clean Architecture, and High Resilience standards.

## Tech Stack
- **Framework:** FastAPI
- **Database:** AWS DynamoDB (NoSQL)
- **Compute:** AWS Lambda & API Gateway
- **Infrastructure:** Serverless Framework
- **CI/CD:** GitHub Actions
- **Testing:** Pytest & Moto

## Architecture & Resilience
- **Layered Architecture:** Separation of API, Service, and Repository layers.
- **Resilience:** 
  - Exponential Backoff & Retries via `tenacity`.
  - Explicit timeouts for database calls.
  - Health check endpoint `/health`.
  - Structured logging for observability.
- **Symmetry:** The application can run locally via Docker (using DynamoDB Local) or in AWS Cloud with zero code changes.

## Local Setup (Zero AWS Required)
1. Run the environment:
   \`\`\`bash
   docker-compose up --build
   \`\`\`
2. Access Swagger UI: `http://localhost:8080/docs`

## AWS Deployment
1. Install Serverless Framework: `npm install -g serverless`
2. Configure AWS CLI: `aws configure`
3. Deploy: `sls deploy`

## CI/CD Pipeline
The project is configured to deploy automatically to AWS whenever code is pushed to the `main` branch via GitHub Actions.
