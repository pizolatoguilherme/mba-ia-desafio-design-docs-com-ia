# PRD: Sistema de Webhooks de Notificação de Pedidos

| Campo | Valor |
|---|---|
| Produto | Order Management System (OMS) |
| Responsável de produto | Marcos (PM) |
| Responsável técnico | Larissa (Tech Lead) |
| Status | Aprovado para design |
| Data | 2026-11-16 |
| Documentos relacionados | [RFC](RFC.md), [FDD](FDD.md), [ADRs](adrs/README.md), [Tracker](TRACKER.md) |

## 1. Resumo e contexto

Três clientes B2B (Atlas Comercial, MaxDistribuição e Nova Cargo) pediram formalmente para ser avisados quando o status dos seus pedidos muda na plataforma ([09:00] Marcos). Hoje eles descobrem as mudanças consultando a listagem de pedidos de tempos em tempos.

Este PRD define uma notificação automática de saída, da plataforma para um endereço cadastrado pelo cliente ([09:02] Marcos, [09:03] Sofia), percebida como tempo real: menos de 10 segundos ([09:02] Marcos). As notificações são assinadas, entregues ao menos uma vez e reenviadas automaticamente quando o cliente está fora do ar. O como fica no [RFC](RFC.md) e no [FDD](FDD.md); o porquê de cada decisão, nos [ADRs](adrs/README.md).

## 2. Problema e motivação

- **Integração lenta e cara:** os clientes ficam batendo em `GET /orders` para ver se algo mudou ([09:00] Marcos). Isso atrasa a reação deles e gera consultas desnecessárias.
- **Risco comercial:** a Atlas sinalizou que pode migrar para um concorrente se a solução não sair até o fim do trimestre, e pediu a entrega para o fim de novembro ([09:00] Marcos, [09:45] Marcos).
- **Expectativa clara de latência:** para os clientes, qualquer coisa abaixo de 10 segundos é tempo real; o importante é não ficarem atualizando manualmente ([09:02] Marcos).

## 3. Público-alvo e cenários de uso

| Público | Necessidade | Fonte |
|---|---|---|
| Clientes B2B integradores (Atlas Comercial, MaxDistribuição, Nova Cargo) | Receber a mudança de status sem consultar a plataforma | [09:00] Marcos |
| Usuários da API que representam o cliente | Cadastrar e manter os endereços de notificação pela API, autenticados como hoje | [09:32] Marcos |
| ADMIN da operação | Reprocessar notificações que esgotaram as tentativas, com rastro de quem fez | [09:36] Sofia |
| Desenvolvedores dos clientes | Saber como validar a assinatura e tratar duplicatas | [09:26] Marcos, [09:40] Marcos |

Cenários:

1. **Só o que interessa.** A Atlas cadastra um endereço para saber apenas quando os pedidos viram SHIPPED e DELIVERED; mudanças para outros status não geram aviso ([09:33] Marcos).
2. **Manutenção planejada.** Um cliente fica duas horas fora do ar em manutenção, como já aconteceu ([09:16] Diego). As notificações desse período chegam sozinhas quando ele volta, sem ninguém intervir.
3. **Chave vazada.** Um cliente vaza a chave de assinatura no log da própria aplicação, como já ocorreu ([09:22] Diego). Ele gera uma nova chave, e a antiga continua valendo por 24 horas para ele ter tempo de migrar os sistemas dele ([09:21] Sofia).
4. **Cliente fora por muito tempo.** Um cliente fica indisponível por mais de 15 horas; as tentativas automáticas, que cobrem quase 15 horas, se esgotam ([09:17] Diego, [09:17] Marcos) e um ADMIN reprocessa os avisos guardados quando o cliente volta ([09:18] Diego).
5. **Vários cadastros.** Um cliente com mais de um endereço cadastrado precisa saber qual cadastro originou cada aviso ([09:44] Sofia).
6. **Aviso repetido.** O cliente recebe o mesmo aviso duas vezes e reconhece a repetição pelo identificador do evento ([09:25] Diego).

## 4. Objetivos e métricas de sucesso

