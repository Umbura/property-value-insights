# Revisão da Fase 3

Status: aguardando revisão supervisionada.

## Objetivo

Transformar a decisão de modelagem em um pipeline treinável, um artefato
verificável e uma saída reproduzível para os exemplos futuros.

## Decisões

- o modelo principal utiliza somente features físicas e espaciais;
- `zipcode` permanece como categoria geográfica;
- as variáveis demográficas permanecem apenas no estudo comparativo;
- 18 registros com eventos posteriores à venda são excluídos no treinamento;
- o período mais recente continua classificado como diagnóstico;
- a versão do candidato é `0.4.0-rc1`.

Na base limpa, o modelo demográfico apresentou ganho de 0,71% na MAE média
das cinco janelas. O modelo físico apresentou melhor desempenho no período
diagnóstico: MAE de aproximadamente US$ 67.106 e R² de 0,8998, ante MAE de
aproximadamente US$ 67.383 e R² de 0,8963. A decisão privilegia desempenho
diagnóstico, menor superfície de dados e menor risco de proxies sociais.

## Entregas

- módulo de persistência e inferência;
- comando reproduzível de treinamento final;
- filtro auditável de consistência temporal;
- artefato Joblib com pipeline completo;
- manifesto com hashes, versões, features, configuração e métricas;
- 100 previsões futuras com identificador e versão do modelo;
- resumo do treinamento e contrato do artefato;
- testes de integridade, persistência e reprodução das previsões;
- teste integral do treinamento sem o arquivo demográfico;
- rejeição de manifesto com schema, nome, versão ou features divergentes.

## Resultados

- linhas históricas recebidas: 21.613;
- linhas excluídas: 18;
- linhas usadas no treino final: 21.595;
- MAE média nas cinco janelas: aproximadamente US$ 63.881;
- MAE no período diagnóstico: aproximadamente US$ 67.106;
- previsões futuras geradas: 100;
- menor previsão: aproximadamente US$ 196.787;
- maior previsão: aproximadamente US$ 2.510.606.

## Limitações

- o teste mais recente foi consultado anteriormente e não é intocado;
- o CEP ainda pode representar diferenças contextuais entre regiões;
- os maiores valores mantêm erro absoluto e subestimação mais elevados;
- Joblib somente deve carregar artefatos de origem confiável;
- os preços reais dos exemplos futuros não estão disponíveis.

## Verificações para aprovação

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m property_value_insights.training --project-root .
```

## Pontos para revisão

- confirmar o modelo físico como artefato principal;
- conferir a justificativa para as 18 exclusões;
- conferir o schema de `reports/future_predictions.csv`;
- aprovar o candidato para incorporação e futura marcação como `v0.4.0`.
