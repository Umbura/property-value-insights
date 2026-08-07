# Revisão da Fase 2.1

> **Snapshot histórico:** este documento registra o estado observado durante uma fase anterior. Ele não substitui o manifesto, o model card, os contratos e as reviews C1 vigentes. Consulte [`docs/reviews/README.md`](README.md) para a hierarquia documental.

Status: aprovada com ressalva; decisão de empacotamento registrada na Fase 3.

## Objetivo

Reduzir a subestimação sistemática observada na escala original, com atenção
especial aos imóveis de maior valor, sem comprometer o desempenho geral nas
cinco janelas temporais de desenvolvimento.

## Implementação

- correção de retransformação por smearing;
- calibração nos 10% finais de cada partição de treino;
- reajuste do estimador com toda a partição após estimar o fator;
- diagnósticos gerais e para a faixa superior de preço;
- regra automatizada de promoção com quatro critérios cumulativos;
- testes unitários da calibração, das métricas e da regra de seleção.

## Decisão

O modelo `hist_demographics_log_temporal_smearing_10` foi promovido. Nas cinco
janelas de desenvolvimento, sua MAE média foi de aproximadamente US$ 63.155,
dentro da margem de 0,5% da referência de US$ 63.128. O MAE médio da faixa
superior caiu de aproximadamente US$ 130.028 para US$ 127.278, com melhora em
quatro das cinco janelas.

O viés médio geral, definido como `previsão - valor observado`, passou de
aproximadamente -US$ 11.579 para -US$ 2.195. Na faixa superior, passou de
aproximadamente -US$ 59.768 para -US$ 42.839.

## Avaliação temporal diagnóstica

Como esse período já havia sido consultado na Fase 2, seus resultados são
apresentados como diagnóstico, e não como estimativa intocada de generalização.
Nele, a calibração apresentou:

- MAE geral de aproximadamente US$ 67.456, ante US$ 73.912;
- viés médio geral de aproximadamente -US$ 20.892, ante -US$ 43.928;
- MAE da faixa superior de aproximadamente US$ 131.243, ante US$ 146.699;
- taxa de subestimação da faixa superior de 68,9%, ante 79,5%.

## Interpretação

A calibração reduz a assimetria de retransformação e melhora o comportamento
vertical, mas não elimina a subestimação da faixa superior. O resultado deve ser
tratado como uma melhora mensurável e limitada, não como solução definitiva do
erro de cauda.

## Limitações e próximos controles

- o período temporal mais recente não pode mais sustentar uma declaração de
  teste intocado para decisões posteriores;
- os dados demográficos agregados por CEP exigem documentação de proveniência
  e não devem ser interpretados causalmente;
- a faixa superior ainda apresenta viés negativo e deve ser monitorada em
  produção;
- uma avaliação futura verdadeiramente externa requer dados posteriores ou
  uma fonte independente.

## Decisão de empacotamento

Embora o modelo demográfico calibrado tenha sido promovido pelos critérios
estatísticos da Fase 2.1, a revisão de governança aprovou o modelo somente
físico para o artefato de produção. Na base temporalmente limpa, o ganho
demográfico de MAE média foi de 0,71%, enquanto o modelo físico apresentou
melhor MAE e R² no período diagnóstico. A escolha reduz o uso de proxies
socioeconômicas sem sacrificar desempenho relevante.

## Verificações para aprovação

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
```

O notebook executado e `reports/model_comparison.md` devem reproduzir os
valores registrados nesta revisão.
