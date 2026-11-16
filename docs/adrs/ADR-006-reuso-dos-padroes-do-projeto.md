# ADR-006: Reuso dos padrões existentes do projeto no módulo de webhooks

## Status

Aceito (2026-11-16). Decidido na reunião técnica de webhooks por: Bruno (Engenheiro Pleno, Pedidos), Larissa (Tech Lead), Diego (Engenheiro Sênior, Plataforma), Sofia (Engenheira de Segurança).

## Contexto

A codebase tem um padrão claro: cada domínio é um módulo próprio com controller, service, repository, routes e schemas ([09:27] Bruno). Os erros derivam de `AppError` (`src/shared/errors/app-error.ts`), com classes específicas e códigos como `INSUFFICIENT_STOCK` e `INVALID_STATUS_TRANSITION` ([09:28] Bruno). O middleware de erro centralizado (`src/middlewares/error.middleware.ts`) já trata AppError, Zod e Prisma ([09:29] Bruno). O logger é Pino, presente em todo o projeto ([09:29] Bruno).

A autorização usa `authenticate` e `requireRole` em `src/middlewares/auth.middleware.ts`, com roles `ADMIN` e `OPERATOR`. A reunião precisou decidir se o webhook segue esse caminho ou introduz estrutura própria, e onde fica o código do worker ([09:28] Diego).

O time é pequeno ([09:07] Diego) e a estimativa total é de três sprints ([09:46] Larissa); cada ferramenta nova seria custo de aprendizado e de manutenção (derivado).

## Drivers da decisão

- Consistência com o resto da codebase ([09:27] Bruno, [09:30] Larissa).
- Nenhuma dependência nova de log ou erro ([09:29] Bruno).
- Erros novos tratados pelo middleware existente sem alteração ([09:29] Bruno).
- Controle de acesso com o mecanismo já existente ([09:36] Larissa).

## Decisão

"Reuso máximo do que já existe" ([09:30] Larissa):

- **Módulo** `src/modules/webhooks/` (novo, a criar) com controller, service, repository, routes e schemas, igual aos demais ([09:27] Bruno, [09:28] Diego).
- **Worker**: entry-point separada e lógica de processamento em arquivo do módulo, conforme o [ADR-002](ADR-002-worker-separado-com-polling.md) ([09:28] Bruno).
- **Erros**: classes derivadas de `AppError`, com **prefixo `WEBHOOK_`** em todos os códigos do módulo, por exemplo `WEBHOOK_NOT_FOUND`, `WEBHOOK_INVALID_URL` e `WEBHOOK_SECRET_REQUIRED` ([09:28] Bruno, [09:29] Larissa).
- **Tratamento de erro**: o error middleware centralizado, sem mudança ([09:29] Bruno).
- **Log**: Pino, sem logger novo ([09:29] Bruno).
- **Validação**: schemas Zod no padrão do projeto, incluindo a recusa de URL não https ([09:23] Sofia, [09:30] Larissa).
- **Autorização**: CRUD de configuração com qualquer role autenticada ([09:37] Sofia); replay da dead letter com `requireRole` para ADMIN ([09:36] Larissa).
- **Identificadores**: UUID, como em todo o projeto ([09:51] Larissa).
- **Integração com Pedidos**: função `publishWebhookEvent` recebendo o tx da transação, sem injetar repository ([09:41] Diego), conforme o [ADR-001](ADR-001-outbox-transacional-no-mysql.md).

## Alternativas Consideradas

### Alternativa 1: id auto incremental na outbox (descartada)
- Usar chave numérica sequencial nas tabelas novas ([09:51] Diego).
- Motivo do descarte: "UUID, segue o padrão do resto do projeto. Tudo é uuid" ([09:51] Larissa).

### Alternativa 2: introduzir ferramentas próprias de log ou erro para o módulo (descartada) (derivado)
- Adotar uma biblioteca ou formato de log e de erro específico para webhooks.
- Motivo do descarte: o Pino "já tá no projeto inteiro. Não vamos botar nada novo", e o middleware existente já pega os erros novos ([09:29] Bruno). Ninguém propôs essa opção na reunião; ela é a negação direta da fala de Bruno.

## Consequências

### Positivas
- Quem conhece um módulo do projeto entende o de webhooks sem curva de aprendizado ([09:27] Bruno).
- Respostas de erro da API mantêm o mesmo formato e os mesmos códigos HTTP, sem mudança no middleware ([09:29] Bruno).
- O prefixo `WEBHOOK_` deixa claro, em log e na resposta, de onde veio o erro ([09:29] Larissa).
- Nenhuma dependência nova obrigatória (derivado de [09:29] Bruno).

### Negativas
- O módulo herda as limitações dos padrões atuais: não há métrica nem tracing no projeto hoje, só logs; as dependências de `package.json` não incluem nenhuma biblioteca de métricas ou tracing (derivado).
- O CRUD de configuração fica aberto a qualquer role autenticada, mais permissivo do que o ideal ([09:37] Sofia).
- Ponto em aberto: endurecer as roles do CRUD ficou para depois ([09:37] Sofia), e o significado exato de `WEBHOOK_SECRET_REQUIRED` foi só citado ([09:28] Bruno); ver [RFC-Q-05](../RFC.md#questões-em-aberto) e [RFC-Q-11](../RFC.md#questões-em-aberto).

### Trade-off
Ganhamos consistência, menor custo de manutenção e entrega mais rápida, ao custo de herdar as limitações dos padrões atuais, como a ausência de métricas e o modelo simples de roles.

## Referências

- Transcrição: [09:27] Bruno, [09:28] Bruno, [09:28] Diego, [09:29] Bruno, [09:29] Larissa, [09:30] Larissa, [09:36] Larissa, [09:37] Sofia, [09:41] Diego, [09:51] Diego, [09:51] Larissa
- Código: `src/shared/errors/app-error.ts` (`AppError`), `src/middlewares/error.middleware.ts` (`errorMiddleware`), `src/middlewares/auth.middleware.ts` (`authenticate`, `requireRole`), `package.json` (dependências `pino`, `zod`, `uuid`), `src/modules/webhooks/` (novo, a criar)

## ADRs relacionados

- Relacionado a: [ADR-001](ADR-001-outbox-transacional-no-mysql.md) (`publishWebhookEvent`)
- Relacionado a: [ADR-002](ADR-002-worker-separado-com-polling.md) (local do worker)
- Relacionado a: [ADR-003](ADR-003-retry-com-backoff-e-dead-letter.md) (`requireRole` no replay)
