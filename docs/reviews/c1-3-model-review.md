# C1.3 — Revisão do comportamento e limitações do modelo

## Identificação

- **Issue:** #36 — C1.3 — Revisar comportamento e limitações do modelo
- **Release avaliada:** `v1.0.0`
- **API:** `0.5.0-rc1`
- **Modelo servido:** `property_value_hist_gradient_boosting_physical`
- **Versão:** `0.4.0-rc1`
- **Data da revisão:** 2026-08-06
- **Natureza:** revisão e diagnóstico, sem retreino ou alteração de runtime

## Decisão executiva

A revisão foi concluída com **limitações confirmadas, sem bug funcional isolado
do artefato aprovado**.

O modelo é reproduzível, numericamente estável e apresenta comportamento
direcional plausível na região central dos dados. A principal limitação é a
degradação progressiva na cauda superior, acompanhada de maior subestimação.
Também foram confirmados tratamento silencioso de entradas fora da distribuição,
heterogeneidade geográfica e piora mensal dentro do período diagnóstico.

O modelo deve permanecer como **champion** da entrega atual. Não houve evidência
suficiente para retreino imediato ou promoção de outro modelo.

## Escopo

A review avaliou:

- previsões negativas, não finitas ou visualmente incompatíveis;
- sensibilidade controlada às principais features;
- comportamento em imóveis de alto valor;
- dependência geográfica e temporal;
- ZIP desconhecido e outros casos OOD;
- interpretação dos intervalos de incerteza;
- identidade do modelo servido;
- necessidade de revisão humana e comunicação de risco.

Permaneceram fora do escopo:

- retreino, tuning ou substituição do modelo;
- modelo especializado para luxo;
- roteamento entre múltiplos modelos;
- promoção da variante demográfica;
- regeneração de artefato, manifesto ou hashes;
- alteração das regras rígidas da API antes da Issue #37.

## Modelo e protocolo confirmados

O artefato servido utiliza 18 características físicas e espaciais. A variante
demográfica permanece como experimento histórico e não participa do serving.

A confecção do modelo utilizou **cinco janelas temporais expansivas** dentro do
período de desenvolvimento. O período mais recente foi mantido como diagnóstico
separado, mas já havia sido consultado e não deve ser apresentado como teste final
completamente intocado.

A auditoria reproduzida partiu de 21.613 linhas, excluiu 18 registros com
inconsistências temporais e reteve 21.595 linhas:

- desenvolvimento: 16.955 linhas;
- diagnóstico: 4.640 linhas;
- fim do desenvolvimento: 2015-03-03;
- início do diagnóstico: 2015-03-04.

## Reprodutibilidade

As métricas reproduzidas coincidiram com o manifesto, com diferenças apenas de
precisão numérica:

| Métrica | Resultado |
|---|---:|
| MAE | US$ 67.105,71 |
| RMSE | US$ 116.547,25 |
| RMSLE | 0,168779 |
| R² | 0,899781 |
| MAPE | 12,07% |
| Erro médio | -US$ 20.577,30 |
| Taxa de subestimação | 58,77% |
| Razão mediana previsão/observado | 0,974369 |

Verificações numéricas:

- previsões negativas: `0`;
- previsões não finitas: `0`;
- menor previsão diagnóstica: `US$ 130.949,51`;
- maior previsão diagnóstica: `US$ 4.819.648,44`.

**Classificação:** reprodutibilidade aprovada.

## M01 — Matriz de sensibilidade

Foram processados 25 casos em um único `POST /predict/batch`, com o modelo
`0.4.0-rc1`, request ID consistente e tempo total de 51 ms.

Principais resultados em relação ao baseline de `US$ 372.953,43`:

| Caso | Previsão | Variação |
|---|---:|---:|
| 1 quarto | US$ 364.817,20 | -2,18% |
| 8 quartos | US$ 349.952,11 | -6,17% |
| 33 quartos | US$ 349.952,11 | -6,17% |
| 800 sqft habitáveis | US$ 311.554,05 | -16,46% |
| 3.000 sqft habitáveis | US$ 492.682,61 | +32,10% |
| 6.000 sqft habitáveis | US$ 523.447,49 | +40,35% |
| `grade = 4` | US$ 337.727,55 | -9,45% |
| `grade = 9` | US$ 670.524,19 | +79,79% |
| `grade = 13` | US$ 692.178,07 | +85,59% |
| waterfront | US$ 431.728,31 | +15,76% |
| vista máxima | US$ 498.898,08 | +33,77% |
| latitude alterada | US$ 502.713,84 | +34,79% |
| coordenadas `(0,0)` | US$ 222.451,18 | -40,35% |
| cenário de luxo | US$ 7.192.756,39 | +1.828,59% |

### Interpretação

- Área, padrão construtivo, vista e waterfront responderam em direção plausível.
- Quartos, área e `grade` apresentaram saturação local em valores altos.
- O caso com 33 quartos produziu a mesma previsão do caso com 8 quartos.
- A latitude apresentou impacto local maior que ZIP e longitude.
- O cenário de luxo ficou dentro do domínio histórico observado e possui
  comparáveis; não foi classificado como explosão absurda.
