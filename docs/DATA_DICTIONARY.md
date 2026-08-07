# Dicionário canônico dos dados

Este documento consolida o significado operacional comprovado pelos arquivos,
schemas e reviews. Quando a fonte original não forneceu definição, unidade,
vintage ou método de cálculo, a lacuna é mantida explicitamente; nomes de colunas
não são tratados como documentação autoritativa.

## Arquivos e papéis

| Arquivo | Linhas | Papel |
| --- | ---: | --- |
| `kc_house_data.csv` | 21.613 | histórico com alvo e metadata de venda |
| `future_unseen_examples.csv` | 100 | entradas oficiais sem alvo |
| `zipcode_demographics.csv` | 70 | lookup experimental por ZIP, fora do serving |

## Histórico e entradas futuras

| Campo | Definição segura | Unidade/codificação | Uso | Presença |
| --- | --- | --- | --- | --- |
| `id` | Identificador de referência do registro; semântica oficial não fornecida | texto/inteiro preservado | auditoria; não é feature | somente histórico |
| `date` | Data histórica da venda | YYYYMMDDT000000 | ordenação e split temporal | somente histórico |
| `price` | Preço observado da venda | USD | alvo; ausente no arquivo futuro | somente histórico |
| `bedrooms` | Quantidade registrada de quartos | contagem inteira | feature física | histórico e futuro |
| `bathrooms` | Quantidade registrada de banheiros | contagem em passos de 0,25 | feature física | histórico e futuro |
| `sqft_living` | Área habitável interna | pés quadrados | feature física | histórico e futuro |
| `sqft_lot` | Área do lote | pés quadrados | feature física | histórico e futuro |
| `floors` | Quantidade registrada de pavimentos | contagem em passos de 0,5 | feature física | histórico e futuro |
| `waterfront` | Indicador de frente/acesso a água | 0 ou 1 | feature física | histórico e futuro |
| `view` | Código ordinal de vista | 0 a 4 | feature física | histórico e futuro |
| `condition` | Código ordinal da condição geral | 1 a 5 | feature física | histórico e futuro |
| `grade` | Código ordinal da qualidade de construção/projeto | 1 a 13 | feature física | histórico e futuro |
| `sqft_above` | Área habitável acima do nível do solo | pés quadrados | feature física | histórico e futuro |
| `sqft_basement` | Área registrada de porão | pés quadrados | feature física | histórico e futuro |
| `yr_built` | Ano registrado de construção | ano | feature física/temporal | histórico e futuro |
| `yr_renovated` | Ano da reforma registrada; zero indica ausência de reforma registrada | ano ou 0 | feature física/temporal | histórico e futuro |
| `zipcode` | Código postal de cinco dígitos | categoria textual | feature espacial e chave do lookup | histórico e futuro |
| `lat` | Latitude | graus decimais | feature espacial | histórico e futuro |
| `long` | Longitude | graus decimais | feature espacial | histórico e futuro |
| `sqft_living15` | Área habitável de referência da vizinhança; método e data de cálculo não fornecidos | pés quadrados | feature contextual física | histórico e futuro |
| `sqft_lot15` | Área de lote de referência da vizinhança; método e data de cálculo não fornecidos | pés quadrados | feature contextual física | histórico e futuro |

### Regras e ressalvas confirmadas

- `sqft_living = sqft_above + sqft_basement` em 100% do histórico e do arquivo futuro;
- 18 registros históricos têm construção ou reforma posterior à venda e são excluídos antes do treinamento;
- zero quartos/banheiros é anomalia heterogênea, não ausência comprovada nem erro universal;
- 33 quartos é provável erro de entrada, sem fonte suficiente para corrigir o valor;
- 176 chaves `id` se repetem; o padrão é compatível com eventos repetidos da mesma entidade, mas a semântica oficial de `id` não foi fornecida;
- ZIP e coordenadas representam cobertura geográfica, não identidade individual.

## Lookup demográfico experimental

Fonte, licença específica, unidade, população-base, vintage e data de extração não
foram fornecidos. As colunas abaixo são catalogadas por nome, sem inventar
definições oficiais. Nenhuma integra o artefato servido.

| Campo | Interpretação permitida | Estado documental | Decisão |
| --- | --- | --- | --- |
| `ppltn_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `urbn_ppltn_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `sbrbn_ppltn_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `farm_ppltn_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `non_farm_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `medn_hshld_incm_amt` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `medn_incm_per_prsn_amt` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `hous_val_amt` | indicador agregado relacionado a valor habitacional, conforme o nome da coluna; unidade e vintage desconhecidos | definição oficial não fornecida | excluído do serving; proxy forte do nível local de preço |
| `edctn_less_than_9_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `edctn_9_12_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `edctn_high_schl_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `edctn_some_clg_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `edctn_assoc_dgre_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `edctn_bchlr_dgre_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `edctn_prfsnl_qty` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_urbn` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_sbrbn` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_farm` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_non_farm` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_less_than_9` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_9_to_12` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_hsd` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_some_clg` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_assoc` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_bchlr` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `per_prfsnl` | indicador agregado cujo significado exato depende da documentação do fornecedor | definição oficial não fornecida | excluído do serving |
| `zipcode` | chave categórica para associação por ZIP | definição oficial não fornecida | usada apenas no merge experimental |

## Governança

A matriz diagnóstica completa por campo está em
[`reviews/evidence/c1-4/c1-4-feature-governance.csv`](reviews/evidence/c1-4/c1-4-feature-governance.csv).
O modelo aprovado permanece físico. A variante demográfica é evidência histórica
de experimento e não deve ser descrita como modelo atual ou fonte de características individuais.
