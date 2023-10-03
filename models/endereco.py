from pydantic import BaseModel


class Endereco(BaseModel):
    id: int
    cep: str
    rua: str
    bairro: str
    cidade: str
    estado: str
    pais: str


class EnderecoIn(BaseModel):
    cep: str
    rua: str
    bairro: str
    cidade: str
    estado: str
    pais: str
