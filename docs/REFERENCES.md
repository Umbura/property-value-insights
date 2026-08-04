# Referências da arquitetura e do ciclo de vida

Fontes consultadas para fundamentar a arquitetura. A solução adota os princípios,
mas não afirma implantação das ferramentas ou plataformas citadas.

## MLOps e entrega

- Google Cloud Architecture Center. [MLOps: Continuous delivery and automation
  pipelines in machine learning](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).
  Fundamenta a separação entre CI, CD e treinamento contínuo, além de validação
  de dados e modelo antes da promoção.
- Google Cloud. [Practitioner's Guide to Machine Learning Operations](https://cloud.google.com/resources/mlops-whitepaper).
  Referência para serving, orquestração, metadados, gestão de datasets e
  monitoramento preditivo.
- AWS Prescriptive Guidance. [Observability and model management](https://docs.aws.amazon.com/prescriptive-guidance/latest/mlops-checklist/observability-model-management.html).
  Apoia versionamento, lineage, recuperação e comparação com execuções de treino.
- GitHub Docs. [Publishing Docker images](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images).
  Referência para construir e publicar imagens a partir de CI.

## Registro e observabilidade

- MLflow. [Model Registry Workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/).
  Fundamenta versões, tags e aliases como `champion` e `challenger`. MLflow é
  uma opção futura e não foi instalado nesta fase.
- Prometheus. [Instrumentation](https://prometheus.io/docs/practices/instrumentation/).
  Referência para taxa de requisições, erros e latência em serviços online.
- Prometheus. [Metric and label naming](https://prometheus.io/docs/practices/naming/).
  Referência para unidades, prefixos e controle de cardinalidade.

## Risco, monitoramento e transparência

- NIST. [Artificial Intelligence Risk Management Framework 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf).
  Fundamenta governança de risco ao longo do desenho, medição, gestão e uso.
- NIST. [Challenges to the Monitoring of Deployed AI Systems](https://doi.org/10.6028/NIST.AI.800-4).
  Apoia a separação entre monitoramento funcional, operacional e de impactos,
  além da necessidade de responsáveis e resposta a incidentes.
- Mitchell, M. et al. (2019). [Model Cards for Model Reporting](https://doi.org/10.1145/3287560.3287596).
  Fundamenta uso pretendido, contexto de avaliação, segmentos, limitações e
  considerações éticas do model card.

## Modelagem já adotada

- Duan, N. (1983). [Smearing Estimate: A Nonparametric Retransformation
  Method](https://doi.org/10.1080/01621459.1983.10478017).
- International Association of Assessing Officers. [Standard on Ratio
  Studies](https://www.iaao.org/wp-content/uploads/Standard_on_Ratio_Studies.pdf).
- scikit-learn. [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html).

## Incerteza e explicabilidade

- SHAP. [Permutation explainer](https://shap.readthedocs.io/en/stable/example_notebooks/api_examples/explainers/Permutation.html).
  Referência para explicações model-agnostic e aditividade das contribuições.
- Lundberg, S. M. e Lee, S.-I. [A Unified Approach to Interpreting Model
  Predictions](https://arxiv.org/abs/1705.07874).
  Fundamenta o uso de valores de Shapley para explicar previsões individuais.
- MAPIE. [Exchangeability testing on a fixed dataset](https://contrib.scikit-learn.org/MAPIE/1.4.1/generated/exchangeability_testing/1-quickstart/plot_exchangeability_fixed_dataset/).
  Apoia a cautela com garantias conformais quando há dependência temporal.
- Barber, R. F. et al. [Conformal Prediction Beyond
  Exchangeability](https://arxiv.org/abs/2202.13415).
  Referência para os limites do conformal clássico sob não intercambialidade.

Consulta realizada em agosto de 2026.
