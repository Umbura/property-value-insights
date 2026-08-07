# Revisão da Fase 2

> **Snapshot histórico:** este documento registra o estado observado durante uma fase anterior. Ele não substitui o manifesto, o model card, os contratos e as reviews C1 vigentes. Consulte [`docs/reviews/README.md`](README.md) para a hierarquia documental.

Status: revisão concluída; complementada pela Fase 2.1.

## Objetivo

Comparar referências e modelos de regressão com um protocolo temporal,
selecionar um candidato sem consultar o teste reservado e registrar o
desempenho geral e por segmentos.

## Entregas

- baseline de mediana;
- referências Ridge com alvo original e logarítmico;
- modelos HistGradientBoosting com e sem dados demográficos;
- busca limitada e determinística de hiperparâmetros;
- cinco janelas temporais expansivas que preservam datas completas;
- regra testável de seleção por MAE média, pior fold e variação;
- comparação com a referência no teste temporal reservado;
- análise por faixa de preço, CEP e importância por permutação;
- notebook executado e relatório técnico gerado.

## Decisão

O modelo principal da Fase 2 foi `hist_demographics_log_default`. Ele apresentou MAE média
de aproximadamente US$ 63.128 nas cinco janelas e MAE de aproximadamente
US$ 73.912 no teste temporal então reservado. O ganho de MAE sobre a mediana foi de
67,2%.

O modelo `hist_demographics_log_regularized` permanece como alternativa. Ele
obteve MAE média de aproximadamente US$ 63.174 e não foi avaliado no teste
reservado.

## Evidências

- o teste temporal contém 4.640 registros posteriores ao desenvolvimento;
- nenhuma data aparece simultaneamente no treino e na validação de um fold;
- somente a mediana e o modelo principal foram medidos no teste reservado;
- o modelo principal atingiu R² de 0,877 no teste temporal;
- o erro permaneceu mais alto na faixa superior de preços e em alguns CEPs.

## Verificações

As verificações devem ser repetidas imediatamente antes da revisão:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
```

O notebook `notebooks/02_modeling.ipynb` deve permanecer executado, sem erros e
com os resultados correspondentes a `reports/model_comparison.md`.

## Limitações conhecidas

- os dados representam uma única região e um intervalo temporal limitado;
- dados demográficos agregados por CEP podem atuar como proxies sociais e não
  devem ser interpretados como atributos individuais ou evidências causais;
- os erros aumentam para imóveis de maior valor;
- o artefato carregável, o manifesto e as previsões futuras pertencem à Fase 3.

## Decisão de continuidade

- o protocolo de cinco janelas com datas completas foi mantido;
- a margem de 0,5% foi mantida para comparar candidatas tecnicamente próximas;
- o diagnóstico de subestimação motivou a Fase 2.1;
- o período mais recente deixou de ser considerado intocado para novas
  decisões de seleção.
