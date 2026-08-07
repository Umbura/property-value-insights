# Agent Orchestration

Guia operacional da orquestração de múltiplos agentes no repositório Property
Value Insights, cobrindo o fluxo Terra + OpenCode/DeepSeek V4 Flash.

Este documento complementa o [`AGENTS.md`](../AGENTS.md) e o
[`docs/REVIEW_AND_DELIVERY_PROCESS.md`](REVIEW_AND_DELIVERY_PROCESS.md). Em
caso de conflito, o `AGENTS.md` e a Issue ativa permanecem as fontes de
verdade. Este guia não altera nenhuma política existente; ele apenas a torna
operacional.

## Purpose

Padronizar como o trabalho da Issue é delegado, executado, revisado e
entregue quando envolve múltiplos agentes. O objetivo é:

- preservar reprodutibilidade, compatibilidade, integridade de artefatos e
  rastreabilidade de decisões técnicas;
- concentrar coordenação, arquitetura e consolidação no orquestrador;
- concentrar implementação focada em um executor bem especificado;
- garantir revisão independente por um agente que não escreveu o diff;
- registrar resultados e comandos exatamente como executados, sem alegar
  execução que não ocorreu.

A orquestração é uma decisão de custo, velocidade, especialização e
verificação independente. Ela só deve ser usada quando a delegação melhora
materialmente um desses fatores; trabalho pequeno e inequívoco não precisa de
delegação.

## Supported stack

Fluxo aprovado e configurado, sem troca automática de provedor:

| Camada | Ferramenta | Papel |
| --- | --- | --- |
| Orquestrador | Terra (reasoning Medium) | escopo, planejamento, tickets, coordenação, decisões arquiteturais, consolidação |
| Executor | OpenCode com DeepSeek V4 Flash (reasoning High) | implementação focada de tickets aprovados e execução de testes relevantes |
| Revisor independente | Sessão nova de Terra (reasoning High) | revisão independente do diff, compatibilidade, regressão e verificação final |

Não adicionar ou trocar para um provedor não aprovado automaticamente. Se o
executor configurado estiver indisponível ou insuficiente, parar e reportar a
limitação; não selecionar um fallback não configurado.

## Roles

### Terra Orchestrator

O orquestrador é o responsável pela Issue como um todo. Ele:

- analisa o escopo da Issue ativa e os critérios de aceite;
- produz o plano aprovado e os tickets executáveis;
- cria um Traycer Task e um worktree isolado por Issue;
- delega trabalho a agentes configurados quando a delegação agrega valor;
- consolida resultados e registra validações com resultados exatos;
- nunca amplia silenciosamente um ticket, aceita alegações sem suporte ou
  trata a resposta de um agente filho como evidência verificada;
- executa as ações de Git e GitHub dentro da autorização permanente e da
  Issue ativa; merge permanece sob autorização explícita do usuário.

### DeepSeek Executor

O executor é o papel com permissão de escrita para implementação. Ele:

- implementa somente a Issue e o plano aprovados, dentro dos arquivos e
  componentes permitidos no ticket;
- preserva a arquitetura existente e o comportamento público por padrão;
- executa testes focados durante a implementação;
- reporta exatamente o trabalho realizado, os arquivos alterados, os comandos
  executados e os resultados observados;
- para quando uma nova decisão for necessária, em vez de adivinhar;
- não enfraquece testes ou validações para obter resultado aprovado.

### Terra Independent Reviewer

O revisor é somente leitura por padrão. Ele:

- revisa o diff de forma independente, sem ter escrito a implementação;
- analisa compatibilidade, regressões, segurança e consistência com a Issue,
  o plano, os contratos e as validações;
- classifica cada observação como achado confirmado bloqueante, achado
  confirmado não bloqueante, evidência ou validação ausente, sugestão
  opcional ou sem problema;
- não edita arquivos durante a revisão e não aprova o próprio trabalho.

Uma revisão final de auditoria de security/compatibility usa uma sessão nova
de Terra com High, distinta da sessão que planejou ou orquestrou a mudança.

## Task routing

| Work type | Agent | Reasoning | Notes |
| --- | --- | --- | --- |
| Inspeção e escopo | Terra | Medium | Investigação somente leitura; produz evidências, escopo e riscos antes de planejar |
| Planejamento e criação de tickets | Terra | Medium | Converte a Issue em plano aprovado e tickets executáveis |
| Documentação/inventário mecânico | DeepSeek (OpenCode) | Low ou High | Tarefas bem especificadas e mecânicas; Low para rotinas triviais, High quando a qualidade da redação importa |
| Implementação normal focada | DeepSeek (OpenCode) | High | Padrão para implementação de tickets aprovados e execução de testes relevantes |
| Caso difícil cross-module | DeepSeek Max | — | Somente após uma tentativa High ter falhado ou após escalonamento aprovado pelo Terra; Max não é o padrão |
| Final diff review | Terra novo | High | Sessão fresca independente que não escreveu o diff; verifica a Issue ativa, o plano, o diff, os testes e o contexto necessário |
| Security/compatibility audit | Terra novo | High | Sessão fresca independente; analisa segurança e compatibilidade, incluindo regressões, antes da validação final |

