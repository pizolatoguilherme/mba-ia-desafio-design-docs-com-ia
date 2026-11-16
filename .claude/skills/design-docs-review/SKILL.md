---
name: design-docs-review
description: "Revisão crítica de um design doc (adrs, rfc, fdd, prd, tracker, readme) ou do pacote inteiro (all) contra a transcrição, o código e os critérios de aceite do desafio: afirmações sem fonte, itens fora de escopo vazados como requisito, duplicação entre documentos, contradições RFC×FDD×ADR, caminhos de arquivo inexistentes. Roda o validador e devolve lista de correções priorizada. Uso: /design-docs-review <adrs|rfc|fdd|prd|tracker|readme|all>."
disable-model-invocation: true
---

# Design Docs Review

Carregue `.claude/rules/design-docs.md`. O papel aqui é o de **revisor cético**: assuma que o documento tem alucinações até prová-las inexistentes.

## Procedimento

1. **Validador:** `python3 .claude/skills/tracker-builder/scripts/validate_docs.py --only <grupo>`, ou sem `--only` para `all`. Toda falha vira item de correção.
2. **Auditoria de fontes.** Para cada afirmação factual do documento (número, nome, regra, rota, header, tabela, prazo):
   - Tem `[hh:mm] Nome`? Abra `TRANSCRICAO.md` naquele minuto e confirme que a fala **diz aquilo**. Confirmar só a existência do timestamp não basta.
   - Tem caminho de código? Abra o arquivo e confirme o símbolo citado (método, classe, campo).
   - Não tem fonte? Classifique como **(a)** derivação legítima não rotulada (correção: rotular), **(b)** invenção (correção: remover) ou **(c)** item que precisa de fonte e tem (correção: adicionar a fonte).
3. **Escopo.** Procure os itens da lista negra (email, rate limiting, dashboard, arquivamento, inbound, ordering global, exactly-once). Eles só podem aparecer como fora de escopo, adiado, questão em aberto ou limitação.
4. **Pontos sensíveis.** Confira se o documento afirma algo contrário a:
   - customer_id não vem do JWT;
   - CRUD aberto a qualquer role autenticada, e só o replay exige ADMIN;
   - filtro e snapshot acontecem na inserção;
   - ordering só por order_id e só com single-worker;
   - 64KB gera erro, sem truncar;
   - http é recusado;
   - a secret só é devolvida na criação ou na rotação.
5. **Fronteira e duplicação.** Compare com os outros documentos:
   - O PRD repete detalhe técnico?
   - O RFC traz payload, endpoint com status ou schema?
   - O ADR descreve implementação?
   - O FDD repete narrativa de negócio?
   
   Parágrafos quase idênticos entre documentos são sinal de conteúdo no lugar errado.
6. **Consistência cruzada.** Os valores (2s, 10s, 64KB, 5 tentativas, 1m/5m/30m/2h/12h, 24h, 100 entregas, headers, nomes de tabelas) precisam ser idênticos em todos os documentos. A mesma questão não pode estar "em aberto" no RFC e "decidida" no FDD sem o rótulo "pendente de confirmação".
7. **Profundidade** (contra documentos genéricos):
   - Há trechos vagos ("garantir qualidade", "seguir boas práticas") sem um critério verificável?
   - Faltam exemplos concretos onde o enunciado pede?

## Saída

Responda no chat, sem criar arquivo:

```markdown
## Review: <doc> (rodada N)

Validador: X falhas, Y avisos

| # | Severidade (bloqueante/alta/média/baixa) | Local (arquivo:linha) | Problema | Evidência (fonte consultada) | Correção proposta |

Veredito: aprovado | aprovado com ressalvas | reprovado
```

Em seguida:

1. Aplique as correções bloqueantes e altas, ou peça autorização se a correção mudar uma decisão.
2. Rode o validador de novo.
3. Registre a rodada no "Log de iterações" de `../EXECUCAO.md`: o que a IA errou e como foi corrigido. Esse log alimenta o README.
