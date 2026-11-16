# Tracker de Rastreabilidade

Mapa de cada item dos design docs à sua origem na transcrição (`TRANSCRICAO.md`) ou no código. Gerado por `/tracker-builder` e verificado por `.claude/skills/tracker-builder/scripts/validate_docs.py`.

**Cobertura:** 186 de 186 IDs (100%) | **TRANSCRICAO:** 165 linhas (88,7%) | **CODIGO:** 21 linhas

Itens marcados `(derivado)` não têm fala direta: são consequência necessária da fonte indicada. O detalhe está em "Notas de derivação", ao final.

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
|---|---|---|---|---|---|
| ADR-001 | docs/adrs/ADR-001-outbox-transacional-no-mysql.md | Decisão | Outbox `webhook_outbox` no MySQL, gravada na mesma transação do `changeStatus` | TRANSCRICAO | [09:06] Diego; [09:08] Larissa; [09:40] Bruno |
| ADR-002 | docs/adrs/ADR-002-worker-separado-com-polling.md | Decisão | Worker em processo separado, polling de 2s, PrismaClient próprio, single-worker | TRANSCRICAO | [09:09] Diego; [09:11] Diego; [09:12] Diego |
| ADR-003 | docs/adrs/ADR-003-retry-com-backoff-e-dead-letter.md | Decisão | 5 tentativas com backoff 1m/5m/30m/2h/12h, dead letter em tabela própria, replay ADMIN | TRANSCRICAO | [09:17] Diego; [09:18] Diego; [09:36] Sofia |
| ADR-004 | docs/adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md | Decisão | HMAC-SHA256 do corpo em X-Signature, secret por endpoint, rotação com grace de 24h | TRANSCRICAO | [09:20] Sofia; [09:21] Sofia; [09:22] Sofia |
| ADR-005 | docs/adrs/ADR-005-entrega-at-least-once-com-x-event-id.md | Decisão | Entrega at-least-once com X-Event-Id (UUID gerado na inserção) para dedup no cliente | TRANSCRICAO | [09:24] Diego; [09:25] Diego; [09:26] Larissa |
| ADR-006 | docs/adrs/ADR-006-reuso-dos-padroes-do-projeto.md | Decisão | Reuso de módulo padrão, AppError, prefixo WEBHOOK_, Pino, error middleware, Zod, requireRole, UUID | TRANSCRICAO | [09:27] Bruno; [09:29] Bruno; [09:30] Larissa |
| ADR-007 | docs/adrs/ADR-007-snapshot-e-filtro-na-insercao.md | Decisão | Payload renderizado (snapshot) e filtro de status aplicados na inserção na outbox | TRANSCRICAO | [09:34] Bruno; [09:52] Larissa; [09:52] Diego |
| RFC-ALT-01 | docs/RFC.md | Alternativa Descartada | Disparo HTTP síncrono no `changeStatus`: cliente lento trava status de outros pedidos | TRANSCRICAO | [09:04] Bruno; [09:06] Diego |
| RFC-ALT-02 | docs/RFC.md | Alternativa Descartada | Redis Streams: mais infraestrutura, overengineering para time pequeno | TRANSCRICAO | [09:07] Larissa; [09:07] Diego |
| RFC-ALT-03 | docs/RFC.md | Alternativa Descartada | Trigger ou NOTIFY/LISTEN: MySQL não tem listener nativo | TRANSCRICAO | [09:09] Bruno; [09:09] Diego |
| RFC-ALT-04 | docs/RFC.md | Alternativa Descartada | Worker no processo da API: reinício da API derruba o worker | TRANSCRICAO | [09:11] Diego |
| RFC-ALT-05 | docs/RFC.md | Alternativa Descartada | Retry indefinido: evento pendurado para sempre | TRANSCRICAO | [09:15] Diego |
| RFC-ALT-06 | docs/RFC.md | Alternativa Descartada | 3 tentativas: mataria o evento em cerca de 30 minutos | TRANSCRICAO | [09:16] Bruno; [09:16] Diego |
| RFC-ALT-07 | docs/RFC.md | Alternativa Descartada | Dead letter como status failed na própria outbox | TRANSCRICAO | [09:17] Larissa; [09:18] Diego |
| RFC-ALT-08 | docs/RFC.md | Alternativa Descartada | Secret global da plataforma: um vazamento compromete todos | TRANSCRICAO | [09:21] Sofia |
| RFC-ALT-09 | docs/RFC.md | Alternativa Descartada | Exactly-once: exige coordenação dos dois lados | TRANSCRICAO | [09:25] Diego |
| RFC-ALT-10 | docs/RFC.md | Alternativa Descartada | customer_id implícito no JWT: o JWT é do operador | TRANSCRICAO | [09:31] Marcos; [09:32] Bruno; [09:32] Larissa |
| RFC-ALT-11 | docs/RFC.md | Alternativa Descartada | Filtrar eventos no envio: grava linhas inúteis | TRANSCRICAO | [09:34] Diego; [09:34] Bruno |
| RFC-ALT-12 | docs/RFC.md | Alternativa Descartada | Guardar só order_id e renderizar no envio: evento deixa de refletir o momento | TRANSCRICAO | [09:51] Bruno; [09:52] Larissa |
| RFC-Q-01 | docs/RFC.md | Questão em Aberto | customer_id no body ou no path; proposta body na criação e query na listagem, pendente | TRANSCRICAO | [09:32] Larissa |
| RFC-Q-02 | docs/RFC.md | Questão em Aberto | Rate limiting de saída: observar e decidir depois | TRANSCRICAO | [09:38] Diego; [09:39] Diego; [09:39] Larissa |
| RFC-Q-03 | docs/RFC.md | Questão em Aberto | Escala para múltiplos workers: particionar por order_id ou lock pessimista | TRANSCRICAO | [09:13] Diego |
| RFC-Q-04 | docs/RFC.md | Questão em Aberto | Retenção e arquivamento das linhas entregues ("30 dias ou assim") | TRANSCRICAO | [09:08] Diego |
| RFC-Q-05 | docs/RFC.md | Questão em Aberto | Endurecer as roles do CRUD de configuração | TRANSCRICAO | [09:37] Sofia |
| RFC-Q-06 | docs/RFC.md | Questão em Aberto | Detalhes de segurança para a revisão da Sofia (X-Timestamp assinado, assinatura no grace) | TRANSCRICAO | [09:46] Sofia; [09:44] Diego; [09:21] Sofia |
| RFC-Q-07 | docs/RFC.md | Questão em Aberto | Email ao cliente em falhas repetidas, condicionado a medir impacto | TRANSCRICAO | [09:37] Marcos; [09:37] Larissa; [09:38] Marcos |
| RFC-Q-08 | docs/RFC.md | Questão em Aberto | As 5 tentativas incluem o envio original? (soma de ~15h só fecha com 5 retentativas) | TRANSCRICAO | [09:15] Diego; [09:17] Diego |
| RFC-Q-09 | docs/RFC.md | Questão em Aberto | X-Event-Id no replay e em múltiplos endpoints do mesmo customer | TRANSCRICAO | [09:18] Diego; [09:25] Diego; [09:44] Sofia |
| RFC-Q-10 | docs/RFC.md | Questão em Aberto | Granularidade da outbox: uma linha por endpoint ou por evento | TRANSCRICAO | [09:33] Marcos; [09:44] Sofia |
| RFC-Q-11 | docs/RFC.md | Questão em Aberto | Significado de WEBHOOK_SECRET_REQUIRED, citado sem explicação | TRANSCRICAO | [09:28] Bruno |
| RFC-Q-12 | docs/RFC.md | Questão em Aberto | Criação do pedido grava PENDING sem passar por changeStatus; reunião não tratou do evento | CODIGO | src/modules/orders/order.service.ts (OrderService.create) |
| RFC-RISK-01 | docs/RFC.md | Risco | Falha ao gravar na outbox derruba a mudança de status | TRANSCRICAO | [09:40] Bruno; [09:46] Larissa |
| RFC-RISK-02 | docs/RFC.md | Risco | Worker único parado ou retido por cliente lento acumula eventos | TRANSCRICAO | [09:11] Diego; [09:42] Diego; [09:06] Diego |
| RFC-RISK-03 | docs/RFC.md | Risco | Cliente não deduplica e processa duas vezes | TRANSCRICAO | [09:25] Sofia; [09:26] Marcos |
| RFC-RISK-04 | docs/RFC.md | Risco | Vazamento de secret pelo cliente | TRANSCRICAO | [09:22] Diego; [09:21] Sofia; [09:46] Sofia |
| RFC-RISK-05 | docs/RFC.md | Risco | Rajada de eventos para o mesmo cliente sem limite de envio | TRANSCRICAO | [09:38] Diego; [09:39] Larissa |
| RFC-RISK-06 | docs/RFC.md | Risco | Crescimento contínuo da outbox sem retenção | TRANSCRICAO | [09:08] Diego |
| RFC-RISK-07 | docs/RFC.md | Risco | Prazo da Atlas (fim de novembro) contra estimativa de 3 sprints | TRANSCRICAO | [09:45] Marcos; [09:46] Larissa; [09:47] Marcos |
| FDD-OBJ-01 | docs/FDD.md | Objetivo | Latência abaixo de 10s no caminho feliz, com polling de 2s | TRANSCRICAO | [09:02] Marcos; [09:09] Diego; [09:10] Larissa |
| FDD-OBJ-02 | docs/FDD.md | Objetivo | Linha na outbox existe se e somente se o changeStatus commitou | TRANSCRICAO | [09:06] Diego; [09:40] Bruno |
| FDD-OBJ-03 | docs/FDD.md | Objetivo | Todo evento termina entregue ou na dead letter; exceção: endpoint removido (exceção derivado) | TRANSCRICAO | [09:24] Diego; [09:18] Diego |
| FDD-OBJ-04 | docs/FDD.md | Objetivo | Ordem por endpoint e order_id com um único worker | TRANSCRICAO | [09:12] Diego; [09:13] Larissa |
| FDD-OBJ-05 | docs/FDD.md | Objetivo | Retry 1m, 5m, 30m, 2h, 12h e depois dead letter | TRANSCRICAO | [09:17] Diego; [09:17] Larissa |
| FDD-OBJ-06 | docs/FDD.md | Objetivo | 100% dos envios com X-Signature HMAC-SHA256 verificável | TRANSCRICAO | [09:20] Sofia; [09:22] Sofia |
| FDD-OBJ-07 | docs/FDD.md | Objetivo | Secret só na criação e na rotação; nunca em listagem, edição ou log (log derivado) | TRANSCRICAO | [09:31] Marcos; [09:22] Diego |
| FDD-FLUXO-01 | docs/FDD.md | Fluxo | Criação do evento: publishWebhookEvent no tx, filtro e snapshot, uma linha PENDING por endpoint | TRANSCRICAO | [09:41] Bruno; [09:41] Diego; [09:34] Bruno |
| FDD-FLUXO-02 | docs/FDD.md | Fluxo | Worker em processo separado: polling 2s, batch, envio sequencial, timeout 10s | TRANSCRICAO | [09:09] Diego; [09:11] Larissa; [09:28] Bruno |
| FDD-FLUXO-03 | docs/FDD.md | Fluxo | Retry com backoff 1m/5m/30m/2h/12h via nextAttemptAt | TRANSCRICAO | [09:17] Diego; [09:17] Larissa |
| FDD-FLUXO-04 | docs/FDD.md | Fluxo | Movimento para webhook_dead_letter e replay ADMIN auditado | TRANSCRICAO | [09:18] Diego; [09:36] Sofia; [09:36] Larissa |
| FDD-FLUXO-05 | docs/FDD.md | Fluxo | Geração, assinatura e rotação da secret com convivência de 24h | TRANSCRICAO | [09:21] Sofia; [09:22] Sofia; [09:31] Marcos |
| FDD-CONTRATO-01 | docs/FDD.md | Contrato | POST /webhooks: url https, events, secret devolvida só aqui | TRANSCRICAO | [09:31] Marcos; [09:33] Marcos; [09:23] Sofia |
| FDD-CONTRATO-02 | docs/FDD.md | Contrato | GET /webhooks por customerId, paginado (customerId pendente RFC-Q-01) | TRANSCRICAO | [09:33] Bruno; [09:32] Larissa |
| FDD-CONTRATO-03 | docs/FDD.md | Contrato | PATCH /webhooks/:id para url, events e active | TRANSCRICAO | [09:33] Bruno; [09:21] Bruno |
| FDD-CONTRATO-04 | docs/FDD.md | Contrato | DELETE /webhooks/:id com 204 | TRANSCRICAO | [09:33] Bruno |
| FDD-CONTRATO-05 | docs/FDD.md | Contrato | Rotação de secret; rota rotate-secret (derivado) | TRANSCRICAO | [09:21] Sofia |
| FDD-CONTRATO-06 | docs/FDD.md | Contrato | GET /webhooks/:id/deliveries com os últimos 100 envios | TRANSCRICAO | [09:34] Marcos; [09:35] Larissa |
| FDD-CONTRATO-07 | docs/FDD.md | Contrato | POST /admin/webhooks/dead-letter/:id/replay, só ADMIN | TRANSCRICAO | [09:18] Diego; [09:35] Diego; [09:36] Sofia |
| FDD-CONTRATO-08 | docs/FDD.md | Contrato | Webhook de saída: headers X-Event-Id, X-Signature, X-Timestamp, X-Webhook-Id e payload sem items | TRANSCRICAO | [09:43] Diego; [09:44] Diego; [09:44] Sofia |
| FDD-ERR-01 | docs/FDD.md | Erro | WEBHOOK_NOT_FOUND 404 | TRANSCRICAO | [09:28] Bruno |
| FDD-ERR-02 | docs/FDD.md | Erro | WEBHOOK_INVALID_URL 400 na validação Zod de https | TRANSCRICAO | [09:28] Bruno; [09:23] Sofia |
| FDD-ERR-03 | docs/FDD.md | Erro | WEBHOOK_SECRET_REQUIRED no worker, falha permanente (interpretação derivado) | TRANSCRICAO | [09:28] Bruno |
| FDD-ERR-04 | docs/FDD.md | Erro | WEBHOOK_DEAD_LETTER_NOT_FOUND 404 no replay (derivado) | TRANSCRICAO | [09:18] Diego; [09:29] Larissa |
| FDD-ERR-05 | docs/FDD.md | Erro | WEBHOOK_ALREADY_REPLAYED 409 (derivado) | TRANSCRICAO | [09:18] Diego; [09:29] Larissa |
| FDD-ERR-06 | docs/FDD.md | Erro | WEBHOOK_ENDPOINT_INACTIVE 422 ou permanente no worker (derivado) | TRANSCRICAO | [09:21] Bruno; [09:29] Larissa |
| FDD-ERR-07 | docs/FDD.md | Erro | WEBHOOK_PAYLOAD_TOO_LARGE acima de 64KB, sem truncar | TRANSCRICAO | [09:23] Sofia; [09:24] Diego; [09:24] Larissa |
| FDD-ERR-08 | docs/FDD.md | Erro | WEBHOOK_DELIVERY_TIMEOUT após 10s, retryable | TRANSCRICAO | [09:42] Diego |
| FDD-ERR-09 | docs/FDD.md | Erro | WEBHOOK_DELIVERY_FAILED para não 2xx ou erro de rede, retryable (não 2xx derivado) | TRANSCRICAO | [09:42] Diego |
| FDD-ERR-10 | docs/FDD.md | Erro | WEBHOOK_RETRIES_EXHAUSTED, vai para a dead letter | TRANSCRICAO | [09:15] Diego; [09:17] Larissa |
| FDD-RES-01 | docs/FDD.md | Resiliência | Outbox transacional | TRANSCRICAO | [09:06] Diego; [09:40] Bruno |
| FDD-RES-02 | docs/FDD.md | Resiliência | Timeout de 10s por chamada | TRANSCRICAO | [09:42] Diego |
| FDD-RES-03 | docs/FDD.md | Resiliência | Retry com backoff via nextAttemptAt | TRANSCRICAO | [09:17] Diego |
| FDD-RES-04 | docs/FDD.md | Resiliência | Dead letter para falhas permanentes e retries esgotados | TRANSCRICAO | [09:18] Diego |
| FDD-RES-05 | docs/FDD.md | Resiliência | X-Event-Id estável para idempotência no cliente | TRANSCRICAO | [09:25] Diego |
| FDD-RES-06 | docs/FDD.md | Resiliência | PROCESSING volta a PENDING ao iniciar o worker (derivado) | TRANSCRICAO | [09:24] Diego |
| FDD-RES-07 | docs/FDD.md | Resiliência | Bloqueio por endpoint e pedido enquanto houver evento anterior pendente (derivado) | TRANSCRICAO | [09:12] Diego |
| FDD-RES-08 | docs/FDD.md | Resiliência | Isolamento de processo entre API e worker | TRANSCRICAO | [09:11] Diego |
| FDD-RES-09 | docs/FDD.md | Resiliência | Encerramento gracioso em SIGTERM no padrão do server (derivado) | CODIGO | src/server.ts (shutdown) |
| FDD-OBS-01 | docs/FDD.md | Observabilidade | Métricas calculadas das tabelas e emitidas em log pelo worker (derivado) | TRANSCRICAO | [09:02] Marcos; [09:42] Diego |
| FDD-OBS-02 | docs/FDD.md | Observabilidade | Logs Pino estruturados com eventId, incluindo auditoria do replay | TRANSCRICAO | [09:29] Bruno; [09:36] Sofia |
| FDD-OBS-03 | docs/FDD.md | Observabilidade | Redact de secret no logger (derivado) | TRANSCRICAO | [09:22] Diego; [09:36] Sofia |
| FDD-OBS-04 | docs/FDD.md | Observabilidade | Sem tracing distribuído; correlação por orderId, eventId e requestId (derivado) | CODIGO | src/middlewares/request-logger.middleware.ts (requestLogger) |
| FDD-INT-01 | docs/FDD.md | Integração | changeStatus chama publishWebhookEvent dentro do $transaction | CODIGO | src/modules/orders/order.service.ts (OrderService.changeStatus) |
| FDD-INT-02 | docs/FDD.md | Integração | Novos models e enum; relação webhookEndpoints em Customer | CODIGO | prisma/schema.prisma (model Customer) |
| FDD-INT-03 | docs/FDD.md | Integração | buildControllers instancia repository, service e controller de webhooks | CODIGO | src/app.ts (buildControllers) |
| FDD-INT-04 | docs/FDD.md | Integração | Controllers ganha webhooks; rotas /webhooks e /admin/webhooks | CODIGO | src/routes/index.ts (buildApiRouter) |
| FDD-INT-05 | docs/FDD.md | Integração | Novas classes de erro no padrão de InsufficientStockError | CODIGO | src/shared/errors/http-errors.ts (InsufficientStockError) |
| FDD-INT-06 | docs/FDD.md | Integração | Barrel exporta as novas classes de erro | CODIGO | src/shared/errors/index.ts |
| FDD-INT-07 | docs/FDD.md | Integração | redactPaths ganha campos de secret (derivado) | CODIGO | src/shared/logger/index.ts (redactPaths) |
| FDD-INT-08 | docs/FDD.md | Integração | envSchema ganha parâmetros opcionais do worker (derivado) | CODIGO | src/config/env.ts (envSchema) |
| FDD-INT-09 | docs/FDD.md | Integração | Scripts worker e worker:dev; nenhuma dependência nova | CODIGO | package.json (scripts) |
| FDD-INT-10 | docs/FDD.md | Integração | beforeEach apaga as novas tabelas antes de customer (derivado) | CODIGO | tests/setup.ts (beforeEach) |
| FDD-INT-11 | docs/FDD.md | Integração | authenticate e requireRole reutilizados sem mudança | CODIGO | src/middlewares/auth.middleware.ts (requireRole) |
| FDD-INT-12 | docs/FDD.md | Integração | errorMiddleware reutilizado sem mudança | CODIGO | src/middlewares/error.middleware.ts (errorMiddleware) |
| FDD-INT-13 | docs/FDD.md | Integração | validate reutilizado sem mudança | CODIGO | src/middlewares/validate.middleware.ts (validate) |
| FDD-INT-14 | docs/FDD.md | Integração | paginated() reutilizado na listagem (derivado) | CODIGO | src/shared/http/response.ts (paginated) |
| FDD-INT-15 | docs/FDD.md | Integração | createPrismaClient() reutilizado pelo worker | CODIGO | src/config/database.ts (createPrismaClient) |
| FDD-INT-16 | docs/FDD.md | Integração | Modelo de bootstrap e shutdown para o worker, sem mudança | CODIGO | src/server.ts (bootstrap) |
| FDD-AC-01 | docs/FDD.md | Critério de Aceite | Uma linha PENDING por endpoint interessado, payload completo sem items | TRANSCRICAO | [09:33] Marcos; [09:43] Diego; [09:52] Larissa |
| FDD-AC-02 | docs/FDD.md | Critério de Aceite | Status não desejado ou endpoint inativo não gera linha | TRANSCRICAO | [09:34] Bruno; [09:21] Bruno |
| FDD-AC-03 | docs/FDD.md | Critério de Aceite | Erro em publishWebhookEvent desfaz a mudança de status | TRANSCRICAO | [09:40] Bruno; [09:41] Diego |
| FDD-AC-04 | docs/FDD.md | Critério de Aceite | URL http recusada com 400 e WEBHOOK_INVALID_URL | TRANSCRICAO | [09:23] Sofia; [09:28] Bruno |
| FDD-AC-05 | docs/FDD.md | Critério de Aceite | Secret só no 201 da criação; ausente em GET e PATCH | TRANSCRICAO | [09:31] Marcos |
| FDD-AC-06 | docs/FDD.md | Critério de Aceite | GET sem customerId retorna 400; com customerId, só os dele | TRANSCRICAO | [09:32] Larissa; [09:33] Bruno |
| FDD-AC-07 | docs/FDD.md | Critério de Aceite | PATCH e DELETE inexistentes retornam 404 WEBHOOK_NOT_FOUND; DELETE retorna 204 | TRANSCRICAO | [09:28] Bruno; [09:33] Bruno |
| FDD-AC-08 | docs/FDD.md | Critério de Aceite | Rotação gera secret nova com convivência de 24h | TRANSCRICAO | [09:21] Sofia |
| FDD-AC-09 | docs/FDD.md | Critério de Aceite | Entrega com todos os headers e X-Signature válida | TRANSCRICAO | [09:44] Diego; [09:44] Sofia; [09:20] Sofia |
| FDD-AC-10 | docs/FDD.md | Critério de Aceite | Resposta 500 deixa FAILED com retry em 1 minuto e registro em deliveries | TRANSCRICAO | [09:15] Diego; [09:17] Diego; [09:34] Marcos |
| FDD-AC-11 | docs/FDD.md | Critério de Aceite | Sem resposta no timeout gera WEBHOOK_DELIVERY_TIMEOUT; default 10000 | TRANSCRICAO | [09:42] Diego |
| FDD-AC-12 | docs/FDD.md | Critério de Aceite | Após o envio 6, evento vai para a dead letter com payload, motivo e failedAt | TRANSCRICAO | [09:18] Diego; [09:17] Larissa |
| FDD-AC-13 | docs/FDD.md | Critério de Aceite | Payload acima de 64KB vai para a dead letter sem requisição | TRANSCRICAO | [09:23] Sofia; [09:24] Diego |
| FDD-AC-14 | docs/FDD.md | Critério de Aceite | Replay: OPERATOR 403, ADMIN 200 com mesmo id, segundo replay 409 | TRANSCRICAO | [09:36] Sofia; [09:36] Larissa; [09:18] Diego |
| FDD-AC-15 | docs/FDD.md | Critério de Aceite | Evento seguinte do mesmo pedido espera o anterior (derivado) | TRANSCRICAO | [09:12] Diego |
| FDD-AC-16 | docs/FDD.md | Critério de Aceite | Deliveries retorna 100 de 120 tentativas, do mais recente | TRANSCRICAO | [09:34] Marcos |
| FDD-AC-17 | docs/FDD.md | Critério de Aceite | PROCESSING volta a PENDING ao iniciar o worker (derivado) | TRANSCRICAO | [09:24] Diego |
| FDD-AC-18 | docs/FDD.md | Critério de Aceite | Secret logada sai como [REDACTED] (derivado) | TRANSCRICAO | [09:22] Diego |
| FDD-RISK-01 | docs/FDD.md | Risco | Evento em retry bloqueia os seguintes do mesmo pedido por até ~15h (derivado) | TRANSCRICAO | [09:12] Diego; [09:17] Diego |
| FDD-RISK-02 | docs/FDD.md | Risco | Cliente lento segura o worker sequencial | TRANSCRICAO | [09:42] Diego; [09:13] Diego |
| FDD-RISK-03 | docs/FDD.md | Risco | Reenvio após queda do worker gera duplicata | TRANSCRICAO | [09:24] Diego; [09:25] Diego |
| FDD-RISK-04 | docs/FDD.md | Risco | Secret recuperável no banco vaza em dump ou log | TRANSCRICAO | [09:22] Diego; [09:46] Sofia |
| FDD-RISK-05 | docs/FDD.md | Risco | Qualquer operador gerencia webhooks de qualquer customer | TRANSCRICAO | [09:37] Sofia; [09:32] Bruno |
| FDD-RISK-06 | docs/FDD.md | Risco | Leitura de endpoints alonga a transação de changeStatus | TRANSCRICAO | [09:04] Bruno; [09:34] Bruno |
| FDD-RISK-07 | docs/FDD.md | Risco | ADMIN sem listagem da dead letter para achar o id (derivado) | TRANSCRICAO | [09:18] Diego |
| PRD-MET-01 | docs/PRD.md | Métrica | Aviso em menos de 10 segundos | TRANSCRICAO | [09:02] Marcos |
| PRD-MET-02 | docs/PRD.md | Métrica | 3 de 3 clientes demandantes recebendo notificações (derivado) | TRANSCRICAO | [09:00] Marcos |
| PRD-MET-03 | docs/PRD.md | Métrica | Entrega em 3 sprints frente ao pedido de fim de novembro, a confirmar | TRANSCRICAO | [09:45] Marcos; [09:47] Larissa; [09:47] Marcos |
| PRD-MET-04 | docs/PRD.md | Métrica | 100% dos avisos entregues ou guardados, exceto cadastro removido (derivado) | TRANSCRICAO | [09:24] Diego; [09:18] Diego |
| PRD-MET-05 | docs/PRD.md | Métrica | Menos consultas periódicas, qualitativa e sem baseline | TRANSCRICAO | [09:00] Marcos |
| PRD-OUT-01 | docs/PRD.md | Fora de Escopo | Email ao cliente em falhas repetidas, adiado | TRANSCRICAO | [09:37] Marcos; [09:37] Larissa; [09:38] Marcos |
| PRD-OUT-02 | docs/PRD.md | Fora de Escopo | Rate limiting de envio, observar e decidir depois | TRANSCRICAO | [09:38] Diego; [09:39] Diego; [09:39] Larissa |
| PRD-OUT-03 | docs/PRD.md | Fora de Escopo | Dashboard ou painel visual, projeto do frontend | TRANSCRICAO | [09:39] Marcos; [09:40] Larissa |
| PRD-OUT-04 | docs/PRD.md | Fora de Escopo | Arquivamento dos avisos entregues | TRANSCRICAO | [09:08] Diego |
| PRD-OUT-05 | docs/PRD.md | Fora de Escopo | Webhooks inbound, não pedido | TRANSCRICAO | [09:02] Marcos; [09:03] Sofia |
| PRD-OUT-06 | docs/PRD.md | Fora de Escopo | Ordem global e processamento paralelo, limitação conhecida | TRANSCRICAO | [09:13] Diego; [09:13] Larissa; [09:14] Marcos |
| PRD-OUT-07 | docs/PRD.md | Fora de Escopo | Exactly-once, descartado | TRANSCRICAO | [09:25] Diego |
| PRD-OUT-08 | docs/PRD.md | Fora de Escopo | Restringir quem configura notificações, adiado | TRANSCRICAO | [09:37] Sofia |
| PRD-OUT-09 | docs/PRD.md | Fora de Escopo | Aviso na criação do pedido, questão em aberto do código | CODIGO | src/modules/orders/order.service.ts (OrderService.create) |
| PRD-FR-01 | docs/PRD.md | Requisito Funcional | Cliente avisado quando o status de um pedido dele muda | TRANSCRICAO | [09:00] Marcos; [09:43] Diego |
| PRD-FR-02 | docs/PRD.md | Requisito Funcional | Cadastro com endereço e status; chave gerada e mostrada uma vez | TRANSCRICAO | [09:31] Marcos |
| PRD-FR-03 | docs/PRD.md | Requisito Funcional | Editar e remover cadastros | TRANSCRICAO | [09:33] Bruno |
| PRD-FR-04 | docs/PRD.md | Requisito Funcional | Listar cadastros; cliente identificado na requisição, não pelo login | TRANSCRICAO | [09:33] Bruno; [09:32] Larissa |
| PRD-FR-05 | docs/PRD.md | Requisito Funcional | Escolher de quais status ser avisado | TRANSCRICAO | [09:33] Bruno; [09:33] Marcos |
| PRD-FR-06 | docs/PRD.md | Requisito Funcional | Ativar e desativar cadastro | TRANSCRICAO | [09:21] Bruno; [09:21] Sofia |
| PRD-FR-07 | docs/PRD.md | Requisito Funcional | Histórico das últimas 100 entregas | TRANSCRICAO | [09:34] Marcos; [09:35] Larissa |
| PRD-FR-08 | docs/PRD.md | Requisito Funcional | Trocar a chave com a anterior válida por 24h | TRANSCRICAO | [09:21] Sofia |
| PRD-FR-09 | docs/PRD.md | Requisito Funcional | Todo aviso assinado para validar origem e integridade | TRANSCRICAO | [09:19] Sofia; [09:20] Sofia |
| PRD-FR-10 | docs/PRD.md | Requisito Funcional | Novas tentativas automáticas e guarda com motivo ao esgotar | TRANSCRICAO | [09:15] Diego; [09:16] Diego; [09:18] Diego |
| PRD-FR-11 | docs/PRD.md | Requisito Funcional | Reprocessamento por ADMIN com registro de quem fez | TRANSCRICAO | [09:18] Diego; [09:36] Sofia |
| PRD-FR-12 | docs/PRD.md | Requisito Funcional | Identificador de evento igual em todas as tentativas | TRANSCRICAO | [09:25] Diego; [09:26] Larissa |
| PRD-FR-13 | docs/PRD.md | Requisito Funcional | Aviso informa o cadastro de origem | TRANSCRICAO | [09:44] Sofia; [09:45] Diego |
| PRD-NFR-01 | docs/PRD.md | Requisito Não Funcional | Aviso em menos de 10s | TRANSCRICAO | [09:02] Marcos |
| PRD-NFR-02 | docs/PRD.md | Requisito Não Funcional | Verificação a cada 2s, espera aceita no pior caso | TRANSCRICAO | [09:09] Diego; [09:10] Larissa |
| PRD-NFR-03 | docs/PRD.md | Requisito Não Funcional | Espera de 10s pela resposta do cliente | TRANSCRICAO | [09:42] Diego |
| PRD-NFR-04 | docs/PRD.md | Requisito Não Funcional | https obrigatório no cadastro | TRANSCRICAO | [09:23] Sofia |
| PRD-NFR-05 | docs/PRD.md | Requisito Não Funcional | HMAC-SHA256 com chave exclusiva por cadastro | TRANSCRICAO | [09:20] Sofia; [09:21] Sofia |
| PRD-NFR-06 | docs/PRD.md | Requisito Não Funcional | Convivência de 24h entre chaves | TRANSCRICAO | [09:21] Sofia |
| PRD-NFR-07 | docs/PRD.md | Requisito Não Funcional | Reprocessamento só ADMIN; configuração por qualquer autenticado | TRANSCRICAO | [09:36] Sofia; [09:37] Sofia |
| PRD-NFR-08 | docs/PRD.md | Requisito Não Funcional | Entrega at-least-once | TRANSCRICAO | [09:24] Diego |
| PRD-NFR-09 | docs/PRD.md | Requisito Não Funcional | 5 tentativas em cerca de 15h | TRANSCRICAO | [09:17] Diego; [09:17] Larissa |
| PRD-NFR-10 | docs/PRD.md | Requisito Não Funcional | Atomicidade entre mudança de status e aviso | TRANSCRICAO | [09:06] Diego; [09:40] Bruno |
| PRD-NFR-11 | docs/PRD.md | Requisito Não Funcional | Ordem por pedido enquanto houver um único processo de envio | TRANSCRICAO | [09:12] Diego; [09:13] Larissa |
| PRD-NFR-12 | docs/PRD.md | Requisito Não Funcional | Limite de 64KB, erro sem cortar | TRANSCRICAO | [09:23] Sofia; [09:24] Larissa |
| PRD-NFR-13 | docs/PRD.md | Requisito Não Funcional | Aviso enxuto sem itens do pedido | TRANSCRICAO | [09:43] Diego; [09:44] Bruno |
| PRD-NFR-14 | docs/PRD.md | Requisito Não Funcional | Reuso dos padrões sem ferramenta nova | TRANSCRICAO | [09:29] Bruno; [09:30] Larissa |
| PRD-DEP-01 | docs/PRD.md | Dependência | Revisão de segurança com 2 dias úteis antes do deploy | TRANSCRICAO | [09:46] Sofia; [09:49] Sofia |
| PRD-DEP-02 | docs/PRD.md | Dependência | Documentação no portal do desenvolvedor | TRANSCRICAO | [09:26] Marcos; [09:40] Marcos |
| PRD-DEP-03 | docs/PRD.md | Dependência | Migração do banco para as estruturas novas (derivado) | CODIGO | prisma/migrations/ |
| PRD-DEP-04 | docs/PRD.md | Dependência | Clientes validam assinatura e descartam repetições | TRANSCRICAO | [09:20] Sofia; [09:25] Diego |
| PRD-DEP-05 | docs/PRD.md | Dependência | Operação de um segundo processo (derivado) | TRANSCRICAO | [09:11] Diego |
| PRD-DEP-06 | docs/PRD.md | Dependência | Confirmação do prazo com a Atlas e comunicação aos clientes | TRANSCRICAO | [09:47] Marcos; [09:49] Marcos |
| PRD-RISK-01 | docs/PRD.md | Risco | Atraso faz a Atlas migrar para concorrente | TRANSCRICAO | [09:00] Marcos; [09:47] Larissa; [09:47] Marcos |
| PRD-RISK-02 | docs/PRD.md | Risco | Cliente não trata repetições | TRANSCRICAO | [09:25] Sofia; [09:26] Marcos |
| PRD-RISK-03 | docs/PRD.md | Risco | Vazamento da chave pelo cliente | TRANSCRICAO | [09:22] Diego; [09:21] Sofia |
| PRD-RISK-04 | docs/PRD.md | Risco | Cliente fora por mais de ~15h deixa de receber automaticamente | TRANSCRICAO | [09:17] Marcos; [09:18] Diego; [09:37] Larissa |
| PRD-RISK-05 | docs/PRD.md | Risco | Muitos avisos seguidos para o mesmo cliente | TRANSCRICAO | [09:38] Diego; [09:39] Larissa |
| PRD-RISK-06 | docs/PRD.md | Risco | Revisão de segurança não agendada segura o deploy | TRANSCRICAO | [09:49] Sofia; [09:46] Sofia; [09:47] Larissa |
| PRD-AC-01 | docs/PRD.md | Critério de Aceite | Aviso de SHIPPED em menos de 10s | TRANSCRICAO | [09:02] Marcos |
| PRD-AC-02 | docs/PRD.md | Critério de Aceite | Sem aviso de status não escolhido | TRANSCRICAO | [09:33] Marcos |
| PRD-AC-03 | docs/PRD.md | Critério de Aceite | Validação com a chave; antiga vale 24h e depois não | TRANSCRICAO | [09:21] Sofia |
| PRD-AC-04 | docs/PRD.md | Critério de Aceite | Cadastro sem https recusado | TRANSCRICAO | [09:23] Sofia |
| PRD-AC-05 | docs/PRD.md | Critério de Aceite | Últimas 100 entregas visíveis | TRANSCRICAO | [09:34] Marcos |
| PRD-AC-06 | docs/PRD.md | Critério de Aceite | Cliente fora por 2h recebe ao voltar, sem intervenção | TRANSCRICAO | [09:16] Diego |
| PRD-AC-07 | docs/PRD.md | Critério de Aceite | Reprocessamento só por ADMIN, com registro | TRANSCRICAO | [09:36] Sofia |
| PRD-AC-08 | docs/PRD.md | Critério de Aceite | Repetições com o mesmo identificador | TRANSCRICAO | [09:25] Diego |
| PRD-AC-09 | docs/PRD.md | Critério de Aceite | Chave não aparece em consultas | TRANSCRICAO | [09:31] Marcos |
| PRD-AC-10 | docs/PRD.md | Critério de Aceite | Integração documentada no portal (prazo antes da liberação derivado) | TRANSCRICAO | [09:26] Marcos; [09:40] Marcos |
| PRD-AC-11 | docs/PRD.md | Critério de Aceite | Os três clientes demandantes recebem avisos dos próprios pedidos | TRANSCRICAO | [09:00] Marcos |

