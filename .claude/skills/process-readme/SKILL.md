---
name: process-readme
description: "Substitui o README.md (enunciado) pela documentação do processo de produção dos design docs: sobre o desafio, ferramentas de IA, workflow, prompts customizados reais em blocos de código, iterações e ajustes reais (lidos do log de EXECUCAO.md) com o número de iterações principais, e como navegar a entrega. Use por último, quando o pacote estiver completo."
disable-model-invocation: true
---

# Process README

Carregue e siga `.claude/rules/design-docs.md`. O README conta **a jornada real**, e só pode afirmar o que aconteceu.

**Fontes obrigatórias:**
- `../EXECUCAO.md`, o arquivo de controle fora do repo. A tabela "Log de iterações" é a **única** fonte da seção "Iterações e ajustes": não invente iterações nem números.
- `.claude/skills/*/SKILL.md` e `.claude/rules/design-docs.md`: os prompts mostrados vêm literalmente daqui, ou dos prompts de correção registrados no log.
- `git log --oneline feature/design-docs`, para a ordem real de produção.
- A árvore final de `docs/`.

## Regras específicas

- **"Sobre o desafio":** 1 a 2 parágrafos, com palavras próprias e não copiados do enunciado. Link para o enunciado original no repositório base: https://github.com/devfullcycle/mba-ia-desafio-design-docs-com-ia
- **"Ferramentas de IA utilizadas":** lista com o papel de cada uma. Inclui:
  - o Claude Code (modelo usado);
  - as skills do curso usadas como base (`product-manager`, `fdd-creator`, `hld-creator` de devfullcycle/mba-ia-dev-workflow; `adr-generator` do plugin `adrs-management` de devfullcycle/claude-mkt-place);
  - as skills próprias do repo;
  - os subagentes de revisão, se tiverem sido usados.
  
  Diga também o que foi **avaliado e não usado**, e por quê. Exemplo: o pipeline `/adr-map` → `/adr-identify` minera decisões do código e do git, mas aqui a fonte é a reunião.
- **"Workflow adotado":** ordem real (inventário → ADRs → RFC → FDD → PRD → Tracker → README → revisão final) e como a interação com a IA foi organizada:
  - skills com `disable-model-invocation`;
  - regra global;
  - checkpoint humano após o inventário;
  - validador automático;
  - review a cada documento.
  
  Uma tabela `Etapa | Comando | Artefato` ajuda.
- **"Prompts customizados":** pelo menos 2, em blocos ```text, cada um com 1 linha de contexto (onde foi usado e qual problema resolvia). Prefira:
  - o prompt de extração do `/transcript-inventory`;
  - um prompt de correção real do log (ex.: o que pediu para separar códigos de erro citados de derivados).
- **"Iterações e ajustes":** lista numerada com o que a IA gerou errado ou superficial, como foi detectado (review, validador ou leitura humana) e a correção. Termine com a frase "**N iterações principais** até o resultado final", com N contado do log.
- **"Como navegar a entrega":** árvore de arquivos (docs/, docs/adrs/, .claude/, analysis/), ordem de leitura sugerida com links (PRD → RFC → ADRs → FDD → TRACKER) e o comando do validador.

## Modelo de saída (exatamente estes headings)

```markdown
# Design Docs com IA: Sistema de Webhooks de Notificação de Pedidos

> Entrega do desafio do módulo Design Docs com IA. Enunciado original: <link>.

## Sobre o desafio
## Ferramentas de IA utilizadas
## Workflow adotado
## Prompts customizados
## Iterações e ajustes
## Como navegar a entrega
```

## Após gerar

Rode `python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only readme`.
