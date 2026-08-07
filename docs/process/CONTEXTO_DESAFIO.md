# Contexto do Desafio Tecnico de AI/MLOps

Este arquivo consolida as demandas do desafio tecnico com base no `README.md`
fornecido pela empresa e no e-mail de orientacao recebido para o processo
seletivo de AI/MLOps Engineer.

## Contexto do problema

Os dados representam propriedades residenciais anonimizadas da regiao de
Seattle, nos Estados Unidos. O objetivo central e prever o preco de imoveis a
partir de caracteristicas fisicas e de informacoes demograficas associadas ao
CEP (`zipcode`).

## Arquivos fornecidos

- `kc_house_data.csv`: dados historicos de imoveis com o preco observado.
- `zipcode_demographics.csv`: dados demograficos agregados por CEP.
- `future_unseen_examples.csv`: imoveis sem preco, usados para gerar as
  previsoes finais depois do treinamento.

## Demandas obrigatorias do README

### 1. Analise e entendimento dos dados

A solucao deve:

- explicar o significado das principais variaveis;
- apresentar correlacoes, outliers e padroes relevantes;
- explicar como os dados fisicos e demograficos foram combinados;
- justificar o tratamento de tipos, valores ausentes, duplicidades e dados
  inconsistentes, caso sejam encontrados.

### 2. Desenvolvimento do modelo de Machine Learning

A solucao deve explicar:

- quais variaveis foram consideradas importantes e por que;
- qual modelo foi escolhido;
- por que o modelo e adequado ao problema;
- como o modelo foi comparado com uma referencia ou baseline;
- como a generalizacao para novos dados foi avaliada;
- qual estrategia de separacao dos dados, validacao cruzada, regularizacao ou
  outro controle foi utilizada.

As escolhas devem ser justificadas. O desafio nao exige um modelo especifico;
XGBoost, Random Forest e Regressao Linear aparecem apenas como exemplos.

### 3. Estrategia de deploy

A entrega deve conter:

- um esquema ou diagrama da arquitetura de producao;
- explicacao da camada de API;
- explicacao da infraestrutura proposta;
- explicacao do monitoramento;
- explicacao do versionamento do modelo;
- relacao entre treinamento, artefato aprovado e servico de inferencia.

O deploy em nuvem nao precisa ser implementado. A exigencia e desenhar e
documentar uma estrategia tecnicamente coerente.

### 4. Aprendizado continuo

A documentacao deve explicar:

- como novos dados entrariam no fluxo;
- quando um novo treinamento seria iniciado;
- como o novo modelo seria avaliado;
- quais criterios permitiriam substituir o modelo atual;
- como seria feito rollback para uma versao anterior;
- como seriam acompanhados mudanca de distribuicao e degradacao de desempenho.

### 5. Comunicacao com stakeholders

A entrega deve mostrar como os resultados seriam apresentados para um publico
de negocio, usando quando fizer sentido:

- graficos interpretaveis;
- metricas traduzidas em impacto de negocio;
- exemplos de previsoes;
- explicacao dos fatores relevantes;
- storytelling sobre limites e uso adequado do modelo.

## Criterios de avaliacao mencionados no e-mail

O e-mail informa que o objetivo tambem e avaliar a abordagem pratica para
problemas reais do ecossistema de dados e IA. Na discussao tecnica, a equipe
deve analisar a solucao e as decisoes tomadas. Por isso, o projeto deve
demonstrar, de forma proporcional ao desafio:

- organizacao de um backend Python;
- uso de FastAPI ou Django;
- conteinerizacao com Docker;
- observabilidade, incluindo logs, health checks e metricas relevantes;
- integracao de componentes ou APIs de IA;
- clareza para explicar arquitetura, decisoes, desafios, limitacoes e
  melhorias futuras.

Esses pontos aparecem como criterios de avaliacao no e-mail. O README nao exige
uma plataforma de producao completa nem define uma API de IA especifica.

## Regras e premissas

- Qualquer linguagem ou framework pode ser utilizado.
- Devem ser aplicadas boas praticas de Ciencia de Dados.
- O dataset deve ser tratado como um projeto realista e anonimizado de cliente.
- Nao e obrigatorio utilizar todas as colunas ou todos os arquivos em todas as
  etapas, mas qualquer exclusao precisa ser justificada.
