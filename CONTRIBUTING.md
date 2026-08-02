# Contribuindo

Este repositorio segue o processo descrito em
`PROCESSO_GIT_GITHUB.md`.

## Fluxo

1. Criar ou atualizar a issue da fase.
2. Trabalhar em uma branch descritiva.
3. Fazer commits atomicos com mensagens claras.
4. Executar os testes locais.
5. Abrir um pull request com objetivo, alteracoes, testes e limitacoes.
6. Aguardar a revisao supervisionada antes do merge.

## Verificacoes locais

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Nao enviar credenciais, arquivos `.env`, logs locais ou dados fora do escopo do
desafio.
