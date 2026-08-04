# Relatório de modelagem, calibração e avaliação

> **Contexto do experimento:** este relatório registra a promoção estatística dos candidatos calibrados. A avaliação de governança posterior selecionou o modelo somente físico como artefato final. Portanto, as seções "modelo promovido" e "importância das variáveis" abaixo descrevem o experimento demográfico e não o modelo servido pela API. Os resultados vigentes estão em [`training_summary.md`](training_summary.md), [`MODEL_CARD.md`](../docs/MODEL_CARD.md) e [`stakeholder_summary.md`](stakeholder_summary.md).

## Protocolo

- Linhas de desenvolvimento: 16,973.
- Linhas do teste temporal: 4,640.
- Última data do desenvolvimento: 2015-03-03.
- Primeira data do teste: 2015-03-04.
- Validação: cinco janelas temporais expansivas com datas completas.
- Faixa superior: valores iguais ou superiores ao terceiro quartil do treino de cada fold.
- Margem máxima para a MAE geral: 0,5% em relação ao melhor candidato e à referência.
- Promoção: melhora do MAE e do viés absoluto da faixa superior em pelo menos quatro folds.
- O teste temporal não participa da seleção da calibração.

## Validação temporal geral

| candidate                                  |   cv_mae_mean |   cv_mae_std |   cv_mae_worst |   cv_rmse_mean |   cv_rmsle_mean |
|:-------------------------------------------|--------------:|-------------:|---------------:|---------------:|----------------:|
| hist_demographics_log_smearing             |     62962.571 |     1355.364 |      64918.225 |     117011.308 |           0.164 |
| hist_demographics_log_default              |     63128.370 |     1547.451 |      65603.156 |     117518.968 |           0.165 |
| hist_demographics_log_temporal_smearing_10 |     63154.780 |     1567.750 |      65740.790 |     116561.311 |           0.165 |
| hist_demographics_log_regularized          |     63174.280 |     1498.971 |      65856.540 |     118599.353 |           0.165 |
| hist_demographics_log_temporal_smearing_20 |     63181.649 |     1576.681 |      65694.686 |     116578.176 |           0.165 |
| hist_demographics_gamma_default            |     63256.844 |     1108.772 |      65147.888 |     119645.068 |           0.164 |
| hist_physical_log_temporal_smearing_10     |     63431.871 |     2025.933 |      66875.891 |     118528.078 |           0.166 |
| hist_physical_log                          |     63446.127 |     1987.592 |      65887.791 |     119528.952 |           0.166 |
| hist_demographics_log_compact              |     63448.359 |     1591.989 |      66517.984 |     118678.396 |           0.164 |
| hist_demographics_poisson_default          |     63476.475 |      588.881 |      64497.774 |     118304.162 |           0.165 |
| hist_demographics_log_wide                 |     63633.244 |     1509.352 |      65680.256 |     120067.486 |           0.166 |
| hist_demographics_absolute_default         |     64731.102 |     1303.092 |      66198.552 |     130719.744 |           0.167 |
| hist_demographics_raw_regularized          |     65237.570 |      918.714 |      66324.755 |     124113.924 |           0.168 |
| hist_demographics_raw_default              |     65281.699 |      648.045 |      66147.670 |     123517.206 |           0.169 |
| hist_demographics_raw_wide                 |     65555.919 |     1048.415 |      66842.948 |     125786.020 |           0.169 |
| hist_demographics_raw_compact              |     65846.619 |      687.676 |      66844.271 |     122395.857 |           0.170 |
| hist_physical_raw                          |     67025.367 |     2115.784 |      70082.978 |     127212.944 |           0.172 |
| ridge_demographics_log                     |     74355.564 |     1593.834 |      77303.053 |     143817.268 |           0.184 |
| ridge_physical_log                         |     75805.686 |     1227.319 |      77879.837 |     139856.263 |           0.186 |
| ridge_demographics_raw                     |     95192.024 |     2158.789 |      98465.767 |     158699.888 |           0.762 |
| ridge_physical_raw                         |     95995.196 |     1840.264 |      98992.201 |     160603.046 |           0.806 |
| baseline_median                            |    219003.585 |     3909.205 |     223307.567 |     369960.663 |           0.527 |

## Candidatos calibrados

