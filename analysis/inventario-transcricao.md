# Inventário da transcrição e do código

> Base de verdade do pacote de design docs. Gerado com o roteiro da skill `/transcript-inventory` em 2026-11-16.
> Toda linha tem fonte: `[hh:mm] Nome` em `TRANSCRICAO.md` ou caminho existente no repositório.
> Categorias: D decisão fechada, RF requisito funcional, RNF não funcional, X descartado, A adiado/fora de escopo, Q em aberto, C gancho com o código, S detalhe secundário.

## 1. Participantes

| Nome | Papel | Observação |
|---|---|---|
| Larissa | Tech Lead, conduz a reunião | Fecha as decisões e faz o resumo final ([09:48] Larissa); vai abrir o doc de design ([09:50] Larissa) |
| Marcos | Product Manager | Traz a demanda dos clientes e os requisitos de produto; sai às 09:50 |
| Bruno | Engenheiro Pleno, time de Pedidos | Conhece o `order.service`; propõe a estrutura do módulo |
| Diego | Engenheiro Sênior, time de Plataforma | Entra às 09:05; propõe outbox, polling, retry e at-least-once |
| Sofia | Engenheira de Segurança | Define HMAC, secrets, TLS e limite de payload; sai às 09:50 |

A reunião acontece numa quinta-feira às 09:00 e dura cerca de 55 minutos. **A data não é informada.**

## 2. Decisões fechadas (D)

