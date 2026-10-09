---
blueprint_state: 1
project: agenda-clinica
starting_point: start
document_language: pt-BR
developers: 1
documents_at: docs/
tasks_at: docs/plan.md
memory: journal
observability: journal
updated: 2026-10-09T15:30:00Z
updated_by: Claude Code
---

# Project state

## Project kind

| Fact | Value | Known how |
|---|---|---|
| has-screens | yes | said |
| stores-data | yes | deduced |
| holds-personal-data | yes | deduced |
| used-by-command-or-code | no | deduced |
| calls-a-model | unknown | - |

Deduced: aplicativo web com telas, que guarda dados de pacientes.

## Criteria the person declared

- Sem verba para serviços pagos: o que for usado precisa ter plano gratuito.
- A recepção usa só o navegador do computador.

## Steps

| Step | Situation | Main questions |
|---|---|---|
| system-description | closed | 4 of 4 |
| requirements | open | 2 of 3 |
| modeling | not-started | 0 of 3 |
| architecture | not-started | 0 of 2 |
| plan | not-started | 0 of 2 |

## Documents

| Document | Situation | Where |
|---|---|---|
| system-description | ready | docs/system-description.md |
| requirements | in-progress | docs/requirements.md |
| research | in-progress | docs/research.md |
| architecture | not-started | - |
| decisions | in-progress | docs/decisions.md |
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
- [x] O que limita o projeto: verba, prazo, lei, o que já é usado
- [ ] Como saber que deu certo

### modeling

- [ ] As jornadas que não podem dar errado
- [ ] O que o sistema guarda, e se há dado pessoal
- [ ] Quais são as telas principais

### architecture

- [ ] Stack
- [ ] Hospedagem

### plan

- [ ] O que vem primeiro
- [ ] Quem faz o quê

## Refinement questions left for later

- [ ] requirements: existe prazo mínimo para cancelar uma consulta? Necessário para desenhar o cancelamento.

## Answers

### system-description · O problema e quem usa

A clínica marca consultas por telefone e perde horários por falta de aviso. Quem
usa: a recepção, que marca e cancela, e o paciente, que confirma a presença.

### system-description · Entrega e escopo

Aplicativo web, usado no navegador. Fora da primeira versão: pagamento e
prontuário.

### requirements · O que cada um faz

A recepção marca, remarca e cancela. O paciente recebe um aviso e confirma ou
desiste. Só a recepção cancela.

## Decisions

- D-001 · Aplicativo web em vez de aplicativo de celular · decided

## Open points

- Como saber que deu certo: a pessoa ficou de dizer quantas faltas a clínica tem hoje.

## Next question

Como vocês vão saber que o sistema deu certo? Por exemplo: menos faltas, ou menos tempo da recepção ao telefone.
