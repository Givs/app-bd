from fastapi import APIRouter, Depends, HTTPException
import psycopg2
from psycopg2 import IntegrityError

from db.connectionn import get_db
from models.reserva import ReservaIn

reserva_route = APIRouter(prefix="/reserva", tags=["reserva"])


@reserva_route.post("/")
def create_reserva(reserva: ReservaIn, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        try:
            # Consultar o número de reservas para o livro
            cursor.execute("SELECT COUNT(*) FROM Reserva WHERE isbn = %s;", (reserva.isbn,))
            count = cursor.fetchone()[0]

            # Verificar se o livro já tem mais de 3 reservas
            if count >= 3:
                raise HTTPException(status_code=400, detail="Não é possível reservar este livro. Ele já tem 3 reservas.")

            # Se o livro tiver 3 ou menos reservas, inserir a nova reserva
            cursor.execute("INSERT INTO Reserva (isbn, cliente_id) VALUES (%s, %s);", (reserva.isbn, reserva.cliente_id))
            db.commit()
            return {"message": "Reserva criada com sucesso!"}
        except IntegrityError:
            db.rollback()  # Reverter a transação
            raise HTTPException(status_code=400, detail="Reserva já existe ou dados inválidos.")
        except Exception as e:
            db.rollback()  # Reverter a transação em caso de qualquer outro erro
            raise e


@reserva_route.delete("/{isbn}/{cliente_id}/")
def delete_reserva(isbn: str, cliente_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Reserva WHERE isbn = %s AND cliente_id = %s;", (isbn, cliente_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reserva não encontrada.")
        db.commit()
    return {"message": "Reserva deletada com sucesso!"}


@reserva_route.get("/cliente/{cpf}/")
def list_reservas_by_cliente(cpf: str, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
               SELECT 
                    Reserva.isbn, 
                    Livro.titulo,
                    Usuario.cpf,
                    Usuario.primeiro_nome,
                    Usuario.sobrenome
                    FROM Reserva
                    JOIN Livro ON Reserva.isbn = Livro.isbn
                    JOIN Cliente ON Reserva.cliente_id = Cliente.id
                    JOIN Usuario ON Cliente.cpf = Usuario.cpf
                    WHERE Usuario.cpf = %s;
        """, (cpf,))
        results = cursor.fetchall()
        if not results:
            return {"message": f"Nenhuma reserva encontrada para o cliente com CPF {cpf}."}

        reservas = [
            {
                "isbn": result[0],
                "titulo": result[1],
                "cpf": result[2],
                "primeiro_nome": result[3],
                "sobrenome": result[4]
            }
            for result in results
        ]
    return reservas


@reserva_route.get("/isbn/{isbn}/cliente/{cliente_id}/")
def get_reserva(isbn: str, cliente_id: int, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Reserva.isbn, 
                Livro.titulo,
                Livro.ano_publicacao,
                Usuario.cpf,
                Usuario.primeiro_nome,
                Usuario.sobrenome,
                Cliente.data_associacao
            FROM Reserva
            JOIN Livro ON Reserva.isbn = Livro.isbn
            JOIN Cliente ON Reserva.cliente_id = Cliente.id
            JOIN Usuario ON Cliente.cpf = Usuario.cpf
            WHERE Reserva.isbn = %s AND Reserva.cliente_id = %s;
        """, (isbn, cliente_id))

        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Reserva não encontrada.")

        reserva = {
            "isbn": result[0],
            "titulo": result[1],
            "ano_publicacao": result[2],
            "cpf": result[3],
            "primeiro_nome": result[4],
            "sobrenome": result[5],
            "data_associacao": result[6]
        }
    return reserva
