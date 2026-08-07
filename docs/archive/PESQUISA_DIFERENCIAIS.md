# Pesquisa de diferenciais para o desafio de AI/MLOps

Data da pesquisa: 02/08/2026

Este documento registra uma pesquisa comparativa realizada antes da
implementacao do desafio de previsao de precos de imoveis. Foram consultados
repositorios publicos no GitHub, relatos de candidatos e profissionais no
Reddit, documentacao tecnica de referencia e artigos sobre sistemas de ML em
producao.

O objetivo nao e copiar uma arquitetura pronta. E identificar o que costuma
aparecer em projetos semelhantes, o que realmente demonstra maturidade e o que
deve ser evitado para nao transformar um desafio de sete dias em uma
arquitetura artificialmente grande.

## Resumo executivo

O minimo esperado neste desafio e relativamente claro: analise dos dados,
modelo de regressao, avaliacao de generalizacao, estrategia de deploy,
aprendizado continuo e comunicacao com stakeholders. O e-mail acrescenta que a
empresa observara backend Python, FastAPI ou Django, Docker, observabilidade e
integracao de componentes ou APIs de IA.

A pesquisa indica que os diferenciais mais defensaveis sao:

1. Avaliar generalizacao de forma realista, usando a ordem temporal das vendas
   e verificando estabilidade entre regioes ou CEPs, em vez de depender apenas
   de uma divisao aleatoria.
2. Criar um contrato de dados verificavel para o merge fisico-demografico,
   incluindo cobertura de CEP, tipos, faixas validas e comportamento para dados
   futuros sem correspondencia.
3. Traduzir o erro do modelo para uma decisao de negocio: erro em dolares,
   erro relativo por faixa de preco, desempenho por regiao e, se validado,
   intervalos de previsao em vez de apenas um valor pontual.
4. Entregar um model card curto e uma avaliacao por segmentos, deixando claro
   onde o modelo funciona, onde falha e que uso nao deve ser feito dele.
5. Implementar observabilidade ligada a falhas concretas: schema, dados
   ausentes, drift de entrada, distribuicao das previsoes, latencia, erros e
   versao do modelo.
6. Tornar treinamento, artefato e API reproduziveis e rastreaveis, com criterio
   explicito de promocao e rollback.
7. Usar a integracao de IA somente como uma camada limitada de explicacao
   baseada em evidencias do modelo. O provedor de IA nao deve inventar fatores
   nem alterar a previsao numerica.

O diferencial nao sera a quantidade de ferramentas. Sera a coerencia entre
risco, evidencia, decisao de negocio e operacao.

## Como a pesquisa foi feita

- GitHub: busca por previsao de precos de imoveis, servico de modelos, API,
  Docker, monitoramento, drift e MLOps.
- Reddit: relatos de take-home assignments em `r/datascience`, `r/mlops` e
  `r/cscareerquestions`.
- Metodologia: documentacao do scikit-learn e do Google, artigos de pesquisa
  sobre testes de ML, model cards, explicabilidade, aprendizado continuo e
  intervalos de previsao.

Os repositorios e relatos sao sinais praticos, nao uma amostra estatistica de
todos os candidatos. Reddit e especialmente util para entender experiencias,
mas suas opinioes nao substituem uma referencia tecnica.

## Repositorios comparaveis

### 1. Projetos de previsao de precos

