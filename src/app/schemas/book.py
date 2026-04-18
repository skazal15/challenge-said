from pydantic import BaseModel, Field

class BookBase(BaseModel):
    id: str = Field(..., description="Unique identifier for the book (e.g., /books/id1)")
    author: str = Field(..., description="Identifier for the author (e.g., /authors/id1)")
    name: str = Field(..., description="Name of the book")
    note: str = Field(..., description="Brief note about the book")
    serial: str = Field(..., description="Serial number of the book")

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    pass
