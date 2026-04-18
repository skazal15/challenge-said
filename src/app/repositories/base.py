from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.app.schemas.book import BookRead, BookCreate

class IBookRepository(ABC):
    @abstractmethod
    def get_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def create(self, book: BookCreate) -> bool:
        pass
