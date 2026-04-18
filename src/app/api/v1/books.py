from fastapi import APIRouter, Depends, HTTPException, status
from src.app.schemas.book import BookCreate, BookRead
from src.app.services.book_service import BookService
from src.app.repositories.book_repo import DynamoDBBookRepository
from src.app.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
import os

router = APIRouter(prefix="/api/books", tags=["Books"])

def get_book_service() -> BookService:
    table_name = os.getenv("BOOKS_TABLE", "BooksTable")
    repo = DynamoDBBookRepository(table_name)
    return BookService(repo)

@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, service: BookService = Depends(get_book_service)):
    try:
        return service.create_book(book)
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/{id}", response_model=BookRead)
def get_book(id: str, service: BookService = Depends(get_book_service)):
    try:
        return service.get_book(id)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