| # | Decisão | Fonte(s) | Alternativas rejeitadas (motivo, fonte) | ADR previsto |
|---|---|---|---|---|
| D1 | Webhook é **outbound** (plataforma → cliente) | [09:02] Marcos; [09:03] Sofia | Inbound: não pedido ([09:02] Marcos) | escopo (PRD/RFC) |
| D2 | **Padrão outbox no MySQL**: inserir em `webhook_outbox` dentro da mesma transação que atualiza `orders` e `order_status_history` | [09:06] Diego; [09:07] Diego; [09:08] Larissa | Disparo síncrono no service: transação já pesada, cliente lento trava mudanças de status, sem resposta para cliente fora do ar ([09:04] Bruno; [09:06] Diego). Redis Streams/fila: mais infra; Redis Cluster é overengineering para time pequeno ([09:07] Larissa; [09:07] Diego) | ADR-001 |
| D3 | Inserção na outbox **dentro da transação do `changeStatus`**; se falhar, rollback ("não pode ter caso de status mudar e evento não sair") | [09:40] Bruno; [09:41] Diego | Inserir fora da transação: perde a garantia ([09:41] Diego) | ADR-001 |
| D4 | Função `publishWebhookEvent(tx, order, fromStatus, toStatus)` recebe o tx da transação atual, sem injetar repository inteiro no OrderService | [09:41] Bruno; [09:41] Diego | Injetar repository de webhook no OrderService ([09:41] Bruno; [09:41] Diego) | ADR-001 / ADR-006 |
| D5 | Worker lê a outbox por **polling a cada 2s**; latência mínima de 2s no pior caso é aceita | [09:09] Diego; [09:10] Marcos; [09:10] Larissa | Trigger do banco / NOTIFY-LISTEN: MySQL não tem listener nativo; trigger só executa SQL e não notifica processo externo ([09:09] Bruno; [09:09] Diego) | ADR-002 |
| D6 | Worker em **processo separado** da API, com nova entry-point `src/worker.ts` (novo, a criar) e script `npm run worker` | [09:11] Diego; [09:11] Larissa | Worker dentro da instância da API: se a API reinicia, perde o worker ([09:11] Diego) | ADR-002 |
| D7 | Worker usa o mesmo banco e a mesma stack, mas uma **instância própria de PrismaClient** (PrismaClient é por processo; mesma DATABASE_URL) | [09:11] Bruno; [09:11] Diego; [09:30] Bruno | Compartilhar o PrismaClient da API: impossível entre processos ([09:30] Bruno) | ADR-002 |
| D8 | **Single-worker**; processa em ordem de created_at; ordering garantido só por order_id e só enquanto houver um worker (limitação conhecida) | [09:12] Diego; [09:13] Larissa; [09:14] Marcos | Ordering global: clientes nunca pediram ([09:14] Marcos) | ADR-002 |
| D9 | **Retry com backoff exponencial**, **5 tentativas**, progressão **1m, 5m, 30m, 2h, 12h** (quase 15h entre a primeira falha e a última tentativa) | [09:15] Diego; [09:16] Larissa; [09:17] Diego; [09:17] Larissa | Retry indefinido: evento pendurado para sempre se o cliente sumiu ([09:15] Diego). 3 tentativas: mataria em 30 min; já houve cliente com 2h de manutenção ([09:16] Bruno; [09:16] Diego) | ADR-003 |
| D10 | **DLQ em tabela separada `webhook_dead_letter`**, com payload, motivo da falha e timestamp | [09:18] Diego; [09:18] Bruno | Marcar "failed" na própria outbox: a tabela separada deixa a leitura da outbox mais limpa e serve de evidência para debug e reprocessamento ([09:17] Larissa; [09:18] Diego) | ADR-003 |
| D11 | **Replay manual da DLQ** via `POST /admin/webhooks/dead-letter/:id/replay`, que recoloca o evento na outbox como pendente | [09:18] Diego; [09:19] Larissa; [09:35] Diego | n/a | ADR-003 |
| D12 | Replay exige **role ADMIN** (reaproveita `requireRole`) e **loga quem executou** (auditoria) | [09:36] Sofia; [09:36] Larissa | Operador fazer replay: "mexer em fila de entrega não é coisa de operador" ([09:36] Sofia) | ADR-003 / ADR-006 |
| D13 | **HMAC-SHA256** sobre o corpo do request, assinatura no header **X-Signature** | [09:20] Sofia; [09:20] Bruno; [09:22] Sofia | n/a (padrão de mercado, "todo cliente sério tem biblioteca" ([09:20] Sofia)) | ADR-004 |
| D14 | **Secret única por endpoint** de webhook | [09:21] Sofia | Secret global da plataforma: "se vaza uma, vaza tudo" ([09:21] Sofia) | ADR-004 |
| D15 | Secret **rotacionável via API**; a antiga vale por **24h** em paralelo (grace period) e depois morre | [09:21] Sofia; [09:22] Diego; [09:22] Sofia | n/a | ADR-004 |
| D16 | Garantia **at-least-once**; o cliente pode receber duplicata e deve estar preparado | [09:24] Diego; [09:26] Larissa | Exactly-once: exigiria coordenação dos dois lados, muito mais complexo ([09:25] Diego) | ADR-005 |
| D17 | Header **X-Event-Id** com UUID gerado quando o evento entra na outbox, único por evento, para dedup no cliente | [09:25] Diego; [09:26] Larissa | n/a | ADR-005 |
| D18 | Módulo **`src/modules/webhooks`** (novo, a criar) no padrão controller/service/repository/routes/schemas | [09:27] Bruno; [09:28] Diego | n/a | ADR-006 |
| D19 | Lógica de processamento num arquivo do módulo (`webhook.worker.ts` ou `webhook.processor.ts`, novo, a criar); `src/worker.ts` (novo, a criar) como entry separada | [09:28] Bruno; [09:28] Diego | n/a | ADR-002 / ADR-006 |
| D20 | **Reuso máximo**: AppError, Pino, error middleware, padrão de módulos, schemas Zod, códigos de erro; nada novo de logger | [09:28] Bruno; [09:29] Bruno; [09:30] Larissa | Introduzir ferramenta nova ("não vamos botar nada novo" ([09:29] Bruno)) | ADR-006 |
| D21 | Códigos de erro com **prefixo `WEBHOOK_`**, ex.: WEBHOOK_NOT_FOUND, WEBHOOK_INVALID_URL, WEBHOOK_SECRET_REQUIRED | [09:28] Bruno; [09:29] Larissa | n/a | ADR-006 |
| D22 | Filtro de eventos por status **na inserção** da outbox: se nenhum webhook do customer quer aquele status, nem insere | [09:33] Marcos; [09:34] Bruno; [09:34] Diego | Filtrar na hora do envio: gasta linhas na tabela à toa ([09:34] Diego; [09:34] Bruno) | ADR-007 |
| D23 | Payload **renderizado (snapshot) na inserção**, refletindo o estado no momento da mudança de status | [09:52] Larissa; [09:52] Diego; [09:52] Bruno | Guardar só order_id e renderizar no envio: "se o pedido mudar depois… tem caso esquisito" ([09:51] Bruno; [09:52] Larissa) | ADR-007 |
| D24 | IDs da outbox em **UUID**, padrão do projeto | [09:51] Diego; [09:51] Larissa | Id auto incremental ([09:51] Diego) | ADR-006 |
| D25 | CRUD de configuração com **qualquer role autenticada** (por enquanto) | [09:36] Marcos; [09:37] Sofia | n/a | (RNF / segurança) |
| D26 | `customer_id` **não vem do JWT**: o JWT é do usuário operador; endpoint autenticado normal, com customer_id no body ou no path | [09:32] Bruno; [09:32] Marcos; [09:32] Larissa | customer_id implícito do JWT ([09:31] Marcos), corrigido em [09:32] | (contrato FDD) |

