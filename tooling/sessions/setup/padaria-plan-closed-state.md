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
updated: 2026-10-10T12:00:00Z
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
- No ar em um mês: até 2026-11-10.

## Steps

| Step | Situation | Main questions |
|---|---|---|
| system-description | closed | 4 of 4 |
| requirements | closed | 3 of 3 |
| modeling | advanced | 3 of 3 |
| architecture | closed | 3 of 3 |
| plan | closed | 1 of 1 |

## Documents

| Document | Situation | Where |
|---|---|---|
| system-description | ready | docs/system-description.md |
| requirements | ready | docs/requirements.md |
| research | ready | docs/research.md |
| architecture | ready | docs/architecture.md |
| decisions | ready | docs/decisions.md |
| plan | ready | docs/plan.md |
| use-cases | not-started | - |
| data-model | not-started | - |
| data-classification | not-started | - |
| wireframes | not-started | - |
| test-plan | ready | docs/test-plan.md |

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

- [x] Hospedagem
- [x] Stack
- [x] Tratamento dos dados pessoais

### plan

- [x] O que vem primeiro

## Refinement questions left for later

- [ ] modeling: a padaria já tem logo e cores? Necessário para o documento de design.

## Answers

### system-description · O problema, quem usa e o escopo

A padaria recebe encomendas pelo WhatsApp e perde pedidos. O cliente passa a
fazer a encomenda num site, e a atendente vê a lista do dia. Fora da primeira
versão: pagamento online; o cliente paga na retirada.

### requirements · O que cada um faz, limites e sucesso

O cliente escolhe os produtos e a data de retirada e deixa nome e telefone. A
atendente vê a lista do dia e marca cada encomenda como pronta ou retirada.
Deu certo se em um mês nenhuma encomenda se perder.

### modeling · O que não pode dar errado, o que guarda e as telas

Não pode dar errado: o cliente conseguir encomendar, e a atendente ver a lista
do dia. O site guarda os produtos, as encomendas e o nome e o telefone do
cliente. Telas: o catálogo, a tela de encomenda e a lista do dia.

### architecture · As três decisões

Hospedagem, stack e tratamento dos dados pessoais, decididas pela pessoa ao
aceitar as recomendações, com a condição de ser tudo gratuito. Estão em
`docs/decisions.md`.

### plan · O que vem primeiro

Primeiro a encomenda pelo cliente, depois a lista da atendente. A pessoa
desenvolve sozinha e pediu para fechar o plano.

## Decisions

- D-001 · Hospedagem na Cloudflare · decided
- D-002 · Stack: Astro com TypeScript e banco D1 · decided
- D-003 · Nome e telefone apagados 90 dias depois da retirada · decided

## Open points

- A leitura da web foi recusada na sessão das decisões: o que conferir está em `docs/test-plan.md`, de T-001 a T-003.
- Documentos da modelagem ainda não são escritos nesta versão do Blueprint. As respostas estão em `## Answers`.

## Next question

Não há pergunta pendente: as cinco etapas foram percorridas e o plano está
fechado.
