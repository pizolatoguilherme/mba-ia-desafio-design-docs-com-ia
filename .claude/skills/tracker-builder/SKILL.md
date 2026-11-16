---
name: tracker-builder
description: "Gera docs/TRACKER.md: tabela de rastreabilidade com uma linha por ID encontrado nos design docs (PRD-*, RFC-*, FDD-*, ADR-NNN), no formato ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização, com Fonte TRANSCRICAO ([hh:mm] Nome) ou CODIGO (caminho real). Roda o validador automático dos critérios de aceite em loop até ficar verde."
disable-model-invocation: true
---

# Tracker Builder

Carregue e siga `.claude/rules/design-docs.md`. O tracker é a defesa contra alucinação: **se uma linha não tem Localização válida, o item do documento está errado**. Nesse caso, corrija ou remova o item no documento, não invente a fonte.

## Procedimento

1. Extraia todos os IDs dos documentos com
   `python3 .claude/skills/tracker-builder/scripts/validate_docs.py --list-ids`.
   A saída lista ID, documento e linha.
2. Para cada ID, leia o item no documento e escreva **uma** linha da tabela:
   - **ID:** exatamente como no documento.
   - **Documento:** caminho relativo (`docs/PRD.md`, `docs/adrs/ADR-002-....md`).
   - **Tipo:** um de `Requisito Funcional`, `Requisito Não Funcional`, `Decisão`, `Restrição`, `Trade-off`, `Alternativa Descartada`, `Questão em Aberto`, `Fora de Escopo`, `Métrica`, `Risco`, `Dependência`, `Contrato`, `Erro`, `Fluxo`, `Integração`, `Critério de Aceite`, `Resiliência`, `Observabilidade`, `Objetivo`.
   - **Conteúdo (resumo):** uma linha. Se o item for derivado, termine com `(derivado)`.
   - **Fonte:** `TRANSCRICAO` ou `CODIGO`, nada mais.
   - **Localização:**
     - TRANSCRICAO: `[hh:mm] Nome`. Pode listar até 3, separados por `; `, por exemplo `[09:15] Diego; [09:17] Larissa`.
     - CODIGO: caminho existente, opcionalmente com o símbolo entre parênteses.
3. **Preferência de fonte:** use TRANSCRICAO quando a reunião discutiu o item, mesmo que ele toque o código. Use CODIGO para itens de integração, padrões existentes e lacunas do código. Meta: ≥75% de linhas TRANSCRICAO (o mínimo do desafio é 70%) e ≥5 linhas CODIGO.
4. Itens derivados também entram na tabela principal, com a fonte mais próxima. Depois da tabela, uma seção `## Notas de derivação` lista ID, o que foi derivado e a base rastreável.
5. Se faltar fonte para um ID, **não** preencha. Registre o caso e corrija o documento.
6. Rode o validador completo, corrija e repita até `RESULTADO: OK`. Cada rodada com correções relevantes vira uma linha no log de iterações de `../EXECUCAO.md`.

## Modelo de saída

```markdown
# Tracker de Rastreabilidade

Mapa de cada item dos design docs à sua origem na transcrição (`TRANSCRICAO.md`) ou no código. Gerado por `/tracker-builder` e verificado por `.claude/skills/tracker-builder/scripts/validate_docs.py`.

**Cobertura:** N de M IDs (X%) | **TRANSCRICAO:** a linhas (y%) | **CODIGO:** b linhas

| ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização |
|---|---|---|---|---|---|
| PRD-FR-01 | docs/PRD.md | Requisito Funcional | ... | TRANSCRICAO | [09:31] Marcos |

## Notas de derivação

| ID | O que foi derivado | Base rastreável |
|---|---|---|
```

## Validador

`scripts/validate_docs.py`, em Python stdlib. Rode a partir da raiz do repo:

```bash
python3 .claude/skills/tracker-builder/scripts/validate_docs.py            # tudo
python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only rfc # prd|rfc|fdd|adrs|tracker|readme|paths
python3 .claude/skills/tracker-builder/scripts/validate_docs.py --list-ids
```
