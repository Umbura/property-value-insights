# Relatorio de EDA e qualidade dos dados

Status: artefato da Fase 1, sujeito a revisao supervisionada.

## Qualidade estrutural

| dataset      |   rows |   columns |   missing_cells |   exact_duplicate_rows |   unique_zipcodes |
|:-------------|-------:|----------:|----------------:|-----------------------:|------------------:|
| historical   |  21613 |        21 |               0 |                      0 |                70 |
| demographics |     70 |        27 |               0 |                      0 |                70 |
| future       |    100 |        18 |               0 |                      0 |                45 |

## Merge por CEP

- Linhas historicas: 21,613.
- Linhas apos o merge: 21,613.
- Retencao de linhas: 100.00%.
- CEPs historicos: 70.
- CEPs com correspondencia: 70.
- Cobertura de CEP: 100.00%.
- Linhas sem correspondencia: 0.
- Chaves de ID repetidas: 176.
- Linhas inteiramente duplicadas: 0.

O merge foi configurado como muitos-para-um. Nenhuma linha historica e
removida automaticamente nesta fase.

## Outliers pelo criterio IQR

| column      |     q1 |     q3 |   lower_bound |     upper_bound |   outlier_rows |   outlier_pct |
|:------------|-------:|-------:|--------------:|----------------:|---------------:|--------------:|
| price       | 321950 | 645000 |     -162625   |     1.12958e+06 |           1146 |       5.30236 |
| sqft_living |   1427 |   2550 |        -257.5 |  4234.5         |            572 |       2.64656 |
| sqft_lot    |   5040 |  10688 |       -3432   | 19160           |           2425 |      11.2201  |

## Correlacoes numericas com o preco

| feature       |   correlation |   abs_correlation |
|:--------------|--------------:|------------------:|
| sqft_living   |      0.702035 |          0.702035 |
| grade         |      0.667434 |          0.667434 |
| sqft_above    |      0.605567 |          0.605567 |
| sqft_living15 |      0.585379 |          0.585379 |
| bathrooms     |      0.525138 |          0.525138 |
| view          |      0.397293 |          0.397293 |
| sqft_basement |      0.323816 |          0.323816 |
| bedrooms      |      0.30835  |          0.30835  |
| lat           |      0.307003 |          0.307003 |
| waterfront    |      0.266369 |          0.266369 |

## Decisoes para a modelagem

- `id` sera mantido para rastreabilidade, mas excluido das features.
- `date` sera usada para ordenacao e separacao temporal, nao como feature
  final, pois nao aparece nos exemplos futuros.
- `zipcode` sera tratado como categoria e os dados demograficos serao
  avaliados com estudo de ablation.
- Outliers serao investigados e nao removidos apenas por regra estatistica.
