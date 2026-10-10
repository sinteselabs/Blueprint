const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const DADOS = path.join(__dirname, "..", "data");
const JSON_UTF8 = { "Content-Type": "application/json; charset=utf-8" };

const servidor = http.createServer((pedido, resposta) => {
  const endereco = new URL(pedido.url, "http://localhost");

  if (pedido.method === "GET" && endereco.pathname === "/produtos") {
    const produtos = JSON.parse(fs.readFileSync(path.join(DADOS, "produtos.json"), "utf-8"));
    const aVenda = produtos.filter((p) => p.aVenda).map((p) => ({ nome: p.nome, precoCentavos: p.precoCentavos }));
    resposta.writeHead(200, JSON_UTF8);
    resposta.end(JSON.stringify(aVenda));
    return;
  }

  if (pedido.method === "GET" && endereco.pathname === "/clientes") {
    const clientes = JSON.parse(fs.readFileSync(path.join(DADOS, "clientes.json"), "utf-8"));
    resposta.writeHead(200, JSON_UTF8);
    resposta.end(JSON.stringify(clientes.map((c) => ({ nome: c.nome, telefone: c.telefone }))));
    return;
  }

  if (pedido.method === "GET" && endereco.pathname === "/pedidos") {
    const dia = endereco.searchParams.get("dia") || new Date().toISOString().slice(0, 10);
    const pedidos = JSON.parse(fs.readFileSync(path.join(DADOS, "pedidos.json"), "utf-8"));
    resposta.writeHead(200, JSON_UTF8);
    resposta.end(JSON.stringify(pedidos.filter((p) => p.retirada === dia)));
    return;
  }

  if (pedido.method === "POST" && endereco.pathname === "/pedidos") {
    let corpo = "";
    pedido.on("data", (parte) => {
      corpo += parte;
    });
    pedido.on("end", () => {
      let novo;
      try {
        novo = JSON.parse(corpo);
      } catch {
        novo = null;
      }
      if (!novo || !novo.cliente || !Array.isArray(novo.produtos) || novo.produtos.length === 0 || !novo.retirada) {
        resposta.writeHead(400, JSON_UTF8);
        resposta.end(JSON.stringify({ erro: "pedido sem cliente, sem produto ou sem dia de retirada" }));
        return;
      }
      const arquivo = path.join(DADOS, "pedidos.json");
      const pedidos = JSON.parse(fs.readFileSync(arquivo, "utf-8"));
      const gravado = { numero: pedidos.length + 1, cliente: novo.cliente, produtos: novo.produtos, retirada: novo.retirada };
      pedidos.push(gravado);
      fs.writeFileSync(arquivo, JSON.stringify(pedidos, null, 2));
      resposta.writeHead(201, JSON_UTF8);
      resposta.end(JSON.stringify(gravado));
    });
    return;
  }

  if (pedido.method === "GET" && endereco.pathname === "/saude") {
    resposta.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
    resposta.end("ok");
    return;
  }

  resposta.writeHead(404);
  resposta.end();
});

if (require.main === module) {
  servidor.listen(process.env.PORT || 3000);
}

module.exports = { servidor };