**House Price Prediction Project for a US-based housing company**
([ChaitanyaC22/House-Price-Prediction-Project-for-a-US-based-housing-company](https://github.com/ChaitanyaC22/House-Price-Prediction-Project-for-a-US-based-housing-company))

O repositorio concentra EDA, limpeza, engenharia de atributos e comparacao de
regressoes Ridge e Lasso. Representa o caminho comum de um projeto de ciencia
de dados: notebook, modelo e metricas.

Licao: um modelo de regressao bem explicado e uma boa base, mas sozinho nao
responde ao que o e-mail pede sobre API, Docker, observabilidade e ciclo de
vida.

**house_price_prediction**
([Rishiraj8/house_price_prediction](https://github.com/Rishiraj8/house_price_prediction))

Combina um frontend React com uma API Flask e um regressor Random Forest. E um
exemplo de projeto de portfolio que prioriza a demonstracao visual e a
interacao do usuario.

Licao: uma interface pode ser interessante, mas nao deve consumir o tempo que
precisamos usar para validacao, contrato de dados e operacao do modelo. O
desafio nao pede frontend.

### 2. Projetos MLOps com previsao de precos

**MLOps House Price Prediction**
([srnurizki/mlops-house-price-prediction](https://github.com/srnurizki/mlops-house-price-prediction))

O README descreve Docker Compose com PostgreSQL, MLflow, treinador, API
FastAPI e monitor separado. A estrutura cobre varias fases do ciclo de vida.
Ao mesmo tempo, o proprio README informa que algoritmo, features e metricas
do modelo ainda nao estavam documentados.

Licao: arquitetura e componentes nao substituem evidencia. Um projeto com
menos servicos, mas com metricas, decisoes e testes claros, pode ser mais
convincente que uma arquitetura maior sem resultados verificaveis.

**MLOps-Model-Monitoring**
([rilufiyy/MLOps-Model-Monitoring](https://github.com/rilufiyy/MLOps-Model-Monitoring))

O projeto apresenta separacao entre dados, modelos, utilitarios, API, logs,
MLflow, FastAPI, Docker e monitoramento basico de drift. Tambem distingue
funcionalidades atuais de melhorias futuras, como CI/CD e monitoramento
estatistico mais avancado.

Licao: separar explicitamente o que foi implementado do que e proposta futura
e uma pratica importante para o nosso README. Nao devemos apresentar
retreinamento automatico ou cloud como se existissem quando forem apenas
desenhados.

**Rental Price Prediction - End-to-End MLOps Project**
([Issa-db/Rental-Price-Prediction-End-to-End-MLOps-Project](https://github.com/Issa-db/Rental-Price-Prediction-End-to-End-MLOps-Project))

O repositorio organiza configuracao, dados, pipeline de modelo, inferencia,
logs, testes, API e containerizacao. Usa Flask, Celery, Docker e bibliotecas
de validacao e persistencia.

Licao: modularidade, testes e separacao de responsabilidades sao sinais mais
uteis para uma vaga de AI/MLOps do que simplesmente escolher o modelo com a
maior pontuacao.

**House-price-prediction com Kubeflow/Azure DevOps**
([debago/House-price-prediction_Kubeflow_Azure_devops_CI-CD](https://github.com/debago/House-price-prediction_Kubeflow_Azure_devops_CI-CD))

O projeto apresenta ingestion, validacao, feature engineering, treinamento,
avaliacao, drift, gatilho de retreinamento, MLflow, Kubeflow, Kubernetes,
Helm, API e CI/CD.

Licao: a cobertura e ampla, mas a quantidade de ferramentas nao e um
diferencial automaticamente. Para o nosso prazo, Kubernetes, Kubeflow,
MLflow, cloud e CI/CD completos aumentariam o risco de incompatibilidade e
documentacao superficial. Devemos adotar somente componentes que resolvam um
problema demonstrado.

### 3. Projetos de monitoramento

**Production-Grade Fraud Detection System with API, Docker and Drift
Monitoring**
([mauryag113/Production-Grade-Fraud-Detection-System-with-API-Docker-Drift-Monitoring](https://github.com/mauryag113/Production-Grade-Fraud-Detection-System-with-API-Docker-Drift-Monitoring))

O README mostra um fluxo com FastAPI, Docker, logs de previsao e drift por KS
ou PSI, alem de metricas especificas do problema de fraude.

Licao: monitoramento deve estar associado ao risco do dominio. Para precos,
nao basta dizer "detectar drift": precisamos definir quais mudancas importam,
como detectar a falta de dados de entrada, como observar a distribuicao de
precos previstos e como avaliar qualidade quando o preco real ainda nao
chegou.

## O que profissionais relatam sobre take-home assignments

### Clareza e justificativa vencem complexidade sem explicacao

No relato [Take home assessments during Interviews?](https://www.reddit.com/r/datascience/comments/1557wv5/take_home_assessments_during_interviews/), uma pessoa descreve varios
projetos de uma semana envolvendo limpeza e modelagem. Um comentario destaca
que o teste deve avaliar habilidades centrais, logica e capacidade de comunicar
resultados, e nao uma semana de trabalho sem limite.

Aplicacao ao nosso caso: o README deve funcionar como um relatorio de decisoes.
Cada etapa precisa dizer o que foi observado, qual hipotese foi levantada,
qual teste foi feito e qual decisao resultou dele.

No relato [Solution completeness and take home assignments for
interviews?](https://www.reddit.com/r/datascience/comments/1i2mh17/solution_completeness_and_take_home_assignments/), o autor descreve um
escopo que inclui limpeza, dados adicionais, engenharia de atributos e varios
modelos. A resposta mais util recomenda explicitar o processo, construir
baseline, declarar premissas e dizer o que seria explorado com mais tempo.

Aplicacao ao nosso caso: uma secao "escopo e proximos passos" aumenta a
credibilidade. Nao precisamos fingir que entregamos um sistema de meses em
sete dias.

No relato [DS take home assignment requires building an entire
project](https://www.reddit.com/r/datascience/comments/nurs3c/ds_take_home_assignment_requires_building_an_entire_project_using_skills_i_dont_have/),
o desafio inclui banco, treinamento e API. Os comentarios observam que uma
API simples e viavel, mas que um sistema completo de producao e muito maior que
um teste curto.

Aplicacao ao nosso caso: FastAPI e Docker devem ser um MVP executavel e
compreensivel. O deploy de producao deve ser documentado, pois o README nao
exige que ele seja implementado.

No relato [Skill test for MLOps Engineer / ML Engineer](https://www.reddit.com/r/mlops/comments/1ff633a/),
um profissional descreve um teste limitado a duas a quatro horas e menciona
que pediu citacoes das fontes usadas. Isso e um sinal de que capacidade de
pesquisa, automacao e justificativa fazem parte da avaliacao, nao apenas o
resultado do modelo.

No relato [What does a typical MLOps interview really look like?](https://www.reddit.com/r/mlops/comments/1ltum3d/),
aparecem como temas recorrentes CI/CD, containerizacao, infraestrutura como
codigo, monitoramento e system design. O relato e anedotico e nao define o
processo desta empresa, mas e coerente com os pontos citados no nosso e-mail.

## Referencias metodologicas

### Leakage, pipeline e avaliacao

O guia do scikit-learn sobre [common pitfalls and recommended
practices](https://scikit-learn.org/stable/common_pitfalls.html) recomenda
separar os dados antes de ajustar transformacoes e usar `Pipeline` para
reduzir risco de vazamento e inconsistencias entre treino e inferencia.

Aplicacao:

- o merge e as transformacoes devem ter etapas reproduziveis;
- estatisticas aprendidas, como imputacao e codificacao, devem vir apenas do
  treino;
- o conjunto temporal final nao deve orientar escolhas de modelo;
- o mesmo pre-processamento deve ser usado no notebook e na API.

### Generalizacao temporal e training-serving skew

As [Rules of Machine Learning do Google](https://developers.google.com/machine-learning/guides/rules-of-ml)
recomendam testar com dados posteriores ao periodo usado no treinamento e
monitorar diferencas entre treino e servico. A documentacao de
[productionization](https://developers.google.com/machine-learning/managing-ml-projects/production)
tambem lista drift de features, drift de previsoes, tipos invalidos, latencia,
indisponibilidade e qualidade do modelo como sinais de monitoramento.

Aplicacao:

- usar `date` para construir uma separacao temporal, mas nao como feature final
  se ela nao existir nos exemplos futuros;
- registrar a distribuicao observada no treino para comparar com entradas da
  API;
- testar a consistencia do contrato entre notebook e inferencia;
- acompanhar a idade e a versao do modelo.

### Testes de sistemas de ML

O artigo [The ML Test Score: A Rubric for ML Production
Readiness](https://research.google/pubs/whats-your-ml-test-score-a-rubric-for-ml-production-systems/)
propoe testes e necessidades de monitoramento para avaliar prontidao de
sistemas de ML. A ideia central e tratar o sistema como mais do que um
algoritmo: dados, treinamento, servico, monitoramento e confiabilidade tambem
precisam ser verificados.

Aplicacao pratica para o desafio:

- teste de schema e ranges das entradas;
- teste do merge por CEP;
- teste de ausencia de NaN no artefato final;
- teste de que a API aceita uma amostra valida e rejeita uma invalida;
- teste de que o artefato carregado possui versao e conjunto de features;
- teste de latencia e resposta do health check;
- teste de regressao para garantir que uma nova versao nao seja promovida sem
  atingir um criterio minimo.

### Model cards, data cards e riscos de uso

O trabalho [Model Cards for Model Reporting](https://research.google/pubs/model-cards-for-model-reporting/)
recomenda acompanhar modelos com documentacao de uso pretendido, desempenho e
limites, inclusive em grupos ou contextos relevantes. O [Data Cards
Playbook](https://developers.google.com/learn/pathways/data-cards-playbook)
aplica uma ideia semelhante para documentar origem, finalidade, contexto e
limites dos dados.

Aplicacao:

- criar um model card curto em `reports/model_card.md`;
- documentar que o dataset e anonimizado e representa uma regiao especifica;
- medir erros por faixa de preco e por CEP ou agrupamento geografico;
- tratar variaveis demograficas por CEP como possiveis proxies sociais, sem
  fazer conclusoes causais sobre pessoas ou comunidades;
- declarar que a previsao e uma estimativa, nao uma avaliacao imobiliaria nem
  uma recomendacao automatica de credito.

O [NIST AI Risk Management Framework](https://airc.nist.gov/airmf-resources/airmf/)
reforca que validade, confiabilidade, transparencia, explicabilidade e
monitoramento devem ser considerados ao longo do ciclo de vida. Nao e
necessario transformar o desafio em uma auditoria formal, mas o model card e
uma forma proporcional de demonstrar essa preocupacao.

### Explicabilidade

O artigo [A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874)
apresenta SHAP como uma abordagem para interpretar contribuicoes de features.
Para este desafio, SHAP pode gerar uma explicacao tecnica e rastreavel para
uma previsao. Uma eventual API de IA generativa deve apenas converter essa
evidencia em linguagem de negocio, nunca criar uma justificativa livre ou
alterar o valor previsto.

### Incerteza da previsao

O artigo [Conformalized Quantile Regression](https://proceedings.neurips.cc/paper_files/paper/2019/hash/5103c3584b063c431bd1268e9b5e76fb-Abstract.html)
mostra uma forma de construir intervalos de previsao calibrados usando
conformal prediction. Essa e uma referencia para a ideia de retornar, por
exemplo, uma estimativa central e uma faixa de valores.

Aplicacao com cautela:

- a faixa deve ser avaliada por cobertura e largura, nao apenas exibida;
- a documentacao deve deixar claro que a garantia depende das hipoteses do
  metodo e da estabilidade do processo de dados;
- se a implementacao ameacar a qualidade da entrega principal, fica como
  extensao documentada, nao como enfeite incompleto.

### Ciclo operacional de ML

O estudo [Operationalizing Machine Learning: An Interview Study](https://arxiv.org/abs/2209.09125)
descreve o ciclo de coleta e rotulagem, experimentacao, avaliacao em etapas de
deploy e monitoramento de degradacao. O trabalho [We Have No Idea How Models
will Behave in Production until Production](https://arxiv.org/abs/2403.16795)
resume a tensao entre velocidade, visibilidade e versionamento.

Aplicacao: nossa proposta de aprendizado continuo deve ser um fluxo de
promocao controlada, e nao apenas uma frase dizendo "retreinar
automaticamente".

## O que fazer e o que evitar

### Fazer

- registrar o contrato de dados e o resultado do merge antes de modelar;
- usar baseline e comparar modelos com o mesmo protocolo de avaliacao;
- justificar `id`, `date`, `zipcode` e as features demograficas;
- medir MAE e erro em dolares, alem de RMSE, RMSLE e R2;
- avaliar por faixa de preco e localizacao;
- mostrar o caminho do artefato, do treinamento ate a API;
- incluir testes pequenos, mas executaveis;
- logar versao do modelo, latencia, erros e caracteristicas de entrada;
- separar no README o que foi implementado, proposto e nao foi feito;
- documentar limitacoes e proximos passos;
- citar fontes tecnicas usadas durante a pesquisa.

### Evitar

- escolher o vencedor apenas por R2 ou por uma unica divisao aleatoria;
- usar `id` como sinal de valor ou usar `date` no servico quando os exemplos
  futuros nao possuem essa coluna;
- ajustar imputacao, codificacao ou selecao de features antes da separacao;
- chamar um sistema de "production-ready" sem testes e evidencias;
- adicionar AWS, Kubernetes, Kubeflow, Kafka, feature store ou MLflow apenas
  para aumentar a lista de tecnologias;
- criar uma interface visual antes de resolver avaliacao e reprodutibilidade;
- usar LLM para gerar explicacoes que nao possam ser conferidas nos dados;
- inventar monitoramento de qualidade quando o preco real ainda nao esta
  disponivel;
- declarar que o modelo mede causalidade ou valor justo de um imovel;
- simular dados de producao e apresentar o resultado como observacao real;
- colocar chaves, tokens, credenciais ou arquivos pessoais no repositorio.

## Diferenciais mapeados para as etapas do desafio

| Diferencial | Etapa principal | Valor para a avaliacao | Custo e risco | Decisao |
| --- | --- | --- | --- | --- |
| Contrato de dados, validacao do merge e relatorio de qualidade | Analise | Demonstra engenharia e evita falhas silenciosas | Baixo | Obrigatorio |
| Baseline, modelo final e comparacao temporal | Modelagem | Demonstra generalizacao e criterio de escolha | Medio | Obrigatorio |
| Avaliacao por CEP/faixa de preco e ablation sem demografia | Modelagem/stakeholders | Mostra estabilidade e evita conclusao superficial | Medio | Forte recomendacao |
| MAE em dolares, erro relativo e exemplos de negocio | Stakeholders | Traduz o modelo para quem toma decisao | Baixo | Obrigatorio |
| Intervalo de previsao calibrado | Modelagem/API | Mostra consciencia de risco e incerteza | Medio/alto | Implementar se validado |
| Model card e documentacao de limites | Stakeholders/governanca | Aumenta transparencia com pouco custo | Baixo | Forte recomendacao |
| Logs, schema, drift, latencia e versao | API/observabilidade | Responde diretamente ao e-mail | Medio | Obrigatorio em escopo minimo |
| Artefato versionado, manifest e gate de promocao | Aprendizado continuo | Demonstra rastreabilidade e rollback | Medio | Forte recomendacao |
| Explicacao SHAP com camada de IA opcional | Integracao de IA | Responde ao e-mail sem deixar LLM controlar o modelo | Medio/alto | Fase final e opcional |
| Frontend completo | Stakeholders | Baixo para o escopo do teste | Alto | Nao priorizar |
| Cloud, Kubernetes e plataforma MLOps completa | Deploy | Baixo se nao houver requisito operacional | Alto | Nao fazer |

## Pacote de diferencial recomendado

Depois da pesquisa, o pacote mais equilibrado para este desafio e:

1. **Fundacao confiavel:** contrato de dados, merge auditavel, pipeline sem
   leakage e testes de schema.
2. **Avaliacao realista:** baseline, comparacao de modelos, holdout temporal,
   verificacao por CEP/faixa de preco e estudo com/sem dados demograficos.
3. **Decisao explicavel:** metricas em dolares, exemplos de erro, SHAP e model
   card. Intervalos de previsao entram se conseguirmos validar cobertura e
   largura.
4. **Servico operavel:** FastAPI, Docker, logs estruturados, health check,
   metricas operacionais, validacao de entrada e versao do modelo.
5. **Ciclo de vida:** fluxo documentado de novos dados, avaliacao do
   candidato, promocao, rollback e monitoramento de drift.
6. **IA com limites:** um adaptador opcional para transformar evidencias
   estruturadas em texto para stakeholders, com fallback local e sem poder de
   alterar a previsao.

Esse pacote diferencia a solucao por confiabilidade e capacidade de explicar
decisoes. Ele tambem permanece defensavel na entrevista: cada componente tem
uma finalidade, um teste e uma limitacao conhecida.

## Perguntas que devemos conseguir responder na entrevista

- Por que o split temporal e mais representativo que um split aleatorio neste
  dataset?
- Por que `id` foi removido e `zipcode` nao foi tratado como numero continuo?
- O que acontece se um novo CEP nao existir na tabela demografica?
- Como sabemos que o pre-processamento da API e igual ao do treinamento?
- Qual erro seria mais preocupante para o negocio: erro absoluto, relativo ou
  concentrado em uma faixa de preco?
- Como monitorar qualidade quando o preco real chega depois da previsao?
- Quando um novo modelo pode substituir o atual e como fazer rollback?
- Que risco existe em usar dados demograficos por CEP como feature?
- Qual parte foi implementada, qual foi simulada e qual ficou como proposta?
- Por que uma API de IA generativa nao deve alterar o valor previsto?

## Limites desta pesquisa

A busca encontrou exemplos publicos variados, mas nao existe acesso ao
criterio interno de avaliacao da empresa nem aos trabalhos dos outros
candidatos. Repositorios podem estar incompletos, desatualizados ou ter README
mais ambicioso que a implementacao. Relatos do Reddit sao experiencias
individuais. Por isso, as conclusoes acima devem orientar prioridades e testes,
nao ser tratadas como garantia de aprovacao.
