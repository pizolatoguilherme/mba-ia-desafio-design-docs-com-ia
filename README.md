# Design Docs com IA: Sistema de Webhooks de Notificação de Pedidos

> Entrega do desafio do módulo Design Docs com IA. Enunciado original: https://github.com/devfullcycle/mba-ia-desafio-design-docs-com-ia

## Sobre o desafio

O ponto de partida é uma API de gestão de pedidos (OMS) já em produção e a transcrição de uma reunião de cerca de 55 minutos (`TRANSCRICAO.md`). Nessa reunião, tech lead, PM, dois engenheiros e a engenheira de segurança decidiram como construir webhooks que avisam clientes B2B quando o status de um pedido muda. Nada além da conversa foi registrado. O trabalho foi transformar essa conversa, junto com o código existente, em um pacote de design docs que um time consiga usar para começar a implementar.

O pacote tem PRD, RFC, FDD, 7 ADRs e um tracker de rastreabilidade. A restrição que orientou todo o processo: cada afirmação precisa apontar para uma fala da reunião (`[hh:mm] Nome`) ou para um arquivo real do repositório. O que não tem fonte direta aparece marcado como **(derivado)**, e o que a reunião não fechou aparece como questão em aberto, nunca como decisão. A IA produziu o conteúdo; o meu papel foi definir as regras, revisar com ceticismo e decidir nos pontos ambíguos.

## Ferramentas de IA utilizadas

