# Conexão com o banco de dados
import psycopg2


def get_db():
    connection = psycopg2.connect(
        dbname="biblioteca",
        user="professor",
        password="professor",
        host="database-givaldo.cyvusllqjwio.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    try:
        yield connection
    finally:
        connection.close()
