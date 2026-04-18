from typing import Optional
from src.app.repositories.base import IBookRepository
from src.app.schemas.book import BookRead, BookCreate
from src.app.core.exceptions import EntityNotFoundError

class BookService:
    def __init__(self, repository: IBookRepository):
        self.repository = repository

    def get_book(self, book_id: str) -> BookRead:
        # Try searching with the exact ID provided in the URL
        book_data = self.repository.get_by_id(book_id)
        
        # If not found and ID doesn't already start with /books/, 
        # try searching with the /books/ prefix as per requirement examples
        if not book_data and not book_id.startswith("/books/"):
            prefixed_id = f"/books/{book_id}"
            book_data = self.repository.get_by_id(prefixed_id)
            
        if not book_data:
            raise EntityNotFoundError("Book", book_id)
            
        return BookRead(**book_data)

    def create_book(self, book_in: BookCreate) -> BookRead:
        # Normalize ID to ensure consistency and prevent collisions
        book_data = book_in.model_dump()
        if not book_data['id'].startswith("/books/"):
            book_data['id'] = f"/books/{book_data['id']}"
        
        normalized_book = BookCreate(**book_data)
        
        # The repository handles the Conflict check atomically using ConditionExpression
        self.repository.create(normalized_book)
        return BookRead(**normalized_book.model_dump())