## 3. Requisitos funcionais (RF)

| # | Requisito | Fonte(s) | Observação |
|---|---|---|---|
| RF1 | Notificar o cliente quando o status de um pedido dele muda | [09:00] Marcos | Hoje os clientes fazem polling em GET /orders |
| RF2 | Cadastrar webhook via `POST` com url e lista de status desejados; a secret é **gerada pela plataforma e devolvida na criação** | [09:31] Marcos | O customer_id vem do body ou do path (D26) |
| RF3 | Editar webhook (`PATCH`) | [09:33] Bruno | |
| RF4 | Remover webhook (`DELETE`) | [09:33] Bruno | |
| RF5 | Listar os webhooks de um customer (`GET`) | [09:33] Bruno | |
| RF6 | Escolher, por endpoint, quais eventos (status) receber | [09:33] Bruno; [09:33] Marcos | ex.: "só SHIPPED e DELIVERED" |
| RF7 | Histórico de entregas: últimos 100 webhooks enviados, com sucesso/falha, payload, response e tempo de resposta (`GET /webhooks/:id/deliveries`) | [09:34] Marcos; [09:35] Larissa | |
| RF8 | Rotacionar secret: endpoint para o cliente pedir nova secret | [09:21] Sofia | Rota não nomeada na reunião |
| RF9 | Replay manual de evento da DLQ (ADMIN) | [09:18] Diego; [09:35] Diego; [09:36] Sofia | D11, D12 |
| RF10 | Retry automático de entregas falhas e envio para a DLQ após esgotar | [09:15] Diego; [09:17] Larissa | D9, D10 |
| RF11 | Assinar cada envio (HMAC) para o cliente validar origem e integridade | [09:19] Sofia; [09:20] Sofia | D13 |
| RF12 | Registro em log de auditoria de quem executou o replay | [09:36] Sofia | D12 |
| RF13 | Ativar/desativar endpoint (estado ativo na configuração) | [09:21] Bruno; [09:21] Sofia | "url + secret + customer_id + estado ativo" |

## 4. Requisitos não funcionais (RNF)

