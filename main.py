from fastapi import FastAPI

from routes import editora, livro, autor, endereco, cliente, reserva

app = FastAPI()

app.include_router(editora.editora_route)
app.include_router(livro.livro_route)
app.include_router(autor.autor_route)
app.include_router(endereco.endereco_route)
app.include_router(cliente.cliente_route)
app.include_router(reserva.reserva_route)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
