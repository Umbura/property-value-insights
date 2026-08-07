# Método de reprodução da C1.6

## Ambiente observado

- GitHub-hosted runner Ubuntu 24.04;
- Docker e Docker Compose fornecidos pelo runner;
- auditoria executada na branch da Issue #39 sem alterações funcionais no
  Dockerfile, Compose, API, modelo ou artefato em relação à base da PR;
- workflow e script de orquestração temporários removidos antes do diff final.

A execução que gerou as evidências ocorreu no GitHub Actions run
`31140629002`. Os tempos e IDs de imagem são específicos desse runner e dessa
execução.

## 1. Validação do Compose e build

```bash
docker compose config --quiet
docker build --no-cache --tag property-value-insights:c1-6-review .
docker image inspect property-value-insights:c1-6-review
docker history --no-trunc property-value-insights:c1-6-review
```

Registrar ID, tamanho, usuário configurado, diretório de trabalho, comando,
healthcheck, quantidade de camadas, labels OCI e `RepoDigests`.

## 2. Execução protegida

```bash
docker run --detach \
  --name pvi-c1-6-review \
  --publish 18000:8000 \
  --read-only \
  --tmpfs /tmp \
  --security-opt no-new-privileges:true \
  property-value-insights:c1-6-review
```

Aguardar `State.Health.Status=healthy` e executar:

```bash
docker exec pvi-c1-6-review id -u
docker exec pvi-c1-6-review id -g
docker exec pvi-c1-6-review sh -c "grep '^NoNewPrivs:' /proc/1/status"
docker exec pvi-c1-6-review sh -c "touch /app/write-test"
docker exec pvi-c1-6-review sh -c "touch /tmp/write-test && rm /tmp/write-test"
```

O teste deve confirmar usuário não root, escrita rejeitada em `/app`, escrita
permitida no tmpfs e `NoNewPrivs: 1`.

Verificar também a ausência dos caminhos `/app/data`, `/app/tests`, `/app/.git`
e `/app/notebooks`, além de `gcc`, `git` e `curl` no `PATH`.

## 3. Endpoints e request IDs

Usar o payload válido mantido no job `container` de
[`../../../../.github/workflows/ci.yml`](../../../../.github/workflows/ci.yml).

Consultar:

```text
GET  http://127.0.0.1:18000/health
GET  http://127.0.0.1:18000/model-info
GET  http://127.0.0.1:18000/metrics
POST http://127.0.0.1:18000/predict
```

Repetir o `POST /predict` em três condições:

1. `X-Request-ID: c1-6-valid-001`, que deve ser preservado no header e body;
2. `X-Request-ID: invalid request id`, que deve ser substituído;
3. sem header, para geração automática.

## 4. Repetição, concorrência e latência

Com o mesmo payload válido:

- executar 100 chamadas sequenciais;
- executar 50 chamadas concorrentes com `ThreadPoolExecutor(max_workers=10)`;
- medir a duração de cada requisição e o tempo total do bloco concorrente;
- exigir HTTP 200 em todas;
- exigir que todas as previsões coincidam com o baseline observado;
- exigir 150 request IDs não vazios e distintos;
- calcular mínimo, média, mediana, P95 e máximo das latências.

Esse procedimento caracteriza somente carga moderada no runner. Ele não define
SLA nem capacidade de produção.

## 5. Falhas controladas do artefato

Executar containers separados, sem publicar porta, e aguardar o encerramento do
processo:

### Artefato ausente

```bash
docker run --name pvi-missing \
  -e MODEL_ARTIFACT_PATH=/app/artifacts/missing.joblib \
  property-value-insights:c1-6-review
```

### Manifesto inválido

Criar um arquivo temporário que não seja JSON válido, montá-lo como somente
leitura e apontar `MODEL_MANIFEST_PATH` para ele.

### Hash divergente

Copiar o manifesto para um diretório temporário, alterar somente o valor
`artifact.sha256`, montar esse manifesto como somente leitura e iniciar a imagem
com `MODEL_MANIFEST_PATH` apontando para a cópia.

Nos três casos, registrar exit code, `OOMKilled`, duração até encerramento e
apenas trechos sanitizados dos logs. O processo não deve permanecer em execução.

## 6. Logs e métricas

Após a carga:

```bash
docker logs pvi-c1-6-review
```

Para cada linha não vazia:

- tentar parsear JSON;
- classificar como texto quando o parse falhar;
- contar registros `request_completed`;
- verificar a presença dos campos operacionais esperados;
- procurar nomes das features de entrada nos registros JSON.

Uma busca somente pelos valores do payload não deve ser usada como prova, pois
números de baixa cardinalidade também aparecem em status, duração e versões.

Consultar `/metrics` antes e depois da carga e registrar contadores de
requisições, duração e previsões.

## 7. Encerramento

```bash
docker stop --time 10 pvi-c1-6-review
docker inspect pvi-c1-6-review
docker rm pvi-c1-6-review
```

Registrar tempo de parada, exit code e `OOMKilled`.

## Limite de reprodutibilidade

Este arquivo preserva o procedimento e os critérios. O script temporário exato
que automatizou a execução não foi mantido para não adicionar infraestrutura de
review à árvore permanente. Portanto, os controles são reproduzíveis, mas a
implementação de orquestração não é bit a bit idêntica à execução original.
