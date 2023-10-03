import psycopg2
from fastapi import HTTPException, Depends, APIRouter
from psycopg2 import IntegrityError
from pydantic import EmailStr

from db.connectionn import get_db
from models.editora import EditoraIn, Editora
from utils.error_messages.editora import EMAIL_EXISTS, EDITORA_NOT_FOUND
from utils.helpers.extract_table_from_error import extract_table_from_error
from utils.helpers.pg_codes import FOREIGN_KEY_VIOLATION_CODE

editora_route = APIRouter(prefix="/editora", tags=["lessons"])


@editora_route.post("/")
def create_editora(editora: Editora, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO Editora (email, nome) VALUES (%s, %s) RETURNING email;", (editora.email, editora.nome))
            email = cursor.fetchone()[0]
            db.commit()
        return {"email": email, "nome": editora.nome}
    except IntegrityError:
        raise HTTPException(status_code=400, detail=EMAIL_EXISTS)


@editora_route.get("/")
def read_all_editoras(db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Editora;")
        result = cursor.fetchall()
        if not result:
            return {"message": "Nenhuma editora encontrada"}
        editoras = [{"email": email, "nome": nome} for email, nome in result]
    return editoras


@editora_route.get("/{email}/")
def read_editora(email: EmailStr, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Editora WHERE email = %s;", (email,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail=EDITORA_NOT_FOUND)
    return {"email": result[0], "nome": result[1]}


@editora_route.put("/{email}/")
def update_editora(email: EmailStr, editora: EditoraIn, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("UPDATE Editora SET nome = %s WHERE email = %s;", (editora.nome, email))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=EDITORA_NOT_FOUND)
        db.commit()
    return {"email": email, "nome": editora.nome}


@editora_route.delete("/{email}/")
def delete_editora(email: EmailStr, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM Editora WHERE email = %s;", (email,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=EDITORA_NOT_FOUND)
            db.commit()
        except IntegrityError as e:
            if e.pgcode == FOREIGN_KEY_VIOLATION_CODE:
                table_name = extract_table_from_error(str(e))
                raise HTTPException(status_code=400,
                                    detail=f"Não é possível excluir porque ainda há registros associados na tabela {table_name}.")
    return {"message": "Editora deletada com sucesso!"}
