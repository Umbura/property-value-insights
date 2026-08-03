# Estrategia de execucao do desafio de AI/MLOps

Este documento transforma o contexto do desafio e a pesquisa de diferenciais
em um plano de execucao. Ele deve ser lido junto com:

- `CONTEXTO_DESAFIO.md`: exigencias do README e do e-mail;
- `PESQUISA_DIFERENCIAIS.md`: referencias, comparacoes e justificativas.

## 1. Posicionamento da solucao

Vamos construir uma solucao de previsao de precos que possa ser apresentada
como um pequeno sistema de ML auditavel:

```text
dados confiaveis -> avaliacao realista -> modelo versionado -> API operavel
       ^                  |                    |                  |
       |                  v                    v                  v
   contrato         metricas de negocio   promocao/rollback   logs e monitoramento
```

O objetivo nao e produzir a maior quantidade de infraestrutura. O objetivo e
mostrar que conseguimos levar um modelo desde os dados ate um servico,
explicando riscos, limites e decisoes.

A tese do projeto sera:

> Uma previsao de preco so e util quando seus dados de entrada, seu erro e sua
> operacao podem ser verificados.

## 2. Prioridades de escopo

### Nivel 1: obrigatorio para a entrega

- EDA com dicionario de dados, qualidade, correlacoes, outliers e padroes.
- Merge auditavel entre imoveis e dados demograficos por `zipcode`.
- Baseline e comparacao de modelos de regressao.
- Avaliacao com separacao temporal e metricas adequadas.
- Modelo final reproduzivel e arquivo de previsoes para os exemplos futuros.
- API FastAPI de inferencia.
- Dockerfile executavel localmente.
- Logs, health check, validacao de entrada e metricas operacionais basicas.
- Diagrama e documentacao de deploy.
- Fluxo documentado de aprendizado continuo, promocao e rollback.
- Comunicacao para stakeholders com metricas em dolares e limitacoes.
- README claro, notebooks, codigo, resultados, testes e diagramas.

### Nivel 2: diferenciais de alto valor e risco controlado

- Contrato de dados formalizado em codigo e testes.
- Relatorio de cobertura e qualidade do merge por CEP.
- Comparacao com e sem dados demograficos.
- Erro por faixa de preco e por agrupamento geografico.
- Model card com uso pretendido, limites, desempenho e riscos.
- Manifesto do artefato com versao de codigo, dados, features e metricas.
- Gate de promocao: um candidato so substitui o modelo atual se cumprir
  criterios definidos.
- Monitoramento de schema, drift de entrada, distribuicao de previsoes,
  latencia, erros e idade do modelo.

### Nivel 3: diferenciais condicionais

- Intervalos de previsao calibrados por conformal prediction, somente se a
  cobertura e a largura puderem ser avaliadas corretamente.
- Explicacoes locais com SHAP ou importancia de features.
- Adaptador opcional de IA generativa para converter evidencias estruturadas
  em texto de negocio, com fallback local e sem alterar a previsao.

### Fora do escopo

- Deploy real em AWS ou outra nuvem.
- Kubernetes, Kubeflow, Kafka ou feature store.
- Banco de dados de producao.
- Frontend completo.
- Retreinamento automatico em ambiente real.
- Chatbot generico ou agente com acesso amplo ao sistema.
- Uso de dados ficticios apresentado como dado de producao.

Se uma funcionalidade opcional ameacar os niveis 1 ou 2, ela sera removida ou
documentada como trabalho futuro.

## 3. Decisoes de dados antes da modelagem

### Fontes e chaves

1. `kc_house_data.csv` sera a fonte historica principal e possui o alvo
   `price`.
2. `zipcode_demographics.csv` sera associado por `zipcode`.
3. `future_unseen_examples.csv` sera usado somente depois que o pipeline e a
   avaliacao forem definidos.
4. O merge deve validar cardinalidade e cobertura de CEP. Nao sera permitido
   duplicar linhas de imoveis silenciosamente.

### Disponibilidade no momento da previsao

- `id` nao sera feature: identifica um registro, mas nao e uma caracteristica
  do imovel.
- `date` sera usada para ordenar e construir avaliacao temporal, mas nao sera
  feature final enquanto nao existir nos exemplos futuros.
- `zipcode` sera tratado como categoria, nao como distancia numerica.
- Latitude e longitude poderao ser mantidas como variaveis espaciais, com
  justificativa baseada na avaliacao.
- Features demograficas serao avaliadas por ablation: modelo fisico/espacial
  contra modelo com dados demograficos.

### Contrato minimo de dados

O contrato devera definir:

- colunas obrigatorias e colunas opcionais;
- tipos esperados;
- faixas validas, incluindo valores nao negativos quando aplicavel;
- categorias permitidas ou tratamento de categorias desconhecidas;
- regra para CEP sem correspondencia demografica;
- comportamento diante de valores ausentes, duplicados ou invalidos;
- colunas esperadas na saida de previsao.

O mesmo codigo de preparacao deve ser usado no treinamento e na API. Isso
reduz training-serving skew e evita que o notebook produza uma representacao
diferente daquela recebida pelo servico.

## 4. Protocolo de avaliacao

O protocolo deve ser definido antes da escolha do modelo final.

### Divisoes

1. Ordenar o historico pela data da venda.
2. Reservar o periodo mais recente como teste final, sem usa-lo para ajustar
   hiperparametros ou escolher features.
3. Usar validacao temporal dentro do conjunto de desenvolvimento para comparar
   alternativas.
4. Fazer uma analise adicional por grupos de `zipcode` para verificar se o
   desempenho depende excessivamente de regioes muito representadas.

O resultado por grupos sera diagnostico de robustez. Nao sera tratado como
uma promessa de generalizacao para um CEP nunca observado sem antes verificar
quantos registros existem e como o pipeline lida com categorias novas.

### Modelos candidatos

- baseline de mediana do preco no treino;
- regressao linear regularizada, como Ridge ou ElasticNet;
- modelo nao linear para dados tabulares, preferencialmente disponivel no
  conjunto de dependencias escolhido.

O vencedor sera escolhido por desempenho, estabilidade, interpretabilidade,
custo operacional e compatibilidade com a API. Nao sera escolhido apenas por
ter a menor metrica em uma divisao.

### Metricas

Metricas principais:

- MAE em dolares: erro medio facil de traduzir para negocio;
- RMSE em dolares: penaliza erros grandes;
- RMSLE: compara erro na escala logaritmica quando apropriado;
- R2: referencia complementar, nao criterio unico;
- erro relativo ou mediano absoluto percentual, com cautela para faixas de
  preco pequenas.

Relatorios complementares:

- erro por faixa de preco;
- erro por agrupamento geografico ou CEP;
- residuos e previsoes extremas;
- ganho sobre o baseline;
- comparacao com e sem dados demograficos.

### Decisao sobre o modelo de ML

O modelo final ainda nao sera definido. Primeiro construiremos um protocolo
fixo e compararemos candidatos sob as mesmas condicoes.

#### Candidatos

1. **Baseline de mediana:** estima a mediana dos precos observados no conjunto
   de treino. Ele mostra quanto o sistema precisa superar para justificar
   complexidade.
2. **Modelo linear regularizado:** Ridge ou ElasticNet, com pipeline de
   imputacao, codificacao e regularizacao. Ele funciona como referencia
   interpretavel e ajuda a medir o ganho de modelos mais complexos.
3. **Modelo nao linear tabular:** um algoritmo disponivel e bem suportado no
   ambiente escolhido, como HistGradientBoostingRegressor ou Random Forest.
   XGBoost somente sera usado se a dependencia puder ser fixada e se o ganho
   justificar a complexidade adicional.

#### Protocolo de comparacao

Todos os candidatos deverao:

- receber exatamente a mesma divisao temporal;
- usar o mesmo tratamento de merge e disponibilidade de features;
- aprender imputacao e codificacao somente no treino;
- ser avaliados no mesmo conjunto temporal final;
- gerar metricas gerais e por segmentos;
- registrar tempo de treinamento, tamanho do artefato e compatibilidade com a
  API.

Podemos comparar o alvo original com `log1p(price)` para lidar com assimetria,
mas qualquer escolha sera avaliada novamente na escala original de dolares.
Uma melhora em RMSLE nao sera aceita como suficiente se o MAE em dolares ou os
erros em segmentos relevantes piorarem.

#### Regra de escolha

O modelo final sera o menor sistema que apresentar desempenho consistente e
justificavel. A ordem de decisao sera:

1. passar no contrato e nos testes;
2. superar o baseline de forma clara;
3. apresentar desempenho aceitavel no teste temporal;
4. nao possuir regressao grave por faixa de preco ou agrupamento geografico;
5. ser reproduzivel e carregavel pela API;
6. oferecer complexidade operacional compativel com o desafio.

Nao vamos declarar antecipadamente que XGBoost, Random Forest ou qualquer outro
modelo sera o vencedor. O notebook de modelagem devera mostrar a tabela de
comparacao e a justificativa da escolha.

#### Treinamento final

