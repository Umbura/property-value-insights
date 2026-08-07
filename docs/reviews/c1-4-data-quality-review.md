# C1.4 — Revisão de qualidade dos dados e registros anômalos

## Escopo e decisão

Esta revisão investiga os três CSVs fornecidos ao projeto sem modificar dados
brutos, features, splits, modelo, artefato, manifesto ou previsões.

A análise utiliza cópias com os mesmos hashes normalizados registrados ou
verificados no projeto:

| Arquivo | Linhas | SHA-256 com quebras normalizadas para LF |
|---|---:|---|
| `kc_house_data.csv` | 21,613 | `d0875baa0251b21d4bdc9d2ae940a4fe0bb6009824f23dd0e2a5b2bf04557b7e` |
| `zipcode_demographics.csv` | 70 | `8d9be9398129f6a9dde49678524103548d02373715f57cf57121d0fcb33f02a5` |
| `future_unseen_examples.csv` | 100 | `5a31ff0c888bef204776208fcd7360859f12cab5e5bff30a8252715928cdd517` |

## Resumo executivo

- Os três arquivos são estruturalmente completos: não existem células ausentes,
  linhas exatamente duplicadas ou ZIPs sem correspondência demográfica.
- As 18 inconsistências temporais conhecidas foram reproduzidas: 12 construções
  e 6 reformas registradas depois da venda. O pipeline aprovado já exclui essas
  linhas antes de treinar.
- O registro com 33 quartos é uma anomalia de alta confiança, mas o valor
  correto não pode ser provado apenas pelos arquivos fornecidos.
- Quartos ou banheiros iguais a zero não podem ser rejeitados automaticamente:
  aparecem em estruturas muito pequenas e também em imóveis grandes, indicando
  mistura de casos plausíveis com possíveis valores ausentes ou codificados.
- A identidade `sqft_living = sqft_above + sqft_basement` é satisfeita em todas
  as 21.613 linhas históricas e nos 100 exemplos futuros. É a regra cruzada mais
  forte encontrada.
- Existem 176 chaves `id` repetidas, totalizando 353 vendas. As 18 features
  físicas permanecem idênticas entre registros com o mesmo `id`. Esse padrão é
  compatível com revendas da mesma entidade imobiliária, mas a semântica de
  `id` não está formalmente documentada nos arquivos fornecidos.
- Noventa e oito chaves `id` aparecem tanto no desenvolvimento quanto no período
  diagnóstico, representando 2,11% das linhas diagnósticas. Como `id` não é
  feature, não há leakage direto de identificador, mas as observações não são
  totalmente independentes.
- `hous_val_amt` é um proxy muito forte do nível de preço por ZIP e não possui
  fonte ou data de referência documentada. A decisão de não usá-lo no modelo
  servido é mantida.
- Os 100 exemplos futuros usam somente ZIPs conhecidos, respeitam as identidades
  cruzadas verificadas e permanecem dentro dos mínimos e máximos univariados do
  histórico. Isso demonstra cobertura estrutural e univariada, não cobertura
  multivariada nem garantia de acurácia.

## 1. Qualidade estrutural

| Dataset | Linhas | Colunas | Ausências | Duplicatas exatas | ZIPs |
|---|---:|---:|---:|---:|---:|
| Histórico | 21,613 | 21 | 0 | 0 | 70 |
| Demografia | 70 | 27 | 0 | 0 | 70 |
| Futuro | 100 | 18 | 0 | 0 | 45 |

A cardinalidade do arquivo demográfico é de uma linha por ZIP. Todos os 70 ZIPs
históricos e todos os 45 ZIPs presentes nos exemplos futuros possuem
correspondência.

### IDs repetidos

- chaves de `id` repetidas: **176**;
- linhas envolvidas: **353**;
- 175 chaves aparecem duas vezes;
- 1 chave aparece três vezes;
- as 18 features físicas são idênticas em todas as vendas do mesmo `id`;
- datas e preços mudam, comportamento compatível com eventos de venda repetidos da mesma entidade.

**Classificação:** não são duplicatas exatas e não devem ser eliminadas
automaticamente. O padrão é compatível com eventos de venda distintos da mesma
entidade, mas essa interpretação permanece inferencial enquanto a definição
formal de `id` não estiver documentada.

## 2. Registro com 33 quartos

O registro é:

| Campo | Valor |
|---|---:|
| `id` | `2402100895` |
| venda | `2014-06-25` |
| preço | US$ 640.000 |
| quartos | 33 |
| banheiros | 1,75 |
| área habitável | 1.620 sqft |
| ZIP | `98103` |
| condição | 5 |
| grade | 7 |