| # | Requisito | Valor | Fonte(s) |
|---|---|---|---|
| RNF1 | Latência percebida como "tempo real" | **< 10 s** | [09:02] Marcos |
| RNF2 | Intervalo de polling do worker | **2 s** (latência mínima aceita de 2 s) | [09:09] Diego; [09:10] Larissa |
| RNF3 | Timeout da chamada HTTP ao cliente | **10 s**; sem resposta conta como falha e vai para retry | [09:42] Diego; [09:42] Sofia |
| RNF4 | TLS obrigatório: URL tem de ser https; http é recusado com erro de validação no schema Zod | https | [09:23] Sofia |
| RNF5 | Tamanho máximo do payload | **64 KB**; acima disso gera erro, não trunca | [09:23] Sofia; [09:24] Diego; [09:24] Larissa |
| RNF6 | Tentativas de entrega | **5**, janela de **~15 h** | [09:15] Diego; [09:17] Diego; [09:17] Marcos |
| RNF7 | Grace period na rotação de secret | **24 h** | [09:21] Sofia |
| RNF8 | Garantia de entrega | **at-least-once** | [09:24] Diego |
| RNF9 | Índices na outbox | status (pendente, processando, falhou, entregue) e created_at; leitura em batch pequeno | [09:08] Diego |
| RNF10 | Atomicidade: evento registrado se e somente se a transação de status commitar | rollback conjunto | [09:06] Diego; [09:40] Bruno |
| RNF11 | Payload enxuto, sem items do pedido | | [09:43] Diego; [09:44] Bruno |
| RNF12 | Revisão de segurança antes do deploy | **≥ 2 dias úteis** (HMAC e geração de secret) | [09:46] Sofia; [09:49] Sofia |

## 5. Descartados (X)

| # | Item | Motivo | Fonte |
|---|---|---|---|
| X1 | Disparo síncrono no service de orders | Transação pesada; cliente lento trava outros pedidos; sem resposta para cliente fora do ar (não dá para fazer rollback do status) | [09:04] Bruno; [09:06] Diego |
| X2 | Redis Streams / Redis Cluster | Exige subir infra nova; overengineering para time pequeno | [09:07] Larissa; [09:07] Diego |
| X3 | Trigger do banco / LISTEN-NOTIFY para acordar o worker | MySQL não tem listener nativo; trigger não notifica processo externo; alternativas seriam improvisos | [09:09] Bruno; [09:09] Diego |
| X4 | Worker no mesmo processo da API | Se a API reinicia, perde o worker | [09:11] Diego |
| X5 | 3 tentativas de retry | Pouco: mataria o evento em ~30 min; já houve cliente 2h em manutenção | [09:16] Bruno; [09:16] Diego |
| X6 | Retry indefinido | Evento fica pendurado para sempre se o cliente sumiu | [09:15] Diego |
| X7 | DLQ como status "failed" na própria outbox | A tabela separada deixa a outbox mais limpa e guarda evidência para debug e reprocessamento | [09:17] Larissa; [09:18] Diego |
| X8 | Secret global da plataforma | Se vaza uma, vaza tudo | [09:21] Sofia |
| X9 | Exactly-once | Exige coordenação dos dois lados; muito mais complexo | [09:25] Diego |
| X10 | Truncar payload grande | Se chegou nesse tamanho, tem algo errado; preferem erro | [09:23] Sofia |
| X11 | customer_id vindo do JWT | O JWT é do usuário operador, não do cliente | [09:32] Bruno; [09:32] Larissa |
| X12 | Renderizar payload no envio (guardar só order_id) | O evento deve refletir o estado do momento da mudança | [09:52] Larissa |
| X13 | Filtrar eventos na hora do envio | Desperdiça linhas na outbox | [09:34] Bruno |
| X14 | Id auto incremental na outbox | O projeto usa UUID em tudo | [09:51] Larissa |

## 6. Adiados / fora de escopo (A)

