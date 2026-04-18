from pydantic import BaseModel, Field

class BookBase(BaseModel):
    id: str = Field(..., pattern=r"^[A-Za-z0-9/\-_]+$", min_length=1, max_length=100, description="Unique identifier for the book (e.g., /books/id1)")
    author: str = Field(..., pattern=r"^[A-Za-z0-9/\-_]+$", min_length=1, max_length=100, description="Identifier for the author (e.g., /authors/id1)")
    name: str = Field(..., min_length=1, max_length=200, description="Name of the book")
    note: str = Field(..., min_length=0, max_length=1000, description="Brief note about the book")
    serial: str = Field(..., pattern=r"^[A-Za-z0-9\-_]+$", min_length=1, max_length=50, description="Serial number of the book")

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    pass