A razão é de **49,09 sqft por quarto**. O segundo menor valor do dataset é
**163,33 sqft por quarto**, diferença de **69,94%**.

Nenhuma outra linha possui mais de 11 quartos. A combinação de 33 quartos,
1,75 banheiro e 1.620 sqft é incompatível com o restante da distribuição.

**Classificação:** provável erro de entrada, com alta confiança estatística, mas
sem fonte autoritativa suficiente para afirmar que o valor pretendido era `3`
ou outro número.

**Decisão:** não corrigir silenciosamente e não alterar o artefato atual. Uma
correção futura exige consulta a uma fonte primária, registro da decisão,
reexecução da avaliação e novo artefato.

## 3. Quartos e banheiros iguais a zero

- `bedrooms = 0`: **13** linhas;
- `bathrooms = 0`: **10** linhas;
- ambos iguais a zero: **7** linhas;
- 9 imóveis com zero quartos possuem pelo menos 1.000 sqft;
- 5 imóveis com zero banheiros possuem pelo menos 1.000 sqft;
- 2 casos de cada grupo foram vendidos por pelo menos US$ 1 milhão.

A menor estrutura possui 290 sqft, zero quartos, zero banheiros e grade 1, o que
pode representar uma estrutura incomum. Em contraste, há linhas com zero
quartos e/ou banheiros acima de 3.000 ou 4.000 sqft, sugerindo valor ausente,
codificação especial ou problema de origem.

**Classificação:** anomalia heterogênea. O valor zero não é prova suficiente de
erro para todas as linhas.

**Decisão:** não criar regra rígida `> 0` nesta revisão. Esses valores devem
gerar warning de qualidade ou cobertura limitada até que a semântica da fonte
seja confirmada.

## 4. Consistência temporal

| Regra | Ocorrências |
|---|---:|
| `yr_built > sale_year` | 12 |
| `yr_renovated > sale_year` e diferente de zero | 6 |
| União das duas regras | 18 |
| `0 < yr_renovated < yr_built` | 0 |

As 18 linhas inconsistentes são exatamente as excluídas por
`filter_temporally_consistent_rows()` antes do treinamento. O filtro é
reproduzível e preserva 21.595 linhas.

**Classificação:** inconsistências confirmadas e já mitigadas no treinamento.

**Limitação:** a API não recebe a data de venda ou uma data de referência. Ela
não consegue aplicar a mesma regra histórica sem definir a semântica temporal
da previsão. Anos posteriores ao máximo do treinamento devem ser tratados como
OOD, e não automaticamente como erro de formato.

## 5. Relações entre áreas e contagens

| Verificação | Violações históricas | Violações futuras |
|---|---:|---:|
| `sqft_living = sqft_above + sqft_basement` | 0 | 0 |
| `sqft_above <= sqft_living` | 0 | 0 |
| `sqft_basement <= sqft_living` | 0 | 0 |
| banheiros em incrementos de 0,25 | 0 | 0 |
| pavimentos em incrementos de 0,5 | 0 | 0 |
| reforma anterior à construção | 0 | 0 |

A identidade das áreas internas é determinística nos dois arquivos e pode ser
considerada uma regra forte de domínio.

Foram encontrados 4 casos em que a aproximação
`sqft_above / floors` supera `sqft_lot`. Essa aproximação não é uma identidade
do dataset: meio pavimento, áreas comuns, condomínios, parcelamento e o
significado cadastral do lote podem invalidá-la.

**Classificação:** os quatro casos são candidatos a revisão, não erros
confirmados. `sqft_living > sqft_lot` também não deve ser rejeitado, pois área
habitável soma pavimentos.

## 6. Cobertura geográfica

- ZIPs históricos: 70;
- ZIPs demográficos: 70;
- cobertura do merge: 100%;
- ZIPs futuros: 45, todos observados no histórico;
- latitude histórica: 47,1559 a 47,7776;
- longitude histórica: -122,519 a -121,315;
- exemplos futuros fora dessas faixas: 0.

Alguns ZIPs cobrem áreas geograficamente extensas ou descontínuas no próprio
dataset. O ZIP `98014`, por exemplo, possui amplitude longitudinal de
aproximadamente 0,647 grau. Portanto, comparar coordenadas apenas ao centroide
do ZIP pode produzir falsos positivos.

**Decisão para regras futuras:**

- ZIP desconhecido: `limited_coverage` ou OOD;
- coordenada fora do retângulo histórico: OOD;
- incompatibilidade ZIP/coordenada: warning baseado em suporte observado ou
  polígonos postais autoritativos, não em uma distância fixa ao centroide;
