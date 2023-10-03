import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError

from db.connectionn import get_db
from models.endereco import Endereco, EnderecoIn
from utils.error_messages.endereco import ENDERECO_NOT_FOUND
from utils.helpers.extract_table_from_error import extract_table_from_error
from utils.helpers.pg_codes import FOREIGN_KEY_VIOLATION_CODE

endereco_route = APIRouter(prefix="/endereco", tags=["endereco"])


@endereco_route.post("/")
def create_endereco(endereco: EnderecoIn, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Endereco (cep, rua, bairro, cidade, estado, pais) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """, (endereco.cep, endereco.rua, endereco.bairro, endereco.cidade, endereco.estado, endereco.pais))
        endereco_id = cursor.fetchone()[0]
        db.commit()
    return {"id": endereco_id, **endereco.model_dump()}


@endereco_route.get("/{endereco_id}/")
def read_endereco(endereco_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Endereco WHERE id = %s;", (endereco_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=ENDERECO_NOT_FOUND)
    return Endereco(id=result[0], cep=result[1], rua=result[2], bairro=result[3], cidade=result[4], estado=result[5], pais=result[6])


@endereco_route.put("/{endereco_id}/")
def update_endereco(endereco_id: int, endereco: EnderecoIn, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            UPDATE Endereco SET cep = %s, rua = %s, bairro = %s, cidade = %s, estado = %s, pais = %s 
            WHERE id = %s;
        """, (endereco.cep, endereco.rua, endereco.bairro, endereco.cidade, endereco.estado, endereco.pais, endereco_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=ENDERECO_NOT_FOUND)
        db.commit()
    return {"id": endereco_id, **endereco.dict()}


@endereco_route.delete("/{endereco_id}/")
def delete_endereco(endereco_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM Endereco WHERE id = %s;", (endereco_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=ENDERECO_NOT_FOUND)
            db.commit()
        except IntegrityError as e:
            if e.pgcode == FOREIGN_KEY_VIOLATION_CODE:
                table_name = extract_table_from_error(str(e))
                raise HTTPException(status_code=400,
                                    detail=f"Não é possível excluir o endereço porque ainda há registros associados na tabela {table_name}.")
    return {"message": "Endereço deletado com sucesso!"}

