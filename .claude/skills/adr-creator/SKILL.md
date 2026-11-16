---
name: adr-creator
description: "Gera um ADR (formato MADR em PT-BR) para UMA decisão arquitetural fechada na reunião de webhooks, em docs/adrs/ADR-NNN-titulo-em-kebab-case.md, com as seções Status, Contexto, Decisão, Alternativas Consideradas e Consequências (positivas, negativas, trade-off), rastreadas a [hh:mm] Nome e ao código. Uso: /adr-creator <NNN> <tema> ou /adr-creator all."
disable-model-invocation: true
---

# ADR Creator

Registra **uma decisão fechada por arquivo**. A base é o `adr-generator` do plugin `adrs-management` do curso (devfullcycle/claude-mkt-place), adaptada em três pontos:

- **A fonte é a reunião**, não o histórico do git.
- **Os headings estão em PT** e seguem o que o desafio exige.
- **Numeração e caminho são finais**: sem `ADR-XXX` e sem pasta `generated/`.

Carregue e siga `.claude/rules/design-docs.md`. Leia `analysis/inventario-transcricao.md`; se ele não existir, pare e peça `/transcript-inventory`.

## Entrada

- `/adr-creator <NNN> <tema>`: gera um ADR.
- `/adr-creator all`: gera todos os ADRs do mapa abaixo, um por vez, na ordem.

## Mapa de ADRs do pacote

| NNN | Arquivo | Decisão |
|---|---|---|
| 001 | `ADR-001-outbox-transacional-no-mysql.md` | Padrão outbox no MySQL na mesma transação do `changeStatus` |
| 002 | `ADR-002-worker-separado-com-polling.md` | Worker em processo separado, polling de 2s, single-worker |
| 003 | `ADR-003-retry-com-backoff-e-dead-letter.md` | 5 tentativas, backoff 1m/5m/30m/2h/12h, DLQ em tabela própria, replay ADMIN |
| 004 | `ADR-004-hmac-sha256-com-secret-por-endpoint.md` | HMAC-SHA256, secret por endpoint, rotação com grace de 24h |
| 005 | `ADR-005-entrega-at-least-once-com-x-event-id.md` | At-least-once com X-Event-Id para dedup no cliente |
| 006 | `ADR-006-reuso-dos-padroes-do-projeto.md` | Reuso de módulo, AppError, WEBHOOK_, Pino, error middleware, Zod, requireRole (ancorado em código) |
| 007 | `ADR-007-snapshot-e-filtro-na-insercao.md` | Payload renderizado e filtro de eventos no momento da inserção na outbox |

## Regras de conteúdo (do adr-generator do curso)

- **Alvo:** 80 a 200 linhas. Foque na decisão e no porquê, não na implementação.
- **Arquivos:** no máximo 5 referências, todas existentes ou rotuladas "(novo, a criar)".
- **Proibido:**
  - trechos de código e hierarquia de classes;
  - sugestões de futuro ("considerar X");
  - marcadores `[NEEDS INPUT]`.
  
  Lacunas reais viram uma linha "Ponto em aberto" dentro de Consequências, com timestamp, e apontam para o RFC.
- **Alternativas Consideradas:** pelo menos 1 real, discutida na reunião (prefira as rejeitadas com motivo explícito). Cada alternativa traz o motivo do descarte com `[hh:mm] Nome`. Uma alternativa "plausível" não discutida só entra se rotulada (derivado).
- **Consequências:** sempre com `### Positivas`, `### Negativas` e `### Trade-off`, este último em uma frase explícita "ganhamos X ao custo de Y".
- **Status:** `Aceito`. Data: data de redação. Decisores: os participantes que fecharam a decisão.

## Modelo de saída (exatamente estes headings)

```markdown
# ADR-NNN: Título curto da decisão

## Status

Aceito (AAAA-MM-DD). Decidido na reunião técnica de webhooks por: Nome (papel), Nome (papel).

## Contexto

Problema e forças em jogo, 2 a 4 parágrafos. Cada afirmação factual termina com a fonte ([hh:mm] Nome) ou o caminho do arquivo.

## Drivers da decisão

- Driver 1 ([hh:mm] Nome)
- Driver 2 (`caminho/do/arquivo.ts`)

## Decisão

Enunciado direto do que foi decidido, com os valores fechados na reunião ([hh:mm] Nome).

## Alternativas Consideradas

### Alternativa 1: nome (descartada)
- Descrição curta.
- Motivo do descarte: ... ([hh:mm] Nome).

### Alternativa 2: nome (descartada)
...

## Consequências

### Positivas
- ...

### Negativas
- ...

### Trade-off
Ganhamos X ao custo de Y.

## Referências

- Transcrição: [hh:mm] Nome, [hh:mm] Nome
- Código: `caminho/existente.ts` (símbolo)

## ADRs relacionados

- Depende de: [ADR-NNN](ADR-NNN-....md)
- Relacionado a: [ADR-NNN](ADR-NNN-....md)
```

## Após gerar

1. Atualize `docs/adrs/README.md` como índice. Ele deve conter:
   - a convenção `ADR-NNN-titulo-em-kebab-case.md` (substitui a antiga `0001-...`);
   - uma tabela `| ADR | Título | Status | Decisão em uma linha |` com links.
2. Confira que os links "ADRs relacionados" resolvem.
3. Rode `python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only adrs`.
4. Sugira `/design-docs-review adrs`.