| # | Item | Situação | Fonte |
|---|---|---|---|
| A1 | Email ao cliente quando o webhook falha repetidamente | Fora desta fase; talvez a próxima, depois de medir impacto ("futuro") | [09:37] Marcos; [09:37] Larissa; [09:38] Marcos |
| A2 | Rate limiting de envio para o cliente | Fora do escopo; "observar e decidir depois" | [09:38] Diego; [09:39] Diego; [09:39] Larissa |
| A3 | Dashboard / painel visual para o cliente | Fora agora; é projeto separado do time de frontend | [09:39] Marcos; [09:40] Larissa |
| A4 | Arquivamento de linhas entregues (após ~30 dias) | Fora do escopo desta feature | [09:08] Diego |
| A5 | Webhooks inbound | Não pedido | [09:02] Marcos |
| A6 | Múltiplos workers em paralelo / ordering global | Futuro; particionar por order_id ou usar lock pessimista | [09:12] Diego; [09:13] Diego; [09:13] Larissa |
| A7 | Endurecer as permissões do CRUD de configuração | "Mais pra frente" | [09:37] Sofia |

## 7. Questões em aberto (Q)

| # | Questão | Fonte | Por que está em aberto |
|---|---|---|---|
| Q1 | Rate limiting de saída: 50 mudanças em um minuto geram 50 chamadas ao cliente? | [09:38] Diego; [09:39] Larissa | Registrado explicitamente como "ponto em aberto", a observar |
| Q2 | Escala para múltiplos workers: particionar por order_id ou lock pessimista? | [09:13] Diego | "Problema do futuro" |
| Q3 | Retenção/arquivamento das linhas entregues (prazo "30 dias ou assim") | [09:08] Diego | Valor aproximado e fora do escopo; sem dono |
| Q4 | customer_id no body ou no path? | [09:32] Larissa | Larissa cita as duas opções sem escolher |
| Q5 | Endurecer as roles do CRUD de configuração | [09:37] Sofia | "Por enquanto sim. Mais pra frente a gente pode endurecer" |
| Q6 | Detalhes de segurança da implementação (HMAC e geração de secret) passam pela revisão da Sofia | [09:46] Sofia | Revisão marcada para antes do deploy; o resultado ainda não existe |
| Q7 | Email de alerta na próxima fase depende de medir o impacto | [09:37] Larissa | Condição futura |

## 8. Ganchos com o código (C)

