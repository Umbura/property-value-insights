# Contrato inicial de dados

Status: proposta da Fase 0, pendente de revisao supervisionada.

## Fontes

| Arquivo | Finalidade | Linhas | Colunas |
| --- | --- | ---: | ---: |
| `data/raw/kc_house_data.csv` | historico com alvo | 21.613 | 21 |
| `data/raw/zipcode_demographics.csv` | lookup demografico por CEP | 70 | 27 |
| `data/raw/future_unseen_examples.csv` | exemplos para inferencia final | 100 | 18 |

## Regras estruturais

- O historico deve conter `price`, `id`, `date` e `zipcode`.
- Os exemplos futuros nao devem conter `price`, `id` ou `date`.
- O lookup demografico deve conter exatamente uma linha por `zipcode`.
- As colunas numericas devem ser parseaveis e nao negativas quando a regra de
  negocio exigir isso.
- Identificadores, datas, preco e CEP nao podem ser nulos no historico.
- Todo CEP observado no historico e nos exemplos futuros deve existir no lookup
  demografico.
- O contrato rejeita colunas inesperadas para evitar entrada silenciosamente
  incompatível.

## Resultado da auditoria inicial

- O historico possui 21.613 linhas e 70 CEPs.
- O lookup demografico possui 70 CEPs unicos.
- Os 100 exemplos futuros usam 45 CEPs.
- Nao foram encontrados CEPs historicos ou futuros sem correspondencia.
- O historico possui 176 valores de `id` repetidos, abrangendo 353 linhas.
- Nao foram encontrados registros inteiramente duplicados.
- O menor preco observado e 75.000 e o maior e 7.700.000.
- As datas observadas vao de 2014-05-02 a 2015-05-27.

## Decisoes

### `id`

`id` sera mantido para rastreabilidade e auditoria, mas nao sera usado como
feature e nao sera tratado como chave unica. A repeticao de IDs sem linhas
inteiramente duplicadas deve ser investigada durante a EDA; nao vamos remover
linhas automaticamente nesta fase.

### `date`

`date` sera usada para ordenacao e separacao temporal. Nao sera feature final
enquanto nao existir nos exemplos futuros.

### `zipcode`

`zipcode` sera tratado como categoria. A tabela demografica sera combinada com
validacao de cardinalidade e cobertura.

### Dados demograficos

As variaveis demograficas serao avaliadas em uma comparacao com e sem essa
fonte. A analise nao devera apresentar uma associacao demografica como
causalidade ou como caracteristica individual de uma pessoa.

## Integridade dos arquivos

Os hashes SHA-256 registrados na auditoria inicial sao:

```text
kc_house_data.csv
d0875baa0251b21d4bdc9d2ae940a4fe0bb6009824f23dd0e2a5b2bf04557b7e

zipcode_demographics.csv
8d9be9398129f6a9dde49678524103548d02373715f57cf57121d0fcb33f02a5

future_unseen_examples.csv
5a31ff0c888bef204776208fcd7360859f12cab5e5bff30a8252715928cdd517
```

Os hashes servem para identificar a versao dos arquivos usados na entrega.
