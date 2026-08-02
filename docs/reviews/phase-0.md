# Revisao da Fase 0

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

## Verificacao

Ainda sera executada depois da instalacao do ambiente:

```powershell
py -3.13 -m pytest
py -3.13 -m ruff check .
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
