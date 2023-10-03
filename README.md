# app-bd
Esta API foi desenvolvida para gerenciar os principais aspectos de uma livraria, incluindo livros, autores, editoras, clientes, endereços e reservas.

# Tabelas e Relacionamentos
Editora

    email (chave primária)
    nome
    telefone

Livro
    
    isbn (chave primária)
    titulo
    ano_publicacao
    editora_email (chave estrangeira para Editora)
    
Autor
  
    id (chave primária)
    nome
    biografia

Autor_Livro (relacionamento muitos-para-muitos entre Autor e Livro)
    
    autor_id (chave estrangeira para Autor)
    isbn (chave estrangeira para Livro)

Endereco
    
    id (chave primária)
    cep
    rua
    bairro
    cidade
    estado
    pais

Usuario
    
    cpf (chave primária)
    primeiro_nome
    sobrenome
    telefone
    endereco_id (chave estrangeira para Endereco)

Cliente
   
    id (chave primária)
    cpf (chave estrangeira para Usuario e única)
    data_associacao

Reserva (relacionamento livro-cliente)
    
    isbn (chave estrangeira para Livro)
    cliente_id (chave estrangeira para Cliente)
    A combinação de isbn e cliente_id é única.

# Rotas Principais
CRUD para Editora, Livro, Autor, Endereco, Usuario/Cliente e Reserva.


Rota para listar todos os autores.


Rota para listar todas as reservas de um cliente específico.


Rota para obter detalhes de uma reserva específica.

# Funcionalidades Especiais
Ao criar um livro, é possível associar múltiplos autores.


Ao criar um cliente, o usuário associado é criado na mesma transação.


Ao deletar um cliente, o usuário associado é deletado automaticamente (CASCADE).


Ao deletar um livro, as associações na tabela Autor_Livro são removidas primeiro.


Ao criar uma reserva, a API verifica se o livro já tem mais de 3 reservas. Se tiver, a reserva não é permitida. Se não tiver, insere (transction, consulta + insert)

# Erros e Exceções
A API lida com vários erros e exceções, como:

Tentar inserir um livro com ISBN já existente.


Tentar inserir/editar um livro com um ano de publicação inválido.


Tentar deletar uma editora que ainda tem livros associados.

# Como Rodar
Instale as dependências: ```pip install -r requirements.txt```


Execute o servidor: ```uvicorn main:app --reload```


Acesse a documentação da API via swagger em: http://localhost:8000/docs

Se preferir, você pode baixar as requisições pré-configuradas para o Insomnia. [Clique aqui](https://drive.google.com/file/d/1cbjinPdK_vZUW8BzrNCrSbWb0X4GiOwL/view?usp=sharing) para baixar o arquivo JSON do Insomnia.

Após baixar o arquivo, abra o Insomnia, clique em "Import/Export" no canto superior direito, escolha "Import Data" > "From File" e selecione o arquivo JSON baixado.

