---
name: rfc-creator
description: "Gera docs/RFC.md: proposta técnica do Sistema de Webhooks submetida à equipe para revisão, em nível de arquitetura (2 a 4 páginas), com metadados, TL;DR, contexto, proposta, alternativas descartadas na reunião com trade-off, questões em aberto, impacto/riscos e links para os ADRs. Não desce ao detalhe do FDD."
disable-model-invocation: true
---

# RFC Creator

O RFC **propõe e abre para revisão**. Ele fala em decisão, não em implementação. A base é a estrutura de arquitetura do `hld-creator` do curso (componentes, fluxo em alto nível, riscos, ADRs associados), mais as seções que o desafio exige de um RFC.

Carregue e siga `.claude/rules/design-docs.md`.

**Pré-requisitos:**
- `analysis/inventario-transcricao.md`
- ADRs em `docs/adrs/`

Leia ambos antes de escrever.

## Regras específicas

- **Tamanho:** 1.000 a 2.200 palavras, ou seja, 2 a 4 páginas. O validador mede.
- **Nível de detalhe:**
  - Sem payload JSON, sem lista de endpoints com status codes, sem schema de tabela e sem matriz de erros. Isso é FDD.
  - Pode nomear componentes (outbox, worker, DLQ, módulo `src/modules/webhooks` (novo, a criar)) e mostrar **um** diagrama de alto nível em Mermaid ou ASCII.
- **Metadados:**
  - Autora: Larissa (Tech Lead), que se comprometeu a abrir o doc de design ([09:50] Larissa).
  - Revisores: Marcos (PM), Bruno (Eng. Pleno, Pedidos), Diego (Eng. Sênior, Plataforma) e Sofia (Eng. de Segurança). Sofia fica marcada como revisora obrigatória de segurança, com 2 dias úteis ([09:46] Sofia).
  - Status: `Em revisão`.
  - Data: data de redação.
- **Alternativas consideradas:** só as **discutidas e descartadas na reunião**, pelo menos 2 (o pacote tem 6 ou mais). Cada uma traz o trade-off que motivou o descarte, com `[hh:mm] Nome`, e o ID `**RFC-ALT-nn**`.
- **Questões em aberto:** pelo menos 2 **levantadas na reunião e não decididas ou adiadas**, cada uma com `**RFC-Q-nn**`, fonte, o que falta decidir, quem decide e quando (se a reunião disse). Lacunas encontradas só no código entram depois, rotuladas "identificada no código", e não contam para o mínimo.
- **Decisões relacionadas:** link relativo para **todos** os ADRs (`adrs/ADR-NNN-....md`). Na proposta, cada componente aponta para o ADR que o justifica, em vez de repetir a justificativa.
- **Riscos:** `**RFC-RISK-nn**` com probabilidade, impacto e mitigação, em nível arquitetural.

## Modelo de saída (exatamente estes headings)

```markdown
# RFC: Sistema de Webhooks de Notificação de Pedidos

## Metadados

| Campo | Valor |
|---|---|
| Autor | Larissa (Tech Lead) |
| Status | Em revisão |
| Data | AAAA-MM-DD |
| Revisores | ... |
| Documentos relacionados | PRD, FDD, ADRs, Tracker (links) |

## Resumo executivo (TL;DR)

5 a 8 linhas: problema, proposta, garantias, o que fica fora.

## Contexto e problema

Situação atual do OMS (sem notificação externa; clientes fazendo polling em GET /orders), pedido dos clientes B2B, restrições técnicas do código atual.

## Proposta técnica

### Visão geral
Diagrama de alto nível + parágrafo.

### Componentes
Tabela: componente, responsabilidade, ADR.

### Garantias e limites
Entrega, ordering, segurança, latência, em 1 linha cada, com fonte.

## Alternativas consideradas

| ID | Alternativa | Trade-off que motivou o descarte | Fonte |

## Questões em aberto

| ID | Questão | O que falta decidir | Fonte |

## Impacto e riscos

### Impacto
No código existente, na operação (novo processo), nos clientes (dedup, verificação HMAC).

### Riscos
| ID | Risco | Prob. | Impacto | Mitigação |

## Decisões relacionadas

- [ADR-001: ...](adrs/ADR-001-....md)
```

## Após gerar

1. Rode `python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only rfc`.
2. Confira a contagem de palavras.
3. Sugira `/design-docs-review rfc`.