| candidate                                  |   cv_mae_mean |   cv_mape_mean |   cv_mean_error_mean |   cv_underprediction_rate_mean |   cv_prd_mean |   cv_high_price_mae_mean |   cv_high_price_mean_error_mean |   cv_high_price_underprediction_rate_mean |   high_price_mae_improved_folds |
|:-------------------------------------------|--------------:|---------------:|---------------------:|-------------------------------:|--------------:|-------------------------:|--------------------------------:|------------------------------------------:|--------------------------------:|
| hist_demographics_log_smearing             |    62962.5713 |         0.1193 |           -8775.6547 |                         0.5194 |        1.0290 |              128907.1255 |                     -54671.0024 |                                    0.6266 |                               5 |
| hist_demographics_log_default              |    63128.3704 |         0.1190 |          -11579.3703 |                         0.5373 |        1.0290 |              130027.9650 |                     -59767.7314 |                                    0.6452 |                               0 |
| hist_demographics_log_temporal_smearing_10 |    63154.7804 |         0.1210 |           -2194.7020 |                         0.4788 |        1.0290 |              127277.6685 |                     -42838.9080 |                                    0.5861 |                               4 |
| hist_demographics_log_temporal_smearing_20 |    63181.6488 |         0.1210 |           -2554.2536 |                         0.4809 |        1.0290 |              127428.9544 |                     -43533.8095 |                                    0.5863 |                               5 |
| hist_demographics_gamma_default            |    63256.8443 |         0.1195 |           -8402.9421 |                         0.5196 |        1.0289 |              130320.3761 |                     -52948.7174 |                                    0.6236 |                               2 |
| hist_physical_log_temporal_smearing_10     |    63431.8707 |         0.1213 |           -2016.6437 |                         0.4779 |        1.0288 |              127964.3447 |                     -42684.0028 |                                    0.5972 |                               3 |
| hist_demographics_poisson_default          |    63476.4749 |         0.1206 |           -6985.1151 |                         0.5132 |        1.0302 |              130158.1661 |                     -51304.8940 |                                    0.6205 |                               2 |
| hist_demographics_absolute_default         |    64731.1018 |         0.1210 |          -10173.9347 |                         0.5157 |        1.0370 |              137560.2453 |                     -66119.9677 |                                    0.6480 |                               0 |

As métricas de razão são diagnósticos adaptados para monitoramento preditivo e não representam uma avaliação formal de conformidade tributária.

## Decisão de promoção

| candidate                                  |   cv_mae_mean |   cv_mape_mean |   cv_mean_error_mean |   cv_underprediction_rate_mean |   cv_prd_mean |   cv_high_price_mae_mean |   cv_high_price_mean_error_mean |   cv_high_price_underprediction_rate_mean |   high_price_mae_improved_folds | role             |
|:-------------------------------------------|--------------:|---------------:|---------------------:|-------------------------------:|--------------:|-------------------------:|--------------------------------:|------------------------------------------:|--------------------------------:|:-----------------|
| hist_demographics_log_temporal_smearing_10 |    63154.7804 |         0.1210 |           -2194.7020 |                         0.4788 |        1.0290 |              127277.6685 |                     -42838.9080 |                                    0.5861 |                               4 | modelo promovido |
| hist_demographics_log_default              |    63128.3704 |         0.1190 |          -11579.3703 |                         0.5373 |        1.0290 |              130027.9650 |                     -59767.7314 |                                    0.6452 |                               0 | referência       |

O modelo `hist_demographics_log_temporal_smearing_10` foi promovido porque permaneceu dentro da margem de 0.5%, reduziu o MAE e o viés absoluto da faixa superior e melhorou pelo menos 4 folds.

## Janelas temporais do modelo promovido

|   fold | train_end           | validation_start    | validation_end      |   train_rows |   validation_rows |   high_price_threshold |   high_price_rows |
|-------:|:--------------------|:--------------------|:--------------------|-------------:|------------------:|-----------------------:|------------------:|
|      1 | 2014-06-22 00:00:00 | 2014-06-23 00:00:00 | 2014-08-10 00:00:00 |         3235 |              3442 |                 660000 |               840 |
|      2 | 2014-08-10 00:00:00 | 2014-08-11 00:00:00 | 2014-09-28 00:00:00 |         6677 |              3058 |                 657000 |               698 |
|      3 | 2014-09-28 00:00:00 | 2014-09-29 00:00:00 | 2014-11-16 00:00:00 |         9735 |              2792 |                 650000 |               664 |
|      4 | 2014-11-16 00:00:00 | 2014-11-17 00:00:00 | 2015-01-10 00:00:00 |        12527 |              2392 |                 649000 |               563 |
|      5 | 2015-01-10 00:00:00 | 2015-01-12 00:00:00 | 2015-03-03 00:00:00 |        14919 |              2054 |                 645000 |               440 |

