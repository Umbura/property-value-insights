# Consolidação do Ciclo 1 — revisão e diagnóstico

## Escopo e decisão

Este documento consolida as Reviews #34–#39 coordenadas pela Issue #33. O Ciclo
1 foi concluído com evidências suficientes para distinguir comportamento
aprovado, limitações confirmadas, melhorias já implementadas, trabalho futuro e
pendências da entrega final.

A consolidação não altera API, modelo, artefato, manifesto, hashes, dados brutos,
previsões, Dockerfile ou versão da release. Ela também não apresenta trabalho
aberto como concluído.

**Decisão:** o Ciclo 1 pode ser encerrado. A próxima etapa obrigatória da entrega
é a Issue #68, que concentra a lapidação do repositório, a validação limpa, a nova
release e a imagem Docker final.

## Baseline preservado

- release do projeto: `1.0.0`;
- contrato da API: `0.5.0-rc1`;
- modelo servido: `property_value_hist_gradient_boosting_physical`;
- versão do modelo: `0.4.0-rc1`;
- período mais recente: diagnóstico previamente inspecionado, não test set final
  intocado;
- variante demográfica: experimento histórico, não modelo servido;
- backward compatibility: padrão para mudanças posteriores.

## Reviews concluídas

| Review | Resultado consolidado | Evidência principal | Integração |
| --- | --- | --- | --- |
| #34 — contrato e OpenAPI | baseline do contrato registrado e backlog documental separado | Issue #34 | Issues #43–#48 e PRs #49, #56–#60 |
| #35 — testes manuais da API | 22 testes; 17 aprovados; 5 limitações; nenhum bug contratual confirmado | `c1-2-api-manual-tests.md` | PR #61 |
| #36 — comportamento do modelo | métricas reproduzidas; degradação de alto valor, geográfica, temporal e OOD quantificada | `c1-3-model-review.md` e `evidence/c1-3/` | PR #63 |
| #37 — qualidade dos dados | anomalias, proxy, consistências, cobertura e dependência entre chaves documentados sem alterar os dados | `c1-4-data-quality-review.md` e `evidence/c1-4/` | PRs #66 e #67 |
| #38 — documentação e governança | README, versões, dicionário, model card, histórico, links e decisões de serving auditados | `c1-5-documentation-governance-review.md` e `evidence/c1-5/` | PR #69 |
| #39 — Docker e operação | build, isolamento, integridade, endpoints, concorrência, logs e métricas validados em Linux | `c1-6-docker-operations-review.md` e `evidence/c1-6/` | PR #71 |

Todas as Issues #34–#39 estão encerradas como `completed`.

## Conclusões transversais

### API e contrato

Os endpoints públicos, schemas e status codes observados permaneceram
compatíveis. A bateria manual não confirmou bug contratual, divergência
documental ou instabilidade. Foram confirmadas limitações de domínio e cobertura:
ZIP desconhecido, coordenadas fora da região, ano futuro e combinações extremas
podem ser formalmente aceitos sem comunicar risco operacional.

As melhorias documentais da Review #34 receberam Issues próprias e já foram
integradas:

- #43 / PR #49 — tags, summaries e descriptions;
- #44 / PR #56 — exemplos, descrições e unidades;
- #45 / PR #57 — semântica de `/health`;
- #46 / PR #58 — contrato e rastreabilidade do batch;
- #47 / PR #59 — identidade e versões em `/model-info`;
- #48 / PR #60 — métricas, limitações e decisão de serving em linguagem humana.

Essas implementações ocorreram com rastreabilidade própria; não foram mudanças
silenciosas da Issue coordenadora.

### Modelo

O modelo físico `0.4.0-rc1` permaneceu aprovado para serving. Não foram observadas
previsões negativas ou não finitas, mas a review confirmou:

- subestimação progressiva na cauda superior;
- erro elevado acima de US$ 1 milhão e especialmente acima de US$ 2 milhões;
- heterogeneidade por ZIP e período;
- piora mensal no diagnóstico;
- aceitação silenciosa de entradas potencialmente OOD;
- intervalos empíricos úteis como diagnóstico, sem garantia individual.

Não foi confirmado um bug funcional isolado que justificasse substituir o
artefato. Challengers e promoção futura permanecem na Issue #62.

### Dados

Os CSVs brutos permaneceram intocados. A investigação confirmou:

- 18 inconsistências temporais já removidas pelo pipeline;
- um registro com 33 quartos, provável erro de entrada sem fonte primária para
  uma correção segura;
- registros com zero quartos ou zero banheiros de semântica heterogênea;
- identidade de áreas internas reproduzida no histórico e nos exemplos futuros;
- `hous_val_amt` como proxy forte de nível de preço por ZIP, com origem e vintage
  insuficientemente documentados;
- 98 chaves `id` presentes no desenvolvimento e no diagnóstico, sem leakage
  direto confirmado, mas com dependência que merece análise de sensibilidade;
- cobertura estrutural e univariada dos exemplos futuros, sem prova de cobertura
  multivariada ou de acurácia.

A verificação futura das anomalias e da independência por chave está na Issue #65.

### Documentação e governança

A documentação atual distingue projeto, API, modelo e artefato; explicita a
seleção por governança do modelo físico; mantém a variante demográfica como
experimento histórico; registra limitações de alto valor, tempo, geografia e OOD;
e recomenda revisão humana para usos consequenciais.

O repositório foi confirmado como público e os links relativos auditados. A
organização física dos documentos históricos foi deliberadamente adiada para a
Issue #68, evitando movimentações durante o Ciclo 1.

### Docker e operação

A imagem atual foi validada como base técnica para a etapa final, sem equivaler à
imagem publicada de entrega:

- build sem cache concluído;
- execução como usuário não root;
- root filesystem somente leitura com `/tmp` em tmpfs;
- `no-new-privileges` ativo;
- healthcheck e endpoints disponíveis;
- artefato ausente, manifesto inválido e hash divergente impedem startup;
- 150 requisições de carga moderada concluídas com respostas estáveis;
- request IDs, logs estruturados da aplicação e métricas Prometheus observados.

Permanecem limitações não bloqueantes: stream misto entre JSON e texto do Uvicorn,
tracebacks detalhados em falhas de startup e imagem local com aproximadamente
490 MB. Elas estão registradas na Issue #70.

## Backlog derivado e prioridade

### Concluído durante a janela de revisão

- #43–#48: melhorias documentais e aditivas do contrato OpenAPI, todas integradas.

### Pendente para decisão ou estabilização

- #64 — sinais estruturados de cobertura, risco, warnings e revisão humana na API.
  É a principal melhoria funcional registrada e ainda não implementada. Sua
  execução permanece pendente de priorização, e ela não deve ser apresentada como
  concluída na entrega final.

### Trabalho futuro não bloqueante

- #62 — challengers para reduzir degradação em imóveis de alto valor;
- #65 — verificação de anomalias históricas e avaliação agrupada por chave `id`;
- #70 — hardening de logs e análise segura do tamanho da imagem.

### Entrega final

- #68 — lapidar a árvore do repositório, revisar o README final, validar instalação
  limpa e CI, preparar release e publicar/verificar a imagem Docker de entrega.

## Limitações e pontos não verificados

O encerramento do Ciclo 1 não afirma que foram verificados:

- desempenho em dados externos ou posteriores;
- fairness entre atributos protegidos;
- causalidade das features ou explicações;
- produção real, tráfego real, TLS, autenticação, autoscaling ou SLO;
- soak test prolongado ou carga distribuída;
- imagem multi-arquitetura;
- digest de registry, pull por digest e labels OCI finais;
- SBOM ou scanner de vulnerabilidades da imagem;
- secret scan abrangente de todos os logs;
- correção autoritativa do registro de 33 quartos;
- cobertura multivariada OOD das entradas futuras;
- implementação dos controles da Issue #64.

Esses limites devem permanecer visíveis na apresentação e na release final.

## Critérios de encerramento da Issue #33

- [x] todas as reviews confirmadas do Ciclo 1 foram abertas e concluídas;
- [x] cada review possui escopo, evidências e fora do escopo;
- [x] achados confirmados foram classificados sem implementação silenciosa;
- [x] bugs, improvements e pendências confirmadas possuem Issues próprias;
- [x] limitações e pontos não verificados foram registrados;
- [x] o Ciclo 1 produziu evidência suficiente para orientar estabilização e entrega;
- [x] modelo, artefato, manifesto, hashes, dados brutos e previsões permaneceram
  preservados pela consolidação.

## Próximo passo

Após o merge desta consolidação, executar a Issue #68. A release e a imagem Docker
finais somente devem ser publicadas depois da lapidação, da revisão independente
e da CI verde no estado final do repositório.
