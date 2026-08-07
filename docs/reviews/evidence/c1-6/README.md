# Evidências C1.6 — operação e imagem Docker

Esta pasta preserva resultados pequenos e auditáveis da Issue #39. A imagem
local usada na review não foi publicada e os workflows/scripts temporários de
auditoria não fazem parte do diff final.

| Arquivo | Conteúdo | Limite de interpretação |
| --- | --- | --- |
| `METHOD.md` | ambiente, comandos e procedimento de reprodução | preserva o método, não a implementação temporária exata |
| `summary.json` | síntese dos controles e achados | não substitui os arquivos detalhados |
| `image-inspect.json` | ID, tamanho, usuário, healthcheck e camadas | imagem local sem digest de registry |
| `runtime-checks.json` | non-root, read-only, tmpfs, endpoints, métricas e request IDs | execução única em runner Linux |
| `load-latency-summary.json` | 100 chamadas sequenciais e 50 concorrentes | não é SLA nem teste de capacidade |
| `logging-review.json` | estrutura e amostras sanitizadas de logs | não contém o stream completo |
| `artifact-failure-scenarios.json` | artefato ausente, manifesto inválido e hash divergente | logs reduzidos aos trechos relevantes |

A revisão consolidada está em
[`../../c1-6-docker-operations-review.md`](../../c1-6-docker-operations-review.md).