- O foco principal e clareza, justificativa e comunicacao tecnica e de negocio.

## Entrega no GitHub

Ao finalizar, a empresa solicita:

1. Criacao de um repositorio publico no GitHub.
2. Inclusao de todos os arquivos e notebooks da solucao.
3. Inclusao do README, resultados, diagramas e demais documentos necessarios.
4. Envio do link do repositorio por e-mail.
5. Concessao de acesso ao usuario GitHub `rdgpires`, conforme solicitado no
   e-mail.

## Prazo

O prazo informado e de sete dias a partir do recebimento do e-mail. A empresa
permite solicitar mais tempo caso ocorram imprevistos, desde que seja feito um
novo alinhamento.

## O que nao foi exigido explicitamente

Os documentos nao exigem:

- deploy real em AWS ou em qualquer nuvem;
- uso de um provedor especifico de LLM;
- frontend completo;
- banco de dados de producao;
- retreinamento automatico funcionando em ambiente real;
- arquitetura distribuida ou uma plataforma MLOps completa.

Uma API local em FastAPI, executavel com Docker, pode demonstrar backend,
conteinerizacao e observabilidade sem transformar o desafio em um projeto de
infraestrutura de nuvem.

## Estrategia de execucao proposta

Esta secao registra como as demandas serao atendidas. Os itens abaixo sao uma
proposta de implementacao e nao devem ser confundidos com exigencias adicionais
da empresa.

### Analise e entendimento dos dados

Criar `notebooks/01_eda.ipynb` com:

- dicionario das principais variaveis;
- analise de tipos, valores ausentes e duplicidades;
- distribuicao do preco;
- correlacoes, outliers e padroes relevantes;
- analise por CEP, localizacao, area, padrao e condicao;
- validacao do relacionamento entre `kc_house_data.csv` e
  `zipcode_demographics.csv`;
- justificativa das colunas mantidas ou removidas.

O merge sera feito por `zipcode`, com validacao de cardinalidade. A analise
devera registrar quantos imoveis encontraram dados demograficos e quais medidas
serao tomadas caso novos dados nao possuam correspondencia.

### Modelagem

Criar `notebooks/02_modeling.ipynb` e um pipeline reutilizavel em `src/`.
Comparar, no minimo:

1. Um baseline baseado em mediana.
2. Um modelo linear regularizado.
3. Um modelo nao linear adequado para dados tabulares.

A escolha final sera baseada nos resultados de validacao. Nao sera escolhido um
modelo apenas por ser popular.

A avaliacao devera:

- respeitar a ordem temporal das vendas no conjunto de teste;
- utilizar validacao cruzada no conjunto de treinamento;
- excluir `id`, pois ele nao representa uma caracteristica do imovel;
- nao usar `date` como feature final, pois ela nao aparece nos exemplos futuros;
- tratar `zipcode` como categoria, e nao como uma medida numerica;
- avaliar o impacto dos dados demograficos comparando modelos com e sem essa
  fonte;
- considerar transformacao logaritmica do preco se ela melhorar a estabilidade
  do treinamento.

As metricas previstas sao MAE, RMSE, RMSLE e R2, complementadas por erro em
dolares, erro por faixa de preco e desempenho por regiao ou CEP.

O resultado final devera gerar um arquivo de previsoes para os 100 exemplos
futuros, com um identificador de linha e o preco estimado.

### Backend, Docker e observabilidade

Como o e-mail menciona esses pontos, criar uma API FastAPI pequena e focada no
servico de inferencia:

- `GET /health` para verificar disponibilidade;
- `GET /model-info` para informar versao e metadados do modelo;
- `POST /predict` para uma previsao;
- `POST /predict/batch` para varias previsoes;
- `GET /metrics` para metricas operacionais.

O projeto devera possuir `Dockerfile` e `compose.yaml` para executar a API de
forma reproduzivel.

A observabilidade minima devera registrar:

- logs estruturados;
- tempo de resposta;
- quantidade de previsoes;
- erros de validacao e inferencia;
- versao do modelo em uso;
- health check da aplicacao.

