# Property Value Insights

Sistema reprodutível de estimativa de preços residenciais com Machine Learning e
práticas de MLOps. O projeto foi desenvolvido para o desafio técnico de previsão
de preços de imóveis e trata os dados como uma solução de cliente real.

Status atual: modelo e API executáveis; arquitetura, ciclo de vida e comunicação
com stakeholders em revisão supervisionada.

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

O ambiente de referência usa Python 3.13. No PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ipykernel install --user --name property-value-insights --display-name "Property Value Insights (project)"
.\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks/01_eda.ipynb --inplace --ExecutePreprocessor.kernel_name=property-value-insights --ExecutePreprocessor.timeout=600
.\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks/02_modeling.ipynb --inplace --ExecutePreprocessor.kernel_name=property-value-insights --ExecutePreprocessor.timeout=600
.\.venv\Scripts\python.exe -m property_value_insights.training --project-root .
.\.venv\Scripts\python.exe -m property_value_insights.stakeholder_reporting --project-root .
docker compose up --build
```

O ambiente `dev` inclui as dependências de geração dos relatórios. Para instalar
somente o projeto e essas dependências, use `pip install -e ".[reporting]"`. A
imagem de serving não inclui Matplotlib nem os dados brutos e executa somente a
API de inferência.

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

## Estrutura

```text
data/raw/       arquivos de entrada fornecidos
src/            codigo reutilizavel do projeto
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