| # | Arquivo (existente) | Símbolo | Como a feature se conecta | Fonte na reunião |
|---|---|---|---|---|
| C1 | `src/modules/orders/order.service.ts` | `OrderService.changeStatus` (usa `this.prisma.$transaction(async (tx) => …)`; atualiza `order`, cria `orderStatusHistory`; `debitStock`/`replenishStock`) | Chamar `publishWebhookEvent(tx, order, from, to)` dentro do mesmo `$transaction` | [09:04] Bruno; [09:40] Bruno; [09:41] Bruno |
| C2 | `src/modules/orders/order.service.ts` | `type TxClient = Prisma.TransactionClient` | Tipo do parâmetro `tx` de `publishWebhookEvent` | [09:41] Bruno |
| C3 | `src/modules/orders/order.status.ts` | `canTransition`, transições PENDING→PAID→PROCESSING→SHIPPED→DELIVERED, CANCELLED | Os status do filtro de eventos são os de `OrderStatus` | [09:12] Larissa; [09:33] Marcos |
| C4 | `prisma/schema.prisma` | `enum OrderStatus`; `model Order` (`orderNumber`, `customerId`, `totalCents`); `@id @default(uuid()) @db.Char(36)`; `@@map` snake_case; `enum UserRole { ADMIN OPERATOR }` | Novos models (outbox, dead letter, endpoints, entregas) seguem a convenção; payload usa os campos de Order | [09:43] Diego; [09:51] Larissa |
| C5 | `src/shared/errors/app-error.ts` | `AppError(message, statusCode, errorCode, details)` | Base das classes de erro do módulo | [09:28] Bruno |
| C6 | `src/shared/errors/http-errors.ts` | `NotFoundError`, `ValidationError`, `ConflictError`, `UnprocessableEntityError`, `ForbiddenError`, `InvalidStatusTransitionError`, `InsufficientStockError` | Padrão de erro específico com código (ex.: `INSUFFICIENT_STOCK`) a seguir com `WEBHOOK_*` | [09:28] Bruno |
| C7 | `src/shared/errors/index.ts` | barrel de exportação | Exportar as novas classes de erro | [09:28] Bruno |
| C8 | `src/middlewares/error.middleware.ts` | `errorMiddleware` trata AppError, ZodError, Prisma P2002/P2025; formato `{ error: { code, message, details? } }` | Pega os erros novos **sem mudança** | [09:29] Bruno |
| C9 | `src/middlewares/auth.middleware.ts` | `authenticate`, `requireRole(...roles)`, `AuthUser.role: 'ADMIN' \| 'OPERATOR'` | CRUD com `authenticate`; replay com `requireRole('ADMIN')` | [09:32] Larissa; [09:36] Larissa |
| C10 | `src/modules/users/user.routes.ts` | uso existente de `requireRole('ADMIN')` | Precedente do padrão para a rota admin | [09:36] Larissa |
| C11 | `src/middlewares/validate.middleware.ts` | `validate({ body, query, params })` com Zod, gera `ValidationError` | Validação dos schemas do módulo (https, filtro de status) | [09:23] Sofia; [09:30] Larissa |
| C12 | `src/shared/logger/index.ts` | `logger` Pino com `redact` (`*.password`, `*.token`…) | Logs do worker e do módulo; incluir a secret no redact (derivado de [09:22] Diego) | [09:29] Bruno |
| C13 | `src/middlewares/request-logger.middleware.ts` | `requestLogger` gera/propaga `X-Request-Id` e loga `http_request` com `userId` | Correlação de logs da API e auditoria de quem fez a chamada | [09:36] Sofia |
| C14 | `src/config/database.ts` | `createPrismaClient()`, `prisma` singleton | O worker cria a própria instância com `createPrismaClient()` | [09:30] Bruno |
| C15 | `src/config/env.ts` | `envSchema` Zod (DATABASE_URL, LOG_LEVEL…) | Mesma DATABASE_URL; parâmetros do worker, se configuráveis, entram aqui | [09:30] Bruno |
| C16 | `src/server.ts` | `bootstrap()` + `shutdown` em SIGINT/SIGTERM + `prisma.$disconnect()` | Modelo para `src/worker.ts` (novo, a criar) | [09:11] Larissa |
| C17 | `src/app.ts` | `buildControllers(prisma)`, `app.use('/api/v1', …)` | Instanciar repository/service/controller do webhook; rotas ficam sob `/api/v1` | [09:27] Bruno |
| C18 | `src/routes/index.ts` | `buildApiRouter(controllers)`, tipo `Controllers` | Registrar `/webhooks` e `/admin/webhooks` | [09:27] Bruno |
| C19 | `src/shared/http/response.ts` | `paginated()`, `PaginatedResponse` | Listagens (webhooks, deliveries) | [09:34] Marcos |
| C20 | `package.json` | scripts `dev`, `start` com `--env-file=.env`; deps pino, zod, prisma, uuid | Novo script `worker` (D6); sem dependência nova obrigatória | [09:11] Larissa; [09:29] Bruno |
| C21 | `tests/orders.test.ts`, `tests/helpers/factories.ts`, `tests/setup.ts`, `vitest.config.ts` | vitest + supertest, `bootstrapAuthenticatedUser`, limpeza de tabelas no `beforeEach` | Padrão para os testes do módulo; o `setup.ts` precisará limpar as novas tabelas | (código) |

## 9. Detalhes secundários (S)

