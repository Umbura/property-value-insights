# Dicionario de dados

Descricao das variaveis utilizadas na analise exploratoria.

| variavel     | descricao                               | papel                          |
|:-------------|:----------------------------------------|:-------------------------------|
| id           | identificador de referencia do registro | rastreabilidade                |
| date         | data da venda historica                 | ordenacao e separacao temporal |
| price        | preco observado do imovel               | alvo                           |
| bedrooms     | quantidade de quartos                   | feature fisica                 |
| bathrooms    | quantidade de banheiros                 | feature fisica                 |
| sqft_living  | area habitavel                          | feature fisica                 |
| sqft_lot     | area do lote                            | feature fisica                 |
| floors       | quantidade de andares                   | feature fisica                 |
| waterfront   | indicador de acesso a agua              | feature categorica             |
| view         | indice de qualidade da vista            | feature categorica             |
| condition    | indice de condicao do imovel            | feature categorica             |
| grade        | classificacao construtiva               | feature categorica/ordinal     |
| yr_built     | ano de construcao                       | feature temporal               |
| zipcode      | codigo postal do imovel                 | chave categorica do merge      |
| lat / long   | coordenadas geograficas                 | localizacao                    |
| demographics | indicadores agregados por CEP           | features contextuais           |
