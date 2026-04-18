from typing import Optional
from src.app.repositories.base import IBookRepository
from src.app.schemas.book import BookRead, BookCreate
from src.app.core.exceptions import EntityNotFoundError

class BookService:
    def __init__(self, repository: IBookRepository):
        self.repository = repository

    def get_book(self, book_id: str) -> BookRead:
        book_data = self.repository.get_by_id(book_id)
        if not book_data:
            raise EntityNotFoundError("Book", book_id)
        return BookRead(**book_data)

    def create_book(self, book_in: BookCreate) -> BookRead:
        self.repository.create(book_in)
        return BookRead(**book_in.model_dump())
