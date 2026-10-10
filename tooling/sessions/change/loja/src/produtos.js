const fs = require("node:fs");
const path = require("node:path");

const ARQUIVO = path.join(__dirname, "..", "data", "produtos.json");

// Devolve os produtos à venda, na ordem em que estão no arquivo.
function listar() {
  const todos = JSON.parse(fs.readFileSync(ARQUIVO, "utf-8"));
  return todos.filter((produto) => produto.aVenda);
}

module.exports = { listar };
