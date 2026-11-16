---
name: transcript-inventory
description: "Extrai da TRANSCRICAO.md e do código um inventário rastreável (decisões fechadas, requisitos funcionais e não funcionais, descartados/adiados, questões em aberto, ganchos com o código, detalhes secundários), cada item com [hh:mm] Nome ou caminho de arquivo. É a base de verdade para gerar PRD, RFC, FDD, ADRs e Tracker. Use antes de gerar qualquer design doc."
disable-model-invocation: true
---

# Transcript Inventory

Produz `analysis/inventario-transcricao.md`: a **fonte única de verdade** do pacote de design docs. Nenhum documento é gerado antes de este inventário ser validado pelo usuário.

Carregue e siga `.claude/rules/design-docs.md`.

## Entradas (ler por inteiro, nesta ordem)

1. `TRANSCRICAO.md`, todas as linhas. Não resuma antes de ler tudo.
2. Código que a reunião cita ou que a feature toca:
   - `prisma/schema.prisma`
   - `src/modules/orders/order.service.ts`
   - `src/modules/orders/order.status.ts`
   - `src/modules/orders/order.routes.ts`
   - `src/shared/errors/app-error.ts`
   - `src/shared/errors/http-errors.ts`
   - `src/shared/errors/index.ts`
   - `src/middlewares/auth.middleware.ts`
   - `src/middlewares/error.middleware.ts`
   - `src/middlewares/validate.middleware.ts`
   - `src/shared/logger/index.ts`
   - `src/config/database.ts`
   - `src/config/env.ts`
   - `src/server.ts`
   - `src/app.ts`
   - `src/routes/index.ts`
   - `src/shared/http/response.ts`
   - `package.json`
   - `tests/`

## Prompt de extração (aplicar a si mesmo, literalmente)

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

## Saída: `analysis/inventario-transcricao.md`

```markdown
# Inventário da transcrição e do código

> Base de verdade do pacote. Gerado por `/transcript-inventory` em AAAA-MM-DD.

## 1. Participantes
| Nome | Papel |

## 2. Decisões fechadas (D)
| # | Decisão | Fonte(s) | Alternativas rejeitadas (com motivo e fonte) | ADR previsto |

## 3. Requisitos funcionais (RF)
| # | Requisito | Fonte(s) | Observação |

## 4. Requisitos não funcionais (RNF)
| # | Requisito | Valor | Fonte(s) |

## 5. Descartados (X)
| # | Item | Motivo | Fonte |

## 6. Adiados / fora de escopo (A)
| # | Item | Situação | Fonte |

## 7. Questões em aberto (Q)
| # | Questão | Fonte | Por que está em aberto |

## 8. Ganchos com o código (C)
| # | Arquivo (existente) | Símbolo | Como a feature se conecta | Fonte na reunião |

## 9. Detalhes secundários (S)
| # | Detalhe | Fonte |

## 10. Lacunas identificadas no código (não discutidas na reunião)
| # | Lacuna | Arquivo |

## 11. Dúvidas para o usuário
```

## Checkpoint (obrigatório)

Ao terminar:

1. Mostre ao usuário as contagens por categoria e as dúvidas da seção 11.
2. Peça confirmação explícita antes de seguir para `/adr-creator`.
3. Registre no log de iterações de `../EXECUCAO.md` o que foi corrigido após a revisão do usuário.
