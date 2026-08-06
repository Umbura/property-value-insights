# Contrato da API de Inferência

## Objetivo

O serviço disponibiliza o modelo aprovado, baseado em características físicas,
por meio de uma interface HTTP versionada. O artefato é carregado e verificado
uma única vez durante a inicialização. O serviço não inicia quando o manifesto
está ilegível ou quando hash, schema, nome, versão ou features são
inconsistentes.

A documentação OpenAPI interativa fica disponível em `/docs` durante a
execução. O contrato da API possui versão `0.5.0-rc1`, enquanto a versão do
modelo candidato é `0.4.0-rc1`. As duas versões evoluem de forma independente,
e a versão do modelo acompanha toda resposta de predição.

## Execução local

```powershell
docker compose up --build
```

A API fica disponível em `http://127.0.0.1:8000`. A porta publicada pode ser
alterada por `API_PORT`, e o tamanho máximo dos lotes, por `MAX_BATCH_SIZE`.

## Identificadores de requisição

Toda resposta HTTP contém `X-Request-ID`. O cliente pode fornecer um
identificador de 1 a 64 letras, dígitos, pontos, sublinhados ou hífens. Valores
ausentes ou inválidos são substituídos por um identificador gerado. As respostas
de predição também incluem o valor no corpo JSON.

## Operações

### `GET /health`

Confirma que a aplicação iniciou e que o artefato verificado está carregado.

```json
{
  "status": "healthy",
  "api_version": "0.5.0-rc1",
  "model_version": "0.4.0-rc1"
}
```

### `GET /model-info`

Retorna identidade, algoritmo, contrato de features, hash do artefato, resumo da
avaliação e limitações documentadas. O binário do modelo e os dados de treino
não são expostos.

### `POST /predict`

Recebe as 18 features físicas e espaciais esperadas pelo modelo. Campos
desconhecidos são rejeitados. O CEP deve ser uma string com cinco dígitos.

O Swagger expõe descrições, unidades e exemplos para cada feature no schema
`PropertyFeatures`. As áreas são informadas em `square feet`. A localização
(latitude, longitude e CEP) é aceita com validação formal de formato e limites,
sem garantia de cobertura do modelo para qualquer ponto ou CEP. O exemplo
principal do contrato corresponde à primeira linha de
`data/raw/future_unseen_examples.csv` e retorna `200` em `/predict`.

Convenções das features:

- `waterfront` indica frente para água: `0` não, `1` sim;
- `view` é um índice de vista de `0` a `4`;
- `condition` é um índice de condição de `1` a `5`;
- `grade` é um índice de qualidade construtiva de `1` a `13`;
- `yr_renovated` igual a `0` significa que não há reforma registrada;
- `sqft_living15` e `sqft_lot15` são referências da vizinhança, não
  características do próprio imóvel.

```powershell
$body = @{
  bedrooms = 4
  bathrooms = 1.0
  sqft_living = 1680
  sqft_lot = 5043
  floors = 1.5
  waterfront = 0
  view = 0
  condition = 4
  grade = 6
  sqft_above = 1680
  sqft_basement = 0
  yr_built = 1911
  yr_renovated = 0
  zipcode = "98118"
  lat = 47.5354
  long = -122.273
  sqft_living15 = 1560
  sqft_lot15 = 5765
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/predict `
  -ContentType application/json `
  -Body $body
```

Exemplo de resposta:

```json
{
  "predicted_price": 372953.43,
  "currency": "USD",
  "model_version": "0.4.0-rc1",
  "request_id": "b55ae80b6ad24ffb97a06e4963781637"
}
```

### `POST /predict/batch`

Recebe `{"items": [...]}` e preserva a ordem de entrada com valores de
`item_id` iniciados em um. A resposta declara `currency` uma vez para todo o
lote. Lotes vazios retornam `422`. Lotes acima de `MAX_BATCH_SIZE` retornam
`413`; o limite padrão é 100.

Os schemas `BatchPredictionRequest`, `PredictionResponse` e
`BatchPredictionResponse` expõem exemplos no Swagger para ilustrar o formato de
requisição e resposta. Os exemplos são metadados OpenAPI e não alteram o JSON
aceito nem o JSON retornado pelo serviço.

### `GET /metrics`

Retorna métricas no formato de exposição do Prometheus: quantidade e duração de
requisições, quantidade de previsões e falhas não tratadas. Esse endpoint
operacional não integra o schema OpenAPI público.

## Tratamento de erros

- `413`: o lote contém mais itens do que o limite configurado;
- `422`: um campo está ausente, desconhecido, com tipo inválido ou fora do
  domínio permitido;
- `500`: ocorreu uma falha inesperada de processamento. A resposta contém
  `detail` e `request_id`, sem expor detalhes internos.

Erros de validação seguem o schema padrão do FastAPI. Toda resposta inclui o
cabeçalho `X-Request-ID`. Falhas inesperadas geram log JSON em nível `ERROR`,
com o mesmo identificador, enquanto os dados recebidos não são escritos nos
logs da aplicação.

## Limites operacionais

- O contêiner executa com usuário sem privilégios e permite sistema de arquivos
  raiz somente leitura.
- O modelo é carregado de um artefato Joblib confiável e verificado por hash.
  Arquivos enviados por clientes nunca devem ser carregados com Joblib.
- As métricas residem no processo e são reiniciadas junto com ele.
- Autenticação, terminação TLS, limitação de tráfego e persistência de métricas
  pertencem à camada de deploy descrita na próxima fase.
- A API estima preço; ela não representa avaliação imobiliária formal nem
  explicação causal do valor do imóvel.
