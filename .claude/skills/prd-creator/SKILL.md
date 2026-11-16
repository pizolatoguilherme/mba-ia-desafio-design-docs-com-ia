---
name: prd-creator
description: "Gera docs/PRD.md do Sistema de Webhooks a partir da transcrição e dos documentos técnicos já produzidos, usando o template e as regras de requisitos (FR/NFR com MoSCoW e critérios testáveis) da skill product-manager do curso, reduzidos às 12 seções exigidas pelo desafio. Fica no nível produto/negócio: por que e o quê."
disable-model-invocation: true
---

# PRD Creator (modo transcrição)

Adaptação da skill `product-manager` do curso (template `prd.template.md`). Aproveitamos dela:

- **Formato de FR:** prioridade MoSCoW e critérios de aceitação testáveis.
- **Categorias de NFR:** Performance, Segurança, Confiabilidade, Manutenibilidade.
- **Princípios:** valor para o usuário, testável e mensurável, rastreável.

O template original tem 15 seções genéricas (personas, épicos, UX, release planning). Aqui ele fica reduzido às **12 seções exigidas pelo desafio**, com os nomes literais.

Carregue e siga `.claude/rules/design-docs.md`. O PRD é gerado **por último entre os grandes documentos**: consolide a partir de `analysis/inventario-transcricao.md`, `docs/RFC.md`, `docs/FDD.md` e `docs/adrs/`, **subindo o nível**. Sem endpoints, payloads, tabelas ou fluxos técnicos.

## Regras específicas

- **Métricas (`PRD-MET-nn`):** pelo menos 1 com número e meta. Candidatas rastreáveis:
  - latência da notificação abaixo de 10s ([09:02] Marcos);
  - os 3 clientes que pediram (Atlas Comercial, MaxDistribuição, Nova Cargo) integrados ([09:00] Marcos);
  - entrega dentro do prazo de 3 sprints, para o fim de novembro ([09:45] Marcos, [09:46]–[09:47] Larissa).
  
  Não invente baseline. A redução do polling em GET /orders é qualitativa ([09:00] Marcos).
- **Público-alvo:** clientes B2B integradores ([09:00] Marcos), usuários da API que representam o cliente ([09:32] Marcos), ADMIN da operação para replay ([09:36] Sofia) e o portal do desenvolvedor ([09:26], [09:40] Marcos). Os cenários de uso são narrativas curtas com fonte.
- **Requisitos funcionais (`PRD-FR-nn`):** pelo menos 8, em linguagem de produto. Formato do curso:
  ```
  **PRD-FR-01** [MUST] Descrição. Fonte: [hh:mm] Nome.
  Critérios: - ... - ...
  ```
- **Requisitos não funcionais (`PRD-NFR-nn`):** com valor e fonte (10s, 2s, 64KB, https, 5 tentativas/~15h, at-least-once, HMAC, 24h).
- **Fora de escopo (`PRD-OUT-nn`):** todos os itens da lista negra, cada um com fonte e situação (adiado, descartado ou observar).
- **Decisões e trade-offs principais:** 1 a 2 linhas por decisão, com link para o ADR. Não repetir o conteúdo do ADR.
- **Dependências (`PRD-DEP-nn`):**
  - revisão de segurança de 2 dias úteis ([09:46] Sofia);
  - documentação no portal do desenvolvedor ([09:26], [09:40] Marcos);
  - migration do banco (`prisma/migrations/`);
  - clientes implementando a verificação HMAC e a dedup ([09:20], [09:25]).
- **Riscos (`PRD-RISK-nn`):** pelo menos 2, cada um com **Probabilidade**, **Impacto** e **Mitigação**. A probabilidade é avaliação da equipe (registrar como tal). A mitigação só usa o que a reunião definiu. Contingência que a reunião não discutiu não entra, ou entra rotulada (derivado).
- **Critérios de aceitação (`PRD-AC-nn`):** observáveis pelo cliente ou pelo PM.
- **Estratégia de testes e validação:** ancorar no que existe (vitest + supertest: `tests/orders.test.ts`, `tests/auth.test.ts`, `tests/helpers/factories.ts`, `vitest.config.ts`), na revisão de segurança ([09:46] Sofia) e na validação com os clientes piloto ([09:47] Marcos). Não citar ferramentas que não estão no `package.json`.

## Modelo de saída (exatamente estes headings)

```markdown
# PRD: Sistema de Webhooks de Notificação de Pedidos

| Campo | Valor |
|---|---|
| Produto | Order Management System (OMS) |
| Responsável de produto | Marcos (PM) |
| Responsável técnico | Larissa (Tech Lead) |
| Status | Aprovado para design |
| Data | AAAA-MM-DD |
| Documentos relacionados | RFC, FDD, ADRs, Tracker |

## 1. Resumo e contexto
## 2. Problema e motivação
## 3. Público-alvo e cenários de uso
## 4. Objetivos e métricas de sucesso
## 5. Escopo
### 5.1 Incluso
### 5.2 Fora de escopo
## 6. Requisitos funcionais
## 7. Requisitos não funcionais
## 8. Decisões e trade-offs principais
## 9. Dependências
## 10. Riscos e mitigação
## 11. Critérios de aceitação
## 12. Estratégia de testes e validação
```

## Após gerar

1. Rode `python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only prd`.
2. Sugira `/design-docs-review prd`, verificando principalmente a duplicação com o RFC e o FDD.
