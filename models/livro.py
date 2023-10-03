from typing import List

from pydantic import BaseModel, EmailStr
from datetime import date


class Livro(BaseModel):
    isbn: str
    titulo: str
    ano_publicacao: date
    editora_email: EmailStr
    autores_ids: List[int]


class LivroIn(BaseModel):
    titulo: str
    ano_publicacao: date
    editora_email: EmailStr
    autores_ids: List[int] = []

