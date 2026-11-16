# ADR-003: Retry com backoff exponencial, dead letter em tabela própria e replay ADMIN

## Status

Aceito (2026-11-16). Decidido na reunião técnica de webhooks por: Diego (Engenheiro Sênior, Plataforma), Larissa (Tech Lead), Bruno (Engenheiro Pleno, Pedidos), Marcos (Product Manager), Sofia (Engenheira de Segurança).

## Contexto

O worker do [ADR-002](ADR-002-worker-separado-com-polling.md) vai encontrar clientes fora do ar, lentos ou com erro. É preciso decidir quantas vezes tentar, com que intervalo e o que fazer quando as tentativas acabarem ([09:14] Larissa).

Há duas pressões opostas. Desistir cedo demais perde eventos em indisponibilidades normais: a plataforma já teve cliente com duas horas de manutenção planejada ([09:16] Diego). Tentar para sempre deixa eventos pendurados indefinidamente quando o cliente some ([09:15] Diego). Do lado de produto, um cliente fora do ar por cerca de 15 horas já tem um problema sério dele, e perder a entrega automática nesse caso é aceitável ([09:17] Marcos).

Eventos que esgotam as tentativas precisam ficar guardados como evidência para debug e para reprocessamento ([09:18] Diego). Reprocessar mexe na fila de entrega, então a operação precisa de controle de acesso e auditoria ([09:36] Sofia). O projeto já tem `requireRole` em `src/middlewares/auth.middleware.ts`, usado com `ADMIN` em `src/modules/users/user.routes.ts`.

## Drivers da decisão

- Cobrir indisponibilidades de horas, como manutenção planejada ([09:16] Diego).
- Não deixar evento pendurado para sempre ([09:15] Diego).
- Outbox principal com leitura limpa ([09:18] Diego).
- Evidência para debug e reprocessamento manual ([09:18] Diego).
- Replay restrito e auditável ([09:36] Sofia).

## Decisão

- **Retry com backoff exponencial**, **5 tentativas**, com progressão **1m, 5m, 30m, 2h, 12h**, totalizando quase 15 horas entre a primeira falha e a última tentativa ([09:15] Diego, [09:16] Larissa, [09:17] Diego, [09:17] Larissa).
- Resposta que não chega em **10 segundos** conta como falha e segue para retry ([09:42] Diego, [09:42] Sofia).
- Esgotadas as tentativas, o evento é considerado falha permanente e movido para a **tabela separada `webhook_dead_letter`**, com o payload, o motivo da falha e o timestamp ([09:15] Diego, [09:18] Diego).
- **Replay manual** pelo endpoint `POST /admin/webhooks/dead-letter/:id/replay`, que recoloca o evento na outbox como pendente ([09:18] Diego, [09:35] Diego).
- O replay exige **role ADMIN**, reaproveitando o `requireRole` existente, e **registra em log quem o executou**, para auditoria ([09:36] Sofia, [09:36] Larissa).

## Alternativas Consideradas

### Alternativa 1: retry indefinido com backoff (descartada)
- Continuar tentando sem teto, só aumentando o intervalo.
- Motivo do descarte: o evento fica pendurado para sempre se o cliente sumiu ([09:15] Diego).

### Alternativa 2: 3 tentativas, mais agressivo (descartada)
- Proposta de reduzir o teto para 3 ([09:16] Bruno).
- Motivo do descarte: com 3 tentativas o evento morreria em cerca de 30 minutos, e já houve cliente com duas horas de manutenção planejada ([09:16] Diego).

### Alternativa 3: marcar "failed" na própria outbox (descartada)
- Manter os eventos esgotados na `webhook_outbox` com um status de falha ([09:17] Larissa).
- Motivo do descarte: a tabela separada deixa a leitura da outbox principal mais limpa e funciona como evidência para debug e reprocessamento ([09:18] Diego, [09:18] Bruno).

### Alternativa 4: replay permitido a operadores (descartada)
- Liberar o replay para qualquer usuário autenticado, como o CRUD de configuração.
- Motivo do descarte: "mexer em fila de entrega de notificação não é coisa de operador" ([09:36] Sofia).

## Consequências

### Positivas
- Indisponibilidades de até cerca de 15 horas são absorvidas sem intervenção humana ([09:17] Diego, [09:17] Marcos).
- Toda falha permanente fica registrada com payload e motivo, pronta para análise ([09:18] Diego).
- A outbox contém apenas trabalho em andamento, o que simplifica a consulta do worker ([09:18] Diego).
- O replay é restrito e auditável, reaproveitando a autorização existente ([09:36] Larissa).

### Negativas
- Um evento pode chegar ao cliente com até cerca de 15 horas de atraso em relação à mudança de status ([09:17] Diego).
- Depois de esgotado, o evento depende de um ADMIN perceber a falha e fazer o replay; não há aviso automático ao cliente, porque o email ficou para a próxima fase ([09:37] Larissa).
- Reentregas aumentam a chance de duplicata no cliente, coberta pelo [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) (derivado).
- Duas tabelas para manter consistentes ao mover um evento da outbox para a dead letter e de volta (derivado).
- Ponto em aberto: a reunião não deixa explícito se as 5 tentativas incluem o envio original; a soma de 1m+5m+30m+2h+12h, quase 15 horas entre a primeira falha e a última tentativa ([09:17] Diego), só fecha com 5 retentativas após a falha inicial. Ver [RFC-Q-08](../RFC.md#questões-em-aberto).

### Trade-off
Ganhamos resiliência a indisponibilidades de horas e um destino limpo e auditável para falhas permanentes, ao custo de entregas que podem atrasar até cerca de 15 horas e de reprocessamento manual dependente de um ADMIN.

## Referências

- Transcrição: [09:15] Diego, [09:16] Bruno, [09:16] Diego, [09:17] Diego, [09:17] Larissa, [09:17] Marcos, [09:18] Diego, [09:35] Diego, [09:36] Sofia, [09:36] Larissa, [09:42] Diego
- Código: `src/middlewares/auth.middleware.ts` (`requireRole`), `src/modules/users/user.routes.ts` (precedente de `requireRole('ADMIN')`), `prisma/schema.prisma` (`enum UserRole`)

## ADRs relacionados

- Depende de: [ADR-002](ADR-002-worker-separado-com-polling.md)
- Relacionado a: [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) (retry gera duplicatas)
- Relacionado a: [ADR-006](ADR-006-reuso-dos-padroes-do-projeto.md) (`requireRole` reaproveitado)
