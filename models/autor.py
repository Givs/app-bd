from pydantic import BaseModel


class Autor(BaseModel):
    id: int
    nome: str
    biografia: str


class AutorIn(BaseModel):
    nome: str
    biografia: str