- coordenadas `(0,0)`: OOD geográfico inequívoco.

## 7. `hous_val_amt`, proxies e disponibilidade temporal

O arquivo demográfico não contém:

- fonte;
- ano ou data de referência;
- data de extração;
- unidade formal;
- período de validade;
- método de atualização.

Resultados observados:

| Relação | Correlação |
|---|---:|
| `hous_val_amt` × preço individual | 0,5797 |
| `hous_val_amt` × mediana de preço por ZIP | 0,9274 |
| `hous_val_amt` × média de preço por ZIP | 0,9394 |
| renda mediana por pessoa × mediana de preço por ZIP | 0,9081 |

A correlação de **0,9274** com a mediana observada por ZIP mostra que
`hous_val_amt` carrega informação muito próxima do nível local do alvo. Isso
pode ser útil preditivamente, mas também cria:

1. risco de proxy do próprio valor imobiliário;
2. risco de disponibilidade posterior ao evento previsto;
3. risco de usar uma fotografia demográfica futura em vendas anteriores;
4. risco de proxies socioeconômicas e de governança.

A variante demográfica melhorou a MAE temporal apenas marginalmente em relação
à variante física comparável, enquanto adicionou esses riscos. O modelo servido
permanece físico.

**Classificação:** proxy forte com vintage desconhecido; inadequado para o
serving atual sem documentação de origem e validação temporal.

## 8. Riscos de leakage e dependência

### Controles adequados existentes

- `price` é utilizado apenas como alvo;
- `id` é excluído das features;
- `date` ordena os splits, mas não é feature;
- o split e os cinco folds preservam a ordem temporal;
- as 18 inconsistências posteriores à venda são excluídas;
- as features demográficas não entram no artefato servido.

### Pontos que exigem ressalva

#### Chaves repetidas entre partições

Existem **98 chaves `id`** presentes no desenvolvimento e no diagnóstico. Elas
representam **98 das 4.640 linhas diagnósticas, ou 2,11%**. As features são
idênticas às do registro anterior com a mesma chave. A lista reproduzível dessas
chaves está em `evidence/c1-4/c1-4-repeated-id-overlap.csv`.

Isso não é leakage direto, pois `id` não entra no modelo e o preço futuro não é
usado no treino. Entretanto, reduz a independência entre as partições e pode
produzir uma estimativa ligeiramente otimista para registros com a mesma chave.

**Decisão:** manter o protocolo atual para a entrega, mas registrar uma análise
futura com split temporal agrupado por imóvel como teste de sensibilidade.

#### Features de vizinhança

`sqft_living15` e `sqft_lot15` estão disponíveis nos exemplos futuros, mas o
repositório não documenta:

- como os 15 imóveis foram selecionados;
- a data de referência;
- se o cálculo usa informação posterior à venda;
- como seria produzido para uma nova requisição.

Não há evidência suficiente para classificá-las como leakage, mas a
disponibilidade operacional e temporal permanece não comprovada.

## 9. Cobertura dos 100 exemplos futuros

Todos os exemplos futuros:

- usam ZIPs vistos no histórico;
- possuem demografia correspondente;
- ficam dentro dos mínimos e máximos históricos de todas as features
  individualmente;
- respeitam `sqft_living = sqft_above + sqft_basement`;
- não possuem reforma anterior à construção;
- não possuem zero quartos ou zero banheiros;
- permanecem dentro da caixa geográfica histórica.

Algumas features aparecem fora do intervalo entre os percentis 1% e 99%, mas
não ultrapassam os extremos observados. Isso caracteriza cauda histórica, não
OOD univariado.

**Classificação:** cobertura estrutural e univariada adequada para o arquivo
oficial de entrega. Esta verificação não avalia distância multivariada ao
suporte de treinamento, raridade conjunta das features nem erro esperado. As
limitações de alto valor e geografia registradas na Issue #36 continuam válidas.

## 10. Completude do dicionário de dados

As 18 features físicas possuem descrições no schema público da API, incluindo
unidades para áreas e coordenadas. Ainda existem lacunas:

- não há um dicionário canônico único para os três CSVs; a matriz diagnóstica
  `evidence/c1-4/c1-4-feature-governance.csv` consolida o estado atual, mas não
  substitui o dicionário definitivo;
- `id`, `date` e `price` não possuem definição formal de origem e unidade no
  mesmo documento;
