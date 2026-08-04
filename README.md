# Property Value Insights

Sistema reprodutível de estimativa de preços residenciais com Machine Learning e
práticas de MLOps. O projeto foi desenvolvido para o desafio técnico de previsão
de preços de imóveis e trata os dados como uma solução de cliente real.

Status atual: versão estável integrada `1.0.0`, com modelo, API, análises e
artefatos reproduzíveis disponíveis para avaliação técnica.

## Objetivo

Estimar o preço de imóveis a partir de características físicas e espaciais,
preservando rastreabilidade dos dados, validação, avaliação do modelo e
documentação das decisões técnicas. Informações demográficas agregadas por CEP
foram avaliadas por ablação, mas não integram o artefato aprovado.

## Dados

Os arquivos fornecidos estão versionados em `data/raw/`:

- `kc_house_data.csv`: histórico de imóveis com o alvo `price`;
- `zipcode_demographics.csv`: dados demográficos agregados por CEP;
- `future_unseen_examples.csv`: exemplos sem preço para a inferência final.

O contrato, a auditoria inicial e os hashes dos arquivos estão documentados em
[`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md). A especificação original do
desafio está preservada em [`docs/CHALLENGE_README.md`](docs/CHALLENGE_README.md).

## Execução local

O ambiente de referência usa Python 3.13 e `uv 0.12.1`. O arquivo `uv.lock`
fixa as dependências diretas e transitivas. No PowerShell:

```powershell
uv sync --locked --extra dev
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked verify-property-release --project-root .
uv run --locked python -m ipykernel install --user --name property-value-insights --display-name "Property Value Insights (project)"
uv run --locked jupyter nbconvert --to notebook --execute notebooks/01_eda.ipynb --inplace --ExecutePreprocessor.kernel_name=property-value-insights --ExecutePreprocessor.timeout=600
uv run --locked jupyter nbconvert --to notebook --execute notebooks/02_modeling.ipynb --inplace --ExecutePreprocessor.kernel_name=property-value-insights --ExecutePreprocessor.timeout=600
uv run --locked sanitize-property-notebooks --project-root .
uv run --locked python -m property_value_insights.training --project-root .
uv run --locked python -m property_value_insights.stakeholder_reporting --project-root .
uv run --locked python -m property_value_insights.uncertainty --project-root .
uv run --locked python -m property_value_insights.explainability --project-root .
docker compose up --build
```

O extra `dev` inclui as dependências de teste, notebooks e geração dos
relatórios. Para instalar somente o projeto e a explicabilidade, use
`uv sync --locked --extra explainability`. O extra `reporting` mantém apenas a
geração dos relatórios de negócio. A imagem de serving não inclui Matplotlib,
SHAP nem os dados brutos e executa somente a API de inferência.

## Modelo e artefato

O artefato principal usa características físicas e espaciais com
HistGradientBoostingRegressor e calibração temporal. A alternativa com dados
demográficos permanece documentada como experimento, mas não integra o modelo
empacotado devido ao ganho marginal e ao risco de proxies socioeconômicas.

O comando de treinamento valida a integridade temporal, exclui 18 registros
com eventos posteriores à venda, treina com 21.595 registros, verifica o
artefato por hash e gera as 100 previsões futuras. O contrato completo está em
[`docs/ARTIFACT_CONTRACT.md`](docs/ARTIFACT_CONTRACT.md).

## API de inferência

A API FastAPI carrega e verifica o artefato durante a inicialização. Ela oferece
predição individual e em lote, metadados do modelo, healthcheck, identificadores
de requisição, logs estruturados e métricas Prometheus. O contrato, os exemplos
de requisição e os limites operacionais estão em
[`docs/API_CONTRACT.md`](docs/API_CONTRACT.md).

Após `docker compose up --build`, a documentação OpenAPI fica disponível em
`http://127.0.0.1:8000/docs`. O contêiner executa como usuário sem privilégios e
é compatível com sistema de arquivos raiz somente leitura.

## Arquitetura e ciclo de vida

A solução distingue o runtime implementado da topologia recomendada para
produção. O [diagrama de arquitetura](diagrams/production_architecture.md) cobre
entrada, serving, observabilidade, CI/CD, registro e rollback. O
[ciclo de vida](diagrams/model_lifecycle.md) mostra a passagem de novos rótulos
por validação, treinamento, gates, staging, aprovação e monitoramento.

A estratégia de reentreinamento está em
[`docs/CONTINUOUS_LEARNING.md`](docs/CONTINUOUS_LEARNING.md). Ela não promove
modelos automaticamente: a automação prepara evidências, e a mudança do
champion exige critérios temporais e aprovação humana.

## Comunicação e governança

O [model card](docs/MODEL_CARD.md) registra uso pretendido, dados, métricas,
importância por permutação, desempenho por faixa, limitações e considerações éticas. O
[resumo para stakeholders](reports/stakeholder_summary.md) traduz as métricas
para decisão de negócio e utiliza um gráfico reproduzido especificamente para o
modelo físico aprovado.

## Análises opcionais

O diagnóstico opcional calibra um intervalo empírico com previsões fora de
amostra das cinco janelas de desenvolvimento e mede cobertura e largura no
período mais recente. Também gera explicações SHAP globais e locais diretamente
do Joblib verificado.
Os resultados e as ressalvas estão no
[`relatório de incerteza e explicabilidade`](reports/optional_analysis.md).

Essas rotinas são offline: não modificam o modelo promovido, as 100 previsões,
o contrato da API ou a imagem de serving. O intervalo não é apresentado como
garantia conformal, e as contribuições SHAP não são efeitos causais.

## Estrutura

```text
data/raw/       arquivos de entrada fornecidos
src/            código reutilizável do projeto
tests/          testes automatizados
docs/           contrato, especificacao e revisoes
artifacts/      artefato e manifesto versionados do modelo
reports/        relatorios e resultados gerados
notebooks/      analises exploratorias reproduziveis
diagrams/       diagramas de arquitetura e deploy
```

## Processo

O desenvolvimento ocorre por fases, branches, commits atômicos, revisão
supervisionada e pull requests. As decisões de modelagem, deploy, aprendizado
contínuo e comunicação com stakeholders são documentadas junto às respectivas
entregas.
O fluxo completo esta em [`PROCESSO_GIT_GITHUB.md`](PROCESSO_GIT_GITHUB.md).

A estratégia de dependências, a verificação em ambiente limpo e as ações
manuais de publicação estão em
[`docs/RELEASE_READINESS.md`](docs/RELEASE_READINESS.md).

## Licença e dados

O código-fonte e a documentação original estão disponíveis sob a
[licença MIT](LICENSE). Os arquivos brutos recebidos para o desafio não são
relicenciados; as condições e os limites aplicáveis estão descritos no
[`DATA_NOTICE.md`](DATA_NOTICE.md).

As mudanças publicadas estão registradas no [`CHANGELOG.md`](CHANGELOG.md).
