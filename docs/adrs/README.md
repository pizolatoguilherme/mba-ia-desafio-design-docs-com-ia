# Architectural Decision Records

Este diretório armazena os ADRs (Architectural Decision Records) do Sistema de Webhooks de Notificação de Pedidos. Cada ADR registra uma decisão fechada na reunião técnica de webhooks (`TRANSCRICAO.md`), com contexto, alternativas descartadas e consequências, rastreadas a `[hh:mm] Nome` da transcrição e a arquivos do código.

## Convenção

- Um arquivo por decisão, nomeado `ADR-NNN-titulo-em-kebab-case.md` (substitui a convenção antiga `0001-titulo-da-decisao.md`).
- Numeração sequencial de três dígitos; números não são reaproveitados.
- Seções: Status, Contexto, Drivers da decisão, Decisão, Alternativas Consideradas, Consequências (Positivas, Negativas, Trade-off), Referências e ADRs relacionados.
- Lacunas que a reunião não fechou aparecem como "Ponto em aberto" dentro de Consequências e apontam para o `RFC-Q` correspondente no [RFC](../RFC.md#questões-em-aberto).

## Índice

| ADR | Título | Status | Decisão em uma linha |
|---|---|---|---|
| [ADR-001](ADR-001-outbox-transacional-no-mysql.md) | Outbox transacional no MySQL | Aceito | Evento gravado em `webhook_outbox` na mesma transação do `changeStatus`, via `publishWebhookEvent(tx, ...)` |
| [ADR-002](ADR-002-worker-separado-com-polling.md) | Worker separado com polling | Aceito | Worker em processo próprio (`npm run worker`), polling de 2s, PrismaClient próprio, single-worker |
| [ADR-003](ADR-003-retry-com-backoff-e-dead-letter.md) | Retry com backoff e dead letter | Aceito | 5 tentativas com backoff 1m/5m/30m/2h/12h, depois `webhook_dead_letter`, replay manual só para ADMIN |
| [ADR-004](ADR-004-hmac-sha256-com-secret-por-endpoint.md) | HMAC-SHA256 com secret por endpoint | Aceito | Assinatura HMAC-SHA256 do corpo em `X-Signature`, secret por endpoint, rotação com grace de 24h |
| [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) | Entrega at-least-once com X-Event-Id | Aceito | Duplicatas possíveis; o cliente deduplica pelo UUID do `X-Event-Id` gerado na inserção |
| [ADR-006](ADR-006-reuso-dos-padroes-do-projeto.md) | Reuso dos padrões do projeto | Aceito | Módulo padrão em `src/modules/webhooks` (novo, a criar), AppError com prefixo `WEBHOOK_`, Pino, error middleware, Zod, `requireRole`, UUID |
| [ADR-007](ADR-007-snapshot-e-filtro-na-insercao.md) | Snapshot e filtro na inserção | Aceito | Payload renderizado na inserção e filtro de status aplicado antes de gravar na outbox |