- as 26 variáveis demográficas não possuem definição individual;
- contagens e percentuais não documentam população-base ou denominador;
- não há fonte, vintage ou licença específica do lookup demográfico;
- `sqft_living15` e `sqft_lot15` não documentam método ou data de cálculo;
- valores zero em quartos e banheiros não possuem semântica registrada.

**Encaminhamento:** a correção documental deve ser incorporada à Issue #38.

## 11. Taxonomia de validação recomendada

### Validação sintática

Pode rejeitar a requisição antes da inferência:

- campos obrigatórios e tipos;
- ZIP com cinco dígitos;
- `waterfront` em {0, 1};
- `view` entre 0 e 4;
- `condition` entre 1 e 5;
- `grade` entre 1 e 13;
- latitude e longitude dentro dos limites globais;
- números não negativos.

Essas regras já estão amplamente implementadas.

### Validação de domínio forte

Candidata a `422`, após decisão do contrato:

- `sqft_living = sqft_above + sqft_basement`;
- `yr_renovated = 0` ou `yr_renovated >= yr_built`;
- valores fisicamente positivos para áreas e pavimentos, caso a regra de
  negócio confirme que a API representa imóveis residenciais existentes.

### Cobertura limitada ou OOD

Deve preservar a previsão central quando permitido, mas retornar warning e
revisão humana:

- ZIP não observado;
- coordenada fora da região;
- `(0,0)`;
- ano posterior ao período de treinamento;
- zero quartos ou banheiros;
- valores fora das faixas históricas;
- combinações raras, como 33 quartos;
- distância elevada do suporte observado para o ZIP.

Uma regra estatística ou OOD não deve ser confundida com erro sintático.

## 12. Evidências e limites de reprodução

As conclusões principais estão acompanhadas pelos seguintes arquivos:

| Arquivo | Finalidade |
|---|---|
| `evidence/c1-4/c1-4-data-quality-summary.json` | hashes, contagens e resultados consolidados |
| `evidence/c1-4/c1-4-temporal-inconsistencies.csv` | 18 registros excluídos pelo filtro temporal |
| `evidence/c1-4/c1-4-anomaly-candidates.csv` | registros anômalos e regras exploratórias |
| `evidence/c1-4/c1-4-future-coverage.csv` | comparação univariada do arquivo futuro |
| `evidence/c1-4/c1-4-feature-governance.csv` | papel, documentação, disponibilidade, risco e decisão por campo |
| `evidence/c1-4/c1-4-repeated-id-overlap.csv` | 98 chaves presentes em desenvolvimento e diagnóstico |

A análise é reproduzível a partir dos três CSVs identificados pelos hashes no
início deste relatório. A pasta de evidências registra os resultados derivados,
mas não constitui um detector multivariado de OOD nem uma nova avaliação do
modelo.

## 13. Decisões finais

| Tema | Decisão |
|---|---|
| 33 quartos | provável erro; não corrigir sem fonte autoritativa |
| zero quartos/banheiros | warning, não rejeição global |
| 18 inconsistências temporais | exclusão existente aprovada |
| identidade das áreas internas | regra forte de domínio |
| ZIP e coordenadas | cobertura/OOD, não validação por centroide simples |
| `hous_val_amt` | manter fora do modelo servido |
| demografia | experimento histórico, não serving |
| IDs repetidos | eventos distintos compatíveis com revenda; registrar dependência entre partições |
| exemplos futuros | cobertura estrutural/univariada adequada; cobertura multivariada não avaliada |
| alteração de dados brutos | não autorizada nem necessária nesta review |
| retreinamento | não executar |
| modelo/artefato | manter `0.4.0-rc1` |

## 14. Encaminhamentos

1. **Issue #38**
   - criar dicionário canônico;
   - documentar fonte, unidade, vintage e semântica dos campos;
   - explicar `sqft_living15`, `sqft_lot15` e zeros;
   - consolidar a decisão de governança da demografia.

2. **Issue #64**
   - incorporar a identidade das áreas;
   - classificar ZIP desconhecido, `(0,0)`, anos futuros e extremos;
   - distinguir erro de domínio, cobertura limitada e OOD;
   - emitir warnings e `review_required` sem alterar o preço.

3. **Melhoria futura de dados e avaliação**
   - verificar o registro de 33 quartos em fonte primária;
   - testar avaliação temporal agrupada por `id`;
   - medir o impacto da remoção ou correção de anomalias somente como
     challenger;
   - não regenerar o artefato sem decisão explícita.

## Situação

A Issue #37 está concluída como revisão. Foram confirmadas limitações e lacunas
de governança, mas nenhuma alteração silenciosa dos dados ou bug isolado no
pipeline servido.
