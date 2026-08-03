# Protocolo de modelagem e avaliacao

## Objetivo

Estimar o preco de imoveis residenciais usando as caracteristicas fisicas,
espaciais e, quando justificadas, as variaveis demograficas agregadas por
`zipcode`.

## Separacao dos dados

Os registros sao ordenados pela data da venda. As datas mais recentes,
correspondentes a aproximadamente 20% dos registros, formam o teste temporal.
Datas completas sao mantidas no mesmo conjunto para evitar que registros do
mesmo dia aparecam nos dois lados da fronteira.

O conjunto de desenvolvimento e avaliado com cinco janelas temporais
expansivas. Cada data completa permanece em apenas um lado de cada divisao,
evitando que vendas do mesmo dia aparecam simultaneamente no treino e na
validacao. O teste temporal permanece reservado para a avaliacao final dos
resultados selecionados.

## Features

- `id` e usado apenas para rastreabilidade e ordenacao;
- `date` e usada para a ordenacao temporal, mas nao entra como feature final;
- `zipcode` e tratado como categoria;
- as features fisicas e espaciais formam o conjunto de referencia;
- as features demograficas sao adicionadas em uma comparacao de ablation;
- o pre-processamento e ajustado dentro de cada pipeline, somente com os dados
  do respectivo treino.

## Candidatos

1. Baseline da mediana do preco no treino.
2. Ridge com features fisicas e espaciais.
3. Ridge com features demograficas.
4. HistGradientBoostingRegressor com features fisicas e espaciais.
5. HistGradientBoostingRegressor com features demograficas.
6. Variantes dos modelos com `log1p(price)`, convertendo as previsoes de volta
   para a escala original antes das metricas.

## Metricas

As metricas principais sao MAE e RMSE em dolares. RMSLE e R2 complementam a
analise. O erro tambem e calculado por faixa de preco e por CEP, permitindo
identificar concentracao de erro em segmentos especificos.

## Busca limitada

Depois da comparacao das referencias, uma busca deterministica avalia um
conjunto pequeno de configuracoes do `HistGradientBoostingRegressor`. A busca
varia transformacao do alvo, taxa de aprendizado, numero de iteracoes, numero
maximo de folhas e regularizacao L2. Todas as configuracoes recebem as mesmas
cinco janelas e nenhuma consulta o teste temporal durante a busca.

## Regra de comparacao

A menor MAE media define a referencia de desempenho da busca. Os candidatos
que ficam ate 0,5% dessa referencia sao considerados tecnicamente proximos.
Entre eles, o champion e aquele com menor MAE no pior fold, seguido pela menor
variacao entre folds. O melhor candidato restante pela MAE media permanece
como challenger.

Depois dessa decisao, somente o champion e a referencia de mediana sao medidos
no teste temporal. O challenger nao consulta esse periodo reservado.

Nenhuma escolha de modelo e considerada suficiente apenas por reduzir uma
metrica. A decisao deve considerar estabilidade entre janelas, erro em
segmentos, desempenho em dolares, complexidade e possibilidade de carregar o
pipeline na API.

## Reproducibilidade

- semente dos experimentos: `42`;
- pipeline de pre-processamento e modelo versionados em codigo;
- resultados e figuras gerados por `notebooks/02_modeling.ipynb`;
- relatorio gerado em `reports/model_comparison.md`.
