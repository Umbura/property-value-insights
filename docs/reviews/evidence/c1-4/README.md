# Evidências C1.4 — qualidade dos dados

Esta pasta contém evidências derivadas da revisão da Issue #37.

| Arquivo | Conteúdo |
|---|---|
| `c1-4-data-quality-summary.json` | contagens, hashes, cobertura e correlações consolidadas |
| `c1-4-temporal-inconsistencies.csv` | 18 linhas excluídas por evento posterior à venda |
| `c1-4-anomaly-candidates.csv` | registros com 33/0 quartos, 0 banheiros ou relação lote/pavimento incomum |
| `c1-4-future-coverage.csv` | comparação univariada das 100 entradas futuras com limites históricos |
| `c1-4-feature-governance.csv` | papel, documentação, disponibilidade, risco e decisão por campo |
| `c1-4-repeated-id-overlap.csv` | 98 chaves presentes em desenvolvimento e diagnóstico |

A verificação de cobertura futura é estrutural e univariada. Ela não demonstra
cobertura multivariada, ausência de combinações raras ou precisão esperada.

Os arquivos são diagnósticos. Eles não modificam os CSVs brutos e não autorizam
correção, exclusão, retreinamento ou regeneração do artefato.
