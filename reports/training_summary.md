# Resumo do treinamento final

## Decisão

O artefato principal utiliza somente características físicas e espaciais. Os dados
demográficos permanecem como experimento documentado e não entram no pipeline final.

## Integridade temporal

- Linhas recebidas: 21,613.
- Linhas excluídas: 18.
- Linhas usadas no treinamento final: 21,595.
- Motivo da exclusão: construção ou reforma registrada após a data da venda.

## Avaliação reproduzida

- MAE temporal média: US$ 63,880.80.
- MAE no período diagnóstico: US$ 67,105.71.
- R² no período diagnóstico: 0.8998.
- O período mais recente é diagnóstico, pois já havia sido consultado.

## Inferência futura

- Previsões geradas: 100.
- Menor previsão: US$ 196,786.80.
- Mediana das previsões: US$ 456,763.07.
- Maior previsão: US$ 2,510,606.44.

As previsões não são métricas de acurácia porque os exemplos futuros não possuem alvo.