Nao sera criado um ambiente AWS, Kubernetes ou uma arquitetura distribuida. O
objetivo e demonstrar o backend e documentar como ele poderia evoluir para
producao.

### Integracao de IA

O modelo de regressao sera o componente de IA principal. Uma camada opcional de
explicacao podera ser criada para demonstrar integracao com um provedor de IA:

1. O modelo calcula o preco.
2. SHAP ou importancia das features identifica os fatores relevantes.
3. Um provedor de IA transforma esses fatores em uma explicacao para negocio.
4. A explicacao nao pode modificar o preco nem tomar decisoes sobre o modelo.

O sistema devera possuir um modo local ou simulado para funcionar sem chave de
API. A integracao externa sera opcional e nao podera impedir os testes ou a
execucao basica do projeto.

### Deploy documentado

O README devera conter um diagrama semelhante a este fluxo:

```text
Dados historicos
        |
        v
Treinamento e validacao
        |
        v
Modelo aprovado e versionado
        |
        v
API FastAPI em Docker
        |
        +--> logs e metricas
        |
        +--> explicacao opcional via IA
```

O documento devera explicar a funcao de cada camada, o caminho do modelo desde
o treinamento ate a inferencia e os componentes necessarios em uma futura
implantacao de producao.

### Aprendizado continuo

Documentar um fluxo em que:

- novos imoveis com preco observado entram na base;
- os dados passam por validacao;
- um novo modelo e treinado;
- o novo modelo e comparado ao modelo atual;
- criterios de qualidade autorizam ou bloqueiam a promocao;
- o artefato aprovado recebe uma nova versao;
- o modelo anterior pode ser restaurado em caso de regressao;
- drift e degradacao de desempenho sao monitorados.

O retreinamento automatico em producao nao sera simulado como se ja existisse.
Ele sera documentado como uma evolucao futura com criterios verificaveis.

### Comunicacao com stakeholders

Os notebooks, resultados e README deverao responder:

> Quao confiavel e a estimativa de preco e em quais tipos de imovel o modelo
> erra mais?

Para isso, apresentar:

- preco real versus preco previsto;
- erro medio em dolares;
- exemplos de previsoes;
- principais fatores de influencia;
- desempenho por faixa de preco;
- limitacoes do modelo;
- explicacao de que a estimativa nao substitui uma avaliacao imobiliaria.

### Estrutura proposta do repositorio

```text
desafio-genai-mlops/
|- data/
|- notebooks/
|  |- 01_eda.ipynb
|  `- 02_modeling.ipynb
|- src/
|  `- house_price/
|     |- data.py
|     |- features.py
|     |- train.py
|     |- predict.py
|     |- api.py
|     `- observability.py
|- tests/
|- artifacts/
|- reports/
|- diagrams/
|- Dockerfile
|- compose.yaml
|- pyproject.toml
|- .env.example
`- README.md
```

### Ordem de implementacao

1. Auditar dados e definir o contrato de entrada e saida.
2. Criar o baseline e a avaliacao temporal.
3. Comparar modelos e registrar a decisao.
4. Implementar o pipeline de treinamento e o artefato versionado.
5. Implementar a API FastAPI.
6. Adicionar Docker, logs, health check e metricas.
7. Adicionar a explicacao opcional via IA, caso ela continue justificavel.
8. Escrever deploy, aprendizado continuo e comunicacao com stakeholders.
9. Executar testes, revisar o repositorio e publicar a entrega.

## Referencias de origem

- `README.md` fornecido no diretorio do desafio.
- E-mail de Ticiana Alves com as instrucoes do desafio tecnico e da etapa de
  discussao tecnica.

## Estrategia consolidada

O plano operacional, as prioridades de escopo, os criterios de promocao, o
cronograma e o checklist final estao em
`ESTRATEGIA_EXECUCAO.md`. A pesquisa que fundamenta os diferenciais esta em
`PESQUISA_DIFERENCIAIS.md`.
O processo de branches, commits, pull requests, tags, releases e verificacoes
de seguranca esta em `PROCESSO_GIT_GITHUB.md`.