Depois de aprovarmos o protocolo e escolhermos o candidato, o modelo final
sera ajustado com todo o historico disponivel, mantendo o teste temporal como
registro da avaliacao realizada. Em seguida, o pipeline aprovado sera usado
para gerar as previsoes de `future_unseen_examples.csv`.

Os resultados futuros serao apresentados como previsoes, nao como metricas de
acuracia, porque o arquivo nao possui os precos reais.

## 5. Diferencial de incerteza e explicacao

### Intervalo de previsao

Depois do modelo pontual estar estavel, avaliaremos um intervalo de previsao.
O retorno esperado seria semelhante a:

```json
{
  "predicted_price": 620000,
  "prediction_interval": {
    "lower": 540000,
    "upper": 720000,
    "coverage": 0.90
  }
}
```

Os valores acima sao apenas o formato de resposta, nao resultados do projeto.
O intervalo so entrara na entrega se conseguirmos medir cobertura e largura no
conjunto de avaliacao. Caso contrario, documentaremos a abordagem como
extensao futura.

### Explicacao

A explicacao devera seguir esta ordem:

1. O modelo calcula o preco.
2. Um metodo deterministico identifica as features que mais contribuiram.
3. A API pode devolver essas evidencias em formato estruturado.
4. Uma camada externa de IA, se usada, apenas redige uma explicacao baseada
   nessas evidencias.

O provedor de IA nao podera modificar a previsao, criar valores ausentes ou
afirmar causalidade. Sem chave de API, o projeto deve continuar executavel por
meio de uma resposta local deterministica.

## 6. Arquitetura de implementacao

### Treinamento

```text
CSV historico
    |
    v
validacao e merge por CEP
    |
    v
preprocessamento versionado
    |
    v
baseline + candidatos
    |
    v
avaliacao temporal e por segmentos
    |
    v
artefato aprovado + manifest + relatorios
```

### Inferencia

```text
cliente
   |
   v
FastAPI -> validacao de schema -> pipeline carregado -> previsao
   |                                      |
   |                                      +--> explicacao estruturada opcional
   +--> logs, metricas, versao e erros
```

### Endpoints planejados

- `GET /health`: disponibilidade da aplicacao e do artefato.
- `GET /model-info`: versao, data de treinamento, features e metricas
  principais.
- `POST /predict`: previsao para um imovel.
- `POST /predict/batch`: previsao para uma lista de imoveis.
- `GET /metrics`: contadores, erros e latencias da aplicacao.
- `POST /explain`: somente se a explicacao estiver pronta e validada.

O endpoint de explicacao pode ser adiado sem comprometer o fluxo principal.

### Docker e observabilidade

O container deve iniciar a API com uma configuracao reproduzivel. A
observabilidade minima sera composta por:

- logs estruturados em stdout;
- identificador da requisicao;
- nome e versao do modelo;
- tempo de resposta;
- quantidade de previsoes;
- erros de validacao e inferencia;
- estatisticas de entradas sem registrar dados pessoais desnecessarios;
- health check.

O drift sera documentado e, se implementado, comparara a distribuicao de
entrada ou previsao com uma referencia do treinamento. Qualidade preditiva
real somente sera calculada quando o preco observado estiver disponivel.

## 7. Aprendizado continuo e promocao

O fluxo proposto e:

```text
novos dados rotulados
        |
        v
validacao do contrato e qualidade
        |
        v
treinamento de candidato
        |
        v
avaliacao temporal, por segmento e contra o champion
        |
   +----+----+
   |         |
 reprovado  aprovado
   |         |
   v         v
 registrar   versionar e promover
              |
              v
        monitorar e permitir rollback
```

### Criterios de promocao

O candidato deve, no minimo:

- passar no contrato de dados e nos testes automatizados;
- melhorar ou manter MAE e RMSE dentro de uma tolerancia definida;
- nao apresentar regressao relevante em uma faixa de preco ou agrupamento
  geografico importante;
- possuir o mesmo contrato de features usado pelo servico;
- gerar manifest e artefato carregavel pela API.

Os limiares numericos serao definidos depois do baseline, para nao inventar
uma meta sem conhecer a variabilidade do dataset.

### Rollback

O servico deve apontar para um artefato versionado. Se uma nova versao falhar
em validacao, health check ou monitoramento, o procedimento documentado sera
restaurar a referencia anterior e registrar a causa.

Nao vamos simular um retreinamento automatico real. Vamos implementar o que e
necessario para demonstrar a decisao e documentar o restante como arquitetura
futura.

## 8. Entregaveis por fase

### Fase 0 - contrato e escopo

Entregas:

- estrutura inicial do repositorio;
- contrato de dados;
- inventario das colunas e disponibilidade nos tres CSVs;
- plano de avaliacao aprovado;
- registro de riscos e decisoes.

Conclusao: sabemos o que pode entrar no modelo e como medir sucesso antes de
treinar candidatos.

### Fase 1 - EDA e qualidade

Entregas:

- `notebooks/01_eda.ipynb`;
- relatorio de merge e cobertura de CEP;
- tratamento justificado de ausentes, duplicados e outliers;
- graficos de distribuicao, correlacao, localizacao e segmentos;
- primeiras hipoteses sobre o preco.

Conclusao: os dados estao compreendidos e o pipeline de entrada tem regras
observaveis.

### Fase 2 - modelagem e avaliacao

Entregas:

- `notebooks/02_modeling.ipynb`;
- baseline, candidatos e comparacao;
- avaliacao temporal;
- metricas gerais, por faixa e por regiao;
- estudo com e sem demografia;
- decisao documentada do modelo final.

Conclusao: o modelo escolhido supera o baseline com evidencia e sem vazamento
conhecido.

### Fase 3 - pipeline e artefato

Entregas:

- codigo reutilizavel em `src/`;
- pipeline de preparacao e treinamento;
- artefato carregavel;
- manifest com versao, features, dados, configuracao e metricas;
- arquivo de previsoes dos exemplos futuros.

Conclusao: treinamento e inferencia usam o mesmo contrato e produzem o mesmo
tipo de entrada/saida.

### Fase 4 - API, Docker e observabilidade

Entregas:

- API FastAPI;
- schemas de entrada e saida;
- testes de endpoints e erros;
- Dockerfile e instrucao de execucao;
- logs, health check, metricas e identificacao do modelo.

Conclusao: outra pessoa consegue iniciar o servico e fazer uma previsao local.

### Fase 5 - deploy, ciclo de vida e stakeholders

Entregas:

- diagrama de deploy;
- fluxo de aprendizado continuo;
- gate de promocao e rollback;
- model card;
- metricas traduzidas para negocio;
- limitacoes e proximos passos.

Conclusao: a entrega explica como o sistema seria operado e discutido com
tecnicos e stakeholders.

### Fase 6 - opcionais com controle de qualidade

Ordem de prioridade:

1. analise de incerteza;
2. explicacao SHAP;
3. adaptador de IA generativa.

Conclusao: nenhum opcional entra somente por existir. Cada um precisa ter
resultado demonstravel, teste e explicacao de limite.

### Fase 7 - revisao e publicacao

Checklist:

- executar a instalacao a partir de um ambiente limpo;
- rodar testes;
- reconstruir o container;
- executar um exemplo de previsao;
- conferir que os notebooks e relatorios abrem;
- conferir que o arquivo futuro possui 100 previsoes;
- revisar links, nomes e instrucoes;
- remover credenciais, arquivos temporarios e dados pessoais;
- publicar repositorio publico somente quando a entrega estiver revisada;
- conceder acesso ao usuario GitHub `rdgpires`, conforme o e-mail;
- enviar o link por e-mail.

## 9. Cronograma de sete dias

O cronograma e relativo ao inicio efetivo do desenvolvimento e pode ser
ajustado se a empresa aprovar um novo prazo.

| Dia | Foco | Saida minima |
| --- | --- | --- |
| 1 | contrato, auditoria e EDA inicial | regras de dados e hipoteses |
| 2 | EDA completa e merge | notebook e relatorio de qualidade |
| 3 | baseline e modelos candidatos | tabela de avaliacao |
| 4 | modelo final e artefato | manifest e previsoes futuras |
| 5 | API, testes e Docker | servico local executavel |
| 6 | observabilidade, deploy, ciclo de vida e model card | documentacao completa |
| 7 | opcionais, revisao, ambiente limpo e publicacao | repositorio pronto |

Se houver atraso, os opcionais serao cortados primeiro. Depois, reduziremos a
complexidade operacional, preservando avaliacao, API, Docker e documentacao.

## 10. Criterio final de sucesso

Consideraremos a solucao pronta quando um avaliador puder:

1. entender os dados e o merge;
2. reproduzir a avaliacao;
3. ver por que o modelo foi escolhido;
4. gerar previsoes para os exemplos futuros;
5. iniciar a API localmente;
6. observar versao, erros e latencia;
7. entender como um novo modelo seria aprovado ou rejeitado;
8. identificar limites, riscos e proximos passos.

Essa e a estrategia aprovada para iniciar a implementacao. Qualquer mudanca de
escopo que altere a arquitetura ou acrescente uma ferramenta deve ser avaliada
contra esses criterios antes de ser incorporada.