## Avaliação temporal diagnóstica

Os resíduos deste período motivaram a calibração adicional. Por isso, os resultados abaixo são diagnósticos posteriores à seleção temporal e não um novo teste completamente intocado.

| candidate                                  |         mae |        rmse |   rmsle |      r2 |   median_absolute_error |   mape |   mean_error |   mean_percentage_error |   underprediction_rate |   median_prediction_ratio |   coefficient_of_dispersion |   price_related_differential |
|:-------------------------------------------|------------:|------------:|--------:|--------:|------------------------:|-------:|-------------:|------------------------:|-----------------------:|--------------------------:|----------------------------:|-----------------------------:|
| baseline_median                            | 225353.8853 | 382414.5500 |  0.5250 | -0.0790 |             149600.0000 | 0.4097 | -103465.4466 |                  0.0717 |                 0.5304 |                    0.9678 |                     42.2629 |                       1.3184 |
| hist_demographics_log_default              |  73912.4389 | 129023.8004 |  0.1818 |  0.8772 |              44598.5181 | 0.1289 |  -43927.8127 |                 -0.0531 |                 0.7147 |                    0.9319 |                     12.1739 |                       1.0286 |
| hist_demographics_log_temporal_smearing_10 |  67455.9069 | 120406.8921 |  0.1700 |  0.8930 |              39888.9647 | 0.1209 |  -20891.8611 |                 -0.0102 |                 0.5890 |                    0.9740 |                     12.1739 |                       1.0286 |

## Comparação com a mediana

| metric   |   median_baseline |   champion | relative_reduction_pct   |   absolute_change |
|:---------|------------------:|-----------:|:-------------------------|------------------:|
| MAE      |        225354     |  67455.9   | 70.1%                    |       -157898     |
| RMSE     |        382415     | 120407     | 68.5%                    |       -262008     |
| RMSLE    |             0.525 |      0.17  | 67.6%                    |            -0.355 |
| R2       |            -0.079 |      0.893 | -                        |             0.972 |

A MAE do modelo promovido foi reduzida em 70.1% em relação à mediana.
O R² passou de -0.079 na mediana para 0.893 no modelo promovido.

## Faixa superior no período diagnóstico

| candidate                                  |   threshold |   rows |         mae |   mape |   mean_error |   underprediction_rate |   median_prediction_ratio |   price_related_differential |
|:-------------------------------------------|------------:|-------:|------------:|-------:|-------------:|-----------------------:|--------------------------:|-----------------------------:|
| hist_demographics_log_default              | 640000.0000 |   1246 | 146699.1973 | 0.1388 | -109978.1061 |                 0.7953 |                    0.8999 |                       1.0102 |
| hist_demographics_log_temporal_smearing_10 | 640000.0000 |   1246 | 131242.9584 | 0.1231 |  -70639.7192 |                 0.6894 |                    0.9407 |                       1.0102 |

## Erro por faixa de preço

| price_band            |   rows |         mae |   mape |   mean_error |   underprediction_rate |   median_prediction_ratio |   price_related_differential |
|:----------------------|-------:|------------:|-------:|-------------:|-----------------------:|--------------------------:|-----------------------------:|
| (80999.999, 330000.0] |   1169 |  35332.4969 | 0.1491 |   12512.6199 |                 0.4508 |                    1.0175 |                       1.0173 |
| (330000.0, 464475.0]  |   1151 |  44420.4877 | 0.1114 |   -5800.1956 |                 0.5995 |                    0.9741 |                       1.0007 |
| (464475.0, 655000.0]  |   1162 |  53988.0277 | 0.0979 |  -16811.8892 |                 0.6119 |                    0.9692 |                       1.0004 |
| (655000.0, 5350000.0] |   1158 | 136295.0345 | 0.1249 |  -73708.1587 |                 0.6952 |                    0.9390 |                       1.0103 |

## Erro mensal

| month   |   rows |        mae |   mape |   mean_error |   underprediction_rate |   median_prediction_ratio |
|:--------|-------:|-----------:|-------:|-------------:|-----------------------:|--------------------------:|
| 2015-03 |   1763 | 62837.9253 | 0.1189 |  -12269.8155 |                 0.5440 |                    0.9871 |
| 2015-04 |   2231 | 68724.9574 | 0.1203 |  -22939.0093 |                 0.6087 |                    0.9682 |
| 2015-05 |    646 | 75676.1084 | 0.1282 |  -37352.3544 |                 0.6440 |                    0.9568 |

