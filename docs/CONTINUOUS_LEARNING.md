# Aprendizado contínuo e governança operacional

## Princípio

Aprendizado contínuo significa repetir um processo controlado quando chegam
novos dados rotulados. Não significa alterar o modelo em produção a cada
requisição. A automação deve produzir um challenger, validar evidências e
interromper o fluxo diante de falhas; a promoção continua sujeita a aprovação
humana.

O desenho completo está em
[`diagrams/model_lifecycle.md`](../diagrams/model_lifecycle.md).

## Dados necessários

Uma nova venda somente entra no treinamento quando possui preço observado,
data, características do imóvel e origem rastreável. Cada lote bruto recebe
identificador, data de extração, hash, schema e política de retenção. Correções
geram nova versão; o lote anterior não é sobrescrito.

As previsões online não devem ser unidas aos rótulos por conteúdo de log. Um
sistema de origem autorizado mantém uma chave de negócio protegida ou
pseudonimizada e a relaciona ao `request_id`, à versão do modelo, ao timestamp,
ao preço estimado e ao conjunto mínimo de features necessário para avaliação
posterior. Esse ledger possui finalidade, retenção, criptografia e acesso
restrito definidos antes da implantação. Logs operacionais permanecem sem
payload.

O monitoramento sem rótulos usa outro caminho. Durante a validação da requisição,
o serviço produz contagens, histogramas e estatísticas agregadas das features e
previsões. Valores individuais não se tornam labels de Prometheus nem conteúdo
de logs. CEPs são acompanhados por cobertura conhecida/desconhecida ou grupos
com suporte suficiente, evitando cardinalidade e exposição desnecessárias.

## Validação antes do treino

- schema, tipos, campos obrigatórios e duplicidade de colunas;
- CEP com cinco dígitos e cobertura geográfica conhecida;
- domínios de `condition`, `grade`, `view` e `waterfront`;
- valores não negativos e coordenadas válidas;
- datas de construção e reforma não posteriores à venda;
- quantidade de linhas, ausências e duplicidades comparadas ao lote anterior;
- período temporal novo e ausência de sobreposição acidental;
- hash e lineage do lote registrados.

Falhas estruturais colocam o lote em quarentena. Mudanças de distribuição
geram investigação, mas não provam degradação e não autorizam promoção.

## Gatilhos e cadência inicial

| Sinal | Cadência proposta | Ação |
| --- | --- | --- |
| Erros, latência e disponibilidade | Contínua | Alertar operação e considerar rollback técnico |
| Qualidade do lote | Em toda ingestão | Bloquear dados inválidos |
| Distribuição de features e previsões | Por janela com volume adequado | Investigar mudança de população |
| Desempenho com preço observado | Ao consolidar novo lote rotulado | Comparar champion e challenger |
| Reentreinamento | Sob demanda após dados aprovados | Produzir candidato, nunca promover diretamente |
| Revisão de uso e risco | Periódica e após incidente | Manter, restringir ou descontinuar o sistema |

A frequência de calendário deve acompanhar a latência real dos preços
observados e o volume de vendas. Antes dessas informações, uma agenda fixa seria
um número sem fundamento. A primeira implantação deve medir esses dois fatores e
registrar a cadência escolhida.

## Pipeline de reentreinamento

1. Congelar o lote novo e registrar hash, schema e lineage.
2. Executar o contrato de dados e produzir relatório de qualidade.
3. Combinar somente períodos aprovados e aplicar o filtro temporal.
4. Executar o mesmo código modular usado no treinamento atual.
5. Avaliar o challenger em cinco janelas temporais de datas completas.
6. Comparar champion e challenger nas mesmas linhas e segmentos.
7. Empacotar pipeline, manifesto, dependências, métricas e model card.
8. Registrar o candidato com status `validation_status=pending`.
9. Construir a imagem, executar testes e registrar seu digest imutável.
10. Executar o mesmo digest em staging e shadow.
11. Submeter evidências técnicas e preditivas à aprovação humana.
12. Promover o digest por canary e depois atualizar o alias `champion`.
13. Preservar a versão anterior e observar o rollout.

## Gates de promoção

Os gates estatísticos existentes continuam válidos e devem ser avaliados nas
cinco janelas de desenvolvimento:

1. MAE média dentro de 0,5% da melhor candidata e da referência.
2. Menor MAE média na faixa superior de preço.
3. Menor viés absoluto médio nessa faixa.
4. Melhora de MAE e viés na faixa superior em pelo menos quatro janelas.

Além disso, o candidato deve satisfazer:

- nenhuma regressão material sem justificativa em tempo, quartil ou CEP com
  suporte suficiente;
- artefato finito, positivo, reproduzível e compatível com o schema da API;
- hashes, versões, runtime, origem de dados e métricas presentes no manifesto;
- testes unitários, integração, concorrência, imagem e healthcheck aprovados;
- model card e limitações atualizados;
- revisão explícita caso novas features aumentem risco de proxy.

O conjunto físico permanece padrão. Variáveis demográficas somente podem ser
reconsideradas com caso de uso, base legal, análise de necessidade e avaliação
de risco aprovados. Um ganho pequeno de MAE não é suficiente.

## Monitoramento

### Operacional

- taxa de requisições, erros por status e falhas inesperadas;
- duração por rota e tamanho do lote;
- CPU, memória, reinicializações e réplicas indisponíveis;
- versão da API, versão do modelo e digest implantado;
- sucesso do healthcheck e do carregamento do artefato.

### Entrada e drift

- ausências, violações de domínio e CEPs não vistos;
- distribuição de features numéricas e categorias;
- distribuição dos preços estimados e frequência por faixa;
- mudança de cobertura espacial e temporal;
- proporção de entradas rejeitadas.

Esses sinais são calculados em agregados operacionais próprios. O ledger
protegido é reservado para análises com rótulo e auditoria; logs da aplicação não
recebem payloads, e identificadores ou CEPs não são usados como labels de alta
cardinalidade.

Os limites de drift devem ser calibrados com janelas históricas por bootstrap ou
backtesting, controlando falsos alertas. Enquanto essa calibração não existir,
drift permanece diagnóstico e exige análise humana.

### Desempenho após rótulo

- MAE, RMSE, RMSLE, R² e erro absoluto mediano;
- MAPE, erro médio, taxa de subestimação e razão mediana;
- coeficiente de dispersão e diferencial relacionado ao preço;
- métricas por período, quartil de preço e CEP com contagem visível;
- diferença entre champion, challenger e baseline de mediana.

R² não é apresentado como percentual de acerto. Segmentos pequenos não devem
acionar decisão automática; devem mostrar tamanho, incerteza e ser agregados
quando necessário.

## Registro e lineage

O estado atual usa Git, manifesto, hash e imagem imutável. Em produção, um
registro como MLflow pode manter versões, tags e aliases. O alias `champion`
aponta para a versão em produção e `challenger` identifica o candidato. Mudar o
alias não apaga versões nem substitui artefatos.

Cada versão registra código-fonte, dados, parâmetros, dependências, métricas,
aprovação, imagem e motivo da decisão. Candidatos rejeitados permanecem
auditáveis com `validation_status=failed` e justificativa.

## Rollout e rollback

Shadow valida comportamento sem usar o resultado na decisão. Canary encaminha
uma parcela controlada somente depois dos testes de staging. A parcela e a
duração dependem do tráfego real e dos requisitos definidos antes da produção.

Rollback técnico é imediato quando há falha de startup, incompatibilidade,
aumento sustentado de `5xx` ou degradação operacional. Rollback preditivo ocorre
após confirmação com rótulos e segmentos, evitando reação automática a drift
isolado. O procedimento restaura o digest e o alias anteriores, confirma health
e contrato, registra o incidente e preserva evidências.

## Responsabilidades

| Ator | Responsabilidade |
| --- | --- |
| Engenharia de dados | Ingestão, qualidade, lineage e disponibilidade de rótulos |
| Ciência de dados | Hipótese, avaliação temporal, segmentos e model card |
| MLOps | Pipeline, registro, imagem, rollout, observabilidade e rollback |
| Produto ou negócio | Uso pretendido, tolerância de risco e impacto esperado |
| Revisor responsável | Aprovação, exceções, incidentes e descontinuação |

## Descontinuação

O modelo deve ser suspenso quando o uso mudar, a cobertura deixar de representar
a população, os rótulos não permitirem monitoramento, o risco superar o benefício
ou não houver responsável operacional. A descontinuação preserva artefatos,
lineage, decisões e período de retenção, mas remove acesso de produção.

As referências utilizadas estão em [`REFERENCES.md`](REFERENCES.md).
