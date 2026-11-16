# ADR-001: Outbox transacional no MySQL para eventos de webhook

## Status

Aceito (2026-11-16). Decidido na reunião técnica de webhooks por: Diego (Engenheiro Sênior, Plataforma), Larissa (Tech Lead), Bruno (Engenheiro Pleno, Pedidos).

## Contexto

Três clientes B2B pediram para ser notificados quando o status dos seus pedidos muda; hoje eles fazem polling em `GET /orders`, o que deixa a integração lenta e cara ([09:00] Marcos). A notificação é só de saída, da plataforma para o cliente ([09:02] Marcos, [09:03] Sofia), e qualquer latência abaixo de 10 segundos é percebida como tempo real ([09:02] Marcos).

O ponto de origem do evento é `OrderService.changeStatus`, que já executa uma transação pesada: atualiza `orders`, insere em `order_status_history` e debita ou repõe estoque, tudo dentro de um único `$transaction` do Prisma ([09:04] Bruno, `src/modules/orders/order.service.ts`). Acrescentar uma chamada HTTP nesse trecho faria qualquer cliente lento travar a mudança de status de outros pedidos ([09:04] Bruno). Além disso, se o cliente estiver fora do ar, não existe resposta aceitável: desfazer a mudança de status por causa de um terceiro não é opção ([09:04] Bruno).

A outra força é a consistência. O time não aceita o caso em que o status muda e o evento não sai ([09:40] Bruno, [09:41] Diego), nem evento registrado de uma mudança que deu rollback ([09:06] Diego). O time é pequeno e não quer operar infraestrutura nova só para isso ([09:07] Diego).

## Drivers da decisão

- Não acoplar a latência e a disponibilidade do cliente à transação de mudança de status ([09:04] Bruno, [09:06] Diego).
- Atomicidade: evento registrado se e somente se a mudança de status commitar ([09:06] Diego, [09:40] Bruno).
- Nenhuma infraestrutura nova para um time pequeno ([09:07] Larissa, [09:07] Diego).
- Integração mínima no `changeStatus` existente, sem injetar dependências pesadas no `OrderService` ([09:41] Bruno, [09:41] Diego).

## Decisão

Adotamos o padrão outbox no MySQL já existente ([09:08] Larissa):

- Ao mudar o status de um pedido, uma linha com o evento é inserida na tabela `webhook_outbox` **dentro da mesma transação** que atualiza `orders` e `order_status_history` ([09:06] Diego, [09:40] Bruno).
- Se a inserção na outbox falhar, a transação inteira faz rollback; se a transação principal fizer rollback, o evento desaparece junto ([09:06] Diego, [09:40] Bruno).
- O `changeStatus` chama uma função `publishWebhookEvent(tx, order, fromStatus, toStatus)` que recebe o client da transação corrente ([09:41] Bruno, [09:41] Diego).
- A entrega HTTP fica fora da transação, a cargo de um worker separado que lê a outbox ([09:06] Diego), detalhado no [ADR-002](ADR-002-worker-separado-com-polling.md).
- A outbox tem estados pendente, processando, falhou e entregue, com índice em status e em `created_at` ([09:08] Diego).

## Alternativas Consideradas

### Alternativa 1: disparo HTTP síncrono no service de orders (descartada)
- Chamar o endpoint do cliente dentro do `changeStatus`, antes do commit.
- Motivo do descarte: a transação já é pesada e um cliente lento travaria a mudança de status de outros pedidos; com o cliente fora do ar não há como reagir, porque desfazer o status não é aceitável ([09:04] Bruno). "Síncrono está fora de questão" ([09:06] Diego).

### Alternativa 2: fila externa com Redis Streams (descartada)
- Publicar o evento em Redis Streams ou estrutura equivalente e consumir de lá.
- Motivo do descarte: exige subir mais infraestrutura ([09:07] Larissa); "subir Redis Cluster pra isso é overengineering" para um time pequeno, e a outbox no MySQL existente resolve ([09:07] Diego).

### Alternativa 3: registrar o evento fora da transação (descartada)
- Inserir na outbox depois do commit da mudança de status.
- Motivo do descarte: "se ficar fora da transação, perde a garantia toda" ([09:41] Diego); não pode existir status alterado sem evento ([09:40] Bruno).

### Alternativa 4: injetar o repository de webhook no OrderService (descartada)
- Passar um repository completo do módulo de webhooks para o `OrderService`.
- Motivo do descarte: uma função que recebe o tx resolve sem injetar o repository inteiro ([09:41] Bruno, [09:41] Diego).

## Consequências

### Positivas
- Consistência entre status e evento garantida pelo próprio banco, sem coordenação distribuída ([09:06] Diego).
- A transação de status não depende da rede nem da disponibilidade do cliente ([09:04] Bruno).
- Zero infraestrutura nova: mesmo MySQL e mesma stack ([09:07] Diego).
- O ponto de integração no `changeStatus` é uma única chamada com o tx corrente ([09:41] Bruno).

### Negativas
- Uma falha ao inserir na outbox faz rollback da mudança de status ([09:40] Bruno); com isso, a feature de webhook passa a poder bloquear uma operação central de Pedidos (derivado).
- A transação de `changeStatus`, já pesada ([09:04] Bruno), ganha mais uma escrita (e a leitura do filtro do [ADR-007](ADR-007-snapshot-e-filtro-na-insercao.md)).
- A entrega deixa de ser imediata: passa a depender do ciclo do worker (ver [ADR-002](ADR-002-worker-separado-com-polling.md)).
- A tabela cresce continuamente; o arquivamento das linhas entregues ficou fora do escopo desta feature ([09:08] Diego).
- Ponto em aberto: retenção e arquivamento da outbox ("30 dias ou assim", [09:08] Diego) não têm prazo nem dono; registrado como questão em aberto no RFC.

### Trade-off
Ganhamos consistência atômica entre mudança de status e evento sem infraestrutura nova, ao custo de acoplar a escrita do evento à transação crítica de Pedidos e de aceitar entrega assíncrona.

## Referências

- Transcrição: [09:04] Bruno, [09:06] Diego, [09:07] Larissa, [09:07] Diego, [09:08] Diego, [09:08] Larissa, [09:40] Bruno, [09:41] Bruno, [09:41] Diego
- Código: `src/modules/orders/order.service.ts` (`OrderService.changeStatus`, `type TxClient`), `prisma/schema.prisma` (models `Order` e `OrderStatusHistory`)

## ADRs relacionados

- Relacionado a: [ADR-002](ADR-002-worker-separado-com-polling.md) (consumo da outbox)
- Relacionado a: [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) (id do evento gerado na inserção)
- Relacionado a: [ADR-007](ADR-007-snapshot-e-filtro-na-insercao.md) (o que é gravado na inserção)
