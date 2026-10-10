# Loja

Servidor que devolve a lista de produtos da loja, para o site e o caixa consultarem.

## Como rodar

    npm start

Sobe em http://localhost:3000. Não tem dependências para instalar.

## Rotas

- `GET /produtos`: os produtos à venda, com nome, preço em centavos e categoria.
- `GET /saude`: responde `ok`.

## Como testar

    npm test
