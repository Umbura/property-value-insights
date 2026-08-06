# C1.2 — Testes manuais e de robustez da API

## Identificação

- **Issue:** #35
- **Data:** 2026-08-06
- **Release:** `v1.0.0`
- **Projeto:** `property-value-insights` `1.0.0`
- **API:** `0.5.0-rc1`
- **Modelo servido:** `0.4.0-rc1`
- **Ambiente:** contêiner Docker local
- **Interfaces:** Swagger UI e PowerShell
- **Natureza:** revisão e diagnóstico; nenhuma correção de runtime foi aplicada

## Objetivo

Executar uma bateria manual reproduzível sobre os fluxos válidos, inválidos,
extremos, em lote e repetidos da API. Os resultados servem como evidência para as
Issues #36 e #37 e não autorizam, isoladamente, retreino ou mudança de contrato.

## Resultado executivo

- **22 testes formais**
- **17 aprovados**
- **5 limitações confirmadas**
- **0 bugs contratuais confirmados**
- **0 divergências documentais confirmadas**
- **0 instabilidades confirmadas**
- **2 tentativas operacionais descartadas**, por uso do endpoint/interface errados

A API permaneceu estável e compatível com o contrato atual em validação de tipos,
campos obrigatórios, campos extras, valores negativos, batch, rastreabilidade e
repetição. As limitações estão concentradas em validação de domínio, coerência
cruzada entre features e entradas fora da distribuição.

## Payload de referência

Os cenários individuais partiram deste payload, salvo quando a alteração é
indicada na tabela:

```json
{
  "bedrooms": 4,
  "bathrooms": 1.0,
  "sqft_living": 1680,
  "sqft_lot": 5043,
  "floors": 1.5,
  "waterfront": 0,
  "view": 0,
  "condition": 4,
  "grade": 6,
  "sqft_above": 1680,
  "sqft_basement": 0,
  "yr_built": 1911,
  "yr_renovated": 0,
  "zipcode": "98118",
  "lat": 47.5354,
  "long": -122.273,
  "sqft_living15": 1560,
  "sqft_lot15": 5765
}
```

## Matriz de resultados

