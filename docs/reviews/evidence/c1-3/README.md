# Evidências da review C1.3

Este diretório contém as evidências mínimas usadas na revisão da Issue #36.
Os arquivos são diagnósticos e não alteram dados brutos, modelo, artefato,
manifesto, hashes de serving ou respostas da API.

## Proveniência

- modelo: `property_value_hist_gradient_boosting_physical`;
- versão: `0.4.0-rc1`;
- release avaliada: `v1.0.0`;
- matriz M01: inferência local contra `POST /predict/batch`;
- auditoria M02: reprodução do protocolo aprovado com os dados e o código versionados;
- relatório consolidado: [`../../c1-3-model-review.md`](../../c1-3-model-review.md).

Os CSVs `top-zipcodes`, `q4-subsegments` e `q4-fixed-bands` foram extraídos
diretamente do JSON consolidado para facilitar inspeção humana. O JSON permanece
como fonte estruturada desses recortes.

## Arquivos

| Arquivo | Bytes | SHA-256 | Conteúdo |
|---|---:|---|---|
| `c1-3-m01-sensitivity-results.csv` | 2406 | `8ab64aee1e75a8dfbf3a3d059b463b58cc91dec2ec2e3a066a60cf283d80deb5` | 25 casos controlados enviados ao endpoint `/predict/batch`. |
| `c1-3-m02-summary.json` | 12322 | `a18fc7ab793b1af4e2c9e2a089f6e32f123dd7311dc65936115a881440143a16` | Resumo consolidado da reprodução diagnóstica, métricas por ZIP e alto valor. |
| `c1-3-m02-top-zipcodes-by-mae.csv` | 2563 | `30adc9cc66cb51d17d1e5d933ce2a4990f66f15f8e3f88fb5b8cd33bb55dc2b9` | Top 10 ZIPs por MAE, extraído de `c1-3-m02-summary.json`. |
| `c1-3-m02-month-metrics.csv` | 912 | `f7b699452b5fb7ca9d88f6b8958b6f1eb4c04dea64cef5b52f40e2e98b70ed25` | Métricas de março, abril e maio de 2015 no período diagnóstico. |
| `c1-3-m02-q4-subsegments.csv` | 1144 | `5afe42d986ba05146d693797194d5b6912dcdfce9524eb8613fc8fec83a04cfd` | Subdivisão do quartil superior em quatro grupos de frequência semelhante. |
| `c1-3-m02-q4-fixed-bands.csv` | 938 | `ed3ed52118b76b401f7d4ba7a4c9519000520ae10e5b4958331467c94d53cb4e` | Métricas para US$ 655 mil–1 mi, US$ 1–2 mi e acima de US$ 2 mi. |
| `c1-3-m02-worst-residuals.csv` | 3557 | `55acc911f6ddcbc7ad6966ed4d0b84dda405e80e82fac5b1e69214713990fa10` | Vinte maiores resíduos absolutos do período diagnóstico. |

## Limites de interpretação

- O período de março a maio de 2015 é diagnóstico e já havia sido consultado.
- Resultados por ZIP não demonstram causalidade do CEP.
- As 100 linhas futuras não possuem preço observado e não medem acurácia.
- Os valores de alto preço exigem revisão humana; não constituem autorização
  para retreino ou promoção automática de outro modelo.
