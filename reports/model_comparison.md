# Relatorio de modelagem e avaliacao

## Protocolo

- Linhas de desenvolvimento: 16,973.
- Linhas do teste temporal: 4,640.
- Ultima data do desenvolvimento: 2015-03-03.
- Primeira data do teste: 2015-03-04.
- Validacao: cinco janelas temporais expansivas com datas completas.
- Busca: conjunto pequeno e deterministico de configuracoes.
- Features demograficas: comparadas por ablation.
- O id foi excluido das features e o zipcode foi tratado como categoria.
- O teste temporal foi consultado somente apos a selecao.

## Validacao temporal

| candidate                         |   cv_mae_mean |   cv_mae_std |   cv_mae_worst |   cv_rmse_mean |   cv_rmsle_mean |
|:----------------------------------|--------------:|-------------:|---------------:|---------------:|----------------:|
| hist_demographics_log_default     |     63128.370 |     1547.451 |      65603.156 |     117518.968 |           0.165 |
| hist_demographics_log_regularized |     63174.280 |     1498.971 |      65856.540 |     118599.353 |           0.165 |
| hist_physical_log                 |     63446.127 |     1987.592 |      65887.791 |     119528.952 |           0.166 |
| hist_demographics_log_compact     |     63448.359 |     1591.989 |      66517.984 |     118678.396 |           0.164 |
| hist_demographics_log_wide        |     63633.244 |     1509.352 |      65680.256 |     120067.486 |           0.166 |
| hist_demographics_raw_regularized |     65237.570 |      918.714 |      66324.755 |     124113.924 |           0.168 |
| hist_demographics_raw_default     |     65281.699 |      648.045 |      66147.670 |     123517.206 |           0.169 |
| hist_demographics_raw_wide        |     65555.919 |     1048.415 |      66842.948 |     125786.020 |           0.169 |
| hist_demographics_raw_compact     |     65846.619 |      687.676 |      66844.271 |     122395.857 |           0.170 |
| hist_physical_raw                 |     67025.367 |     2115.784 |      70082.978 |     127212.944 |           0.172 |
| ridge_demographics_log            |     74355.564 |     1593.834 |      77303.053 |     143817.268 |           0.184 |
| ridge_physical_log                |     75805.686 |     1227.319 |      77879.837 |     139856.263 |           0.186 |
| ridge_demographics_raw            |     95192.024 |     2158.789 |      98465.767 |     158699.888 |           0.762 |
| ridge_physical_raw                |     95995.196 |     1840.264 |      98992.201 |     160603.046 |           0.806 |
| baseline_median                   |    219003.585 |     3909.205 |     223307.567 |     369960.663 |           0.527 |

## Janelas temporais do champion

|   fold | train_end           | validation_start    | validation_end      |   train_rows |   validation_rows |
|-------:|:--------------------|:--------------------|:--------------------|-------------:|------------------:|
|      1 | 2014-06-22 00:00:00 | 2014-06-23 00:00:00 | 2014-08-10 00:00:00 |         3235 |              3442 |
|      2 | 2014-08-10 00:00:00 | 2014-08-11 00:00:00 | 2014-09-28 00:00:00 |         6677 |              3058 |
|      3 | 2014-09-28 00:00:00 | 2014-09-29 00:00:00 | 2014-11-16 00:00:00 |         9735 |              2792 |
|      4 | 2014-11-16 00:00:00 | 2014-11-17 00:00:00 | 2015-01-10 00:00:00 |        12527 |              2392 |
|      5 | 2015-01-10 00:00:00 | 2015-01-12 00:00:00 | 2015-03-03 00:00:00 |        14919 |              2054 |

## Decisao do modelo

| candidate                         |   cv_mae_mean |   cv_mae_std |   cv_mae_worst |   cv_rmse_mean |   cv_rmsle_mean | role       |
|:----------------------------------|--------------:|-------------:|---------------:|---------------:|----------------:|:-----------|
| hist_demographics_log_default     |     63128.370 |     1547.451 |      65603.156 |     117518.968 |           0.165 | champion   |
| hist_demographics_log_regularized |     63174.280 |     1498.971 |      65856.540 |     118599.353 |           0.165 | challenger |

O champion `hist_demographics_log_default` foi escolhido entre os candidatos ate 0.5% da menor MAE media, priorizando o menor erro no pior fold e a menor variacao temporal.
O challenger `hist_demographics_log_regularized` apresentou a menor MAE media entre os candidatos restantes e nao foi avaliado no teste temporal.

