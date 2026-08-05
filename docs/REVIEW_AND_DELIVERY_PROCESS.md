# Processo de revisão e entrega

Este documento define o processo adotado após a publicação da primeira release
estável integrada do projeto. Ele complementa o histórico registrado em
[`PROCESSO_GIT_GITHUB.md`](../PROCESSO_GIT_GITHUB.md) e orienta a revisão
pré-entrega do desafio técnico.

## 1. Estado do projeto

As Fases 0–7 registram a construção da solução e resultaram na release
`v1.0.0`. Essa release reúne modelo, artefatos, API, testes, Docker,
observabilidade e documentação em um estado estável e reproduzível.

A publicação da release não representa, por si só, a submissão do desafio. O
estado atual é de revisão pré-entrega: o sistema existente será auditado,
testado, corrigido quando necessário e validado novamente antes da entrega.

```text
Fases 0–7
    desenvolvimento da primeira versão estável
        ↓
v1.0.0
    baseline integrada para revisão
        ↓
Ciclo 1
    revisão e diagnóstico
        ↓
Ciclo 2
    correções e estabilização
        ↓
Ciclo 3
    validação final e entrega
```

## 2. Dimensões de classificação

Cada demanda deve ser classificada por natureza, área afetada, ciclo e
prioridade. A classificação descreve o trabalho sem substituir o objetivo, as
evidências ou os critérios de aceite da Issue.

### Natureza

- **Review:** teste, auditoria ou investigação destinada a produzir evidências
  e achados. Uma review não autoriza automaticamente a implementação de uma
  correção ou melhoria.
- **Bug:** comportamento incorreto ou regressão confirmada em relação ao código,
  aos testes, ao contrato ou à documentação vigente.
- **Improvement:** mudança aditiva aprovada para melhorar qualidade, clareza,
  robustez, desempenho ou experiência de uso.
- **Maintenance:** manutenção de engenharia que não representa funcionalidade
  nova do produto, como Copilot, integrações com IA, templates, automações,
  dependências, CI ou organização do repositório.
- **Documentation:** correção ou expansão exclusivamente documental, incluindo
  README, contratos, OpenAPI, relatórios e documentos de governança.
- **Release:** versionamento, empacotamento, validação de candidato e preparação
  da entrega.

Cada Issue deve possuir uma natureza principal. Trabalhos distintos devem ser
separados quando exigirem critérios de aceite ou riscos diferentes.

### Áreas

Uma Issue pode afetar uma ou mais áreas:

- API;
- Model;
- Data;
- Testing;
- Docker;
- CI;
- Documentation;
- Governance;
- Repository;
- Automation.

### Prioridade

- **High:** bloqueia a entrega, compromete resultado confiável, segurança,
  reprodutibilidade ou fluxo principal.
- **Medium:** possui impacto relevante, mas existe alternativa ou o problema não
  bloqueia imediatamente a entrega.
- **Low:** melhoria não bloqueante, limpeza ou refinamento de menor impacto.

Enquanto as labels correspondentes não estiverem configuradas no GitHub, a
classificação deve ser registrada explicitamente no corpo da Issue e da pull
request.

## 3. Ciclos de trabalho

### Ciclo 1 — Revisão e diagnóstico

Objetivo: observar o comportamento real da `v1.0.0` e produzir evidências antes
de alterar o sistema.

Inclui:

- revisão de API, OpenAPI, dados, modelo, testes, operação e documentação;
- testes válidos, inválidos, extremos e fora da distribuição quando aplicável;
- análise de consistência entre implementação, testes e documentação;
- registro de riscos, limitações, divergências e pontos não verificados;
- abertura de Issues específicas para bugs confirmados ou melhorias aprovadas.

A review deve registrar o que foi executado e observado. Recomendações, hipóteses
e possibilidades futuras permanecem separadas de requisitos aprovados.

### Ciclo 2 — Correções e estabilização

Objetivo: corrigir problemas confirmados e implementar somente melhorias
aprovadas a partir das evidências do Ciclo 1.

Inclui:

- correções de bugs e regressões;
- hardening de validações e comportamento operacional;
- melhorias aditivas aprovadas;
- testes de regressão e verificação de casos de borda;
- alinhamento entre código, contratos, OpenAPI e documentação;
- avaliação explícita de compatibilidade, riscos e reversibilidade.