| # | Detalhe | Fonte |
|---|---|---|
| S1 | Payload JSON: event_id, event_type `order.status_changed`, timestamp ISO 8601, order_id, order_number, from_status, to_status, customer_id e campos básicos da order como total_cents; **sem items** (o cliente consulta GET /orders/:id) | [09:43] Diego |
| S2 | Headers: X-Event-Id (UUID), X-Signature (HMAC), X-Timestamp (horário do envio, para detectar replay attack), Content-Type application/json | [09:44] Diego |
| S3 | Header X-Webhook-Id com o id do endpoint, para quem tem vários cadastros | [09:44] Sofia; [09:45] Diego |
| S4 | Estados do evento na outbox: pendente, processando, falhou, entregue | [09:08] Diego |
| S5 | Worker busca "os eventos pendentes mais antigos", em "batch pequeno", processa e marca | [09:08] Diego; [09:09] Diego |
| S6 | Tabela de configuração: url + secret + customer_id + estado ativo | [09:21] Bruno; [09:21] Sofia |
| S7 | Já houve cliente que vazou a secret em log da própria aplicação | [09:22] Diego |
| S8 | O cliente com indisponibilidade de 15h "já tá com problema sério dele" (aceitável) | [09:17] Marcos |
| S9 | Stripe e GitHub usam at-least-once com event id | [09:25] Diego |
| S10 | Marcos vai documentar a dedup e a integração no portal do desenvolvedor | [09:26] Marcos; [09:40] Marcos |
| S11 | Prazo: Atlas quer para o fim de novembro; estimativa de 3 sprints com revisão da Sofia incluída | [09:45] Marcos; [09:46] Larissa; [09:47] Larissa |
| S12 | Quebra da estimativa: outbox + DLQ = 1 sprint; worker + retry = 1 sprint; CRUD + deliveries = 0,5; integração no order.service + testes E2E = 0,5; HMAC, schemas e validações, "mais um pouco" | [09:46] Larissa |
| S13 | Clientes demandantes: Atlas Comercial, MaxDistribuição, Nova Cargo (B2B); a Atlas ameaça migrar para concorrente se não sair até o fim do trimestre | [09:00] Marcos |
| S14 | Larissa marca uma sessão para Bruno e Diego revisarem o doc de design antes de codar | [09:50] Larissa |

## 10. Lacunas identificadas no código (não discutidas na reunião)

| # | Lacuna | Arquivo |
|---|---|---|
| L1 | `OrderService.create` grava o histórico inicial (`fromStatus: null → PENDING`) sem passar por `changeStatus`. A reunião só fala em "quando o status muda" e não trata do evento de criação do pedido | `src/modules/orders/order.service.ts` |
| L2 | `changeStatus` com `from === to` lança `ConflictError` antes de qualquer escrita; nenhum evento é gerado nesse caso (comportamento herdado, coerente com "status mudou") | `src/modules/orders/order.service.ts` |
| L3 | Não existe métrica nem tracing no projeto hoje; a única correlação é o `X-Request-Id` do `requestLogger`. Métricas e tracing do FDD serão (derivado) | `src/middlewares/request-logger.middleware.ts`, `package.json` |
| L4 | `tests/setup.ts` apaga as tabelas na ordem de FKs no `beforeEach`; as novas tabelas precisarão entrar ali | `tests/setup.ts` |
| L5 | Todas as rotas ficam sob o prefixo `/api/v1`; os endpoints citados na reunião (`/webhooks`, `/admin/webhooks/...`) ficam efetivamente em `/api/v1/webhooks` etc. | `src/app.ts` |

## 11. Dúvidas para o usuário (resolvidas no checkpoint de 2026-11-16)

| # | Dúvida | Resolução do usuário |
|---|---|---|
| 1 | customer_id no body ou no path (Q4) | Proposta no FDD segue o **texto literal da reunião**: `POST /webhooks` com `customerId` no body e `GET /webhooks?customerId=`, rotulada "pendente de confirmação, ver RFC-Q" |
| 2 | Evento de criação do pedido (L1) | Entra **só como questão em aberto identificada no código** no RFC; não vira requisito |
| 3 | ADR-007 (snapshot + filtro na inserção) | **Mantido**: 7 ADRs no pacote |