## Avaliacao temporal reservada

| candidate                     |        mae |       rmse |   rmsle |     r2 |   median_absolute_error |   fit_seconds |
|:------------------------------|-----------:|-----------:|--------:|-------:|------------------------:|--------------:|
| baseline_median               | 225353.885 | 382414.550 |   0.525 | -0.079 |              149600.000 |         0.000 |
| hist_demographics_log_default |  73912.439 | 129023.800 |   0.182 |  0.877 |               44598.518 |         1.620 |

## Comparacao com a referencia

A versao inicial nao incluia um modelo preditivo. A mediana dos precos no conjunto de desenvolvimento e a referencia quantitativa.

| metric   |   median_baseline |   champion | relative_reduction_pct   |   absolute_change |
|:---------|------------------:|-----------:|:-------------------------|------------------:|
| MAE      |        225354     |  73912.4   | 67.2%                    |       -151441     |
| RMSE     |        382415     | 129024     | 66.3%                    |       -253391     |
| RMSLE    |             0.525 |      0.182 | 65.4%                    |            -0.343 |
| R2       |            -0.079 |      0.877 | -                        |             0.956 |

A MAE do champion foi reduzida em 67.2%.
O R2 passou de -0.079 na referencia para 0.877 no champion.

## Erro por faixa de preco

| price_band            |   rows |      mae |     rmse |    rmsle |        r2 |   median_absolute_error |
|:----------------------|-------:|---------:|---------:|---------:|----------:|------------------------:|
| (80999.999, 330000.0] |   1169 |  34718.3 |  46205.5 | 0.183378 |  0.126784 |                 27079.3 |
| (330000.0, 464475.0]  |   1151 |  48118.6 |  65313.2 | 0.172619 | -1.92648  |                 38345   |
| (464475.0, 655000.0]  |   1162 |  60778.7 |  78448.7 | 0.157619 | -1.04005  |                 49763.9 |
| (655000.0, 5350000.0] |   1158 | 152296   | 232665   | 0.209618 |  0.755688 |                102986   |

## Maiores erros por CEP

|   zipcode |   rows |    mae |   rmse |    rmsle |       r2 |   median_absolute_error |
|----------:|-------:|-------:|-------:|---------:|---------:|------------------------:|
|     98112 |     47 | 222328 | 318463 | 0.202124 | 0.758248 |                146463   |
|     98004 |     63 | 211341 | 304483 | 0.167409 | 0.872907 |                151313   |
|     98040 |     67 | 173003 | 277713 | 0.17334  | 0.805673 |                114904   |
|     98006 |     98 | 158472 | 308898 | 0.202278 | 0.73067  |                 74071.1 |
|     98105 |     49 | 145311 | 209159 | 0.177252 | 0.896309 |                 91608.5 |
|     98005 |     33 | 117792 | 153388 | 0.18218  | 0.791065 |                 87099.9 |
|     98199 |     68 | 117489 | 211267 | 0.178758 | 0.770058 |                 64391.1 |
|     98119 |     36 | 105671 | 139581 | 0.16394  | 0.65242  |                 80388.6 |
|     98033 |     98 | 105584 | 164978 | 0.178168 | 0.795102 |                 73142.2 |
|     98115 |    135 | 104100 | 144589 | 0.216313 | 0.595982 |                 70957.1 |

## Variaveis com maior impacto na MAE

| feature       |   mae_increase |   mae_std |
|:--------------|---------------:|----------:|
| sqft_living   |       54490.9  |  275.212  |
| lat           |       49954.7  |  626.764  |
| grade         |       39444.1  |  691.447  |
| per_bchlr     |       14337.4  |  103.231  |
| per_prfsnl    |       12852.9  |   44.0214 |
| hous_val_amt  |        8944.1  |  299.418  |
| long          |        8171.34 |  431.893  |
| sqft_lot      |        7974.35 |  245.387  |
| view          |        6084.16 |  145.503  |
| yr_built      |        5054.29 |  203.113  |
| sqft_living15 |        4275.94 |  549.857  |
| sqft_above    |        3800.79 |   65.6848 |
| condition     |        3379    |   31.5635 |
| waterfront    |        2753.59 |   56.3702 |
| bathrooms     |        1798.31 |  193.635  |

O desempenho deve ser interpretado junto com a distribuicao temporal, as faixas de preco e a cobertura dos CEPs observados.
