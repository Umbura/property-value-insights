# Revisão da Fase 7

> **Snapshot histórico:** este documento registra o estado observado durante uma fase anterior. Ele não substitui o manifesto, o model card, os contratos e as reviews C1 vigentes. Consulte [`docs/reviews/README.md`](README.md) para a hierarquia documental.

Status: pronta para revisão supervisionada.

## Objetivo

Preparar a entrega integrada para avaliação final, com instalação bloqueada,
auditoria de segurança, notebooks reproduzíveis e verificação automatizada dos
artefatos públicos. Publicação, merge final, tag e release não fazem parte desta
execução.

## Escopo implementado

- versão integrada candidata `1.0.0rc1`;
- Python 3.13 e `uv 0.12.1` declarados explicitamente;
- `uv.lock` para dependências diretas e transitivas em Windows e Linux;
- CI e Docker consumindo o lock em modo bloqueado;
- imagens-base identificadas por tag e digest;
- auditoria com `pip-audit` e manutenção programada por Dependabot;
- verificador executável de versão, arquivos, ambiente, hashes, previsões,
  notebooks, links e higiene de publicação;
- sanitização determinística dos metadados transitórios dos notebooks;
- remoção de configuração não implementada de IA generativa;
- linguagem técnica dos notebooks e relatórios sem referências ao processo de
  desenvolvimento;
- instruções de reprodução e publicação manual atualizadas.

## Correções encontradas na auditoria

1. A versão divergia entre `pyproject.toml` e `__init__.py`.
2. O `.env.example` anunciava uma chave de IA sem integração correspondente.
3. A resolução universal escolhia uma versão de `numba` incompatível com
   Python 3.13; o contrato foi limitado às plataformas verificadas e as versões
   compatíveis foram fixadas.
4. `pytest 8.4.2` possuía vulnerabilidade conhecida; a dependência foi
   atualizada para `9.0.3`.
5. O teste de isolamento do serving dependia do comando antigo do `pip` e foi
   atualizado para o contrato bloqueado do `uv`.
6. O notebook de modelagem não reproduzia a ressalva de governança do relatório.
7. `fit_seconds` introduzia variação sem significado nos artefatos publicados.
8. O Jupyter persistia horários de execução que produziam diffs em cada rodada.
9. O gate de entrega não comparava o conjunto histórico com o hash registrado
   no manifesto; a entrada de treinamento passou a integrar a verificação.
10. A higiene de publicação restringia arquivos sensíveis apenas na raiz; a
    proibição de `.env`, `.env.*`, `*.pem` e `*.key` passou a ser recursiva,
    preservando `.env.example` como contrato público.

## Validação executada

```powershell
uv sync --locked --extra dev
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked verify-property-release --project-root .
uv run --locked pip-audit
docker compose config --quiet
docker build --tag property-value-insights:release-candidate .
```

Resultados:

- ambiente Python 3.13 criado do zero: aprovado;
- Ruff: aprovado;
- pytest: 86 testes aprovados, incluindo cenários negativos de adulteração dos
  dados históricos e arquivos sensíveis aninhados;
- dependências: 124 pacotes resolvidos no lock;
- auditoria: nenhuma vulnerabilidade conhecida;
- verificador da entrega: sete controles aprovados;
- notebooks: execução completa, sem erros e reprodução byte a byte após
  sanitização;
- relatório de modelagem: reprodução byte a byte;
- Docker Compose: configuração válida;
- imagem: build aprovado;
- contêiner: healthcheck aprovado em modo somente leitura;
- inferência: US$ 372.953,43 no exemplo contratual, com modelo `0.4.0-rc1`;
- métricas Prometheus: disponíveis;
- dependências opcionais: ausentes da imagem de serving;
- credenciais: nenhum padrão encontrado no conteúdo atual ou no histórico Git.

GitHub Actions no primeiro envio da branch:

- job `quality`: aprovado em 1 min 31 s;
- job `container`: aprovado em 30 s.

## Limitações e ações manuais

- o lock foi validado em Windows e Linux; macOS não integra o contrato atual;
- o SHAP 0.52.0 emite três avisos de depreciação internos do módulo de cores;
- a escolha de licença depende do titular e da permissão aplicável aos dados;
- a promoção de `1.0.0rc1` para `1.0.0` exige autorização;
- merge dos PRs empilhados, tag, release e envio por e-mail permanecem manuais;
- nenhuma alteração foi feita no modelo, nas previsões ou no schema da API.

## Gate de aprovação

A fase pode ser aprovada quando o responsável confirmar:

- adequação do mecanismo de lock e da limitação de plataformas;
- clareza do README e das instruções de reprodução;
- utilidade do verificador de entrega;
- manutenção das análises opcionais no escopo final;
- ciência das ações manuais antes da publicação.
