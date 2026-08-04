# Property Value Insights

Sistema reprodutível de estimativa de preços residenciais com Machine Learning e
práticas de MLOps. O projeto foi desenvolvido para o desafio técnico de previsão
de preços de imóveis e trata os dados como uma solução de cliente real.

Status atual: análise exploratória e qualidade dos dados concluídas; modelagem em preparação.

## Objetivo

Estimar o preço de imóveis a partir de características físicas e informações
demográficas agregadas por CEP, preservando rastreabilidade dos dados,
validação, avaliação do modelo e documentação das decisões técnicas.

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
```

## Estrutura

```text
data/raw/       arquivos de entrada fornecidos
src/            codigo reutilizavel do projeto
tests/          testes automatizados
docs/           contrato, especificacao e revisoes
artifacts/      artefatos de modelo versionados nas fases futuras
reports/        relatorios e resultados gerados
notebooks/      analises exploratorias reproduziveis
diagrams/       diagramas de arquitetura e deploy
```

## Processo

O desenvolvimento ocorre por fases, branches, commits atomicos, revisao
supervisionada e pull requests. As decisoes de modelagem, deploy, aprendizado
continuo e comunicacao com stakeholders serao incorporadas nas fases seguintes.
O fluxo completo esta em [`PROCESSO_GIT_GITHUB.md`](PROCESSO_GIT_GITHUB.md).
