const http = require("node:http");
const { listar } = require("./produtos");

const servidor = http.createServer((pedido, resposta) => {
  if (pedido.method === "GET" && pedido.url === "/produtos") {
    resposta.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    resposta.end(JSON.stringify(listar()));
    return;
  }
  if (pedido.method === "GET" && pedido.url === "/saude") {
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
