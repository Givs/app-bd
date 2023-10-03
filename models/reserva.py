from pydantic import BaseModel


class ReservaIn(BaseModel):
    isbn: str
    cliente_id: int
