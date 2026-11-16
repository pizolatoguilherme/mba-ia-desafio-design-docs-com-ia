# ADR-004: Assinatura HMAC-SHA256 com secret por endpoint e rotação com grace period de 24h

## Status

Aceito (2026-11-16). Decidido na reunião técnica de webhooks por: Sofia (Engenheira de Segurança), Larissa (Tech Lead), Bruno (Engenheiro Pleno, Pedidos), Diego (Engenheiro Sênior, Plataforma).

## Contexto

Os webhooks expõem dados de pedidos a um endpoint fora da infraestrutura da plataforma. O cliente precisa conseguir validar que a requisição veio realmente da plataforma e que ninguém adulterou o payload no caminho ([09:19] Sofia).

A configuração de cada webhook guarda url, secret, `customer_id` e estado ativo ([09:21] Bruno, [09:21] Sofia), e a secret é gerada pela plataforma e devolvida ao cliente na criação ([09:31] Marcos). Secrets vazam na prática: a plataforma já teve cliente que vazou secret em log da própria aplicação ([09:22] Diego). Um vazamento não pode comprometer todos os clientes, e o cliente precisa conseguir trocar a secret tendo tempo para migrar os sistemas dele ([09:21] Sofia).

O transporte também é tratado: a URL tem de ser https, validada no schema Zod; isso foi classificado como validação, não como decisão arquitetural ([09:23] Sofia). O projeto já usa Pino com `redact` de campos sensíveis em `src/shared/logger/index.ts`.

## Drivers da decisão

- Autenticidade e integridade verificáveis pelo cliente ([09:19] Sofia).
- Padrão de mercado, com biblioteca disponível para qualquer cliente ([09:20] Sofia).
- Raio de impacto de um vazamento limitado a um endpoint ([09:21] Sofia).
- Rotação sem janela de falha para o cliente ([09:21] Sofia).

## Decisão

- Cada envio é assinado com **HMAC-SHA256 sobre o corpo do request**, e a assinatura vai no header **`X-Signature`** ([09:20] Sofia, [09:20] Bruno, [09:22] Sofia).
- A **secret é única por endpoint** de webhook, nunca global da plataforma ([09:21] Sofia), **gerada pela plataforma e devolvida na criação** ([09:31] Marcos).
- A secret é **rotacionável via API**: ao rotacionar, a antiga continua válida por **24 horas** em paralelo (grace period) e depois deixa de valer ([09:21] Sofia, [09:22] Sofia).
- A implementação de HMAC e de geração de secret passa por revisão de segurança da Sofia, com pelo menos dois dias úteis reservados antes do deploy ([09:46] Sofia, [09:49] Sofia).

## Alternativas Consideradas

### Alternativa 1: secret global da plataforma (descartada)
- Uma única secret compartilhada por todos os endpoints de todos os clientes.
- Motivo do descarte: "se vaza uma, vaza tudo" ([09:21] Sofia).

### Alternativa 2: rotação imediata, sem período de convivência (descartada) (derivado)
- A secret antiga deixaria de valer no momento da rotação.
- Motivo do descarte: o cliente precisa de tempo para migrar os sistemas dele, por isso a antiga fica válida por 24 horas ([09:21] Sofia). A alternativa não foi verbalizada como opção na reunião; é a negação direta da justificativa.

## Consequências

### Positivas
- O cliente verifica origem e integridade com biblioteca padrão de mercado ([09:20] Sofia).
- Um vazamento compromete um único endpoint, e o cliente pode rotacionar sozinho pela API ([09:21] Sofia).
- A rotação não gera falha de validação durante a migração do cliente ([09:21] Sofia).

### Negativas
- Como o HMAC exige a secret original para assinar, ela precisa ser armazenada de forma recuperável pela plataforma, e não apenas como hash (derivado de [09:20] Sofia).
- A secret passa a ser dado sensível em banco, em respostas da API e potencialmente em logs; o `redact` do logger precisa incluí-la (derivado de [09:22] Diego).
- Durante as 24 horas de grace há duas secrets válidas por endpoint, o que adiciona estado e lógica à configuração (derivado de [09:21] Sofia).
- A entrega a produção depende de uma revisão de segurança dedicada ([09:46] Sofia).
- Ponto em aberto: a assinatura cobre o corpo ([09:22] Sofia), mas o `X-Timestamp`, pensado para o cliente detectar replay attack ([09:44] Diego), não foi incluído explicitamente no conteúdo assinado; também não foi detalhado como a plataforma assina durante o grace period. Ambos seguem para a revisão de segurança ([09:46] Sofia) e estão registrados como questão em aberto no RFC.

### Trade-off
Ganhamos autenticidade, integridade e isolamento de vazamentos por endpoint com um padrão que o cliente já conhece, ao custo de armazenar secrets recuperáveis, gerenciar duas secrets válidas durante a rotação e depender de revisão de segurança antes do deploy.

## Referências

- Transcrição: [09:19] Sofia, [09:20] Sofia, [09:20] Bruno, [09:21] Bruno, [09:21] Sofia, [09:22] Diego, [09:22] Sofia, [09:23] Sofia, [09:31] Marcos, [09:44] Diego, [09:46] Sofia
- Código: `src/shared/logger/index.ts` (`redact`), `prisma/schema.prisma` (convenção dos models para a tabela de configuração)

## ADRs relacionados

- Relacionado a: [ADR-005](ADR-005-entrega-at-least-once-com-x-event-id.md) (headers do envio)
- Relacionado a: [ADR-006](ADR-006-reuso-dos-padroes-do-projeto.md) (validação Zod da URL https)
