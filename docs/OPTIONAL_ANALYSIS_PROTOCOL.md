# Protocolo de incerteza e explicabilidade

## Escopo

A Fase 6 adiciona duas análises offline ao modelo físico aprovado:

1. intervalo empírico de previsão baseado em resíduos temporais;
2. explicações SHAP globais e locais do artefato servido.

Essas análises não alteram o treinamento aprovado, o artefato, as previsões
publicadas ou o contrato da API. O adaptador de IA generativa não será incluído.

## Intervalo empírico

### Calibração

O período de desenvolvimento é dividido nas mesmas cinco janelas temporais
expansivas usadas na avaliação do modelo. Em cada janela, o estimador é ajustado
somente com datas anteriores e produz previsões fora de amostra para a validação.

Para cada linha calcula-se o escore na escala logarítmica:

```text
|log(1 + preço observado) - log(1 + preço estimado)|
```

Para um nível nominal de 90%, usa-se o quantil empírico com correção finita e
método `higher`. Esse valor é aplicado de forma simétrica ao logaritmo da
previsão e retorna limites multiplicativos na escala de preço.

### Avaliação

O período diagnóstico de março a maio de 2015 não participa da calibração do
intervalo. Ele mede:

- cobertura observada;
- largura média e mediana;
- largura relativa à previsão;
- cobertura e largura por quartil do preço observado;
- estabilidade do escore entre as cinco janelas de desenvolvimento.

O resultado será chamado de intervalo empírico temporal. Não será apresentado
como garantia conformal em produção, pois transações ordenadas no tempo podem
violar intercambialidade e sofrer mudança de distribuição. Cobertura e largura
sempre serão mostradas juntas.

## Explicabilidade SHAP

O processo carrega o Joblib após verificar manifesto e SHA-256. O explainer
model-agnostic opera sobre as 18 features originais do pipeline físico; nenhuma
feature demográfica é aceita.

O baseline usa uma amostra determinística do histórico. As explicações globais
agregam o valor absoluto das contribuições nas 100 linhas futuras, enquanto
exemplos locais mostram como o valor-base e as contribuições reconciliam a
previsão. A diferença de aditividade deve permanecer dentro da tolerância
numérica definida nos testes.

SHAP descreve o comportamento do modelo em relação ao baseline escolhido. Não
mede causalidade, mérito do imóvel nem efeito isolado de features correlacionadas.

## Dependências e runtime

SHAP e Matplotlib permanecem em um grupo opcional. A imagem de serving continua
sem essas dependências e não oferece endpoint de explicação. Essa separação evita
aumento de superfície, latência e custo no caminho de inferência.

## Referências

- SHAP. [Permutation explainer](https://shap.readthedocs.io/en/stable/example_notebooks/api_examples/explainers/Permutation.html).
- Lundberg, S. M. e Lee, S.-I. [A Unified Approach to Interpreting Model Predictions](https://arxiv.org/abs/1705.07874).
- MAPIE. [Exchangeability testing on a fixed dataset](https://contrib.scikit-learn.org/MAPIE/1.4.1/generated/exchangeability_testing/1-quickstart/plot_exchangeability_fixed_dataset/).
- Barber, R. F. et al. [Conformal Prediction Beyond Exchangeability](https://arxiv.org/abs/2202.13415).
