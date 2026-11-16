# ADR-005: Entrega at-least-once com X-Event-Id para deduplicação no cliente

## Status

Aceito (2026-11-16). Decidido na reunião técnica de webhooks por: Diego (Engenheiro Sênior, Plataforma), Larissa (Tech Lead), Marcos (Product Manager).

## Contexto

A arquitetura de outbox ([ADR-001](ADR-001-outbox-transacional-no-mysql.md)), worker ([ADR-002](ADR-002-worker-separado-com-polling.md)) e retry ([ADR-003](ADR-003-retry-com-backoff-e-dead-letter.md)) torna possível que o cliente receba o mesmo evento mais de uma vez ([09:24] Diego). Isso acontece, por exemplo, quando o cliente processa a chamada mas responde depois dos 10 segundos de timeout, que contam como falha e geram retry ([09:42] Diego), ou quando o worker cai entre o envio HTTP e a marcação do evento como entregue (derivado).

O cliente precisa de um jeito de reconhecer a repetição ([09:25] Bruno). A Sofia apontou que isso transfere responsabilidade para o cliente ([09:25] Sofia). O Diego lembrou que é o padrão adotado por Stripe e GitHub e que garantir entrega exatamente uma vez exigiria coordenação dos dois lados ([09:25] Diego).

O projeto já usa UUID como identificador em todos os models (`@default(uuid())` em `prisma/schema.prisma`) e tem a dependência `uuid` em `package.json`.

## Drivers da decisão

- Simplicidade: nenhuma coordenação com o sistema do cliente ([09:25] Diego).
- Padrão de mercado conhecido pelos integradores ([09:25] Diego).
- Identificador estável por evento, gerado do lado da plataforma ([09:25] Diego).
- Comunicação clara ao cliente sobre a responsabilidade de deduplicar ([09:26] Marcos).

## Decisão

- A garantia de entrega é **at-least-once**: o cliente pode receber o mesmo evento mais de uma vez e deve estar preparado ([09:24] Diego, [09:26] Larissa).
- Todo envio leva o header **`X-Event-Id`** com um **UUID gerado quando o evento entra na outbox**, único por evento; o cliente deduplica por esse valor ([09:25] Diego, [09:26] Larissa).
- O mesmo valor aparece no payload como `event_id` ([09:43] Diego).
- O envio leva também `X-Signature` ([ADR-004](ADR-004-hmac-sha256-com-secret-por-endpoint.md)), `X-Timestamp` com o horário do envio, `X-Webhook-Id` com o id do endpoint e `Content-Type: application/json` ([09:44] Diego, [09:44] Sofia, [09:45] Diego).
- O comportamento é documentado em destaque no portal de desenvolvedor ([09:26] Marcos).

## Alternativas Consideradas

### Alternativa 1: entrega exactly-once (descartada)
- Garantir que cada evento seja processado uma única vez pelo cliente.
- Motivo do descarte: exigiria coordenação dos dois lados e fica muito mais complexo; at-least-once com event_id resolve a grande maioria dos casos ([09:25] Diego).

### Alternativa 2: at-least-once sem identificador de evento (descartada) (derivado)
- Reentregar sem dar ao cliente um meio de reconhecer duplicatas.
- Motivo do descarte: o cliente não teria como diferenciar um reenvio de um evento novo, que é exatamente a pergunta feita em [09:25] Bruno e respondida com o `X-Event-Id` ([09:25] Diego).

## Consequências

### Positivas
- A plataforma não precisa de protocolo de confirmação nem de estado compartilhado com o cliente ([09:25] Diego).
- O retry ([ADR-003](ADR-003-retry-com-backoff-e-dead-letter.md)) pode reenviar sem medo, porque a duplicata é tratável pelo cliente ([09:24] Diego).
- Modelo familiar para quem já integra com Stripe ou GitHub ([09:25] Diego).
- O id gerado na inserção da outbox é estável entre todas as tentativas do mesmo evento ([09:25] Diego).

### Negativas
- A responsabilidade de deduplicar fica com o cliente; um cliente que ignore o `X-Event-Id` pode processar o mesmo evento duas vezes ([09:25] Sofia).
- A plataforma depende de documentação e comunicação para que os clientes implementem a deduplicação ([09:26] Marcos).
- Ponto em aberto: a reunião não definiu se o replay da dead letter ([09:18] Diego) preserva o `X-Event-Id` original, nem se um mesmo evento enviado a vários endpoints do customer compartilha o id ([09:44] Sofia); registrado como questão em aberto no RFC.

### Trade-off
Ganhamos uma entrega simples, resiliente e alinhada ao mercado, ao custo de transferir ao cliente a responsabilidade de deduplicar pelo `X-Event-Id`.

## Referências

- Transcrição: [09:24] Diego, [09:25] Bruno, [09:25] Diego, [09:25] Sofia, [09:26] Marcos, [09:26] Larissa, [09:42] Diego, [09:43] Diego, [09:44] Diego, [09:44] Sofia, [09:45] Diego
- Código: `prisma/schema.prisma` (`@default(uuid())`), `package.json` (dependência `uuid`)

## ADRs relacionados

- Depende de: [ADR-001](ADR-001-outbox-transacional-no-mysql.md) (id gerado na inserção)
- Relacionado a: [ADR-003](ADR-003-retry-com-backoff-e-dead-letter.md) (origem das duplicatas)
- Relacionado a: [ADR-004](ADR-004-hmac-sha256-com-secret-por-endpoint.md) (demais headers do envio)
