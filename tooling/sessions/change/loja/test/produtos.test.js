const test = require("node:test");
const assert = require("node:assert");
const { listar } = require("../src/produtos");

test("lista só os produtos à venda", () => {
  const produtos = listar();
  assert.ok(produtos.length > 0);
  assert.ok(produtos.every((produto) => produto.aVenda));
});