| ID | Objetivo | Métrica e meta | Fonte |
|---|---|---|---|
| **PRD-MET-01** | Notificação em tempo real | Tempo entre a mudança de status e a chegada do aviso **abaixo de 10 segundos** quando o cliente está disponível | [09:02] Marcos |
| **PRD-MET-02** | Atender quem pediu | **3 de 3** clientes demandantes (Atlas Comercial, MaxDistribuição, Nova Cargo) recebendo notificações (meta derivada do pedido formal) | [09:00] Marcos |
| **PRD-MET-03** | Cumprir o prazo comercial | Entrega em **3 sprints** (estimativa), com a revisão de segurança incluída. A Atlas pediu o fim de novembro; como a data da reunião não é conhecida, a compatibilidade entre os dois fica a confirmar com a Atlas ([09:47] Marcos) | [09:45] Marcos, [09:47] Larissa |
| **PRD-MET-04** | Nenhum aviso perdido em silêncio | **100%** das mudanças de status notificáveis terminam entregues ou guardadas para reprocessamento; a única exceção são os avisos pendentes de um cadastro que o próprio cliente removeu (derivado da garantia de entrega e do [FDD](FDD.md) FDD-OBJ-03) | [09:24] Diego, [09:18] Diego |
| **PRD-MET-05** | Menos consultas periódicas dos clientes | Qualitativa: os clientes deixam de depender de consultas periódicas à listagem de pedidos. Não há baseline medido, então não há meta numérica | [09:00] Marcos |

## 5. Escopo

### 5.1 Incluso

- Cadastro, edição, remoção, listagem e ativação de endereços de notificação por cliente, com escolha dos status de interesse ([09:31] Marcos, [09:33] Bruno, [09:21] Bruno).
- Chave de assinatura gerada pela plataforma, com rotação ([09:31] Marcos, [09:21] Sofia).
- Envio automático a cada mudança de status de pedido, assinado e com identificador de evento ([09:06] Diego, [09:20] Sofia, [09:25] Diego).
- Novas tentativas automáticas e guarda dos avisos que falharam, com reprocessamento manual por ADMIN ([09:15] Diego, [09:18] Diego, [09:36] Sofia).
- Histórico das últimas 100 entregas por cadastro ([09:34] Marcos).
- Documentação de integração no portal do desenvolvedor ([09:26] Marcos, [09:40] Marcos).

### 5.2 Fora de escopo

