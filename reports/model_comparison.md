# Relatorio de modelagem e avaliacao

## Protocolo

- Linhas de desenvolvimento: 16,973.
- Linhas do teste temporal: 4,640.
- Ultima data do desenvolvimento: 2015-03-03.
- Primeira data do teste: 2015-03-04.
- Validacao: tres janelas temporais expansivas.
- Features demograficas: comparadas por ablation.
- O id foi excluido das features e o zipcode foi tratado como categoria.

## Comparacao

| candidate                  | features          | target   |   cv_mae_mean |   cv_mae_std |   cv_rmse_mean |   cv_rmsle_mean |   holdout_mae |   holdout_rmse |   holdout_rmsle |   holdout_r2 |   fit_seconds |
|:---------------------------|:------------------|:---------|--------------:|-------------:|---------------:|----------------:|--------------:|---------------:|----------------:|-------------:|--------------:|
| hist_demographics_log      | with_demographics | log      |       63078   |      820.937 |         120855 |        0.164848 |       73912.4 |         129024 |        0.1818   |    0.877175  |     1.27002   |
| hist_demographics_log_slow | with_demographics | log      |       63345   |     1276.59  |         121141 |        0.164363 |       73943.7 |         128893 |        0.181868 |    0.877425  |     2.03503   |
| hist_demographics_log_wide | with_demographics | log      |       63734.6 |      812.634 |         121906 |        0.166261 |       74034.9 |         128179 |        0.182726 |    0.878779  |     1.89637   |
| hist_demographics_raw      | with_demographics | raw      |       65522.6 |      340.925 |         126131 |        0.168386 |       72396.8 |         126085 |        0.179011 |    0.882706  |     1.02571   |
| hist_physical_raw          | physical          | raw      |       66489.8 |      903.582 |         127827 |        0.170456 |       74455.2 |         126051 |        0.181861 |    0.88277   |     0.750508  |
| ridge_demographics_log     | with_demographics | log      |       73774.6 |     2071.74  |         143097 |        0.182801 |       84812.2 |         143570 |        0.200393 |    0.84792   |     0.0854065 |
| ridge_physical_log         | physical          | log      |       74844.9 |     1550.09  |         137578 |        0.184403 |       85667.9 |         144298 |        0.201133 |    0.846373  |     0.042778  |
| ridge_demographics_raw     | with_demographics | raw      |       94378.4 |     2609.8   |         158453 |        0.767319 |      101491   |         171105 |        0.727899 |    0.783992  |     0.0814032 |
| ridge_physical_raw         | physical          | raw      |       94989.8 |     2439.96  |         160622 |        0.815319 |      101607   |         170959 |        0.762547 |    0.784359  |     0.0468618 |
| baseline_median            | physical          | raw      |      217589   |     1473.26  |         367729 |        0.524564 |      225354   |         382415 |        0.525018 |   -0.0789836 |     0         |

## Resultado selecionado

O candidato selecionado pela menor MAE media na validacao temporal foi `hist_demographics_log`.
A avaliacao final foi realizada no periodo temporal reservado e nao participou do ajuste.

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
