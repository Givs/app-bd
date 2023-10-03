import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError

from db.connectionn import get_db
from models.livro import Livro, LivroIn
from utils.error_messages.autor import AUTOR_NOT_FOUND
from utils.error_messages.editora import EDITORA_NOT_FOUND
from utils.error_messages.livro import ISBN_EXISTS, LIVRO_NOT_FOUND, ISBN_OR_TITULO_TOO_LONG, ANO_PUBLICACAO_INVALIDO
from utils.helpers.extract_table_from_error import extract_table_from_error
from utils.helpers.pg_codes import FOREIGN_KEY_VIOLATION_CODE

livro_route = APIRouter(prefix="/livro", tags=["books"])


@livro_route.post("/")
def create_livro(livro: Livro, db: psycopg2.extensions.connection = Depends(get_db)):
    # Verificar se pelo menos um autor foi fornecido
    if not livro.autores_ids:
        raise HTTPException(status_code=400, detail="Um livro deve ter pelo menos um autor.")

    try:
        with db.cursor() as cursor:
            # Iniciar transação
            cursor.execute("BEGIN;")

            # Inserir o livro
            cursor.execute(
                "INSERT INTO Livro (isbn, titulo, ano_publicacao, editora_id) VALUES (%s, %s, %s, %s) RETURNING isbn;",
                (livro.isbn, livro.titulo, livro.ano_publicacao, livro.editora_email))
            isbn = cursor.fetchone()[0]

            # Inserir associações na tabela Autor_Livro
            for autor_id in livro.autores_ids:
                cursor.execute("INSERT INTO Autor_Livro (autor_id, isbn) VALUES (%s, %s);", (autor_id, isbn))

            # Confirmar transação
            db.commit()

        return {
            "isbn": isbn,
            "titulo": livro.titulo,
            "ano_publicacao": livro.ano_publicacao,
            "editora_id": livro.editora_email,
            "autores_ids": livro.autores_ids
        }

    except psycopg2.errors.StringDataRightTruncation:
        raise HTTPException(status_code=400, detail=ISBN_OR_TITULO_TOO_LONG)
    except psycopg2.errors.ForeignKeyViolation as e:
        if "editora" in str(e):
            raise HTTPException(status_code=400, detail=EDITORA_NOT_FOUND)
        else:
            db.rollback()  # Reverter transação se algum id de autor passado não existir
            raise HTTPException(status_code=400, detail=AUTOR_NOT_FOUND)
    except psycopg2.errors.CheckViolation:
            raise HTTPException(status_code=400, detail=ANO_PUBLICACAO_INVALIDO)
    except IntegrityError:
        raise HTTPException(status_code=400, detail=ISBN_EXISTS)


@livro_route.get("/")
def read_all_livros(db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Livro;")
        result = cursor.fetchall()
        if not result:
            return {"message": "Nenhum livro encontrado"}
        livros = [{"isbn": isbn, "titulo": titulo, "ano_publicacao": ano_publicacao, "editora_id": editora_id} for isbn, titulo, ano_publicacao, editora_id in result]
    return livros


@livro_route.get("/{isbn}/")
def read_livro(isbn: str, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Livro.isbn, 
                Livro.titulo, 
                Livro.ano_publicacao, 
                Livro.editora_id, 
                Editora.nome,
                ARRAY_AGG(Autor.nome) as autores
            FROM Livro
            JOIN Editora ON Livro.editora_id = Editora.email
            LEFT JOIN Autor_Livro ON Livro.isbn = Autor_Livro.isbn
            LEFT JOIN Autor ON Autor_Livro.autor_id = Autor.id
            WHERE Livro.isbn = %s
            GROUP BY Livro.isbn, Livro.titulo, Livro.ano_publicacao, Livro.editora_id, Editora.nome;
        """, (isbn,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail=LIVRO_NOT_FOUND)
    return {
        "isbn": result[0],
        "titulo": result[1],
        "ano_publicacao": result[2],
        "editora_id": result[3],
        "editora_nome": result[4],
        "autores": result[5]
    }


@livro_route.put("/{isbn}/")
def update_livro(isbn: str, livro: LivroIn, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            # Atualizar detalhes do livro
            cursor.execute("UPDATE Livro SET titulo = %s, ano_publicacao = %s, editora_id = %s WHERE isbn = %s;",
                           (livro.titulo, livro.ano_publicacao, livro.editora_email, isbn))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=LIVRO_NOT_FOUND)

            # Inserir novos relacionamentos na tabela Autor_Livro
            for autor_id in livro.autores_ids:
                cursor.execute("INSERT INTO Autor_Livro (autor_id, isbn) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                               (autor_id, isbn))

            db.commit()

        return {"isbn": isbn, "titulo": livro.titulo, "ano_publicacao": livro.ano_publicacao, "editora_id": livro.editora_email}
    except psycopg2.errors.StringDataRightTruncation:
        raise HTTPException(status_code=400, detail=ISBN_OR_TITULO_TOO_LONG)
    except psycopg2.errors.ForeignKeyViolation as e:
        if "editora_email" in str(e):
            raise HTTPException(status_code=400, detail=EDITORA_NOT_FOUND)
        else:
            raise HTTPException(status_code=400, detail=AUTOR_NOT_FOUND)
    except psycopg2.errors.CheckViolation:
        raise HTTPException(status_code=400, detail=ANO_PUBLICACAO_INVALIDO)
    except IntegrityError:
        raise HTTPException(status_code=400, detail=ISBN_EXISTS)


@livro_route.delete("/{isbn}/")
def delete_livro(isbn: str, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        try:
            # Primeiro, remova as relações de autor-livro para o livro especificado
            cursor.execute("DELETE FROM Autor_Livro WHERE isbn = %s;", (isbn,))

            # Em seguida, exclua o livro
            cursor.execute("DELETE FROM Livro WHERE isbn = %s;", (isbn,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=LIVRO_NOT_FOUND)

            db.commit()
        except IntegrityError as e:
            if e.pgcode == FOREIGN_KEY_VIOLATION_CODE:
                table_name = extract_table_from_error(str(e))
                raise HTTPException(status_code=400,
                                    detail=f"Não é possível excluir o livro porque ainda há registros associados na tabela {table_name}.")
    return {"message": "Livro deletado com sucesso!"}

