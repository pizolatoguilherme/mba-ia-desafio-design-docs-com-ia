---
paths:
  - 'docs/**'
  - 'analysis/**'
  - 'README.md'
description: 'Regras de rastreabilidade, escopo e fronteira para o pacote de design docs do Sistema de Webhooks'
---

# Regras do pacote de design docs (Webhooks de Notificação de Pedidos)

Estas regras valem para **toda** geração ou edição em `docs/`, `analysis/` e `README.md`. Todas as skills do processo (`/transcript-inventory`, `/adr-creator`, `/rfc-creator`, `/fdd-creator`, `/prd-creator`, `/tracker-builder`, `/process-readme`, `/design-docs-review`) as carregam.

## 1. Fontes válidas (única regra inegociável)

Toda informação registrada precisa de origem identificável em uma de duas fontes:

| Fonte | Formato da localização | Exemplo |
|---|---|---|
| `TRANSCRICAO` | `[hh:mm] Nome` (timestamp e falante **exatos** da linha em `TRANSCRICAO.md`) | `[09:17] Diego` |
| `CODIGO` | caminho de arquivo **existente** no repositório | `src/modules/orders/order.service.ts` |

- Antes de citar `[hh:mm] Nome`, confira que aquele falante fala naquele minuto. Não cite intervalo como fonte única quando um minuto exato resolve.
- Item sem fonte direta só entra se for consequência necessária de algo rastreável. Nesse caso, ele recebe o rótulo **(derivado)** e aponta a origem mais próxima. Exemplos: um código de erro que segue a convenção `WEBHOOK_`, o nome de uma métrica.
- **Parâmetro numérico** que não foi dito na reunião (tamanho de batch, porta, limite de página) nunca vira valor decidido. Ele entra como **configuração com default (derivado)**.
- **Plano de contingência, priorização ou corte de escopo** que a reunião não discutiu não entra como decisão. No máximo entra como sugestão rotulada (derivado).
- Na dúvida entre "decidido" e "comentado", trate como comentado e pergunte ao usuário.

## 2. O que a reunião decidiu (não reabrir)

- Outbox `webhook_outbox` no MySQL, inserida **na mesma transação** de `changeStatus` ([09:06] Diego, [09:08] Larissa, [09:40] Bruno, [09:41] Diego).
- Worker em **processo separado** (`src/worker.ts` + `npm run worker`), polling a cada **2s**, PrismaClient próprio na mesma `DATABASE_URL` ([09:09]–[09:11], [09:30] Bruno).
- Single-worker; ordering só por `order_id` e só enquanto houver um único worker ([09:12] Diego, [09:13] Larissa).
- Retry: **5 tentativas**, backoff **1m/5m/30m/2h/12h**, depois DLQ na tabela **`webhook_dead_letter`** com payload, motivo e timestamp ([09:15]–[09:18] Diego, [09:17] Larissa).
- Replay manual `POST /admin/webhooks/dead-letter/:id/replay`: role **ADMIN** via `requireRole`, com log de quem executou ([09:18] Diego, [09:36] Sofia, [09:36] Larissa).
- **HMAC-SHA256** sobre o corpo, no header `X-Signature`. Secret **por endpoint**, gerada pela plataforma e devolvida na criação. Rotação com **grace period de 24h** ([09:20]–[09:22] Sofia, [09:31] Marcos).
- **At-least-once** com `X-Event-Id` (UUID gerado na inserção da outbox) para dedup no cliente ([09:24]–[09:26] Diego, [09:26] Larissa).
- Headers: `X-Event-Id`, `X-Signature`, `X-Timestamp`, `X-Webhook-Id`, `Content-Type: application/json` ([09:44] Diego, [09:44] Sofia, [09:45] Diego).
- Payload JSON enxuto, **sem items**: event_id, event_type `order.status_changed`, timestamp ISO 8601, order_id, order_number, from_status, to_status, customer_id e campos básicos como total_cents ([09:43] Diego).
- Payload **renderizado (snapshot) na inserção** ([09:52] Larissa, [09:52] Diego, [09:52] Bruno).
- Filtro de eventos por status **na inserção**: se nenhum webhook do customer quer o status, nada é inserido ([09:33] Marcos, [09:34] Bruno).
- Timeout HTTP de **10s** ([09:42] Diego). URL só **https**, validada no schema Zod ([09:23] Sofia). Payload acima de **64KB** gera erro e não é truncado ([09:23] Sofia, [09:24] Diego, [09:24] Larissa).
- IDs **UUID** ([09:51] Larissa). Módulo `src/modules/webhooks` no padrão controller/service/repository/routes/schemas ([09:27] Bruno).
- Reuso de AppError, Pino, error middleware, Zod e prefixo `WEBHOOK_` ([09:28]–[09:30] Bruno/Larissa).
- `publishWebhookEvent(tx, order, fromStatus, toStatus)` recebe o tx da transação atual ([09:41] Bruno, [09:41] Diego).
- CRUD de configuração liberado para qualquer role autenticada ([09:37] Sofia). **`customer_id` NÃO vem do JWT** ([09:32] Bruno, [09:32] Marcos, [09:32] Larissa).

