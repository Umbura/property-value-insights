# C1.6 — Revisão de operação, segurança e imagem Docker

## Escopo e decisão

Esta revisão valida a imagem Docker atual da release `v1.0.0` em um runner
efêmero GitHub-hosted Ubuntu 24.04, com build sem cache. Nenhuma imagem foi
publicada e não houve alteração de Dockerfile, Compose, CI permanente, modelo ou
artefato. A imagem é **aprovada para continuidade da entrega**, com melhorias não
bloqueantes de logging, tratamento de falhas e tamanho encaminhadas para trabalho
posterior.

## Resultado executivo

| Controle | Resultado |
| --- | --- |
| Build sem cache | aprovado em `20.186s` |
| Image ID | `e8e89798237e` |
| Tamanho local | `490.39 MB` |
| Camadas RootFS | `8` |
| Usuário do processo | UID `999`, GID `999` — não root |
| Filesystem raiz somente leitura | escrita em `/app` rejeitada |
| Diretório temporário | escrita em `/tmp` aprovada via tmpfs |
| `no-new-privileges` | ativo |
| Healthcheck | `healthy` em `6.099s` |
| Artefato ausente/inválido/hash divergente | três cenários rejeitados no startup |
| Repetição e concorrência | 150/150 respostas HTTP 200 e previsões estáveis |
| Request IDs | válidos preservados; inválidos substituídos; gerados únicos |
| Encerramento | comando concluído em `0.540s`, sem OOM |

O procedimento reproduzível está em
[`evidence/c1-6/METHOD.md`](evidence/c1-6/METHOD.md).

## 1. Build e conteúdo da imagem

O comando principal foi:

```bash
docker build --no-cache --tag property-value-insights:c1-6-review .
```

O Dockerfile usa estágios separados de build e runtime, imagens-base fixadas por
digest, ambiente bloqueado por `uv.lock` e usuário `app`. Nos caminhos testados,
`/app/data`, `/app/tests`, `/app/.git` e `/app/notebooks` não existiam; `gcc`,
`git` e `curl` também não foram encontrados no `PATH` do container.

O diretório `artifacts/` copiado para a imagem continha três entradas
versionadas: `.gitkeep`, `model_manifest.json` e
`property_value_model.joblib`. Além disso, o runtime recebeu o ambiente virtual
instalado no estágio de build.

A imagem local possui `490.39 MB`. Esse tamanho não impede a execução nem indica
que o estágio de build inteiro tenha sido copiado, mas é alto para distribuição
de uma API pequena. Esta revisão não decompôs o volume por pacote ou camada; a
análise e eventual redução segura ficaram registradas na Issue #70.

A ausência de `RepoDigest` é esperada para uma imagem local ainda não enviada a
registry. Já a ausência de labels OCI decorre de elas não estarem definidas no
Dockerfile atual; a decisão sobre metadata final pertence à preparação da
release e imagem de entrega.

Evidência: `evidence/c1-6/image-inspect.json`.

## 2. Isolamento e execução

O container foi iniciado com:

```bash
docker run --read-only --tmpfs /tmp --security-opt no-new-privileges:true ...
```

Resultados:

- processo executado como UID `999` e GID `999`;
- escrita em `/app` rejeitada;
- escrita temporária em `/tmp` permitida;
- `NoNewPrivs: 1` confirmado em `/proc/1/status`;
- `/health`, `/model-info`, `/metrics` e `/predict` disponíveis;
- Compose validado por `docker compose config --quiet`;
- encerramento sem `OOMKilled` e com exit code `0`.

Evidência: `evidence/c1-6/runtime-checks.json`.

## 3. Integridade do artefato

| Cenário | Exit code | Startup rejeitado | Traceback completo | Caminho interno nos logs |
| --- | ---: | --- | --- | --- |
| `missing-artifact` | 3 | sim | sim | sim |
| `invalid-manifest` | 3 | sim | sim | não |
| `hash-mismatch` | 3 | sim | sim | não |

Os três processos encerraram antes de disponibilizar a aplicação:

1. caminho de artefato inexistente;
2. manifesto com JSON inválido;
3. SHA-256 divergente no manifesto.

**Classificação funcional:** aprovada. A API não permanece em execução com estado
de modelo inválido.

