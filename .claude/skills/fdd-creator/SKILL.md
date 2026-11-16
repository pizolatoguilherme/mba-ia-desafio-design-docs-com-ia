---
name: fdd-creator
description: "Gera docs/FDD.md (Feature Design Doc) do Sistema de Webhooks no 'modo transcrição': o roteiro de entrevista do fdd-creator do curso é respondido com a transcrição e o código, não com perguntas ao usuário. Cobre contexto, objetivos, escopo, fluxos (outbox, worker, retry, DLQ), contratos HTTP com exemplos, matriz de erros WEBHOOK_*, resiliência, observabilidade, dependências, critérios de aceite, riscos e a seção obrigatória 'Integração com o sistema existente'."
disable-model-invocation: true
---

# FDD Creator (modo transcrição)

Adaptação da skill `fdd-creator` do curso (devfullcycle/mba-ia-dev-workflow). O FDD descreve **como construir**, em nível acionável para um dev começar a codar.

**O que muda em relação ao original:**
- O original faz uma entrevista com uma pergunta por vez. Aqui, **cada pergunta do roteiro é respondida com a transcrição e o código**, com a fonte citada.
- O usuário só é consultado quando houver ambiguidade real, por exemplo um item da seção 4 de `.claude/rules/design-docs.md`.
- **Hipótese** do original equivale a **(derivado)** aqui.
- Sem travessões, como no original.

Carregue e siga `.claude/rules/design-docs.md`.

**Pré-requisitos:** `analysis/inventario-transcricao.md`, `docs/adrs/*.md` e `docs/RFC.md`.

**Leitura obrigatória antes de escrever a seção 12:**
- `src/modules/orders/order.service.ts`
- `src/modules/orders/order.status.ts`
- `src/shared/errors/app-error.ts`
- `src/shared/errors/http-errors.ts`
- `src/shared/errors/index.ts`
- `src/middlewares/auth.middleware.ts`
- `src/middlewares/error.middleware.ts`
- `src/middlewares/validate.middleware.ts`
- `src/routes/index.ts`
- `src/app.ts`
- `src/server.ts`
- `src/config/database.ts`
- `src/config/env.ts`
- `src/shared/logger/index.ts`
- `src/shared/http/response.ts`
- `prisma/schema.prisma`
- `package.json`
- um módulo existente completo (ex.: `src/modules/customers/*`), para espelhar o padrão

## Roteiro (do curso) respondido pela transcrição

| Etapa do roteiro original | Onde buscar a resposta |
|---|---|
| Contexto e motivação técnica | [09:00]–[09:08], código de `changeStatus` |
| Objetivos técnicos (medida/invariante) | latência <10s [09:02], atomicidade [09:06] e [09:40], at-least-once [09:24] |
| Escopo e exclusões | lista negra das regras |
| Fluxos detalhados | [09:06]–[09:18], [09:33]–[09:34], [09:41]–[09:44], [09:52] |
| Contratos públicos | [09:18], [09:21], [09:31]–[09:36], [09:43]–[09:45] |
| Erros, exceções, fallback | [09:23]–[09:24], [09:28]–[09:29], [09:42], código de erros |
| Observabilidade | Pino [09:29], auditoria do replay [09:36]; métricas e tracing são (derivado) |
| Dependências e compatibilidade | `package.json`, `prisma/schema.prisma`, [09:29]–[09:30] |
| Critérios de aceite técnicos | um critério verificável por decisão/RNF |
| Riscos e mitigação | [09:04], [09:07], [09:12]–[09:13], [09:22], [09:25] |

## Regras específicas

- **Contratos públicos:**
  - Os 7 endpoints da API, cada um com `**FDD-CONTRATO-nn**`, método e rota, auth/role, request de exemplo, response de exemplo, status codes e a fonte:
    - `POST /webhooks`
    - `GET /webhooks` (por customer)
    - `PATCH /webhooks/:id`
    - `DELETE /webhooks/:id`
    - rotação de secret
    - `GET /webhooks/:id/deliveries`
    - `POST /admin/webhooks/dead-letter/:id/replay`
  - O contrato do **webhook de saída** (plataforma → cliente) também entra: headers, payload e semântica da resposta do cliente.
  - Pelo menos 4 endpoints com corpo de request **e** de response. No DELETE, mostre `204` sem corpo mais um exemplo de erro.
  - O formato de erro segue o `errorMiddleware` real: `{ "error": { "code", "message", "details?" } }`.
  - A rota de rotação de secret não foi nomeada na reunião, só a capacidade ([09:21] Sofia). Marque a rota como (derivado).
  - O `customer_id` no body ou no path está em aberto ([09:32] Larissa): proponha e marque "pendente de confirmação, ver RFC-Q-nn". Nunca do JWT.
  - Respostas nunca expõem a secret, exceto na criação ([09:31] Marcos) e na rotação.