## Maiores erros por CEP

|   zipcode |   rows |         mae |        rmse |   rmsle |     r2 |   median_absolute_error |   mape |   mean_error |   mean_percentage_error |   underprediction_rate |   median_prediction_ratio |   coefficient_of_dispersion |   price_related_differential |
|----------:|-------:|------------:|------------:|--------:|-------:|------------------------:|-------:|-------------:|------------------------:|-----------------------:|--------------------------:|----------------------------:|-----------------------------:|
|     98112 |     47 | 200706.9116 | 299200.5139 |  0.1850 | 0.7866 |             122605.1421 | 0.1431 |  -78203.1228 |                 -0.0366 |                 0.6809 |                    0.9439 |                     13.9491 |                       1.0254 |
|     98004 |     63 | 197075.9603 | 281041.3303 |  0.1547 | 0.8917 |             150238.8811 | 0.1258 |  -46220.6673 |                 -0.0124 |                 0.5714 |                    0.9726 |                     12.7972 |                       1.0191 |
|     98040 |     67 | 156490.6304 | 255617.6059 |  0.1582 | 0.8354 |              79792.7374 | 0.1161 |  -53093.4475 |                 -0.0223 |                 0.6269 |                    0.9668 |                     11.4900 |                       1.0219 |
|     98006 |     98 | 143278.6368 | 289298.9339 |  0.1912 | 0.7638 |              66762.9800 | 0.1324 |  -69412.9561 |                 -0.0089 |                 0.6327 |                    0.9764 |                     13.2002 |                       1.0697 |
|     98105 |     49 | 137621.4492 | 191536.1938 |  0.1642 | 0.9130 |             107004.9633 | 0.1342 |  -49545.4484 |                 -0.0152 |                 0.5306 |                    0.9864 |                     13.5466 |                       1.0377 |
|     98199 |     68 | 117046.8257 | 200214.5768 |  0.1717 | 0.7935 |              71138.6626 | 0.1289 |  -23445.2925 |                  0.0087 |                 0.4412 |                    1.0177 |                     12.4788 |                       1.0375 |
|     98005 |     33 | 102960.6210 | 136604.0719 |  0.1619 | 0.8343 |              69757.7676 | 0.1224 |  -51232.3287 |                 -0.0434 |                 0.7273 |                    0.9369 |                     11.1260 |                       1.0175 |
|     98115 |    135 |  94317.1184 | 132737.7238 |  0.1974 | 0.6595 |              68985.5468 | 0.1363 |  -48989.8522 |                 -0.0481 |                 0.6444 |                    0.9302 |                     13.5971 |                       1.0287 |
|     98033 |     98 |  91954.8406 | 145471.3829 |  0.1558 | 0.8407 |              60312.1924 | 0.1075 |  -55493.6763 |                 -0.0511 |                 0.6633 |                    0.9477 |                     10.5753 |                       1.0220 |
|     98107 |     57 |  89363.4707 | 208976.9633 |  0.1793 | 0.6176 |              46745.9561 | 0.1084 |  -63778.4984 |                 -0.0586 |                 0.6667 |                    0.9462 |                     10.1756 |                       1.0425 |

## Variáveis com maior impacto na MAE

| feature       |   mae_increase |   mae_std |
|:--------------|---------------:|----------:|
| sqft_living   |     57049.7347 |  501.9104 |
| lat           |     52916.9683 |  704.8514 |
| grade         |     40388.4989 |  634.3694 |
| per_bchlr     |     14462.0491 |  125.9968 |
| per_prfsnl    |     12818.9729 |  187.8906 |
| long          |      9971.6562 |  271.2515 |
| sqft_lot      |      9803.9362 |  126.4826 |
| hous_val_amt  |      8210.0990 |  193.3719 |
| yr_built      |      6317.6840 |  365.1674 |
| view          |      6177.8794 |  211.5035 |
| sqft_living15 |      4132.0275 |  636.4034 |
| condition     |      3728.3371 |   91.0615 |
| waterfront    |      2635.0549 |   76.7928 |
| sqft_above    |      2452.7666 |   20.9703 |
| bathrooms     |      1203.8389 |  215.3385 |

O desempenho deve ser interpretado junto com a distribuição temporal, as faixas de preço e a cobertura dos CEPs observados.
