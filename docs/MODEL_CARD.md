# Model Card: Property Value Insights

## Identificação

| Campo | Valor |
| --- | --- |
| Nome | `property_value_hist_gradient_boosting_physical` |
| Versão | `0.4.0-rc1` |
| Tipo | Regressão supervisionada |
| Algoritmo | HistGradientBoostingRegressor |
| Alvo | Preço residencial em USD |
| Interface | API FastAPI `0.5.0-rc1` |
| Artefato | Pipeline Joblib verificado por SHA-256 |
| Data do artefato | 3 de agosto de 2026 |

## Uso pretendido

O modelo fornece uma estimativa inicial de preço para imóveis residenciais com
características compatíveis com a região e o período dos dados. O resultado pode
apoiar triagem, comparação de carteira, priorização de análise e construção de
uma segunda opinião quantitativa.

O usuário esperado é um analista ou sistema que conhece as limitações do modelo
e mantém revisão humana. A saída contém preço, moeda e versão para permitir
rastreabilidade.

## Usos fora do escopo

- avaliação imobiliária formal ou laudo;
- decisão automática de crédito, seguro, imposto, compra ou venda;
- definição individual de preço sem vistoria e contexto de mercado;
- inferência fora da região de Seattle sem nova validação;
- aplicação a períodos econômicos diferentes sem monitoramento e reavaliação;
- interpretação causal das features;
- uso de preço futuro previsto como verdade observada.

## Dados

O histórico original contém 21.613 vendas entre 2 de maio de 2014 e 27 de maio
de 2015. Dezoito registros foram excluídos porque indicavam construção ou
reforma posterior à venda. O treinamento final utilizou 21.595 linhas.

O modelo recebe 18 características físicas e espaciais: quartos, banheiros,
áreas, andares, vista, condição, padrão construtivo, anos, CEP e coordenadas.
`id`, data e preço não entram como features. O CEP é categórico e pode funcionar
como proxy contextual.

Dados demográficos agregados foram estudados, mas ficaram fora do artefato. A
redução de 0,71% na MAE média das cinco janelas não compensou o risco adicional
de proxies socioeconômicas e o modelo físico apresentou melhor diagnóstico no
período mais recente.

## Avaliação

As datas foram ordenadas e mantidas integralmente no mesmo lado de cada corte.
O desenvolvimento utilizou 16.955 linhas e cinco janelas temporais expansivas.
As 4.640 vendas de 4 de março a 27 de maio de 2015 formam um período diagnóstico
que já havia sido consultado; ele não é apresentado como teste intocado.

### Validação temporal

| Métrica | Resultado médio |
| --- | ---: |
| MAE | US$ 63.880,80 |
| Desvio da MAE entre janelas | US$ 2.215,21 |
| Pior MAE | US$ 66.613,26 |
| RMSE | US$ 119.965,69 |
| RMSLE | 0,1660 |

### Período diagnóstico

| Métrica | Resultado |
| --- | ---: |
| MAE | US$ 67.105,71 |
| RMSE | US$ 116.547,25 |
| R² | 0,8998 |
| MAPE | 12,07% |
| Erro médio, previsão menos observado | -US$ 20.577,30 |
| Taxa de subestimação | 58,77% |
| Razão mediana entre previsto e observado | 0,9744 |

MAE representa a diferença absoluta média e não garante erro semelhante para
cada imóvel. R² mede ajuste relativo neste período; não é percentual de acerto.
O erro médio negativo e a taxa de subestimação registram tendência de previsão
abaixo do observado.

### Desempenho por faixa de preço

| Faixa | Intervalo observado | Linhas | MAE | Erro médio | Subestimação |
| --- | --- | ---: | ---: | ---: | ---: |
| Q1 | US$ 81.000 a US$ 330.000 | 1.169 | US$ 35.309,65 | US$ 12.020,72 | 46,36% |
| Q2 | US$ 330.490 a US$ 464.000 | 1.151 | US$ 44.065,53 | -US$ 6.505,03 | 59,86% |
| Q3 | US$ 464.950 a US$ 655.000 | 1.162 | US$ 54.376,51 | -US$ 16.495,38 | 61,36% |
| Q4 | US$ 655.100 a US$ 5.350.000 | 1.158 | US$ 134.877,87 | -US$ 71.568,18 | 67,62% |

