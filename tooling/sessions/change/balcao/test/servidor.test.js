const test = require("node:test");
const assert = require("node:assert");
const { servidor } = require("../src/server");

function pedir(caminho) {
  return new Promise((resolve) => {
    servidor.listen(0, async () => {
      const resposta = await fetch(`http://localhost:${servidor.address().port}${caminho}`);
      const texto = await resposta.text();
      servidor.close(() => resolve({ codigo: resposta.status, texto }));
    });
  });
}

test("GET /produtos devolve só os produtos à venda", async () => {
  const { codigo, texto } = await pedir("/produtos");
  assert.strictEqual(codigo, 200);
  assert.deepStrictEqual(JSON.parse(texto).map((produto) => produto.nome), ["Pão francês", "Bolo de cenoura"]);
});

test("GET /saude responde ok", async () => {
  const { codigo, texto } = await pedir("/saude");
  assert.strictEqual(codigo, 200);
  assert.strictEqual(texto, "ok");
});
