# ADR-002: Worker em processo separado com polling de 2 segundos e single-worker

## Status

Aceito (2026-11-16). Decidido na reunião técnica de webhooks por: Diego (Engenheiro Sênior, Plataforma), Larissa (Tech Lead), Bruno (Engenheiro Pleno, Pedidos), Marcos (Product Manager).

## Contexto

Com a outbox do [ADR-001](ADR-001-outbox-transacional-no-mysql.md), algum componente precisa ler os eventos pendentes e fazer as chamadas HTTP aos clientes ([09:06] Diego). O requisito de produto é latência abaixo de 10 segundos ([09:02] Marcos).

O banco é MySQL, que não tem um mecanismo nativo de notificação a processos externos como o NOTIFY/LISTEN do Postgres; uma trigger só executa SQL e não acorda um processo ([09:09] Diego). Reagir a cada inserção exigiria improvisos como escrever em arquivo ou chamar um endpoint ([09:09] Diego).

A API roda hoje como um único processo Node, com bootstrap e shutdown gracioso em `src/server.ts`, e um PrismaClient criado por `createPrismaClient()` em `src/config/database.ts`. Um worker acoplado a esse processo morreria a cada reinício da API ([09:11] Diego).

Há ainda a questão de ordem: se um pedido muda de PAID para PROCESSING e depois para SHIPPED em sequência rápida, o cliente precisa receber na ordem certa ([09:12] Larissa). Os clientes, porém, nunca pediram ordem global, só querem saber se cada pedido mudou ([09:14] Marcos).

## Drivers da decisão

- Latência abaixo de 10 segundos ([09:02] Marcos).
- MySQL sem listener nativo para eventos ([09:09] Diego).
- Ciclo de vida do worker independente do ciclo da API ([09:11] Diego).
- Reaproveitar o mesmo banco e a mesma stack ([09:11] Diego, [09:30] Bruno).
- Ordem por pedido suficiente para o cliente ([09:14] Marcos).

## Decisão

- O worker lê a outbox por **polling em loop a cada 2 segundos**, buscando os eventos pendentes mais antigos em batch pequeno, processando e marcando ([09:09] Diego, [09:08] Diego). A latência adicional de até 2 segundos no pior caso foi aceita ([09:10] Marcos, [09:10] Larissa).
- O worker roda em **processo separado** da API, com a entry-point `src/worker.ts` (novo, a criar) e o script `npm run worker` ([09:11] Diego, [09:11] Larissa).
- A lógica de processamento fica dentro do módulo, em `src/modules/webhooks/webhook.worker.ts` ou `webhook.processor.ts` (novo, a criar); `src/worker.ts` é só a entrada ([09:28] Bruno, [09:28] Diego).
- O worker usa o mesmo banco e a mesma `DATABASE_URL`, com **instância própria de PrismaClient**, porque o PrismaClient é por processo ([09:11] Diego, [09:30] Bruno).
- **Single-worker**: um único worker processa em ordem de `created_at`. A ordem é garantida apenas por `order_id` e apenas enquanto houver um único worker; isso é uma limitação conhecida e documentada ([09:12] Diego, [09:13] Larissa).
- O tamanho do batch não foi fixado na reunião ("batch pequeno", [09:08] Diego) e entra no FDD como configuração com default (derivado).

## Alternativas Consideradas

### Alternativa 1: trigger do banco ou NOTIFY/LISTEN (descartada)
- Usar mecanismo do banco para acordar o worker a cada inserção, em vez de polling ([09:09] Bruno).
- Motivo do descarte: o MySQL não tem listener nativo; a trigger só executa SQL e avisar o worker exigiria improviso; o polling de 2 segundos já atende o requisito de menos de 10 segundos ([09:09] Diego).

### Alternativa 2: worker dentro do processo da API (descartada)
- Rodar o loop de entrega na mesma instância que serve as rotas HTTP.
- Motivo do descarte: se a API reinicia, perde o worker ([09:11] Diego).

### Alternativa 3: compartilhar o PrismaClient da API (descartada)
- O worker reutilizaria o mesmo client da API ([09:11] Bruno).
- Motivo do descarte: o PrismaClient é por processo; o worker abre instância nova com a mesma `DATABASE_URL` ([09:30] Bruno).

### Alternativa 4: múltiplos workers em paralelo com ordem global (descartada nesta fase)
- Escalar horizontalmente o consumo da outbox.
- Motivo do descarte: com vários workers a garantia de ordem se perde ([09:12] Diego); os clientes não pedem ordem global ([09:14] Marcos); particionar por `order_id` ou usar lock pessimista é "problema do futuro" ([09:13] Diego).

## Consequências

### Positivas
- Atende o requisito de latência com folga: pior caso de 2 segundos de espera antes do processamento ([09:09] Diego, [09:10] Larissa).
- Reinícios e deploys da API não interrompem as entregas, e vice-versa ([09:11] Diego).
- Nenhuma tecnologia nova: mesmo banco, mesma stack, mesmo padrão de bootstrap ([09:11] Diego).
- Com um único consumidor, a ordem dos eventos de um mesmo pedido é preservada sem lock ([09:12] Diego).

### Negativas
- Há um processo a mais para implantar, monitorar e manter no ar (derivado de [09:11] Diego e [09:11] Larissa).
- O polling consulta o banco a cada 2 segundos mesmo sem eventos pendentes (derivado de [09:09] Diego).
- O throughput fica limitado a um worker; um cliente lento (até o timeout de 10 segundos, [09:42] Diego) atrasa a fila inteira (derivado).
- Se o único worker parar, nada é entregue até ele voltar; os eventos ficam pendentes na outbox e não se perdem (derivado de [09:06] Diego).
- Ponto em aberto: escala para múltiplos workers (particionar por `order_id` ou lock pessimista, [09:13] Diego); ver [RFC-Q-03](../RFC.md#questões-em-aberto).

### Trade-off
Ganhamos simplicidade operacional, isolamento do ciclo de vida da API e ordem por pedido, ao custo de 2 segundos de latência mínima, um processo extra e throughput limitado a um único worker.

## Referências

- Transcrição: [09:02] Marcos, [09:08] Diego, [09:09] Bruno, [09:09] Diego, [09:10] Larissa, [09:11] Diego, [09:11] Larissa, [09:12] Diego, [09:13] Diego, [09:13] Larissa, [09:14] Marcos, [09:28] Bruno, [09:30] Bruno
- Código: `src/server.ts` (`bootstrap`, `shutdown`), `src/config/database.ts` (`createPrismaClient`), `package.json` (scripts), `src/worker.ts` (novo, a criar)

## ADRs relacionados

- Depende de: [ADR-001](ADR-001-outbox-transacional-no-mysql.md)
- Relacionado a: [ADR-003](ADR-003-retry-com-backoff-e-dead-letter.md) (o que o worker faz quando a entrega falha)
- Relacionado a: [ADR-006](ADR-006-reuso-dos-padroes-do-projeto.md) (onde o código do worker fica)