## 11. Processo de versionamento

O desenvolvimento seguira o fluxo descrito em `PROCESSO_GIT_GITHUB.md`, com
branches por fase, commits atomicos, pull requests, testes, tags e releases.
O historico do Git sera considerado parte da entrega tecnica.

## 12. Decisoes operacionais antes da Fase 0

Os itens abaixo foram definidos para evitar ambiguidades durante a
implementacao. Quando houver dependencia do ambiente local, a verificacao
sera feita antes da instalacao ou escolha definitiva.

### Ambiente e dependencias

- Python 3.13 sera a versao de referencia no ambiente atual.
- A base inicial usara pandas, numpy, scikit-learn, joblib, FastAPI, Pydantic,
  pytest e Ruff.
- XGBoost sera opcional e so entrara se o ganho de desempenho justificar a
  dependencia e se a instalacao puder ser reproduzida.
- As versoes das dependencias serao registradas e fixadas antes da primeira
  release funcional.
- Nao sera adicionada uma ferramenta de infraestrutura apenas para aumentar a
  lista de tecnologias.

### Reprodutibilidade

- A semente inicial dos experimentos sera `42`.
- Os arquivos CSV terao identificadores ou hashes registrados no manifesto dos
  dados.
- O modelo tera manifesto com versao do codigo, dados, features,
  configuracao, metricas e data de treinamento.
- A execucao sera validada em ambiente limpo antes da publicacao final.

### Separacao entre analise e producao

- `notebooks/01_eda.ipynb` concentrara analise e comunicacao dos dados.
- `notebooks/02_modeling.ipynb` concentrara comparacao e justificativa dos
  modelos.
- A logica reutilizavel de merge, features, treino e inferencia ficara em
  `src/`.
- Os notebooks nao serao a unica forma de executar o treinamento ou a API.

### Linguagem dos artefatos destinados a avaliacao

Todo material que possa ser lido pelo avaliador - README, notebooks,
relatorios, diagramas, mensagens da aplicacao e exemplos de uso - devera
conter somente linguagem tecnica, neutra e orientada ao problema. Termos do
processo interno, como `fase`, `criterios de aceite`,
`revisao supervisionada`, `branch`, `PR`, nomes de colaboradores ou
instrucoes de trabalho, nao devem aparecer nesses artefatos.

Esses registros permanecerao restritos ao planejamento interno, issues,
pull requests e `docs/reviews/`. Mensagens exibidas durante a execucao devem
descrever um resultado tecnico, como cobertura, cardinalidade ou validacao
concluida, e nunca o estado da nossa revisao interna.

Antes de cada commit e push de notebook ou relatorio, sera obrigatorio:

1. revisar as celulas Markdown, codigo e saidas renderizadas;
2. pesquisar termos de processo interno no arquivo e nos artefatos gerados;
3. substituir mensagens de processo por descricoes tecnicas ou remover saidas
   desnecessarias;
4. reexecutar o notebook e conferir visualmente o resultado final.

### Artefatos e relatorios

Os resultados serao organizados em:

```text
artifacts/  modelos, manifestos e previsoes
reports/    metricas, model card e relatorios
diagrams/   arquitetura e fluxo operacional
```

Arquivos grandes ou binarios serao avaliados antes de entrar no historico do
Git. Nenhum artefato sera tratado como resultado de producao sem indicar sua
origem e seu contexto de avaliacao.

### Repositorio e publicacao

- O Git local sera inicializado durante a Fase 0.
- O repositorio remoto sera publicado depois da revisao de seguranca da Fase 0
  e da aprovacao supervisionada.
- A primeira versao estavel sera marcada como `v0.1.0`.
- `main` permanecera reservado para fases aprovadas.
- Cada fase tera branch, commits, pull request, revisao e tag proprios.

### Seguranca e licenca

- Credenciais, tokens, arquivos `.env`, dados pessoais e arquivos temporarios
  nao serao publicados.
- `.env.example` tera somente nomes de configuracao sem valores reais.
- O staged diff sera revisado antes de cada commit e push.
- A licenca do codigo sera decidida separadamente da permissao de redistribuir
  os dados fornecidos no desafio.

### Gate da Fase 0

A Fase 0 somente sera concluida quando houver:

- estrutura inicial revisada;
- contrato de dados escrito;
- dependencias verificadas;
- auditoria dos arquivos concluida;
- `.gitignore` e regras de seguranca revisadas;
- teste minimo executado;
- issue, branch e commits documentados;
- revisao supervisionada aprovada.