**Achado de hardening:** os logs de startup incluem traceback Python completo e,
no cenário de artefato ausente, caminho interno do container. Nos trechos
inspecionados não apareceu conteúdo serializado do artefato nem credencial
conhecida, mas esta review não executou um secret scan abrangente. A saída é mais
detalhada do que o necessário para operação comum. O arquivo ausente também
chega como `FileNotFoundError`, enquanto manifesto ilegível e hash divergente são
classificados como `ArtifactIntegrityError`.

Evidência: `evidence/c1-6/artifact-failure-scenarios.json`.

## 4. Estabilidade, concorrência e latência

Foram executadas:

- `100` previsões sequenciais;
- `50` previsões concorrentes com `10` workers;
- total de `150` requisições de carga, além das verificações iniciais.

Todos os status foram `200`, todas as previsões coincidiram com o baseline de
`US$ 372,953.43` e os `150` request IDs observados foram únicos.

| Métrica | Resultado |
| --- | ---: |
| Latência mínima | 11.241 ms |
| Latência média | 64.743 ms |
| Mediana | 11.655 ms |
| P95 | 202.939 ms |
| Máxima | 271.464 ms |
| Throughput concorrente observado | 56.82 req/s |

Esses números caracterizam apenas uma execução em runner compartilhado do GitHub
Actions com carga moderada local. Não são SLA, benchmark de produção ou teste de
capacidade.

Evidência: `evidence/c1-6/load-latency-summary.json`.

## 5. Logs, métricas e request IDs

O logger da aplicação produz JSON estruturado com request ID, método, rota,
status e duração. Nenhum **nome de campo do payload** foi encontrado nos
registros JSON observados. A inspeção do código confirma que os campos adicionados
pelo logger operacional não incluem o objeto de entrada. Uma busca apenas por
valores foi descartada porque números de baixa cardinalidade como `0`, `1` e `4`
também aparecem em status, duração e metadata de versão.

Os contadores e histogramas Prometheus responderam antes e depois da carga,
incluindo requisições, duração e previsões.

Os request IDs seguiram o contrato nesta execução:

- valor válido foi preservado no header e no body;
- valor com espaços foi rejeitado e substituído por UUID hexadecimal;
- ausência de header gerou novo identificador;
- os 150 IDs da carga foram únicos.

**Achado operacional:** o stream agregado do container é misto. Registros da
aplicação estão em JSON, enquanto startup, shutdown e access logs do Uvicorn
permanecem em texto. Isso reduz a uniformidade de ingestão por coletores que
esperam uma linha JSON por evento.

Evidências: `evidence/c1-6/logging-review.json` e
`evidence/c1-6/runtime-checks.json`.

## 6. CI

O workflow permanente separa `quality` e `container`, faz o job de container
depender do quality e cobre:

- ambiente bloqueado;
- Ruff, testes, release-readiness e auditoria de dependências;
- build da imagem;
- read-only, tmpfs e `no-new-privileges`;
- healthcheck e endpoints públicos.

A PR somente deve ser integrada quando ambos os jobs estiverem verdes no commit
final após a revisão independente.

## Classificação dos achados

| Achado | Classificação | Destino |
| --- | --- | --- |
| Build, healthcheck, non-root e read-only aprovados | controle aprovado | manter |
| Falhas de integridade impedem startup | controle aprovado | manter |
| 150 previsões estáveis sob carga moderada | controle aprovado | manter |
| Stream de logs mistura JSON e texto | melhoria operacional | Issue #70 |
| Falhas de startup expõem traceback e caminho interno | hardening de observabilidade | Issue #70 |
| Imagem local com 490.39 MB | otimização de distribuição | Issue #70 |
| Imagem sem digest de registry | pendência da publicação final | Issue #68 |
| Imagem sem labels OCI | metadata de release pendente | Issue #68 |

Nenhum achado justifica alterar o modelo, o artefato ou o contrato de inferência.

## Limites não verificados

- publicação em registry e pull por digest;
- imagem multi-arquitetura;
- soak test prolongado e carga distribuída;
- orquestradores externos, TLS, proxy reverso ou autoscaling;
- SBOM e scanner de vulnerabilidades de imagem, explicitamente fora do escopo;
- secret scan abrangente dos logs;
- comportamento em hosts não Linux.

## Decisão

A Issue #39 pode ser concluída como **review operacional aprovada com melhorias
não bloqueantes**. A imagem atual é adequada para servir como base técnica da
imagem final, que ainda deverá ser reconstruída, etiquetada, publicada e
verificada após a lapidação do repositório.