Backward compatibility é o padrão. Mudanças incompatíveis exigem decisão
registrada, versionamento adequado, plano de migração e rollback.

### Ciclo 3 — Validação final e entrega

Objetivo: validar o estado completo destinado à submissão do desafio técnico.

Inclui:

- execução da bateria final de testes automatizados e manuais;
- validação em ambiente limpo e revisão da reprodutibilidade;
- verificação de documentação, contratos, versões, artefatos e hashes;
- revisão das limitações e das decisões técnicas que devem ser defendidas;
- build e validação final da imagem Docker de runtime;
- verificação dos endpoints públicos, healthcheck, execução sem privilégios e
  condições operacionais documentadas;
- preparação da versão e das notas destinadas à entrega.

A imagem Docker final faz parte deste ciclo, mas não deve incorporar dados
brutos, notebooks ou dependências offline apenas para representar todo o
repositório. O objetivo é empacotar e validar o runtime executável da solução,
preservando a separação já adotada entre serving e análises offline.

## 4. Fluxo entre review, achado e implementação

O fluxo esperado é:

```text
Issue de Review
    ↓
evidência observada e reproduzível
    ↓
classificação do achado
    ├── comportamento incorreto → Issue de Bug
    ├── mudança benéfica aprovada → Issue de Improvement
    ├── divergência documental → Issue de Documentation
    └── manutenção de engenharia → Issue de Maintenance
        ↓
branch específica
        ↓
pull request vinculada à Issue
        ↓
testes, revisão e merge supervisionado
```

Uma Issue de Review pode ser encerrada após produzir suas evidências e abrir as
Issues derivadas necessárias. Ela não deve acumular silenciosamente correções de
naturezas diferentes.

## 5. Manutenção de IA e automação

Copilot, ChatGPT, templates, automações de revisão, rulesets e outras
configurações de engenharia devem ser tratados como **Maintenance** nas áreas
**Repository** ou **Automation**.

Essas ferramentas podem auxiliar leitura, implementação e revisão, mas não são
fontes autônomas de verdade. Escopo, decisões, resultados e aprovação continuam
baseados em Issues, código, testes, contratos e revisão supervisionada.

Mudanças de manutenção não devem receber numeração de fase de desenvolvimento
nem ser apresentadas como novas funcionalidades do sistema de predição.

## 6. Issues, branches e pull requests

Cada mudança deve seguir o fluxo:

1. abrir uma Issue com objetivo, classificação, escopo, critérios de aceite,
   validação e fora do escopo;
2. criar uma branch curta a partir de `main`;
3. implementar somente o escopo aprovado;
4. abrir uma pull request vinculada à Issue;
5. registrar comandos executados, resultados, riscos e pontos não verificados;
6. tratar observações de revisão;
7. realizar merge somente após aprovação explícita.

A pull request deve usar `Closes #<número>` apenas quando concluir integralmente
a Issue relacionada. Referências sem fechamento automático devem usar uma
formulação descritiva, como `Relacionado a #<número>`.

## 7. Relação com milestones e acompanhamento

Os milestones planejados são:

- `Ciclo 1 — Revisão e diagnóstico`;
- `Ciclo 2 — Correções e estabilização`;
- `Ciclo 3 — Validação final e entrega`.

As labels e milestones são metadados de acompanhamento. A definição completa do
trabalho permanece na Issue. Um GitHub Project somente será adotado caso o
volume e a paralelização do backlog justifiquem uma camada adicional.

## 8. Critério de conclusão

A submissão somente será considerada pronta quando:

- as reviews planejadas estiverem concluídas;
- bugs bloqueantes e correções aprovadas estiverem resolvidos;
- testes automatizados e manuais relevantes estiverem aprovados;
- documentação e comportamento estiverem consistentes;
- artefatos, versões e hashes estiverem verificados;
- a imagem Docker final estiver construída e validada;
- limitações e pontos não verificados estiverem explicitamente registrados;
- a revisão final supervisionada estiver aprovada.

Nenhuma ferramenta de IA, check isolado ou release anterior substitui esses
critérios conjuntos.