O quartil superior concentra o maior erro e a maior subestimação. A tabela é
gerada por `python -m property_value_insights.stakeholder_reporting` e pode ser auditada em
[`reports/approved_model_price_bands.csv`](../reports/approved_model_price_bands.csv).

### Importância das variáveis

A importância por permutação foi calculada no mesmo período diagnóstico com o
modelo físico. Em cada repetição, uma feature é embaralhada e mede-se o aumento
da MAE. As quatro maiores variações foram latitude (US$ 112.415,66), área
habitável (US$ 55.841,29), padrão construtivo (US$ 38.219,50) e longitude
(US$ 27.246,21).

Essa medida descreve dependência preditiva no recorte avaliado, não causalidade.
Features espaciais e correlacionadas podem dividir ou concentrar importância. A
tabela completa e o desvio entre repetições estão em
[`reports/approved_model_feature_importance.csv`](../reports/approved_model_feature_importance.csv).

### Incerteza diagnóstica

Um intervalo empírico temporal de nível nominal de 90% foi calibrado com 13.724
resíduos fora de amostra das cinco janelas de desenvolvimento. No período
diagnóstico, a cobertura observada foi de 89,40%, com largura média de
US$ 281.835,45 e mediana de US$ 239.598,20.

| Faixa | Cobertura | Largura média |
| --- | ---: | ---: |
| Q1 | 85,71% | US$ 144.163,08 |
| Q2 | 91,31% | US$ 206.500,44 |
| Q3 | 93,72% | US$ 283.703,72 |
| Q4 | 86,87% | US$ 493.820,50 |

A cobertura inferior a 90% nos extremos e o aumento de largura no Q4 impedem
uma promessa uniforme por imóvel. Dependência temporal e mudança de distribuição
também impedem apresentar esse diagnóstico como garantia conformal em produção.

### Explicabilidade SHAP

O `PermutationExplainer` foi aplicado offline ao Joblib verificado, usando 50
linhas históricas como baseline determinístico e as 100 linhas futuras como
amostra explicada. Latitude, área habitável, padrão construtivo e longitude
apresentaram as maiores contribuições absolutas médias.

As contribuições locais reconciliaram baseline e previsão com erro numérico
máximo de `1,40e-9`. Elas descrevem o comportamento do modelo em relação ao
baseline escolhido; não medem causalidade, acurácia futura nem efeito isolado de
features correlacionadas. Os resultados completos estão no
[`relatório opcional`](../reports/optional_analysis.md).

## Limitações

- cobertura restrita a uma região e pouco mais de um ano;
- ausência de variáveis como conservação detalhada, reformas qualitativas,
  transações comparáveis e condições macroeconômicas;
- CEP e coordenadas podem representar desigualdades territoriais;
- comportamento menos confiável para valores altos e casos raros;
- período diagnóstico previamente inspecionado durante o desenvolvimento;
- exemplos futuros sem preço observado não medem acurácia;
- categorias de CEP desconhecidas são aceitas pelo encoder, mas exigem
  monitoramento de cobertura.

## Considerações éticas

O sistema não deve substituir avaliação humana nem fundamentar sozinho decisões
com efeito financeiro sobre pessoas. Erros podem afetar de forma diferente
proprietários, compradores e regiões. Localização pode atuar como proxy de
condições socioeconômicas mesmo sem demografia explícita.

O dataset não contém atributos protegidos adequados para medir paridade entre
grupos. A ausência desses atributos não demonstra equidade. A avaliação atual
monitora preço, tempo e CEP com contagens visíveis, evitando conclusões sobre
indivíduos.

## Controles

- contrato de dados e filtro de consistência temporal;
- validação temporal com datas completas;
- manifesto com dados, runtime, features, métricas e hashes;
- artefato e imagem imutáveis;
- API com validação estrita, moeda, versão e correlação;
- revisão humana para promoção e rollback;
- monitoramento geral e por segmentos após novos rótulos;
- retenção do champion anterior;
- análises de incerteza e SHAP isoladas do runtime de inferência.

## Manutenção

O modelo é reavaliado quando chegam novos preços observados, quando há mudança
de uso ou quando o monitoramento aponta degradação. Um challenger somente
substitui o champion após os gates temporais, validação do serviço, atualização
deste documento e aprovação humana.

O processo está detalhado em
[`CONTINUOUS_LEARNING.md`](CONTINUOUS_LEARNING.md), e as fontes metodológicas,
em [`REFERENCES.md`](REFERENCES.md).
