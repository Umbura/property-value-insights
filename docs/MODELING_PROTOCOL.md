# Protocolo de modelagem, calibração e avaliação

## Objetivo

Estimar o preço de imóveis residenciais usando características físicas,
espaciais e, quando justificadas, variáveis demográficas agregadas por
`zipcode`.

## Separação dos dados

Os registros são ordenados pela data da venda. As datas mais recentes,
correspondentes a aproximadamente 20% dos registros, formam o período de
avaliação temporal. Datas completas são mantidas no mesmo conjunto para evitar
que registros do mesmo dia apareçam nos dois lados da fronteira.

O conjunto de desenvolvimento é avaliado com cinco janelas temporais
expansivas. Cada data completa permanece em apenas um lado de cada divisão,
evitando que vendas do mesmo dia apareçam simultaneamente no treino e na
validação.

O período mais recente foi consultado na Fase 2 e seus resíduos motivaram a
Fase 2.1. Portanto, ele passa a ser tratado como avaliação diagnóstica, e não
como teste completamente intocado para novas decisões. A promoção da
calibração utiliza exclusivamente as cinco janelas do desenvolvimento.

## Features

- `id` é usado apenas para rastreabilidade e ordenação;
- `date` é usada para ordenação temporal, mas não entra como feature final;
- `zipcode` é tratado como categoria;
- as features físicas e espaciais formam o conjunto de referência;
- as features demográficas são adicionadas em uma comparação de ablação;
- o pré-processamento é ajustado dentro de cada pipeline, somente com os
  dados do respectivo treino.

## Candidatos da Fase 2

1. Baseline da mediana do preço no treino.
2. Ridge com features físicas e espaciais.
3. Ridge com features demográficas.
4. HistGradientBoostingRegressor com features físicas e espaciais.
5. HistGradientBoostingRegressor com features demográficas.
6. Variantes dos modelos com `log1p(price)`, convertendo as previsões para a
   escala original antes das métricas.

## Calibração da Fase 2.1

O modelo de referência usa HistGradientBoostingRegressor com features
demográficas e transformação logarítmica do alvo. A transformação melhora a
robustez diante da assimetria do preço, mas a retransformação direta pode
subestimar a média condicional na escala original.

As alternativas avaliadas incluem perdas `gamma`, `poisson` e
`absolute_error`, correção de retransformação calculada no treino e correção
temporal. Na correção temporal, os 10% finais de cada partição de treino são
usados para estimar o fator de smearing. Em seguida, o estimador é reajustado
com toda a partição de treino e o fator é aplicado às previsões na escala
original.

Esse procedimento preserva a ordem temporal e impede que observações da
janela de validação participem da calibração.

## Métricas

As métricas gerais são MAE e RMSE em dólares, RMSLE, R² e erro absoluto
mediano. A calibração também é acompanhada por:

- erro percentual absoluto médio;
- erro médio assinado, definido como `previsão - valor observado`;
- taxa de subestimação;
- mediana da razão entre previsão e valor observado;
- coeficiente de dispersão das razões;
- diferencial relacionado ao preço.

As mesmas métricas são calculadas para a faixa superior de preço, definida
em cada janela pelo percentil 75 do respectivo treino. As métricas inspiradas
em estudos de razão são diagnósticos de monitoramento preditivo e não
representam uma certificação formal de conformidade tributária.

## Regra de promoção

Uma calibração somente pode substituir o modelo de referência quando satisfaz
simultaneamente os seguintes critérios nas cinco janelas de desenvolvimento:

1. MAE média dentro da margem de 0,5% da melhor candidata e da referência;
2. menor MAE média na faixa superior;
3. menor viés absoluto médio na faixa superior;
4. melhora do MAE da faixa superior em pelo menos quatro das cinco janelas.

Entre as candidatas elegíveis, a ordenação considera MAE e viés absoluto da
faixa superior, desvio do diferencial relacionado ao preço e pior MAE geral.
Nenhuma escolha é considerada suficiente apenas por reduzir uma métrica.

## Reprodutibilidade

- semente dos experimentos: `42`;
- pipeline de pré-processamento, modelo e calibração versionados em código;
- resultados e figuras gerados por `notebooks/02_modeling.ipynb`;
- relatório gerado em `reports/model_comparison.md`;
- critérios de promoção cobertos por testes automatizados.

## Decisão para o artefato

A promoção estatística da Fase 2.1 identificou o modelo demográfico calibrado
como melhor candidato segundo os critérios definidos naquela etapa. A revisão
de governança posterior selecionou o modelo somente físico para o artefato da
Fase 3.

Depois da exclusão dos 18 registros temporalmente inconsistentes, a demografia
reduziu a MAE média das cinco janelas em 0,71%. O modelo físico apresentou MAE
e R² melhores no período diagnóstico. O ganho marginal não foi considerado
suficiente para incorporar variáveis com risco de representar proxies
socioeconômicas. `zipcode` permanece como categoria geográfica e continua
sujeito a monitoramento por segmento.

## Referências metodológicas

- Duan, N. (1983). *Smearing Estimate: A Nonparametric Retransformation
  Method*. Journal of the American Statistical Association, 78(383), 605-610.
  DOI: https://doi.org/10.1080/01621459.1983.10478017.
- International Association of Assessing Officers (2013). *Standard on Ratio
  Studies*. https://www.iaao.org/wp-content/uploads/Standard_on_Ratio_Studies.pdf.
- scikit-learn. *TransformedTargetRegressor*.
  https://scikit-learn.org/stable/modules/generated/sklearn.compose.TransformedTargetRegressor.html.
- scikit-learn. *HistGradientBoostingRegressor*.
  https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html.
