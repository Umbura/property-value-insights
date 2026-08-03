# Revisao da Fase 2

Status: aguardando revisao supervisionada.

## Objetivo

Comparar referencias e modelos de regressao com um protocolo temporal,
selecionar um candidato sem consultar o teste reservado e registrar o
desempenho geral e por segmentos.

## Entregas

- baseline de mediana;
- referencias Ridge com alvo original e logaritmico;
- modelos HistGradientBoosting com e sem dados demograficos;
- busca limitada e deterministica de hiperparametros;
- cinco janelas temporais expansivas que preservam datas completas;
- regra testavel de selecao por MAE media, pior fold e variacao;
- comparacao com a referencia no teste temporal reservado;
- analise por faixa de preco, CEP e importancia por permutacao;
- notebook executado e relatorio tecnico gerado.

## Decisao

O modelo principal e `hist_demographics_log_default`. Ele apresentou MAE media
de aproximadamente US$ 63.128 nas cinco janelas e MAE de aproximadamente
US$ 73.912 no teste temporal reservado. O ganho de MAE sobre a mediana foi de
67,2%.

O modelo `hist_demographics_log_regularized` permanece como alternativa. Ele
obteve MAE media de aproximadamente US$ 63.174 e nao foi avaliado no teste
reservado.

## Evidencias

- o teste temporal contem 4.640 registros posteriores ao desenvolvimento;
- nenhuma data aparece simultaneamente no treino e na validacao de um fold;
- somente a mediana e o modelo principal foram medidos no teste reservado;
- o modelo principal atingiu R2 de 0,877 no teste temporal;
- o erro permanece mais alto na faixa superior de precos e em alguns CEPs.

## Verificacoes

As verificacoes devem ser repetidas imediatamente antes da revisao:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
```

O notebook `notebooks/02_modeling.ipynb` deve permanecer executado, sem erros e
com os resultados correspondentes a `reports/model_comparison.md`.

## Limitacoes conhecidas

- os dados representam uma unica regiao e um intervalo temporal limitado;
- dados demograficos agregados por CEP podem atuar como proxies sociais e nao
  devem ser interpretados como atributos individuais ou evidencias causais;
- os erros aumentam para imoveis de maior valor;
- o artefato carregavel, o manifesto e as previsoes futuras pertencem a Fase 3.

## Pontos para aprovacao

- aprovar o protocolo de cinco janelas com datas completas;
- aprovar a margem de 0,5% para comparar estabilidade entre candidatos;
- aprovar `hist_demographics_log_default` como modelo principal;
- decidir se a Fase 2 pode ser incorporada e marcada como `v0.3.0`.
