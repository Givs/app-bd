import psycopg2
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import IntegrityError

from db.connectionn import get_db
from models.cliente import ClienteIn
from utils.helpers.extract_table_from_error import extract_table_from_error

cliente_route = APIRouter(prefix="/cliente", tags=["cliente"])


@cliente_route.post("/")
def create_cliente(cliente: ClienteIn, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            # Primeiro, inserimos o Usuario
            cursor.execute("""
                INSERT INTO Usuario (cpf, primeiro_nome, sobrenome, telefone, endereco_id)
                VALUES (%s, %s, %s, %s, %s);
            """, (cliente.cpf, cliente.primeiro_nome, cliente.sobrenome, cliente.telefone, cliente.endereco_id))

            # Em seguida, inserimos o Cliente usando o cpf do Usuario
            cursor.execute("""
                INSERT INTO Cliente (cpf, data_associacao)
                VALUES (%s, %s);
            """, (cliente.cpf, cliente.data_associacao))

            db.commit()
        return {"message": "Cliente e usuário criados com sucesso!"}
    except psycopg2.errors.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="CPF já existe ou referência de endereço inválida.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@cliente_route.get("/{cpf}/")
def read_cliente(cpf: str, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Cliente.id, 
                Usuario.cpf, 
                Usuario.primeiro_nome, 
                Usuario.sobrenome, 
                Usuario.telefone, 
                Usuario.endereco_id, 
                Cliente.data_associacao
            FROM Usuario
            JOIN Cliente ON Usuario.cpf = Cliente.cpf
            WHERE Usuario.cpf = %s;
        """, (cpf,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return {
        "id": result[0],
        "cpf": result[1],
        "primeiro_nome": result[2],
        "sobrenome": result[3],
        "telefone": result[4],
        "endereco_id": result[5],
        "data_associacao": result[6]
    }


@cliente_route.get("/")
def list_all_clientes(db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Cliente.id, 
                Usuario.cpf, 
                Usuario.primeiro_nome, 
                Usuario.sobrenome, 
                Usuario.telefone, 
                Usuario.endereco_id, 
                Cliente.data_associacao
            FROM Usuario
            JOIN Cliente ON Usuario.cpf = Cliente.cpf;
        """)
        results = cursor.fetchall()
        if not results:
            return {"message": "Nenhum cliente encontrado."}

        clientes = [
            {
                "id": result[0],
                "cpf": result[1],
                "primeiro_nome": result[2],
                "sobrenome": result[3],
                "telefone": result[4],
                "endereco_id": result[5],
                "data_associacao": result[6]
            }
            for result in results
        ]
    return clientes


@cliente_route.put("/{cpf}/")
def update_cliente(cpf: str, cliente: ClienteIn, db: psycopg2.extensions.connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            # Atualizar Usuario
            cursor.execute("""
                UPDATE Usuario 
                SET primeiro_nome = %s, sobrenome = %s, telefone = %s, endereco_id = %s
                WHERE cpf = %s;
            """, (cliente.primeiro_nome, cliente.sobrenome, cliente.telefone, cliente.endereco_id, cpf))

            # Atualizar Cliente
            cursor.execute("""
                UPDATE Cliente 
                SET data_associacao = %s
                WHERE cpf = %s;
            """, (cliente.data_associacao, cpf))

            db.commit()
        return {"message": "Cliente e usuário atualizados com sucesso!"}
    except psycopg2.errors.ForeignKeyViolation as e:
        if 'endereco_id' in str(e):
            raise HTTPException(status_code=400, detail="Endereço não encontrado.")
        raise


@cliente_route.delete("/{cpf}/")
def delete_cliente(cpf: str, db: psycopg2.extensions.connection = Depends(get_db)):
    with db.cursor() as cursor:
        try:
            # Deletar Usuário (o Cliente será deletado automaticamente devido à restrição de chave estrangeira CASCADE)
            cursor.execute("DELETE FROM Usuario WHERE cpf = %s;", (cpf,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Cliente não encontrado.")
            db.commit()
        except IntegrityError as e:
            table_name = extract_table_from_error(str(e))
            raise HTTPException(status_code=400,
                            detail=f"Não é possível excluir o cliente porque ainda há registros associados na tabela {table_name}.")
    return {"message": "Cliente deletado com sucesso!"}

