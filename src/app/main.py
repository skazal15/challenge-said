from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1.books import router as books_router

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Book Management API",
    description="A resilient REST API for managing books using FastAPI and DynamoDB",
    version="1.0.0",
    root_path="/dev"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Override the default FastAPI 422 Unprocessable Entity error.
    Returns a 400 Bad Request with a custom, cleaner error structure.
    """
    simplified_errors = []
    for error in exc.errors():
        field_name = error["loc"][-1] if error.get("loc") else "unknown"
        simplified_errors.append({
            "field": field_name,
            "message": error.get("msg")
        })

    return JSONResponse(
        status_code=400,
        content={
            "error": "Bad Request",
            "message": "Input validation failed. Please check your payload.",
            "details": simplified_errors
        }
    )

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router)

@app.get("/")
def root():
    return {"message": "Welcome to the Book API. Please refer to /docs for API specifications."}
