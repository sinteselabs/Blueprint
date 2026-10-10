---
blueprint_state: 1
project: padaria-pedidos
starting_point: start
document_language: pt-BR
developers: 1
documents_at: docs/
tasks_at: docs/plan.md
memory: journal
observability: journal
updated: 2026-10-09T23:29:40Z
updated_by: Claude Code
---

# Project state

## Project kind

| Fact | Value | Known how |
|---|---|---|
| has-screens | yes | said |
| stores-data | yes | said |
| holds-personal-data | yes | said |
| used-by-command-or-code | no | deduced |
| calls-a-model | no | deduced |

Deduced: site com telas, que guarda os produtos, as encomendas e o nome e o telefone de quem encomenda, sem IA.

## Criteria the person declared

- Sem verba para serviço pago: o que for usado precisa ter plano gratuito.
- Precisa funcionar bem no celular do cliente.
- Deu certo se em um mês nenhuma encomenda se perder.

## Steps

| Step | Situation | Main questions |
|---|---|---|
| system-description | closed | 4 of 4 |
| requirements | closed | 3 of 3 |
| modeling | advanced | 3 of 3 |
| architecture | open | 0 of 3 |
| plan | not-started | 0 of 1 |

## Documents

| Document | Situation | Where |
|---|---|---|
| system-description | ready | docs/system-description.md |
| requirements | ready | docs/requirements.md |
| research | ready | docs/research.md |
| architecture | not-started | - |
| decisions | not-started | - |
| plan | not-started | - |
| use-cases | not-started | - |
| data-model | not-started | - |
| data-classification | not-started | - |
| wireframes | not-started | - |

## Main questions

### system-description

- [x] Que problema o sistema resolve, e para quem
- [x] O que a pessoa quer conseguir com ele
- [x] Como ele chega a quem usa
- [x] O que fica fora da primeira versão

### requirements

- [x] O que cada tipo de usuário precisa conseguir fazer
- [x] O que limita o projeto
- [x] Como saber que deu certo

### modeling

- [x] As jornadas que não podem dar errado
- [x] O que o sistema guarda, e se há dado pessoal
- [x] Quais são as telas principais

### architecture

- [ ] Hospedagem
- [ ] Stack
- [ ] Tratamento dos dados pessoais

### plan

- [ ] O que vem primeiro

## Refinement questions left for later

Nenhuma ainda.

## Answers

### system-description · O problema, quem usa e o escopo

A padaria recebe encomendas pelo WhatsApp e perde pedidos. O cliente passa a
fazer a encomenda num site, e a atendente vê a lista do dia. Fora da primeira
versão: pagamento online; o cliente paga na retirada.

### requirements · O que cada um faz, limites e sucesso

O cliente escolhe os produtos e a data de retirada e deixa nome e telefone. A
atendente vê a lista do dia e marca cada encomenda como pronta ou retirada.
Limites: sem verba, e precisa funcionar bem no celular do cliente. Deu certo se
em um mês nenhuma encomenda se perder.

### modeling · O que não pode dar errado, o que guarda e as telas

Não pode dar errado: o cliente conseguir encomendar, e a atendente ver a lista
do dia. O site guarda os produtos, as encomendas e o nome e o telefone do
cliente. Telas principais: o catálogo, a tela de encomenda e a lista do dia.

### architecture · Pesquisa da hospedagem

A hospedagem foi pesquisada e está em `docs/research.md`. Nenhuma fonte pôde
ser lida na sessão, e a pessoa ainda não escolheu.

## Decisions

Nenhuma ainda.

## Open points

- A hospedagem, a stack e o tratamento dos dados pessoais ainda não foram decididos. A stack depende da hospedagem.

## Next question

Onde o site fica hospedado, junto com o banco de dados?
