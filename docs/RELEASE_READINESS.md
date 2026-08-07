# Preparação da entrega final

## Identidade

| Componente | Versão da entrega |
| --- | --- |
| projeto/pacote | `1.0.1` |
| API | `0.5.0-rc1` |
| modelo | `0.4.0-rc1` |
| imagem | `ghcr.io/umbura/property-value-insights:1.0.1` |

A promoção de patch consolida documentação, governança, organização e
publicação. Ela não modifica o modelo, o Joblib, o manifesto, os hashes, os dados
brutos nem as previsões.

## Validação antes do merge

```bash
uv sync --locked --extra dev
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked verify-property-release --project-root .
uv run --locked pip-audit
docker build --tag property-value-insights:1.0.1 .
```

O gate verifica versão, caminhos obrigatórios, ambiente, artefato, hashes, 100
previsões, notebooks, links relativos e ausência de padrões de credenciais.

## Publicação

1. incorporar a PR final na `main` após revisão independente e CI verde;
2. criar e publicar a GitHub Release `v1.0.1` no commit aprovado;
3. o evento de publicação aciona `.github/workflows/release.yml`;
4. o workflow verifica a tag, publica tags semânticas no GHCR e testa a imagem
   pelo digest retornado pelo registry;
5. confirmar que o pacote GHCR está público e que o pull anônimo funciona;
6. registrar o digest final na Release ou na Issue #68.

O `GITHUB_TOKEN` recebe apenas `contents: read` e `packages: write` no job de
publicação. A imagem é vinculada automaticamente a este repositório. O primeiro
pacote do GHCR pode nascer privado e exige confirmação manual de visibilidade.

## Critério final

A entrega somente está concluída quando a CI da `main`, o workflow de publicação,
o pull por digest e os endpoints da imagem publicada estiverem aprovados.
