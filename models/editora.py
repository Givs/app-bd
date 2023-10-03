from pydantic import BaseModel, EmailStr


class Editora(BaseModel):
    email: EmailStr
    nome: str


class EditoraIn(BaseModel):
    nome: str
