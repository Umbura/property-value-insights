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

Retorna `healthy` somente depois que o processo da API conclui o startup, o
bundle do modelo é carregado e o artefato e o manifesto são aceitos pelas
verificações executadas durante a inicialização. Essas verificações incluem a
leitura do manifesto, a compatibilidade do schema, a correspondência do
SHA-256 do artefato e a coerência entre os metadados do manifesto e do bundle.

A chamada de `/health` não executa uma inferência de teste, não verifica
conectividade com serviços externos e não relê nem recalcula o hash do artefato
a cada requisição. Portanto, o endpoint descreve o estado resultante do startup
do processo atual, e não uma revalidação completa em tempo real.

```json
{
  "status": "healthy",
  "api_version": "0.5.0-rc1",
  "model_version": "0.4.0-rc1"
}
```

`api_version` identifica o contrato HTTP/OpenAPI da aplicação, enquanto
`model_version` identifica o modelo carregado e servido pelo processo. As duas
versões evoluem de forma independente.

### `GET /model-info`

Retorna identidade, algoritmo, contrato de features, hash do artefato, avaliação
e limitações documentadas. Todos os campos top-level históricos permanecem
presentes com os mesmos valores. Quatro blocos aditivos tornam as identidades e
versões visualmente distintas:

- `project`: nome e release da distribuição instalada;
- `api`: versão do contrato HTTP/OpenAPI;
- `model`: nome legível, nome técnico, versão, algoritmo, feature set e status de
  serving;
- `artifact`: SHA-256, data de criação e versão do schema do artefato/manifesto.

A release do projeto, a versão da API e a versão do modelo evoluem de forma
independente. O valor `model.serving_status="approved"` registra a decisão de
governança para disponibilização do modelo físico; ele não declara vitória
estatística automática sobre todas as variantes avaliadas.

O nome e a release do projeto vêm do metadata do pacote instalado. A versão da
API vem do contrato versionado da aplicação. A identidade do modelo, o hash, a
data e a versão do schema vêm do manifesto já aceito durante o startup. Caminhos
internos do artefato e do manifesto não são expostos.

Exemplo abreviado, omitindo apenas detalhes internos de `evaluation` e a lista
completa de `feature_columns`:

```json
{
  "name": "property_value_hist_gradient_boosting_physical",
  "model_version": "0.4.0-rc1",
  "algorithm": "HistGradientBoostingRegressor",
  "feature_set": "physical",
  "feature_columns": ["bedrooms", "bathrooms", "sqft_living"],
  "created_at_utc": "2026-08-03T23:24:44.139717Z",
  "artifact_sha256": "90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439",
  "evaluation": {"protocol": "five expanding temporal folds on the development period"},
  "limitations": ["Os dados cobrem uma região e um intervalo temporal limitado."],
  "project": {
    "name": "property-value-insights",
    "release": "1.0.0"
  },
  "api": {
    "version": "0.5.0-rc1"
  },
  "model": {
    "display_name": "HistGradientBoostingRegressor (physical feature set)",
    "technical_name": "property_value_hist_gradient_boosting_physical",
    "version": "0.4.0-rc1",
    "algorithm": "HistGradientBoostingRegressor",
    "feature_set": "physical",
    "serving_status": "approved"
  },
  "artifact": {
    "sha256": "90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439",
    "created_at_utc": "2026-08-03T23:24:44.139717Z",
    "schema_version": "1.0"
  }
}
```

A mudança é aditiva. Clientes que leem somente os campos históricos continuam
compatíveis. Existe risco residual apenas para consumidores que rejeitam
propriedades JSON adicionais, comportamento não recomendado para esse endpoint.
O binário do modelo, dados de treino e paths internos não são expostos.

### `POST /predict`

Recebe as 18 features físicas e espaciais esperadas pelo modelo. Campos
desconhecidos são rejeitados. O código postal deve ser enviado como uma string
com cinco dígitos.

#### Campos de entrada

Todas as áreas identificadas por `sqft` usam pés quadrados. Os códigos de
`view`, `condition` e `grade` são escalas ordinais; devem ser enviados como os
números definidos na tabela, não como rótulos de texto.

