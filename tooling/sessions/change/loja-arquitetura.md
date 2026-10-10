# Arquitetura

O servidor é um processo Node só, sem dependências.

- O servidor fica em `src/app.js` e responde em `/produtos` e `/saude`.
- Os produtos são lidos de `data/produtos.json` por `src/produtos.js`, que devolve só os que estão à venda.
- Os testes rodam com Jest: `npm test`.
