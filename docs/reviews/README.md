# Índice e status das reviews

## Fontes atuais da revisão pré-entrega

| Documento | Status | Papel |
| --- | --- | --- |
| `c1-2-api-manual-tests.md` | atual | comportamento manual da API |
| `c1-3-model-review.md` | atual | comportamento, cauda, geografia, tempo e OOD |
| `c1-4-data-quality-review.md` | atual | qualidade, anomalias, proxy e cobertura dos dados |
| `c1-5-documentation-governance-review.md` | atual | auditoria documental e de governança |

## Snapshots históricos das Fases 0–7

Os arquivos `phase-*.md` preservam decisões e verificações no momento de cada
fase. Eles não são fontes canônicas do estado atual do serving. Quando houver
divergência, prevalecem o manifesto versionado, o contrato da API, o model card
e as reviews C1.

## Relatórios históricos de experimentos

`reports/model_comparison.md` contém uma promoção estatística intermediária da
variante demográfica. A avaliação de governança posterior aprovou o modelo
físico para serving. Portanto, “modelo promovido” naquele relatório não significa
“modelo servido atualmente”.

## Organização futura

Os snapshots permanecem nos caminhos atuais para evitar quebrar links durante o
Ciclo 1. A mudança de documentos de processo ou históricos para `docs/process/`
ou `docs/archive/` deve ocorrer somente na lapidação final do repositório, com
atualização de todos os links em PR própria.
