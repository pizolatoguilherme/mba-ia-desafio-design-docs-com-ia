# ADR-007: Payload renderizado e filtro de eventos no momento da inserção na outbox

## Status

Aceito (2026-11-16). Decidido na reunião técnica de webhooks por: Larissa (Tech Lead), Diego (Engenheiro Sênior, Plataforma), Bruno (Engenheiro Pleno, Pedidos), Marcos (Product Manager).

## Contexto

A outbox do [ADR-001](ADR-001-outbox-transacional-no-mysql.md) é gravada dentro da transação de `changeStatus` em `src/modules/orders/order.service.ts`, e o worker do [ADR-002](ADR-002-worker-separado-com-polling.md) envia depois, às vezes horas depois por causa do retry ([09:17] Diego). Duas perguntas ficaram para decidir: o que exatamente gravar na linha da outbox e quando aplicar o filtro de eventos de cada endpoint.

Cada endpoint escolhe quais status quer receber, por exemplo "só SHIPPED e DELIVERED" ([09:33] Bruno, [09:33] Marcos). Os status possíveis são os do `enum OrderStatus` (`prisma/schema.prisma`), com as transições definidas em `src/modules/orders/order.status.ts`.

O payload é JSON enxuto, sem items: `event_id`, `event_type` `order.status_changed`, timestamp ISO 8601, `order_id`, `order_number`, `from_status`, `to_status`, `customer_id` e campos básicos como `total_cents` ([09:43] Diego, [09:44] Bruno). Entre a mudança de status e o envio, o pedido pode mudar de novo ([09:52] Larissa).

## Drivers da decisão

- O evento deve refletir o estado do pedido no momento da mudança ([09:52] Larissa).
- Evitar linhas inúteis na outbox ([09:34] Bruno).
- Manter o worker simples, sem precisar ler `orders` para montar o envio (derivado de [09:52] Diego).

## Decisão

- O payload é **renderizado na inserção** e gravado como snapshot na outbox, refletindo o estado do pedido no momento em que o status mudou ([09:52] Larissa, [09:52] Diego, [09:52] Bruno).
- O **filtro de eventos por status é aplicado na inserção**: se nenhum webhook do customer quer aquele status, nada é inserido na outbox ([09:33] Marcos, [09:34] Bruno, [09:34] Diego).
- Como a inserção na outbox é feita por `publishWebhookEvent` dentro da transação de `changeStatus` ([09:41] Bruno), filtro e renderização acontecem nesse mesmo ponto (derivado de [09:33] Marcos e [09:41] Bruno).

## Alternativas Consideradas

### Alternativa 1: guardar só o `order_id` e renderizar no envio (descartada)
- A outbox guardaria apenas a referência ao pedido, e o worker montaria o payload na hora do envio ([09:51] Bruno).
- Motivo do descarte: se o pedido mudar depois, o evento deixaria de refletir o estado de quando o status mudou; "senão tem caso esquisito" ([09:52] Larissa).

### Alternativa 2: filtrar na hora do envio (descartada)
- Inserir todos os eventos e o worker descartaria os que nenhum endpoint quer ([09:34] Diego).
- Motivo do descarte: gasta linhas na tabela à toa; filtrando na inserção, "se nenhum webhook do customer quer aquele status, nem insere" ([09:34] Bruno), com concordância de [09:34] Diego.

## Consequências

### Positivas
- O cliente recebe o retrato fiel do pedido no instante da mudança, mesmo em reentregas horas depois ([09:52] Larissa).
- A outbox só contém eventos que algum endpoint quer, e o worker não processa linhas descartáveis ([09:34] Bruno).
- O worker não consulta `orders` para montar o envio, o que reduz acoplamento com o módulo de Pedidos (derivado de [09:52] Diego).

### Negativas
- A transação de `changeStatus`, já pesada ([09:04] Bruno), passa a ler a configuração de webhooks do customer e a montar o payload antes do commit (derivado de [09:34] Bruno).
- Mudanças posteriores no filtro ou no cadastro não afetam eventos já enfileirados, e um webhook cadastrado depois não recebe eventos anteriores (derivado).
- O payload fica duplicado em cada linha da outbox, o que aumenta o volume da tabela (derivado de [09:52] Larissa).
- Ponto em aberto: a reunião não definiu se, quando o customer tem mais de um endpoint interessado ([09:44] Sofia), a outbox recebe uma linha por endpoint ou uma por evento com distribuição no worker; registrado como questão em aberto no RFC.

### Trade-off
Ganhamos fidelidade do evento ao momento da mudança e uma outbox sem linhas inúteis, ao custo de mais trabalho dentro da transação de `changeStatus` e de eventos que não refletem alterações posteriores de configuração.

## Referências

- Transcrição: [09:33] Bruno, [09:33] Marcos, [09:34] Bruno, [09:34] Diego, [09:43] Diego, [09:51] Bruno, [09:52] Larissa, [09:52] Diego, [09:52] Bruno
- Código: `src/modules/orders/order.service.ts` (`changeStatus`), `src/modules/orders/order.status.ts` (transições), `prisma/schema.prisma` (`enum OrderStatus`, campos `orderNumber`, `customerId`, `totalCents`)

## ADRs relacionados

- Depende de: [ADR-001](ADR-001-outbox-transacional-no-mysql.md)
- Relacionado a: [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) (`event_id` no payload)