## Notas de derivação

| ID | O que foi derivado | Base rastreável |
|---|---|---|
| FDD-OBJ-03, PRD-MET-04 | Exceção para pendentes de endpoint removido pelo cliente | Garantia at-least-once ([09:24] Diego) e DELETE do CRUD ([09:33] Bruno) |
| FDD-OBJ-07 | Secret nunca em log | Vazamento de secret em log de cliente ([09:22] Diego) |
| FDD-CONTRATO-05 | Rota `rotate-secret` | A reunião definiu só a capacidade de rotação ([09:21] Sofia) |
| FDD-CONTRATO-08 | Método POST, formato `sha256=` e ISO 8601 em X-Timestamp | Headers e payload JSON decididos ([09:44] Diego) |
| FDD-ERR-03 | WEBHOOK_SECRET_REQUIRED como falha permanente no worker | Código só citado ([09:28] Bruno); ver RFC-Q-11 |
| FDD-ERR-04, FDD-ERR-05, FDD-ERR-06, FDD-ERR-09 | Códigos e regras não citados | Convenção do prefixo WEBHOOK_ ([09:29] Larissa); timeout como falha ([09:42] Diego) |
| FDD-RES-06, FDD-AC-17, FDD-RISK-03 | Recuperação de PROCESSING ao iniciar | At-least-once aceita reenvio ([09:24] Diego) |
| FDD-RES-07, FDD-AC-15, FDD-RISK-01 | Bloqueio por endpoint e pedido durante retry | Garantia de ordem por order_id com single-worker ([09:12] Diego) |
| FDD-RES-09 | Encerramento gracioso | Padrão de `shutdown` em `src/server.ts` |
| FDD-OBS-01 | Métricas calculadas das tabelas | Alvo de 10s ([09:02] Marcos) e timeout de 10s ([09:42] Diego); `package.json` sem biblioteca de métricas |
| FDD-OBS-03, FDD-INT-07, FDD-AC-18 | Redact de secret no logger | [09:22] Diego; `redactPaths` em `src/shared/logger/index.ts` |
| FDD-OBS-04 | Correlação sem tracing | `requestLogger` em `src/middlewares/request-logger.middleware.ts` |
| FDD-INT-08, FDD-INT-10, FDD-INT-14 | Parâmetros no env, limpeza de tabelas nos testes, paginação | `envSchema`, `beforeEach` de `tests/setup.ts`, `paginated()` |
| FDD-RISK-07 | Ausência de listagem da dead letter | Replay por id ([09:18] Diego) sem endpoint de listagem na reunião |
| PRD-MET-02 | Meta de 3 de 3 clientes | Pedido formal dos três clientes ([09:00] Marcos) |
| PRD-DEP-03, PRD-DEP-05 | Migração e operação de segundo processo | Tabelas novas ([09:06] Diego, [09:18] Diego); worker separado ([09:11] Diego) |
| PRD-AC-10 | Publicar antes da liberação | Documentação no portal ([09:26] Marcos) |
| RFC-RISK-01 a 07, FDD-RISK-01 a 07, PRD-RISK-01 a 06 | Probabilidade e impacto | Avaliação de cada documento; as mitigações citam só o que a reunião definiu |
