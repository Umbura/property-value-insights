# Preparação da versão integrada

## Escopo

Este documento descreve como reproduzir e verificar a versão candidata do
projeto. A preparação não publica pacotes, não cria tags e não altera o modelo
aprovado nem o contrato da API.

## Identidade das versões

O projeto mantém versões independentes para componentes com ciclos de vida
distintos:

| Componente | Versão candidata | Finalidade |
| --- | --- | --- |
| entrega integrada | `1.0.0rc1` | código, documentação e artefatos reunidos |
| API | `0.5.0-rc1` | contrato HTTP de inferência |
| modelo | `0.4.0-rc1` | pipeline treinado e previsões associadas |

A versão integrada somente deve mudar para `1.0.0` após a revisão final e a
autorização do responsável pela publicação. Alterar a versão da entrega não
renomeia retroativamente a API nem o artefato de modelo.

## Dependências

- Python é restrito à série `3.13` e indicado em `.python-version`;
- `pyproject.toml` declara dependências diretas e extras por finalidade;
- `uv.lock` fixa a resolução transitiva para desenvolvimento e serving;
- `uv 0.12.1` é exigido pelo projeto, pelo CI e pelo build do contêiner;
- `numba` e `llvmlite` são fixados nos extras que usam SHAP porque a versão
  atual do SHAP não declara limites suficientes para uma resolução compatível
  com Python 3.13;
- o lock cobre Windows e Linux, as plataformas efetivamente verificadas no
  desenvolvimento e no contêiner; macOS não integra o contrato validado;
- as imagens de Python e `uv` são identificadas por tag e digest no Dockerfile;
- `pip-audit` verifica vulnerabilidades conhecidas no ambiente bloqueado;
- Dependabot monitora `uv`, GitHub Actions e a imagem-base do Docker.

Atualizações devem ocorrer em pull requests próprios. Para atualizar uma
dependência específica:

```powershell
uv lock --upgrade-package nome-do-pacote
uv sync --locked --extra dev
uv run --locked pytest -q
uv run --locked pip-audit
```

## Instalação limpa

Com `uv 0.12.1` disponível:

```powershell
uv sync --locked --extra dev
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked verify-property-release --project-root .
uv run --locked pip-audit
docker build --tag property-value-insights:release-candidate .
```

`verify-property-release` confere a identidade do pacote, os caminhos
obrigatórios, o contrato de ambiente, os hashes do artefato e dos dados, as 100
previsões, os notebooks executados, os links relativos da documentação e a
ausência de arquivos sensíveis em toda a árvore publicada.

Após executar notebooks, `sanitize-property-notebooks --project-root .` remove
somente os horários transitórios registrados pelo Jupyter. Células, contagens
de execução e saídas permanecem intactas, evitando diffs sem significado.

## Publicação manual

As ações abaixo permanecem intencionalmente manuais:

1. concluir a revisão dos pull requests empilhados;
2. definir a licença do código e confirmar a permissão aplicável aos dados;
3. promover a versão integrada de `1.0.0rc1` para `1.0.0`;
4. regenerar `uv.lock` e repetir todas as verificações;
5. incorporar as branches aprovadas no `main`;
6. criar a tag e as notas de release;
7. enviar o link do repositório conforme as instruções do desafio.

Não existe workflow de publicação automática nem credencial de publicação no
repositório.

## Evidências locais

Validação executada em 4 de agosto de 2026:

- instalação criada do zero com Python 3.13 e `uv sync --locked --extra dev`;
- Ruff aprovado e 86 testes automatizados aprovados;
- `pip-audit` sem vulnerabilidades conhecidas nas dependências publicadas;
- sete controles de integridade da entrega aprovados;
- notebooks exploratório e de modelagem reproduzidos byte a byte após a
  sanitização dos horários de execução;
- relatório de modelagem reproduzido byte a byte;
- imagem construída com as bases fixadas por digest;
- contêiner saudável em sistema de arquivos somente leitura;
- `/predict` retornou previsão válida e `/metrics` publicou as métricas
  operacionais;
- SHAP, Matplotlib e `pip-audit` permaneceram fora da imagem de serving;
- busca no conteúdo atual e no histórico Git sem padrões de credenciais.

Os três `PendingDeprecationWarning` observados vêm do módulo de cores do SHAP
0.52.0 e não alteram as explicações, os testes ou o runtime de serving.