| ID | Item | Situação | Fonte |
|---|---|---|---|
| **PRD-OUT-01** | Email ao cliente quando a notificação falha repetidamente | Adiado para a próxima fase, depois de medir o impacto | [09:37] Marcos, [09:37] Larissa, [09:38] Marcos |
| **PRD-OUT-02** | Rate limiting de envio para o cliente | Observar e decidir depois | [09:38] Diego, [09:39] Diego, [09:39] Larissa |
| **PRD-OUT-03** | Dashboard ou painel visual para o cliente | Fora agora; projeto separado do time de frontend | [09:39] Marcos, [09:40] Larissa |
| **PRD-OUT-04** | Arquivamento dos avisos já entregues | Fora do escopo desta feature | [09:08] Diego |
| **PRD-OUT-05** | Webhooks inbound (cliente enviando para a plataforma) | Não pedido | [09:02] Marcos, [09:03] Sofia |
| **PRD-OUT-06** | Ordem global dos avisos e processamento paralelo | Limitação conhecida; a ordem vale só por pedido | [09:13] Diego, [09:13] Larissa, [09:14] Marcos |
| **PRD-OUT-07** | Entrega exactly-once | Descartado; o cliente trata duplicatas | [09:25] Diego |
| **PRD-OUT-08** | Restringir quem pode configurar notificações | Adiado ("mais pra frente") | [09:37] Sofia |
| **PRD-OUT-09** | Aviso na criação do pedido | Não tratado na reunião; questão em aberto identificada no código ([RFC-Q-12](RFC.md#questões-em-aberto)) | [09:00] Marcos |

## 6. Requisitos funcionais

Prioridades MoSCoW são avaliação deste PRD (derivado): todos os requisitos abaixo foram decididos na reunião como parte da entrega, por isso são MUST. O que a reunião adiou está em Fora de escopo, não como COULD ou WON'T.

**PRD-FR-01** [MUST] O cliente é avisado sempre que o status de um pedido dele muda. Fonte: [09:00] Marcos.
Critérios: - Toda mudança de status de pedido do cliente gera aviso para os cadastros interessados. - O aviso informa o pedido, o status anterior e o novo ([09:43] Diego).

**PRD-FR-02** [MUST] O cliente cadastra um endereço de notificação informando o endereço e os status de interesse; a plataforma gera a chave de assinatura e a mostra uma única vez, na criação. Fonte: [09:31] Marcos.
Critérios: - O cadastro devolve a chave uma vez. - Consultas posteriores não mostram a chave.

**PRD-FR-03** [MUST] O cliente edita e remove seus cadastros. Fonte: [09:33] Bruno.
Critérios: - Mudanças no cadastro valem para os próximos avisos. - Um cadastro removido deixa de receber avisos.

**PRD-FR-04** [MUST] O cliente lista seus cadastros. O cliente é identificado explicitamente na requisição, e não pelo login do operador. Fonte: [09:33] Bruno, [09:32] Larissa.
Critérios: - A listagem mostra só os cadastros do cliente informado. - O formato da identificação está pendente de confirmação ([RFC-Q-01](RFC.md#questões-em-aberto)).

**PRD-FR-05** [MUST] Cada cadastro escolhe de quais mudanças de status quer ser avisado. Fonte: [09:33] Bruno, [09:33] Marcos.
Critérios: - Um cadastro só com SHIPPED e DELIVERED não recebe aviso de PAID.

**PRD-FR-06** [MUST] O cadastro pode ser ativado e desativado. Fonte: [09:21] Bruno, [09:21] Sofia.
Critérios: - Um cadastro desativado não recebe avisos novos.

**PRD-FR-07** [MUST] O cliente consulta o histórico das últimas 100 entregas de um cadastro, com sucesso ou falha, conteúdo enviado, resposta e tempo de resposta. Fonte: [09:34] Marcos, [09:35] Larissa.
Critérios: - O histórico traz no máximo 100 registros, do mais recente para o mais antigo.

**PRD-FR-08** [MUST] O cliente troca a chave de assinatura quando quiser; a chave anterior continua válida por 24 horas. Fonte: [09:21] Sofia.
Critérios: - Depois da troca, avisos validam com a chave nova e, por 24 horas, também com a antiga.

**PRD-FR-09** [MUST] Todo aviso é assinado, para o cliente confirmar que veio da plataforma e não foi alterado. Fonte: [09:19] Sofia, [09:20] Sofia.
Critérios: - Um aviso alterado no caminho falha na validação com a chave do cliente.

**PRD-FR-10** [MUST] Se o cliente estiver fora do ar, a plataforma tenta de novo automaticamente; esgotadas as tentativas, o aviso fica guardado com o motivo da falha. Fonte: [09:15] Diego, [09:18] Diego.
Critérios: - Uma indisponibilidade de 2 horas não exige intervenção humana ([09:16] Diego).

**PRD-FR-11** [MUST] Um ADMIN reprocessa um aviso guardado, e a plataforma registra quem fez. Fonte: [09:18] Diego, [09:36] Sofia.
Critérios: - Usuário sem perfil ADMIN não consegue reprocessar. - O registro identifica o ADMIN que executou.

**PRD-FR-12** [MUST] Cada aviso traz um identificador de evento, o mesmo em todas as tentativas, para o cliente ignorar repetições. Fonte: [09:25] Diego, [09:26] Larissa.
Critérios: - Dois recebimentos do mesmo aviso trazem o mesmo identificador.

**PRD-FR-13** [MUST] Cada aviso informa qual cadastro o originou, para clientes com mais de um cadastro. Fonte: [09:44] Sofia, [09:45] Diego.
Critérios: - Um cliente com dois cadastros distingue a origem de cada aviso.

## 7. Requisitos não funcionais

| ID | Categoria | Requisito | Valor | Fonte |
|---|---|---|---|---|
| **PRD-NFR-01** | Performance | Tempo até o aviso, com o cliente disponível | abaixo de 10 s | [09:02] Marcos |
| **PRD-NFR-02** | Performance | Intervalo com que a plataforma verifica mudanças a notificar; no pior caso, uma mudança espera esse tempo antes de ser processada, o que a reunião aceitou | 2 s | [09:09] Diego, [09:10] Larissa |
| **PRD-NFR-03** | Performance | Tempo máximo de espera pela resposta do cliente; sem resposta conta como falha | 10 s | [09:42] Diego |
| **PRD-NFR-04** | Segurança | Endereço de notificação só com conexão segura; endereço inseguro é recusado no cadastro | https obrigatório | [09:23] Sofia |
| **PRD-NFR-05** | Segurança | Assinatura de cada aviso com chave exclusiva por cadastro | HMAC-SHA256 | [09:20] Sofia, [09:21] Sofia |
| **PRD-NFR-06** | Segurança | Convivência das chaves antiga e nova na troca | 24 h | [09:21] Sofia |
| **PRD-NFR-07** | Segurança | Reprocessamento só por ADMIN; configuração por qualquer usuário autenticado | perfis existentes | [09:36] Sofia, [09:37] Sofia |
| **PRD-NFR-08** | Confiabilidade | Garantia de entrega: ao menos uma vez; repetições são possíveis | at-least-once | [09:24] Diego |
| **PRD-NFR-09** | Confiabilidade | Tentativas automáticas antes de guardar o aviso | 5 tentativas após a falha inicial, uma por intervalo (1m/5m/30m/2h/12h), cerca de 15 h (contagem exata em [RFC-Q-08](RFC.md#questões-em-aberto)) | [09:17] Diego, [09:17] Larissa |
| **PRD-NFR-10** | Confiabilidade | Nenhuma mudança de status sem aviso registrado, e nenhum aviso de mudança desfeita | atômico | [09:06] Diego, [09:40] Bruno |
| **PRD-NFR-11** | Confiabilidade | Ordem dos avisos de um mesmo pedido preservada **enquanto houver um único processo de envio**; não há ordem global entre pedidos (PRD-OUT-06) | por pedido, com processo único | [09:12] Diego, [09:13] Larissa |
| **PRD-NFR-12** | Confiabilidade | Tamanho máximo do aviso; acima disso é erro, sem cortar o conteúdo | 64 KB | [09:23] Sofia, [09:24] Larissa |
| **PRD-NFR-13** | Manutenibilidade | Aviso enxuto, sem os itens do pedido; detalhes ficam na consulta do pedido | sem itens | [09:43] Diego, [09:44] Bruno |
| **PRD-NFR-14** | Manutenibilidade | Reuso dos padrões e ferramentas atuais do projeto, sem ferramenta nova | reuso máximo | [09:29] Bruno, [09:30] Larissa |

## 8. Decisões e trade-offs principais

- **Registro na mesma transação da mudança de status:** consistência garantida sem infraestrutura nova, ao custo de acoplar a gravação do aviso à operação de Pedidos. [ADR-001](adrs/ADR-001-outbox-transacional-no-mysql.md)
- **Processo separado verificando a cada 2 s:** a latência de 2 s é aceita em troca de simplicidade e de independência da API. [ADR-002](adrs/ADR-002-worker-separado-com-polling.md)
- **5 tentativas em cerca de 15 h, depois guarda e reprocessamento por ADMIN:** cobre manutenções de horas sem deixar aviso pendurado para sempre. [ADR-003](adrs/ADR-003-retry-com-backoff-e-dead-letter.md)
- **Assinatura com chave por cadastro e troca com 24 h de convivência:** um vazamento afeta um só cadastro. [ADR-004](adrs/ADR-004-hmac-sha256-com-secret-por-endpoint.md)
- **Ao menos uma vez, com identificador de evento:** simples e padrão de mercado, mas o cliente precisa tratar repetições. [ADR-005](adrs/ADR-005-entrega-at-least-once-com-x-event-id.md)
- **Reuso dos padrões do projeto:** entrega mais rápida e consistente, herdando as limitações atuais. [ADR-006](adrs/ADR-006-reuso-dos-padroes-do-projeto.md)
- **Conteúdo fotografado no momento da mudança e filtro aplicado na hora:** o aviso reflete o pedido naquele instante e nada é gravado à toa. [ADR-007](adrs/ADR-007-snapshot-e-filtro-na-insercao.md)

## 9. Dependências

| ID | Dependência | Responsável | Fonte |
|---|---|---|---|
| **PRD-DEP-01** | Revisão de segurança da assinatura e da geração de chave, com pelo menos 2 dias úteis antes do deploy | Sofia | [09:46] Sofia, [09:49] Sofia |
| **PRD-DEP-02** | Documentação de integração no portal do desenvolvedor, com destaque para o tratamento de repetições | Marcos | [09:26] Marcos, [09:40] Marcos |
| **PRD-DEP-03** | Migração do banco de dados para as estruturas novas, no fluxo atual de `prisma/migrations/` | Time técnico (derivado) | derivado das tabelas novas: [09:06] Diego, [09:18] Diego |
| **PRD-DEP-04** | Clientes implementando a validação da assinatura e o descarte de repetições | Clientes | [09:20] Sofia, [09:25] Diego |
| **PRD-DEP-05** | Operação de um segundo processo além da API | Time técnico (derivado) | [09:11] Diego |
| **PRD-DEP-06** | Confirmação do prazo com a Atlas e comunicação aos clientes | Marcos | [09:47] Marcos, [09:49] Marcos |

## 10. Riscos e mitigação

A probabilidade e o impacto são avaliação da equipe registrada neste PRD (derivado). As mitigações usam só o que a reunião definiu.

| ID | Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|---|
| **PRD-RISK-01** | Atraso faz a Atlas migrar para um concorrente ([09:00] Marcos) | Média | Alto | Estimativa de 3 sprints com a revisão de segurança incluída ([09:47] Larissa); Marcos confirma o prazo com a Atlas e atualiza os clientes ([09:47] Marcos, [09:49] Marcos) |
| **PRD-RISK-02** | Cliente não trata repetições e processa o mesmo aviso duas vezes ([09:25] Sofia) | Média | Médio | Identificador de evento em todo aviso ([09:25] Diego) e documentação em destaque no portal ([09:26] Marcos) |
| **PRD-RISK-03** | Vazamento da chave de assinatura pelo cliente ([09:22] Diego) | Média | Alto | Chave exclusiva por cadastro e troca com 24 h de convivência ([09:21] Sofia); revisão de segurança antes do deploy ([09:46] Sofia) |
| **PRD-RISK-04** | Cliente fora do ar por mais de cerca de 15 h deixa de receber avisos automaticamente ([09:17] Marcos) | Baixa | Médio | Avisos guardados com o motivo e reprocessamento por ADMIN ([09:18] Diego); aviso por email fica para a próxima fase ([09:37] Larissa) |
| **PRD-RISK-05** | Muitas mudanças em pouco tempo geram muitos avisos seguidos para o mesmo cliente ([09:38] Diego) | Baixa | Médio | Observar e decidir depois ([09:39] Larissa) |
| **PRD-RISK-06** | A revisão de segurança não é agendada a tempo e segura o deploy ([09:49] Sofia) | Baixa | Alto | Revisão já incluída na estimativa ([09:47] Larissa), com 2 dias úteis reservados ([09:46] Sofia) |

## 11. Critérios de aceitação

- **PRD-AC-01** Com um cadastro para SHIPPED, quando um pedido do cliente muda para SHIPPED, o aviso chega em menos de 10 s com o cliente disponível ([09:02] Marcos).
- **PRD-AC-02** O cliente não recebe aviso de status que não escolheu ([09:33] Marcos).
- **PRD-AC-03** O aviso valida com a chave recebida no cadastro; após a troca, a chave antiga ainda valida por 24 h e depois não valida mais ([09:21] Sofia).
- **PRD-AC-04** O cadastro de endereço sem https é recusado ([09:23] Sofia).
- **PRD-AC-05** O cliente vê as últimas 100 entregas com resultado, conteúdo, resposta e tempo ([09:34] Marcos).
- **PRD-AC-06** Um cliente fora do ar por 2 h recebe os avisos do período ao voltar, sem intervenção ([09:16] Diego).
- **PRD-AC-07** Um aviso que esgotou as tentativas é reprocessado por um ADMIN; um operador não consegue; o registro mostra quem reprocessou ([09:36] Sofia).
- **PRD-AC-08** Avisos repetidos chegam com o mesmo identificador de evento ([09:25] Diego).
- **PRD-AC-09** A chave de assinatura não aparece em nenhuma consulta depois do cadastro ou da troca ([09:31] Marcos).
- **PRD-AC-10** A integração está documentada no portal, incluindo validação da assinatura e tratamento de repetições ([09:26] Marcos, [09:40] Marcos); publicar antes da liberação aos clientes é (derivado).
- **PRD-AC-11** Atlas Comercial, MaxDistribuição e Nova Cargo recebem avisos das mudanças dos próprios pedidos (PRD-MET-02) ([09:00] Marcos).

## 12. Estratégia de testes e validação

- **Testes automatizados:** vitest e supertest, no padrão de `tests/orders.test.ts` e `tests/auth.test.ts`, com as fábricas de `tests/helpers/factories.ts` e a configuração de `vitest.config.ts` (execução sequencial em um único processo). Os critérios técnicos detalhados estão na seção 12 do [FDD](FDD.md), um por decisão e requisito não funcional.
- **Testes ponta a ponta da integração** com a mudança de status de pedidos, previstos na estimativa ([09:46] Larissa).
- **Revisão de segurança** da assinatura e da geração de chave pela Sofia, com 2 dias úteis antes do deploy ([09:46] Sofia).
- **Validação com os clientes demandantes:** os três clientes do pedido formal confirmam o recebimento e a validação dos avisos antes de PRD-MET-02 ser considerada atingida (derivado de [09:00] Marcos e [09:49] Marcos).
- **Validação do desenho** na sessão de revisão do doc com Bruno e Diego antes de começar a codar ([09:50] Larissa).
