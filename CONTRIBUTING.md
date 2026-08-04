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

## Idioma

Documentacao, issues, pull requests e comunicacao voltada a avaliadores devem
ser escritas em portugues do Brasil. Identificadores de codigo, nomes de
pacotes, campos de API, branches e mensagens de commit devem permanecer em
ingles, seguindo as convencoes do ecossistema de software.

## Verificacoes locais

```powershell
uv sync --locked --extra dev
uv run --locked pytest
uv run --locked ruff check .
uv run --locked verify-property-release --project-root .
```

Nao enviar credenciais, arquivos `.env`, logs locais ou dados fora do escopo do
desafio.
