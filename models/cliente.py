from datetime import date
from typing import Optional

from pydantic import BaseModel


class ClienteIn(BaseModel):
    cpf: str
    primeiro_nome: str
    sobrenome: str
    telefone: Optional[str]
    endereco_id: int
    data_associacao: date
