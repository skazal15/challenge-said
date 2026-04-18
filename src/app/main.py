from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1.books import router as books_router

app = FastAPI(
    title="Book Management API",
    description="A resilient REST API for managing books using FastAPI and DynamoDB",
    version="1.0.0"
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
