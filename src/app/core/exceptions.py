from typing import Optional
from fastapi import HTTPException, status

class DomainError(Exception):
    pass

class EntityAlreadyExistsError(DomainError):
    def __init__(self, entity_name: str, entity_id: str):
        self.message = f"{entity_name} with ID {entity_id} already exists"
        super().__init__(self.message)

class EntityNotFoundError(DomainError):
    def __init__(self, entity_name: str, entity_id: str):
        self.message = f"{entity_name} with ID {entity_id} not found"
        super().__init__(self.message)