- Nenhum resultado da matriz demonstrou instabilidade ou preço negativo.

## Entradas fora da distribuição

Foram aceitos sem warning explícito:

- ZIP desconhecido;
- coordenadas `(0,0)`;
- ano de construção futuro;
- combinações estruturais próximas dos mínimos aceitos.

O ZIP `99999` e o ZIP válido testado `98115` produziram a mesma previsão no caso
controlado. Isso é compatível com o uso de
`OneHotEncoder(handle_unknown="ignore")`, mas não comunica a cobertura ao
consumidor.

As coordenadas `(0,0)` produziram um preço positivo e visualmente plausível.
Esse é o achado OOD de maior prioridade, pois o formato normal da resposta pode
induzir o consumidor a confiar em uma entrada geograficamente incompatível.

**Classificação:** problema de cobertura e comunicação, não bug numérico.

## Desempenho por preço

O Q4 contém 1.158 imóveis observados entre `US$ 655.100` e `US$ 5.350.000`.

### Subdivisão interna do Q4

| Subfaixa | Linhas | MAE | Viés médio | Subestimação |
|---|---:|---:|---:|---:|
| Q4-A | 298 | US$ 71.441,35 | -US$ 27.498,89 | 61,41% |
| Q4-B | 292 | US$ 89.046,03 | -US$ 43.430,45 | 67,12% |
| Q4-C | 278 | US$ 118.294,93 | -US$ 67.238,55 | 70,86% |
| Q4-D | 290 | US$ 262.109,03 | -US$ 149.335,45 | 71,38% |

Do primeiro para o último grupo, o MAE aumenta 3,67 vezes e o viés negativo
absoluto aumenta 5,43 vezes.

### Faixas fixas

| Preço observado | Linhas | MAE | MAPE | Viés médio | Subestimação |
|---|---:|---:|---:|---:|---:|
| > US$ 655 mil até US$ 1 mi | 823 | US$ 88.435,42 | 11,11% | -US$ 43.201,46 | 66,10% |
| > US$ 1 mi até US$ 2 mi | 289 | US$ 201.930,60 | 15,06% | -US$ 103.431,31 | 69,55% |
| > US$ 2 mi | 46 | US$ 544.527,87 | 19,86% | -US$ 378.902,28 | 82,61% |

Acima de US$ 2 milhões:

- o MAE é 8,11 vezes o MAE geral;
- 82,61% dos casos são subestimados;
- a previsão mediana equivale a aproximadamente 85,09% do preço observado.

**Classificação:** limitação forte e material na cauda superior, compatível com
compressão em direção ao centro da distribuição.

## Maiores resíduos

Entre os vinte maiores erros absolutos:

- todos os preços observados superam US$ 1,05 milhão;
- 17 estão acima de US$ 2 milhões;
- 17 são subestimações;
- erro absoluto médio: US$ 887.858,71;
- erro absoluto mediano: US$ 777.582,58;
- preço observado mediano: US$ 2.580.000.

O ZIP `98006` concentra cinco desses vinte casos. Os maiores resíduos não apontam
para uma única feature defeituosa; o padrão dominante combina alto valor,
raridade estrutural e concentração parcial em regiões valorizadas.

**Classificação:** limitação estatística e de cobertura, não registro único
suficiente para caracterizar bug do modelo.

## Desempenho geográfico

Considerando ZIPs com pelo menos vinte observações:

| ZIP | Linhas | MAE | Viés médio | Subestimação |
|---|---:|---:|---:|---:|
| `98112` | 47 | US$ 193.317,44 | -US$ 67.700,42 | 68,09% |
| `98004` | 63 | US$ 174.034,21 | -US$ 54.296,15 | 55,56% |
| `98040` | 67 | US$ 158.538,17 | -US$ 59.087,81 | 64,18% |
| `98105` | 49 | US$ 153.012,13 | -US$ 35.470,35 | 55,10% |
| `98006` | 98 | US$ 141.905,89 | -US$ 79.449,94 | 64,29% |

A heterogeneidade geográfica está confirmada, mas a tabela não demonstra que o
ZIP seja causa isolada: preço, latitude, longitude e características do imóvel
são correlacionados.

O notebook histórico também calculou resultados por ZIP, porém antes da exclusão
das 18 inconsistências temporais. Por isso seus valores não são a fonte canônica
do modelo `0.4.0-rc1`.

## Dependência temporal

| Mês | Linhas | MAE | RMSE | Viés médio | Subestimação |
|---|---:|---:|---:|---:|---:|
| 2015-03 | 1.763 | US$ 62.835,96 | US$ 105.940,94 | -US$ 12.160,25 | 54,17% |
| 2015-04 | 2.231 | US$ 67.985,49 | US$ 117.991,58 | -US$ 23.116,90 | 60,51% |
| 2015-05 | 646 | US$ 75.719,93 | US$ 137.307,81 | -US$ 34.777,61 | 65,33% |

De março para maio, o MAE aumentou 20,50% e a taxa de subestimação subiu 11,16
pontos percentuais.

