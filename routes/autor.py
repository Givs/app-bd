from fastapi import APIRouter, Depends, HTTPException
import psycopg2
from psycopg2 import IntegrityError

from db.connectionn import get_db
from models.autor import Autor, AutorIn
from utils.error_messages.autor import NOME_TOO_LONG, AUTOR_NOT_FOUND, BIOGRAFIA_TOO_LONG
from utils.helpers.extract_table_from_error import extract_table_from_error

autor_route = APIRouter(prefix="/autor", tags=["autor"])


@autor_route.post("/")
def create_autor(autor: AutorIn, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO Autor (nome, biografia) VALUES (%s, %s) RETURNING id;",
                           (autor.nome, autor.biografia))
            autor_id = cursor.fetchone()[0]
            db.commit()
        return {"id": autor_id, "nome": autor.nome, "biografia": autor.biografia}
    except psycopg2.errors.StringDataRightTruncation as e:
        if "nome" in str(e):
            raise HTTPException(status_code=400, detail=NOME_TOO_LONG)
        elif "biografia" in str(e):
            raise HTTPException(status_code=400, detail=BIOGRAFIA_TOO_LONG)


@autor_route.get("/")
def list_all_autores(db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Autor;")
        results = cursor.fetchall()

        if not results:
            return {"message": "Nenhum autor encontrado."}

        autores = [
            {
                "id": result[0],
                "nome": result[1],
                "biografia": result[2]
            }
            for result in results
        ]
    return autores


@autor_route.get("/{autor_id}/")
def read_autor(autor_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Autor WHERE id = %s;", (autor_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail=AUTOR_NOT_FOUND)
    return {"id": result[0], "nome": result[1], "biografia": result[2]}


@autor_route.put("/{autor_id}/")
def update_autor(autor_id: int, autor: AutorIn, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        try:
            cursor.execute("UPDATE Autor SET nome = %s, biografia = %s WHERE id = %s;",
                           (autor.nome, autor.biografia, autor_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=AUTOR_NOT_FOUND)
            db.commit()
        except psycopg2.errors.StringDataRightTruncation as e:
            if "nome" in str(e):
                raise HTTPException(status_code=400, detail=NOME_TOO_LONG)
            elif "biografia" in str(e):
                raise HTTPException(status_code=400, detail=BIOGRAFIA_TOO_LONG)
    return {"id": autor_id, "nome": autor.nome, "biografia": autor.biografia}


@autor_route.delete("/{autor_id}/")
def delete_autor(autor_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM Autor WHERE id = %s;", (autor_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=AUTOR_NOT_FOUND)
            db.commit()
        except IntegrityError as e:
            table_name = extract_table_from_error(str(e))
            raise HTTPException(status_code=400,
                                detail=f"Não é possível excluir o autor porque ainda há registros associados na tabela {table_name}.")
    return {"message": "Autor deletado com sucesso!"}
