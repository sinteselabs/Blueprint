# Requisitos

| Nº | Requisito |
|---|---|
| FR-01 | `GET /produtos` devolve os produtos à venda, com nome e preço em centavos |
| FR-02 | `GET /clientes` devolve os clientes, com nome e telefone |
| FR-03 | `GET /pedidos?dia=AAAA-MM-DD` devolve os pedidos com retirada naquele dia; sem `dia`, devolve os de hoje |
| FR-04 | `POST /pedidos` grava um pedido com cliente, produtos e dia de retirada, e recusa com 400 o pedido sem cliente, sem produto ou sem dia |
| FR-05 | `GET /saude` responde `ok` |