Maio é parcial e o período inteiro já foi consultado. Portanto, o resultado é
uma dependência temporal diagnóstica, não evidência suficiente de drift de
produção.

## Intervalos de incerteza

O intervalo empírico nominal de 90% apresentou:

- cobertura geral: 89,40%;
- cobertura no Q1: 85,71%;
- cobertura no Q4: 86,87%;
- largura média geral: US$ 281.835,45;
- largura média no Q4: US$ 493.820,50.

O intervalo é útil como diagnóstico offline, mas não representa garantia
uniforme por imóvel e ainda não é exposto por `/predict`.

## Classificação consolidada

| Tema | Conclusão |
|---|---|
| Reprodutibilidade | Aprovada |
| Previsões negativas ou não finitas | Não encontradas |
| Coerência direcional | Confirmada nas principais features |
| Saturação local | Confirmada em alguns extremos |
| Alto valor | Degradação forte e progressiva |
| Dependência geográfica | Heterogeneidade confirmada |
| Dependência temporal | Piora mensal diagnóstica |
| ZIP desconhecido | Aceito sem comunicação de cobertura |
| Coordenadas `(0,0)` | OOD geográfico de alta prioridade |
| Ano futuro | OOD temporal aceito silenciosamente |
| Variante demográfica | Experimento, não modelo servido |
| Bug funcional isolado | Não demonstrado |
| Revisão humana | Necessária para alto valor, OOD e casos raros |
| Retreino imediato | Não justificado nesta review |

## Controles aprovados

### 1. Concluir regras de domínio na Issue #37

A Issue #37 deve investigar 33 quartos, zero banheiros, anos, áreas, ZIPs,
coordenadas, `hous_val_amt` e riscos de leakage antes de definir rejeições
rígidas.

### 2. Adicionar warnings e cobertura/OOD

Após a #37, a API deve ser capaz de sinalizar, conforme regras aprovadas:

- ZIP desconhecido;
- coordenadas fora da região coberta;
- ano futuro ou incompatível;
- combinações raras;
- ausência de cobertura suficiente.

### 3. Criar níveis de risco e revisão humana

A resposta ou a camada de decisão deve distinguir casos normais, cobertura
limitada e OOD, incluindo campos equivalentes a:

- `coverage_status`;
- `risk_tier`;
- `review_required`;
- `warnings`.

A trava recomendada limita a **automação da decisão**, não o valor da previsão.

### 4. Expor intervalo somente com comunicação adequada

A estimativa pode futuramente apresentar faixa de incerteza, desde que:

- o método e o nível nominal sejam informados;
- cobertura e largura sejam monitoradas;
- a faixa não seja descrita como garantia;
- imóveis de alto valor continuem sujeitos a revisão humana.

### 5. Manter o modelo atual como champion

O modelo físico `0.4.0-rc1` permanece como champion da entrega atual. Nenhum
artefato, manifesto ou hash foi alterado nesta review.

## Melhorias futuras

A avaliação e eventual promoção de challengers foi registrada na **Issue #62**.

Essa issue exige:

- os mesmos cinco folds temporais;
- comparação geral, Q4, acima de US$ 1 milhão e acima de US$ 2 milhões;
- análise de viés e subestimação;
- ausência de degradação geral inaceitável;
- dados suficientes antes de modelo especializado para luxo;
- aprovação humana antes de qualquer promoção.

A Issue #62 não bloqueia a entrega atual.

## Encaminhamentos

- **#37:** investigar dados, outliers e regras de domínio;
- **#38:** consolidar documentação, limites de uso e resultados canônicos;
- **após #37:** implementar warnings, cobertura/OOD, níveis de risco e revisão;
- **#62:** pesquisar challengers apenas em trabalho futuro;
- **monitoramento futuro:** MAE, MAPE, viés e subestimação por preço, ZIP e mês.

## Evidências

As evidências essenciais estão em
[`docs/reviews/evidence/c1-3/`](evidence/c1-3/):

- matriz de sensibilidade M01;
- resumo estruturado M02;
- top 10 ZIPs por MAE;
- métricas mensais;
- subdivisões e faixas fixas do Q4;
- vinte maiores resíduos;
- manifesto de proveniência e hashes das evidências.

Tentativas inválidas, scripts auxiliares e arquivos redundantes não foram
versionados.

## Validação da review

- JSON consolidado: parseado com sucesso;
- CSVs: parseados com sucesso;
- consistência com o manifesto: aprovada;
- alterações de runtime: nenhuma;
- alterações de modelo ou artefato: nenhuma;
- CI: indisponível; validação local executada.

## Critérios de aceite da Issue #36

- [x] coerência básica das previsões avaliada;
- [x] sensibilidade às principais features testada;
- [x] comportamento em imóveis de alto valor revisado;
- [x] dependência geográfica, temporal e OOD discutida com evidências;
- [x] intervalos avaliados sem apresentá-los como garantia;
- [x] modelo servido distinguido de candidatos experimentais;
- [x] limitações e necessidade de revisão humana registradas;
- [x] melhoria de challengers registrada na Issue #62.

A Issue #36 deve ser encerrada somente após revisão humana e merge da PR.