| Ferramenta | Papel |
|---|---|
| **Claude Code** (extensão do VS Code), com o modelo **Claude Opus 5.5** (`claude-opus-5-5`) em todas as etapas | Leitura do código e da transcrição, geração de todos os documentos, revisões e execução do validador |
| Skill `product-manager` (devfullcycle/mba-ia-dev-workflow) | Base do `/prd-creator`: formato de requisito com MoSCoW e critério testável, categorias de NFR |
| Skill `fdd-creator` (devfullcycle/mba-ia-dev-workflow) | Base do `/fdd-creator`: roteiro de seções do FDD |
| Skill `hld-creator` (devfullcycle/mba-ia-dev-workflow) | Base do `/rfc-creator`: componentes, fluxo em alto nível, riscos e ADRs associados |
| Agente `adr-generator` do plugin `adrs-management` (devfullcycle/claude-mkt-place) | Base do `/adr-creator`: formato MADR, alternativas, consequências e trade-off |
| 8 skills próprias em `.claude/skills/` | Uma por etapa do processo (detalhes em [Workflow adotado](#workflow-adotado)) |
| Regra global `.claude/rules/design-docs.md` | Fontes válidas, decisões fechadas, lista negra de escopo, questões em aberto, IDs, fronteira entre documentos e estilo |
| Validador `validate_docs.py` (Python stdlib) | Checagens automáticas de seções, IDs, timestamps, caminhos, cobertura do tracker e integridade do código |

**Avaliado e não usado:**

- **As fases do `adrs-management` anteriores ao `adr-generator`.** Elas identificam "ADRs potenciais" a partir do código e do histórico do git. Aqui as decisões nasceram na reunião e o código ainda não tem nada de webhooks, então a fonte certa é a transcrição. Mantive só o formato do gerador.
- **O modo entrevista do `fdd-creator` e do `hld-creator`.** Os originais fazem uma pergunta por vez ao usuário. Nas versões adaptadas, cada pergunta do roteiro é respondida com a transcrição e o código, e o usuário só é consultado nas ambiguidades reais.
- **A priorização RICE do `product-manager`.** Não há dados de alcance nem de esforço na reunião; usei só MoSCoW, marcado como avaliação do PRD.
- **O `/mermaid-generate` (plugin `diagrams-generator`).** Era opcional na skill do FDD e não foi executado; os diagramas foram revisados na própria review.
- **Subagentes.** O log de execução não registra uso de subagentes; as revisões foram feitas pela skill `/design-docs-review` na sessão principal.

## Workflow adotado

| Etapa | Comando | Artefato | Commit |
|---|---|---|---|
| 1. Regras, skills e validador | n/a | `.claude/rules/`, `.claude/skills/`, `validate_docs.py` | `0eb1f7e` |
| 2. Inventário da transcrição e do código | `/transcript-inventory` | `analysis/inventario-transcricao.md` | `1fde667` |
| 3. ADRs | `/adr-creator all` + `/design-docs-review adrs` | `docs/adrs/ADR-001` a `ADR-007` | `c6db34b` |
| 4. RFC | `/rfc-creator` + `/design-docs-review rfc` | `docs/RFC.md` | `c607ab9`, `948887a` |
| 5. FDD | `/fdd-creator` + `/design-docs-review fdd` | `docs/FDD.md` | `f145e9e` |
| 6. PRD | `/prd-creator` + `/design-docs-review prd` | `docs/PRD.md` | `67851a9` |
| 7. Tracker | `/tracker-builder` | `docs/TRACKER.md` | `c3c5102` |
| 8. README | `/process-readme` | `README.md` | `7f80a9f` |
| 9. Revisão final | `/design-docs-review all` | pacote inteiro | commit da revisão final |

Como a interação com a IA foi organizada:

- **Ordem de baixo para cima.** O inventário vem primeiro e é a única base de verdade. Depois vêm os ADRs (o porquê de cada decisão) e o RFC, que propõe e linka os ADRs. O FDD detalha o RFC. O PRD é gerado por último entre os grandes documentos, consolidando os anteriores e "subindo o nível". O tracker fecha o ciclo.
- **Skills com `disable-model-invocation: true`.** As 8 skills só rodam quando chamadas explicitamente. Assim a IA não pula etapas nem gera um documento antes da hora.
- **Regra global carregada por todas as skills.** Lista o que a reunião decidiu (para não reabrir), o que está em aberto (para não afirmar como decidido), a lista negra de escopo e a fronteira entre documentos.
- **Checkpoint humano depois do inventário e depois do FDD.** No inventário, decidi três pontos que a reunião deixou em aberto. No FDD, aprovei sete escolhas derivadas antes do commit.
- **Validador automático** a cada geração e a cada correção, mais o checklist de review cético em cada documento.
- **Arquivo de controle fora do repositório** (`EXECUCAO.md`), com o painel de etapas e o log de iterações que alimenta a próxima seção.

Um detalhe operacional: na etapa 2, as skills do projeto não carregaram porque o Claude Code foi aberto na pasta acima do clone (elas só carregam com a sessão iniciada no próprio repositório). O roteiro do `/transcript-inventory` foi seguido manualmente, à risca; da etapa 3 em diante, as skills foram chamadas normalmente.

## Prompts customizados

**1. Extração do inventário.** Usado no `/transcript-inventory` para classificar a transcrição. Resolve o principal risco do desafio, que é promover comentário a decisão, e impede que itens fora de escopo virem requisito.

```text
Leia a TRANSCRICAO.md inteira antes de classificar qualquer coisa. Para cada
fala relevante, classifique em UMA categoria:
  D  decisão fechada (alguém propôs e o grupo/condutora fechou: "decidido",
     "anotado", "beleza", "combinado", ou o resumo das [09:48] confirma)
  RF requisito funcional (capacidade que o sistema/cliente precisa ter)
  RNF requisito não funcional (limite, latência, segurança, tamanho, timeout)
  X  descartado (alternativa rejeitada, com o motivo)
  A  adiado / fora de escopo (explicitamente empurrado para depois)
  Q  em aberto (levantado e NÃO decidido)
  C  gancho com o código existente (arquivo, classe, função, padrão citado)
  S  detalhe técnico secundário (formato, header, id, snapshot)
Para cada item registre: timestamp e falante EXATOS ("[09:17] Diego"), uma
paráfrase curta e, quando houver, o trecho literal entre aspas.
Não promova comentário a decisão. Se não tiver certeza da categoria, marque
"?" e liste ao final em "Dúvidas para o usuário".
Itens da lista negra (email, rate limiting, dashboard, arquivamento, inbound,
ordering global, exactly-once) NUNCA podem cair em RF/RNF.
Para cada gancho C, confirme que o arquivo existe e cite o símbolo real
(ex.: OrderService.changeStatus, requireRole, AppError, createPrismaClient).
```

**2. Separar códigos de erro citados dos derivados.** Trecho do `/fdd-creator`. A reunião citou só três códigos `WEBHOOK_*`; sem essa regra, a matriz de erros mistura o que foi dito com o que a IA inventou para completar.

```text
- **Matriz de erros:** `**FDD-ERR-nn**`, colunas `Código | HTTP | Quando ocorre | Classe base (existente) | Tratamento | Fonte`.
  - Os 3 códigos citados ([09:28] Bruno) aparecem com essa fonte. Os demais `WEBHOOK_*` são (derivado), pela convenção do prefixo ([09:29] Larissa).
  - Erros do worker, que não são HTTP, aparecem como `n/a (worker)` e indicam se a falha é retryable ou permanente.
  - A classe base deve existir em `src/shared/errors/http-errors.ts` (NotFoundError, ValidationError, ConflictError, UnprocessableEntityError, BadRequestError, ForbiddenError).
```

**3. Review cético.** Trecho do `/design-docs-review`, rodado após cada documento. Foi o prompt que mais encontrou problemas: o validador confere que o timestamp existe, mas só a leitura da fala confere que ela **diz aquilo**.

```text
O papel aqui é o de **revisor cético**: assuma que o documento tem alucinações até prová-las inexistentes.

2. **Auditoria de fontes.** Para cada afirmação factual do documento (número, nome, regra, rota, header, tabela, prazo):
   - Tem `[hh:mm] Nome`? Abra `TRANSCRICAO.md` naquele minuto e confirme que a fala **diz aquilo**. Confirmar só a existência do timestamp não basta.
   - Tem caminho de código? Abra o arquivo e confirme o símbolo citado (método, classe, campo).
   - Não tem fonte? Classifique como **(a)** derivação legítima não rotulada (correção: rotular), **(b)** invenção (correção: remover) ou **(c)** item que precisa de fonte e tem (correção: adicionar a fonte).
```

## Iterações e ajustes

Cada linha vem do log de iterações do arquivo de controle da execução.

1. **Validador (teste contra o README original).** A checagem "README substituído" passava em falso: a frase-sentinela escolhida não existia no enunciado. *Detectado* ao testar o validador contra os placeholders. *Correção:* sentinelas trocadas por trechos reais do enunciado; o teste passou a falhar corretamente.
2. **Inventário: fala corrigida tratada como decisão.** "Usar o mesmo Prisma client" ([09:11] Bruno) quase virou decisão, mas o próprio Bruno corrige em [09:30]. O mesmo aconteceu com "customer_id implícito do JWT" ([09:31] Marcos), corrigido em [09:32]. *Detectado* na classificação. *Correção:* o prompt de extração exige ler a transcrição inteira antes de classificar; a versão rejeitada vai para "Descartados".
3. **Inventário: três pontos sem decisão.** customer_id no body ou no path, evento de criação do pedido (lacuna do código) e manter ou não o ADR-007. *Detectado* pela seção "Dúvidas para o usuário". *Correção:* checkpoint humano; nenhum dos três virou requisito fechado.
4. **ADRs (geração): lacunas que a IA poderia ter fechado sozinha.** Entre elas: se as 5 tentativas incluem o envio original, se o X-Timestamp entra no HMAC, se o replay preserva o X-Event-Id. *Detectado* ao escrever as consequências. *Correção:* cada uma virou "Ponto em aberto", com link para o `RFC-Q` correspondente.
5. **ADRs (review): validador 100% verde, mas com alucinações.** Uma invenção ("trocar a secret sem perder eventos", quando a Sofia só disse "tempo de migrar"), uma alternativa nunca discutida apresentada como real, derivações sem rótulo, 6 arquivos citados num ADR com limite de 5 e uma decisora que tinha questionado a decisão. *Detectado* pelo review cético. *Correção:* 9 ajustes com a fala literal e o rótulo (derivado).
6. **RFC (geração): tamanho e links.** Cerca de 2.325 palavras, acima do teto de 2.200, e ADRs apontando para "questão em aberto no RFC" sem número. *Detectado* pelo validador e na revisão dos links. *Correção:* texto enxugado; cada ponto em aberto dos ADRs passou a linkar seu `RFC-Q`.
7. **RFC (review): detalhes "óbvios" sem fonte.** Método POST no diagrama, prazo "confirmado" com a Atlas (Marcos disse que *vai* confirmar), "observar em produção", questões em aberto sem dono. *Detectado* pelo review cético. *Correção:* 9 ajustes, incluindo a coluna "Responsável / prazo" com "Não definido" explícito.
8. **Resíduo de correção.** O "em produção" removido na iteração 7 sobreviveu na mitigação do RFC-RISK-05. *Detectado* numa validação de progresso que pedi entre as etapas: a IA releu o RFC confrontando cada fala com a transcrição. *Correção:* fala literal "observar e decidir depois" e a regra de fazer `grep` do termo removido em todo o `docs/` após cada correção.
9. **FDD (geração): o código contrariou o óbvio.** `NotFoundError` e `ValidationError` fixam o código de erro, a garantia de ordem por pedido quebra com retry e checar 64KB na inserção derrubaria a mudança de status. *Detectado* pela leitura obrigatória do código antes de escrever. *Correção:* classes e local de validação ajustados; sete escolhas derivadas levadas ao checkpoint humano.
10. **FDD (review): contradição interna e testes inexecutáveis.** O objetivo prometia "nenhum evento descartado", mas o DELETE apagava pendentes. Além disso, `vi.spyOn` não funciona em export ESM, e o timeout não pode vir do `env`, que é lido uma vez. *Detectado* pelo review cético. *Correção:* exceção explícita, `vi.mock` e configuração por parâmetro.
11. **PRD (geração): o mesmo acréscimo de novo.** Um critério dizia "em produção" sem fonte. *Detectado* pelo `grep` da iteração 8, antes do review. *Correção:* texto reescrito.
12. **PRD (review): linguagem de produto escondendo uma condição.** "Ordem por pedido preservada" sem "enquanto houver um único processo"; a métrica de 100% contradizia o FDD corrigido; uma dependência citava uma fala que não a sustentava. *Detectado* pelo review cético. *Correção:* 9 ajustes, propagando ao PRD as correções do FDD.
13. **Tracker: 15 IDs invisíveis.** O coletor achou 171 IDs em vez de 186, porque no FDD o ponto estava dentro do negrito (`**FDD-FLUXO-01.**`). *Detectado* pelo `--list-ids` do tracker. *Correção:* formato corrigido; tracker com 100% de cobertura.
14. **README: prompts "limpos".** Na primeira versão deste README, dois prompts tinham perdido a formatação Markdown original, e o processo exige cópia literal. *Detectado* na auto-revisão antes do commit. *Correção:* texto restaurado e conferido por script contra os `SKILL.md`.
15. **Revisão final: duplicação entre documentos.** Com o validador 100% verde, uma checagem cruzada por script (valores, nomes de tabelas, headers, lista negra e trechos de 9 palavras repetidos entre documentos) achou o ponto em aberto do ADR-003 copiado quase literalmente no RFC-Q-08. *Detectado* pelo script de sobreposição da revisão `all`. *Correção:* o ADR passou a ter uma linha com link para o RFC, que é dono do detalhe; os demais valores e nomes estavam idênticos em todo o pacote.

16. **Validação pré-entrega: o próprio README impreciso.** Com o validador verde (131 checagens) e uma amostragem de 18 linhas do tracker confrontadas com a fala citada (todas sustentadas), a leitura do README achou duas afirmações falsas sobre o processo: o modelo aparecia como usado só "da etapa de ADRs em diante", embora tenha sido o mesmo desde o setup, e a iteração 8 dizia "leitura humana" para um achado da IA numa validação pedida por mim. *Detectado* na validação de progresso antes do merge. *Correção:* as duas frases foram reescritas conforme o que aconteceu. Lição: o README também é documento rastreável, e a fonte dele é o log de execução.

17. **Validação contra o enunciado: exemplos de request faltando.** Uma checagem independente do validador do projeto, contrato por contrato, mostrou que só 2 dos 8 contratos do FDD (POST e PATCH) tinham exemplo de requisição; os endpoints sem corpo e o webhook de saída mostravam só a resposta, ou só o corpo enviado. O validador contava blocos JSON na seção inteira (16), não por endpoint. A mesma checagem achou o inventário citando `src/worker.ts` sem o rótulo "(novo, a criar)". *Detectado* na validação final contra o enunciado e o plano. *Correção:* exemplo de requisição HTTP em todos os contratos, mais a resposta 204 do DELETE e a resposta do cliente no webhook de saída, reaproveitando só valores que o FDD já definia (alinhado o `X-Timestamp` com o horário da tentativa no histórico); rótulo aplicado no inventário. Lição: "passou no validador" mede o que o validador sabe medir; o critério do enunciado precisa ser checado na granularidade dele (por endpoint).

18. **Validação completa sobre o fork publicado: dois riscos de leitura estrita.** Num clone limpo do GitHub, com checagens independentes (todo ID do tracker presente no documento indicado, 28 linhas do tracker confrontadas com a fala, 0 trechos de conteúdo repetidos entre documentos, valores-chave idênticos em todo o pacote), todos os critérios passaram. Restaram dois pontos que um avaliador literal poderia ler como falha: os arquivos futuros eram rotulados um a um, sem convenção declarada, e o FDD citava pelo nome o arquivo compilado do worker, um artefato de build que não existe no repositório; e "5 tentativas" da reunião aparecia ao lado de "6 envios" no FDD sem explicar a relação. *Detectado* na validação final contra o enunciado. *Correção:* convenção explícita de "(novo, a criar)" no FDD e no README; script `worker` descrito pelo padrão do `start`, sem nomear o artefato; FDD e PRD explicam que as 5 tentativas são as retentativas após a falha inicial, uma por intervalo (ver RFC-Q-08).

**18 iterações principais** até o resultado final.

## Como navegar a entrega

```text
.
├── README.md                          este arquivo (processo)
├── TRANSCRICAO.md                     fonte: a reunião
├── analysis/
│   └── inventario-transcricao.md      base de verdade: decisões, requisitos, descartes, dúvidas
├── docs/
│   ├── PRD.md                         por que e o quê
│   ├── RFC.md                         como pretendemos resolver e o que está em aberto
│   ├── FDD.md                         como construir em detalhe
│   ├── TRACKER.md                     de onde veio cada item (186 IDs)
│   └── adrs/
│       ├── README.md                  índice dos ADRs
│       └── ADR-001 ... ADR-007        por que decidimos exatamente assim
└── .claude/
    ├── rules/design-docs.md           regra global de rastreabilidade e escopo
    └── skills/                        8 skills do processo + validate_docs.py
```

Caminhos marcados (novo, a criar) são arquivos que a feature vai criar, nomeados na reunião ([09:11] Larissa, [09:27] Bruno, [09:28] Bruno); todos os demais caminhos citados existem no repositório.

Ordem de leitura sugerida:

1. [PRD](docs/PRD.md): problema, público, métricas e escopo.
2. [RFC](docs/RFC.md): a proposta, as 12 alternativas descartadas e as 12 questões em aberto.
3. [ADRs](docs/adrs/README.md): uma decisão por arquivo, com contexto e trade-off.
4. [FDD](docs/FDD.md): modelo de dados, fluxos, contratos, erros e critérios de aceite.
5. [Tracker](docs/TRACKER.md): cada ID ligado a `[hh:mm] Nome` ou a um arquivo do código.

Para conferir o pacote:

```bash
python3 .claude/skills/tracker-builder/scripts/validate_docs.py            # tudo
python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only fdd # um grupo
python3 .claude/skills/tracker-builder/scripts/validate_docs.py --list-ids # IDs rastreáveis
```