Regras de roteamento:

- **High é o padrão** para implementação normal focada.
- **Max é condicional**: exige tentativa High prévia falha ou escalonamento
  aprovado pelo Terra. Se o modelo Max não estiver configurado, parar e
  reportar a limitação em vez de trocar de provedor automaticamente.
- Tarefas pequenas (documentação curta, correção pontual) podem usar Low;
  tarefas médias (feature aditiva, testes de regressão) usam High; tarefas
  grandes (cross-module, refatoração arriscada) começam em High e só escalam
  para Max sob condição.
- Toda delegação deve melhorar materialmente custo, velocidade,
  especialização ou verificação independente; caso contrário, manter o
  trabalho no orquestrador.

### Operating model

O modelo operacional varia com o tamanho da tarefa:

- **Tarefa pequena** (correção pontual, documentação curta, inventário
  mecânico): um único agente apropriado executa e valida o trabalho; sem
  delegação em cadeia desnecessária.
- **Tarefa média** (feature aditiva, testes de regressão, mudança local): o
  Terra planeja e cria o ticket, o DeepSeek implementa e executa testes
  focados, e uma sessão nova de Terra revisa o diff de forma independente.
- **Tarefa grande e divisível** (cross-module, refatoração arriscada): o Terra
  primeiro cria os tickets independentes e os worktrees isolados, e somente
  então autoriza implementação paralela nos tickets sem sobreposição; a
  consolidação e a revisão final permanecem com o Terra e uma sessão nova de
  revisão.

## Ticket contract

Todo ticket delegado deve definir, antes da execução:

- **Objetivo:** o que deve ser alcançado, ligado à Issue ativa;
- **Arquivos ou componentes permitidos:** o executor não edita nada fora
  disso;
- **Comportamento exigido:** comportamento esperado e resultado de referência;
- **Restrições e comportamento preservado:** o que não pode mudar, incluindo
  compatibilidade e políticas do `AGENTS.md`;
- **Validação:** comandos e testes a executar e critério de aprovação;
- **Evidência de conclusão:** o que constitui entrega concluída;
- **Condições de parada:** quando o executor deve parar e retornar em vez de
  prosseguir.

O executor implementa somente o ticket aprovado. O orquestrador não deve
ampliar o ticket sem nova autorização, e o executor não deve resolver
ambiguidade adivinhando: deve parar e reportar quando uma decisão for
necessária.

## Handoff format

O retorno de execução deve conter exatamente:

- **Trabalho realizado:** o que foi feito e o que foi intencionalmente
  preservado;
- **Arquivos alterados ou inspecionados;**
- **Testes e comandos realmente executados**, com os comandos reportados
  exatamente como digitados e executados;
- **Resultados exatos:** Passed, Failed, Blocked ou Not run, com a razão
  quando não executado;
- **Bloqueios, riscos, limitações e decisões não resolvidas;**
- **Desvios em relação ao ticket**, se houver.

Nunca escrever "passou", "aprovado", "verificado" ou equivalente para um
comando que não foi executado com sucesso. O orquestrador deve verificar cada
resultado delegado em vez de confiar na resposta do agente filho como
evidência verificada.

## Templates

Templates copiáveis para o ticket de executor, o retorno de execução e a
revisão independente. Preencher todos os campos; omitir um campo é um desvio
que deve ser declarado.

```markdown
### Ticket

**Objective:**
**Allowed files/components:**
**Required behavior:**
**Must preserve:**
**Validation:**
**Completion evidence:**
**Out of scope:**
**Stop and return when:**
```

```markdown
### Execution result

**Status:** Completed | Partial | Blocked | Failed
**Work performed:**
**Files changed:**
**Commands and tests:**
**Outcomes:**
**Preserved behavior:**
**Risks and limitations:**
**Deviations:**
**Decisions required:**
```

```markdown
### Independent review

**Verdict:** Ready | Ready with notes | Changes required | Blocked
**Confirmed blocking findings:**
**Confirmed non-blocking findings:**
**Missing evidence:**
**Optional suggestions:**
**Required corrections and validation:**
```

## One-writer rule

- Apenas um agente pode escrever em um worktree por vez.
- Investigações e revisões somente leitura podem operar em paralelo quando não
  interferem no escritor ativo.
- Implementação paralela exige worktrees isolados e tickets sem sobreposição.
- Issues dependentes que alteram arquivos sobrepostos devem ser executadas
  sequencialmente, partindo de uma base atualizada após a integração do
  predecessor, salvo demonstração de independência e aprovação do usuário.

## Shared-context rules

- A Issue ativa, o plano aprovado, os contratos e a documentação vigente são
  as fontes de verdade compartilhadas.
- Um agente não deve tratar sugestão de IA, nota histórica, comentário de
  revisão ou conversa anterior como requisito aprovado; deve confirmar contra
  a Issue ativa e o repositório atual.