| ID | Cenário / alteração principal | Endpoint | HTTP | Resultado | Request ID | Classificação |
|---|---|---|---:|---|---|---|
| T01 | Saúde do serviço | `GET /health` | 200 | `healthy`; API `0.5.0-rc1`; modelo `0.4.0-rc1` | `manual-c1-2-health-001` | Aprovado |
| T02 | Metadados e limitações | `GET /model-info` | 200 | Blocos técnicos e humanos presentes | `manual-c1-2-model-info-001` | Aprovado |
| T03 | Payload de referência | `POST /predict` | 200 | USD 372,953.43 | `18c45c70c19a4c379912b99d0adc93bd` | Aprovado |
| T04 | Imóvel pequeno e simples | `POST /predict` | 200 | USD 245,755.77 | `d735c841e07342758706df0ff2da5867` | Aprovado |
| T05 | Imóvel grande e de alto valor | `POST /predict` | 200 | USD 2,375,320.20 | `ac67d789e9aa4a508eb0209adb848ed0` | Aprovado tecnicamente |
| T06 | Imóvel novo (`yr_built=2014`) | `POST /predict` | 200 | USD 737,324.91 | `d0416dcf07da4bbfa65e7d818e1bcabb` | Aprovado |
| T07 | Mesmo cenário, `yr_built=1950` | `POST /predict` | 200 | USD 646,248.31 | `b80399163d10496da11d097e67e0ae5b` | Aprovado |
| T08 | T07 com `yr_renovated=2010` | `POST /predict` | 200 | USD 752,571.23 | `f1660763742a4618b15c3a26a3179bdc` | Aprovado |
| T09 | T06 em ZIP/coordenadas diferentes | `POST /predict` | 200 | USD 757,276.19 | `d4133a19f9264fbc9254fc851c8cbb77` | Aprovado |
| T10 | T03 e T04 em batch | `POST /predict/batch` | 200 | Resultados idênticos aos individuais | `b20c88d04bd94e7081dce813c49f48c8` | Aprovado |
| T11 | `zipcode="99999"` | `POST /predict` | 200 | USD 373,605.68; sem alerta | `ef79bceca1c5451eb7932884d0ce14e7` | Limitação confirmada |
| T12 | `bedrooms=33` | `POST /predict` | 200 | USD 349,952.11; sem alerta | `0ffc1fe3040e4dcdb7b4bdb0343907bb` | Limitação confirmada |
| T13 | `sqft_living=-1` | `POST /predict` | 422 | `greater_than_equal` em `sqft_living` | `3a9ad105b5c94487bea54c90f66f43b6` | Aprovado |
| T14 | `sqft_living` ausente | `POST /predict` | 422 | `Field required` | `9a49a85cb6e246469c8f2ce9938a77f4` | Aprovado |
| T15 | Campo extra `actual_price` | `POST /predict` | 422 | `extra_forbidden` | `c60a771bf6e94c8da06c05c689631ca6` | Aprovado |
| T16 | `bathrooms="1.0"` | `POST /predict` | 422 | `float_type` | `bf7d540baf6a41a29bdc8eb4c2b0e7a1` | Aprovado |
| T17 | `yr_renovated=1900 < yr_built` | `POST /predict` | 200 | USD 371,629.11; sem validação cruzada | `737e81a957a5424fb7235e7bfec90dda` | Limitação confirmada |
| T18 | `sqft_above=2000`, `sqft_basement=500`, `sqft_living=1680` | `POST /predict` | 200 | USD 378,894.29; sem validação cruzada | `06ed01ad45fa40c4b01c90848978dac8` | Limitação confirmada |
| T19 | ZIP `98118` com coordenadas `(0,0)` | `POST /predict` | 200 | USD 222,451.18; sem alerta geográfico/OOD | `2ca2794d7241418085c7e637aadb06fa` | Limitação confirmada |
| T20 | `{"items":[]}` | `POST /predict/batch` | 422 | `too_short`; mínimo 1 item | `41a91dc2bb3a4c9fa89d7f4c3b0cae7d` | Aprovado |
| T21 | Batch com 101 itens | `POST /predict/batch` | 413 | Limite de 100 itens preservado | `manual-c1-2-batch-limit-001` | Aprovado |
| T22 | Payload de referência repetido 10 vezes | `POST /predict` | 200 em 10/10 | Mesma previsão; 10 IDs únicos | IDs registrados localmente | Aprovado |

## Comparações controladas

### Idade e reforma

- T06 → T07: `yr_built` de 2014 para 1950 reduziu a previsão em
  **USD 91,076.60 (12.35%)**.
- T07 → T08: `yr_renovated` de 0 para 2010 aumentou a previsão em
  **USD 106,322.92 (16.45%)**.

A direção foi coerente nos pares testados, mas os testes não comprovam acurácia,
causalidade ou calibração da magnitude.

### Localização válida

T06 → T09, com mudança conjunta de ZIP e coordenadas, aumentou a previsão em
**USD 19,951.28 (2.71%)**. Como três features geográficas mudaram juntas, o teste
não atribui o efeito a uma feature isolada.

### Individual versus batch

Os dois itens do T10 reproduziram exatamente as previsões dos T03 e T04, mantendo
ordem, versão do modelo e rastreabilidade.

## Validações aprovadas

A API rejeitou corretamente, antes da inferência:

- valores negativos;
- campos obrigatórios ausentes;
- campos extras;
- strings em campos numéricos estritos;
- batch vazio;
- batch acima do limite de 100 itens.

O formato atual de erro `422` e o comportamento `413` foram preservados.

## Limitações confirmadas

### T11 — ZIP desconhecido

O ZIP `99999`, embora fora da cobertura esperada, foi aceito sem alerta e produziu
uma previsão apenas **0.17%** diferente do cenário de referência. O contrato atual
valida o formato, não a cobertura.

**Encaminhamento:** #36 para risco/OOD e #37 para cobertura dos dados.

### T12 — 33 quartos