- **Matriz de erros:** `**FDD-ERR-nn**`, colunas `Código | HTTP | Quando ocorre | Classe base (existente) | Tratamento | Fonte`.
  - Os 3 códigos citados ([09:28] Bruno) aparecem com essa fonte. Os demais `WEBHOOK_*` são (derivado), pela convenção do prefixo ([09:29] Larissa).
  - Erros do worker, que não são HTTP, aparecem como `n/a (worker)` e indicam se a falha é retryable ou permanente.
  - A classe base deve existir em `src/shared/errors/http-errors.ts` (NotFoundError, ValidationError, ConflictError, UnprocessableEntityError, BadRequestError, ForbiddenError).
- **Modelo de dados:**
  - Tabelas `webhook_outbox` e `webhook_dead_letter` com os nomes da reunião ([09:06], [09:18]).
  - Configuração de endpoint com url, secret, customer_id e estado ativo ([09:21] Bruno).
  - Registro de entregas, necessário para [09:34] Marcos.
  - Nomes de tabelas, colunas e campos não citados são (derivado) e seguem as convenções do `prisma/schema.prisma`: `@id @default(uuid()) @db.Char(36)`, `@@map` em snake_case, `createdAt`/`updatedAt`.
- **Parâmetros:** os valores decididos (2s, 10s, 64KB, 5 tentativas, backoff, 24h, 100 entregas) aparecem com a fonte. Valores não ditos (tamanho do batch, por exemplo) viram configuração com default (derivado).
- **Observabilidade:** subseções **Métricas**, **Logs** e **Tracing**, todas obrigatórias.
  - Logs com Pino (`src/shared/logger/index.ts`), incluindo redact da secret (derivado, motivado por [09:22] Diego).
  - Auditoria do replay ([09:36] Sofia).
  - Métricas e tracing (derivado): o projeto não tem nenhum dos dois hoje, então propor o mínimo sem adicionar ferramenta como decisão.
- **Integração com o sistema existente:** `**FDD-INT-nn**`, um por arquivo, com pelo menos 4 caminhos **existentes**, cada um dizendo *o que muda* ou *o que é reutilizado sem mudança*. Arquivos novos vão numa subtabela à parte, com "(novo, a criar)" e a fonte.
- **Critérios de aceite técnicos:** checklist `**FDD-AC-nn**`, objetivos e testáveis com vitest/supertest, seguindo `tests/orders.test.ts` e `tests/helpers/factories.ts`.
- **Diagramas:** Mermaid `sequenceDiagram` para os fluxos principais e um `stateDiagram-v2` para os estados do evento (pendente, processando, entregue, falhou), citados em [09:08] Diego.

## Modelo de saída (exatamente estes headings numerados)

```markdown
# FDD: Sistema de Webhooks de Notificação de Pedidos

Versão: 1.0 | Data: AAAA-MM-DD | Responsável: Larissa (Tech Lead) | Revisão de segurança: Sofia | Relacionados: PRD, RFC, ADRs, Tracker

## 1. Contexto e motivação técnica
## 2. Objetivos técnicos
## 3. Escopo e exclusões
## 4. Modelo de dados
## 5. Fluxos detalhados
### 5.1 Criação do evento na outbox
### 5.2 Processamento pelo worker
### 5.3 Retry com backoff
### 5.4 DLQ e replay manual
### 5.5 Gestão de secret e rotação
## 6. Contratos públicos
### 6.1 ... (um por endpoint)
### 6.N Webhook de saída (plataforma → cliente)
## 7. Matriz de erros
## 8. Estratégias de resiliência
## 9. Observabilidade
### Métricas
### Logs
### Tracing
## 10. Integração com o sistema existente
## 11. Dependências e compatibilidade
## 12. Critérios de aceite técnicos
## 13. Riscos e mitigação
## 14. Parâmetros configuráveis
```

## Após gerar

1. Opcional: `/mermaid-generate docs/FDD.md`, se o plugin `diagrams-generator` do curso estiver instalado, para revisar os diagramas.
2. Rode `python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only fdd`.
3. Sugira `/design-docs-review fdd`.