- Contexto relevante de uma sessão (decisões, restrições, comandos de
  validação) deve ser passado explicitamente no ticket, porque um agente filho
  inicia com contexto fresco.
- Não varrer repetidamente o repositório inteiro: referenciar arquivos,
  seções e artifacts específicos em vez de duplicar contexto extenso no
  ticket ou no retorno. O contexto compartilhado permanece no repositório;
  o ticket aponta para ele.
- O orquestrador deve verificar o base do worktree e confirmar que ele parte
  do commit pretendido antes da execução.

## Review and correction loop

1. O executor implementa o plano aprovado e executa testes focados.
2. O executor executa a suíte completa e as verificações aplicáveis antes da
   pull request.
3. O revisor independente revisa a Issue ativa, o plano aprovado, os arquivos
   alterados, o diff, os testes e o contexto necessário.
4. O revisor classifica cada observação como achado bloqueante, não
   bloqueante, evidência ausente, sugestão opcional ou sem problema, com
   arquivo, evidência, comportamento esperado, impacto e correção mínima.
5. O executor corrige somente os achados confirmados e aprovados.
6. As validações finais são registradas com resultados exatos.
7. O revisor não aprova o próprio trabalho; revisão exige sessão ou agente
   que não escreveu o diff.

## Failure and escalation policy

- Limitar tentativas: após duas tentativas falhas para a mesma causa não
  resolvida, parar e devolver o bloqueio ao usuário, sem criar loop de
  agentes.
- Uma falha em uma tentativa High pode justificar escalonamento para Max
  somente com aprovação do Terra, nunca automaticamente.
- Bloqueios, limitações e comandos não executados devem ser reportados com o
  comando exato, o motivo da não execução, o que permanece não verificado, o
  risco residual e como um mantenedor pode executá-lo.
- Nunca usar reset destrutivo, `clean` destrutivo, force push ou reescrita de
  histórico como atalho de recuperação.

## Cost and context control

- Delegar apenas o que agrega valor; trabalho trivial permanece no
  orquestrador.
- Preferir o menor reasoning que atenda à tarefa: Low para rotinas triviais,
  High como padrão, Max somente sob condição.
- Priorizar testes focados durante a implementação e executar a suíte
  completa antes da pull request.
- Usar tickets autossuficientes para reduzir idas e vindas, mantendo o
  contexto necessário dentro do ticket.
- Não manter loops de retry infinitos nem retries automáticos que aumentem
  custo sem progresso.

## Git and GitHub delivery

- As ações de Git e GitHub ocorrem dentro da autorização permanente e da
  Issue ativa: criar branches de trabalho, commits, push para branches que
  não sejam `main`, abrir e atualizar pull requests e responder a revisões.
- Merge exige autorização explícita do usuário para a pull request específica;
  o orquestrador não faz merge por padrão.
- Antes de ações de escrita, inspecionar `git status`, o diff completo e
  garantir que apenas arquivos aprovados estejam incluídos.
- Usar mensagens de commit no estilo Conventional Commits e descrições de
  pull request proporcionais ao tamanho e risco, vinculadas à Issue com
  `Closes #<número>` somente quando a mudança conclui integralmente a Issue.
- Nunca incluir segredos, caminhos absolutos locais, caches, logs ou
  arquivos temporários em arquivos rastreados, commits ou pull requests.

## Manual fallback

Quando a orquestração não é viável ou não agrega valor:

- o trabalho permanece no fluxo supervisionado padrão: Issue ativa, plano
  aprovado, um executor (humano ou agente único), validação e revisão;
- qualquer decisão não resolvida ou bloqueio recorrente é devolvida ao
  usuário;
- a automação auxilia, mas não é fonte autônoma de verdade; escopo,
  decisões, resultados e aprovação continuam baseados em Issues, código,
  testes, contratos e revisão supervisionada.

## End-to-end example

Cenário: Issue aprovada exige uma correção confirmada de bug na API e uma
atualização documental relacionada, ambas sem mudança de produto, modelo,
dados ou Docker.

1. O Terra cria um Traycer Task e um worktree isolado a partir do base
   pretendido.
2. O Terra (Medium) inspeciona o escopo, registra a evidência do bug e produz
   o plano aprovado.
3. O Terra abre um ticket de executor definindo objetivo, arquivos
   permitidos, comportamento exigido, restrições, validação, evidência de
   conclusão e condições de parada.
4. O OpenCode com DeepSeek V4 Flash (High) implementa somente o escopo do
   ticket e executa os testes focados da API.
5. O executor executa a suíte completa e as verificações aplicáveis antes da
   pull request, reportando comandos e resultados exatos.
6. O Terra (nova sessão, High) revisa o diff de forma independente e
   classifica as observações.
7. O executor corrige somente os achados confirmados e aprovados.
8. O Terra registra as validações finais com resultados exatos e abre a pull
   request vinculada à Issue, sem merge.
9. O merge aguarda autorização explícita do usuário.