## 3. Lista negra: nunca como requisito

Estes itens só aparecem em "Fora de escopo", "Questões em aberto" ou "Limitações", sempre com timestamp:

| Item | Situação | Fonte |
|---|---|---|
| Email ao cliente quando o webhook falha | adiado para a próxima fase | [09:37] Larissa |
| Rate limiting de saída | observar e decidir depois | [09:39] Diego, [09:39] Larissa |
| Dashboard/painel visual | fora; projeto do time de frontend | [09:40] Larissa |
| Arquivamento de entregues (~30 dias) | fora do escopo da feature | [09:08] Diego |
| Webhooks inbound (cliente → plataforma) | não pedido | [09:02] Marcos, [09:03] Sofia |
| Ordering global / múltiplos workers | limitação conhecida | [09:13] Diego, [09:13] Larissa |
| Exactly-once | descartado | [09:25] Diego |

## 4. Em aberto (não afirmar como decidido)

- `customer_id` no body ou no path ([09:32] Larissa). Um documento pode **propor**, mas marca a proposta como "pendente de confirmação, ver RFC-Q".
- Rate limiting ([09:39]); retenção/arquivamento ([09:08]); escala multi-worker, particionando por order_id ou com lock pessimista ([09:13] Diego); endurecer as roles do CRUD ([09:37] Sofia); detalhes de segurança para a revisão da Sofia ([09:46] Sofia).
- Identificado no código: `OrderService.create` grava o histórico inicial PENDING sem passar por `changeStatus` (`src/modules/orders/order.service.ts`). A reunião não tratou do evento de criação.
- O significado de `WEBHOOK_SECRET_REQUIRED` foi só citado, sem explicação ([09:28] Bruno). A interpretação adotada é (derivado).

## 5. Arquivos citados

- Todo caminho `src/…`, `prisma/…` e `tests/…` citado tem de **existir** no repositório, exceto os arquivos futuros desta lista branca. Esses sempre levam o rótulo **"(novo, a criar)"**:
  - `src/worker.ts` ([09:11] Larissa)
  - `src/modules/webhooks/` e seus arquivos `webhook.controller.ts`, `webhook.service.ts`, `webhook.repository.ts`, `webhook.routes.ts`, `webhook.schemas.ts` ([09:27] Bruno)
  - `src/modules/webhooks/webhook.worker.ts` ou `webhook.processor.ts` ([09:28] Bruno)
- Linhas `CODIGO` do tracker usam **somente** arquivos existentes.

## 6. IDs rastreáveis (obrigatórios no texto dos documentos)

| Documento | Prefixos |
|---|---|
| PRD | `PRD-MET-nn`, `PRD-FR-nn`, `PRD-NFR-nn`, `PRD-OUT-nn`, `PRD-DEP-nn`, `PRD-RISK-nn`, `PRD-AC-nn` |
| RFC | `RFC-ALT-nn`, `RFC-Q-nn`, `RFC-RISK-nn` |
| FDD | `FDD-OBJ-nn`, `FDD-FLUXO-nn`, `FDD-CONTRATO-nn`, `FDD-ERR-nn`, `FDD-RES-nn`, `FDD-OBS-nn`, `FDD-INT-nn`, `FDD-AC-nn`, `FDD-RISK-nn` |
| ADR | `ADR-NNN` (o próprio arquivo) |

Cada ID aparece em negrito no início do item (ex.: `**PRD-FR-01**`). O tracker terá uma linha por ID.

## 7. Fronteira entre documentos (sem duplicação)

| Documento | Responde | Não contém |
|---|---|---|
| PRD | por que e o quê | contratos, payloads, tabelas, fluxos técnicos; decisões só em 1 linha com link para o ADR |
| RFC | como pretendemos resolver e o que está em aberto | detalhamento de endpoints, matriz de erros, schema (isso fica no FDD); 2 a 4 páginas |
| ADR | por que decidimos exatamente assim | implementação detalhada; máximo de 5 referências de arquivo |
| FDD | como construir em detalhe | narrativa de negócio do PRD |
| TRACKER | de onde veio cada item | opinião ou conteúdo novo |

## 8. Estilo

- PT-BR técnico, direto. Sem travessão (—): use vírgula, dois-pontos ou parênteses.
- Nomes de seções **literalmente** iguais aos exigidos pelo enunciado (o validador confere).
- Sem placeholders (`[NEEDS INPUT]`, `ADR-XXX`, `TODO`, `{{…}}`).
- A data da reunião não é conhecida (a transcrição diz só "quinta-feira"). Datas de documento = data de redação.