A API aceitou `33` quartos com apenas `1680` pés² e a previsão caiu
**6.17%** em relação ao cenário de 4 quartos. O resultado não confirma bug do
contrato, mas evidencia ausência de validação de domínio e possível resposta não
confiável fora da distribuição.

**Encaminhamento:** #36 para sensibilidade/OOD e #37 para investigar o registro
real de 33 quartos.

### T17 — reforma anterior à construção

A combinação `yr_built=1911` e `yr_renovated=1900` foi aceita sem validação
cruzada. A previsão variou apenas **0.36%** em relação ao cenário de referência.

**Encaminhamento:** #37 para confirmar a semântica e futura Issue de API somente
após a regra ser validada.

### T18 — áreas inconsistentes

A API aceitou `sqft_above + sqft_basement = 2500` com `sqft_living = 1680`.
Os campos são validados isoladamente, mas não existe regra cruzada.

**Encaminhamento:** #37 para confirmar a relação correta e futura Issue de API
após decisão de compatibilidade.

### T19 — coordenadas fora da cobertura

As coordenadas `(0,0)` foram aceitas com o ZIP `98118`. A previsão caiu
**USD 150,502.25 (40.35%)**, sem alerta de cobertura ou OOD.

**Encaminhamento prioritário:** #36 para sensibilidade geográfica/OOD e #37 para
mapear ZIPs e coordenadas observados.

## Alto valor e hipótese de guardrail

O T05 produziu USD 2,375,320.20, mas não possui preço real de referência.
A confiabilidade para imóveis caros deve ser avaliada na #36. Antes de considerar
um modelo especializado, deve-se avaliar alerta de risco, detecção OOD e revisão
humana. Truncar artificialmente a previsão não é recomendado.

## Repetição e latência

No T22:

- 10 de 10 respostas retornaram `200`;
- a previsão foi sempre `372953.43`;
- foram observados 10 Request IDs distintos;
- corpo e cabeçalho coincidiram em todas as chamadas;
- latência mínima: `30 ms`;
- latência máxima: `59 ms`;
- média: `34.9 ms`;
- mediana: `32.5 ms`;
- média sem a primeira chamada: `32.22 ms`.

Não foi observada instabilidade funcional.

## Classificação e prioridade

| Achado | Natureza principal | Prioridade preliminar | Próxima review |
|---|---|---:|---|
| T19 — coordenadas fora da cobertura | Geografia/OOD | Alta | #36 e #37 |
| T12 — 33 quartos | Dados, domínio e OOD | Alta para investigação | #36 e #37 |
| T17 — anos incoerentes | Validação cruzada | Média | #37 |
| T18 — áreas inconsistentes | Validação cruzada | Média | #37 |
| T11 — ZIP desconhecido | Cobertura/OOD | Média | #36 e #37 |

## Decisão sobre API versus modelo

Os testes não demonstram overfitting. Essa conclusão exige comparar treino,
validação e períodos realmente não vistos, além de analisar resíduos por faixa de
preço e região.

A ordem recomendada é:

1. concluir esta Review #35;
2. executar #36 para comportamento, alto valor, geografia e OOD;
3. executar #37 para regras de domínio e qualidade dos dados;
4. abrir Issues independentes para validações, guardrails, dados e modelo;
5. considerar retreino apenas com evidência estatística reproduzível.

## Critérios de aceite da Issue #35

- [x] endpoints básicos testados;
- [x] previsão simples válida confirmada;
- [x] casos normais variados executados;
- [x] consistência individual versus batch avaliada;
- [x] entradas inválidas e extremas exercitadas;
- [x] respostas repetidas avaliadas;
- [x] achados registrados com evidência reproduzível;
- [x] achados classificados e encaminhados para #36 e #37.

## Conclusão

A execução da Issue #35 está concluída. A API está operacionalmente estável dentro
do contrato atual. Não foi confirmada necessidade imediata de retreino nem bug
contratual. As limitações devem avançar pelas Reviews #36 e #37 antes de qualquer
validação rígida, alteração de dados, guardrail ou regeneração de artefatos.