| Campo | Domínio aceito | Significado |
| --- | --- | --- |
| `bedrooms` | inteiro maior ou igual a 0 | Quantidade de quartos do imóvel. |
| `bathrooms` | número maior ou igual a 0 | Quantidade de banheiros; valores fracionários representam banheiros parciais. |
| `sqft_living` | inteiro maior ou igual a 0 | Área interna habitável, em pés quadrados. |
| `sqft_lot` | inteiro maior ou igual a 0 | Área total do terreno, em pés quadrados. |
| `floors` | número maior ou igual a 0 | Quantidade de pavimentos; aceita configurações com meio pavimento. |
| `waterfront` | `0` ou `1` | Indicador de frente para água: `0` = não; `1` = sim. |
| `view` | inteiro de 0 a 4 | Código ordinal da avaliação da vista. |
| `condition` | inteiro de 1 a 5 | Código ordinal da condição geral do imóvel. |
| `grade` | inteiro de 1 a 13 | Código ordinal da qualidade de construção e projeto. |
| `sqft_above` | inteiro maior ou igual a 0 | Área habitável acima do nível do solo, em pés quadrados. |
| `sqft_basement` | inteiro maior ou igual a 0 | Área do porão, em pés quadrados; `0` indica ausência de área registrada. |
| `yr_built` | inteiro maior ou igual a 0 | Ano de construção do imóvel. |
| `yr_renovated` | inteiro maior ou igual a 0 | Ano da última reforma; `0` indica que não há reforma registrada. |
| `zipcode` | string de cinco dígitos | Código postal dos Estados Unidos, preservado como texto. |
| `lat` | número de -90 a 90 | Latitude da localização, em graus decimais. |
| `long` | número de -180 a 180 | Longitude da localização, em graus decimais. |
| `sqft_living15` | inteiro maior ou igual a 0 | Área habitável de referência da vizinhança, em pés quadrados; não é a área do imóvel consultado. |
| `sqft_lot15` | inteiro maior ou igual a 0 | Área de terreno de referência da vizinhança, em pés quadrados; não é a área do imóvel consultado. |

As validações de formato do código postal e dos limites formais de latitude e
longitude não confirmam, por si só, que a localização esteja dentro da cobertura
geográfica representada pelos dados do modelo.

O exemplo abaixo corresponde a uma linha real do conjunto de exemplos futuros
versionado e é aceito pelo schema atual.

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

Recebe um objeto `{"items": [...]}` com pelo menos um imóvel. Cada item usa os
mesmos 18 campos e convenções documentados em `/predict`. O limite máximo é o
valor atual de `MAX_BATCH_SIZE`; o padrão é 100 e a configuração aceita valores
de 1 a 1000.

A validação é `all-or-nothing` e ocorre antes da inferência. Um lote vazio ou
qualquer item inválido retorna `422` e impede o processamento do lote inteiro;
não existem resultados parciais. Um lote que ultrapassa o limite configurado
retorna `413` com uma mensagem controlada.

A resposta preserva a ordem de entrada. `item_id` é somente a posição 1-based do
item no lote, não um identificador único do imóvel. O campo `zipcode` continua
sendo um atributo geográfico e não é usado como chave de identidade. O
`request_id` no corpo e no cabeçalho `X-Request-ID` identifica a requisição
completa, não cada item.

A moeda e a versão do modelo são comuns a todo o lote. Para o mesmo imóvel e a
mesma versão do modelo, `/predict` e `/predict/batch` devem produzir o mesmo
preço previsto.

### `GET /metrics`

Retorna métricas no formato de exposição do Prometheus: quantidade e duração de
requisições, quantidade de previsões e falhas não tratadas. Esse endpoint
operacional não integra o schema OpenAPI público.

## Tratamento de erros

- `413`: o lote contém mais itens do que o limite configurado;
- `422`: um campo está ausente, desconhecido, com tipo inválido ou fora do
  domínio permitido; no batch, um único item inválido rejeita o lote inteiro;
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
