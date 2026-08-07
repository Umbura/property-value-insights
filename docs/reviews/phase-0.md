# Revisao da Fase 0

> **Snapshot histórico:** este documento registra o estado observado durante uma fase anterior. Ele não substitui o manifesto, o model card, os contratos e as reviews C1 vigentes. Consulte [`docs/reviews/README.md`](README.md) para a hierarquia documental.

Status: em andamento; aguardando revisao supervisionada.

## Objetivo

Preparar o repositorio, registrar o contrato inicial dos dados e criar a
primeira verificacao automatizada antes da modelagem.

## Entregas desta etapa

- estrutura inicial de diretorios;
- arquivos de entrada em `data/raw/`;
- `pyproject.toml` com dependencias e ferramentas de desenvolvimento;
- `.gitignore` e `.env.example`;
- pacote inicial em `src/property_value_insights/`;
- testes do contrato em `tests/`;
- contrato documentado em `docs/DATA_CONTRACT.md`;
- copia da especificacao original em `docs/CHALLENGE_README.md`.

## Auditoria observada

- 21.613 registros historicos;
- 70 linhas demograficas;
- 100 exemplos futuros;
- cobertura completa dos CEPs observados;
- 176 IDs repetidos, sem registros inteiramente duplicados;
- nenhum modelo de ML treinado nesta fase.

## Verificacao executada

- Python 3.13.7;
- `.venv\Scripts\python.exe -m pytest -q`: 11 testes aprovados;
- `.venv\Scripts\python.exe -m ruff check .`: todos os checks aprovados;
- `.venv\Scripts\python.exe -m pip check`: nenhuma dependencia quebrada;
- contrato reforçado com validacao de numericidade, nulos, faixas categoricas,
  percentuais, CEPs e coordenadas;
- branch sem alteracoes pendentes depois dos commits da fase;
- Docker disponivel no ambiente, mas ainda nao utilizado porque a API pertence
  a Fase 4.

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

## Pontos para revisao de Iago

- aprovar a reorganizacao dos CSVs em `data/raw/`;
- aprovar Python 3.13 como versao local de referencia;
- aprovar o tratamento de `id` repetido como referencia, nao como chave unica;
- revisar as colunas e regras do contrato;
- revisar a estrutura inicial do repositorio;
- decidir se a Fase 0 pode ser versionada como `v0.1.0`.

## Status da aprovacao

Pendente de revisao supervisionada.
