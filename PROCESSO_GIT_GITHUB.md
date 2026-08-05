# Processo Git e GitHub do desafio

Este documento define como o projeto sera versionado, revisado e publicado.
Ele foi elaborado a partir do [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow),
da documentacao de README do GitHub, das orientacoes de CI para Python e das
recomendacoes de seguranca para secrets.

O repositorio tambem sera tratado como parte da avaliacao tecnica. A historia
deve tornar visiveis as decisoes, os testes, os problemas encontrados e as
correcoes realizadas.

## Nota de contexto após a v1.0.0

Este documento registra o planejamento e a execução histórica das Fases 0–7,
concluídas com a primeira release estável integrada, `v1.0.0`. Nesse contexto
histórico, a expressão "entrega final revisada" marca o encerramento do ciclo de
construção da release; ela não significa que o desafio técnico já foi submetido.

O processo atual de revisão pré-entrega, correções, validação e preparação da
submissão está em
[`docs/REVIEW_AND_DELIVERY_PROCESS.md`](docs/REVIEW_AND_DELIVERY_PROCESS.md).

## 1. Principios

- `main` deve permanecer executavel e representar uma versao revisada.
- Cada mudanca deve ter uma finalidade unica e ser reversivel.
- Commits nao serao criados artificialmente apenas para aumentar a atividade.
- Nomes, mensagens e descricoes serao objetivos e profissionais.
- O README sera atualizado junto com a funcionalidade correspondente.
- Nenhum commit deve conter segredo, token, senha, arquivo pessoal ou dado que
  nao possa ser publicado.
- O estado da implementacao sera distinguido de proposta futura.

O GitHub recomenda branches curtas e descritivas, commits isolados, pull
requests com resumo e verificacoes antes do merge. Esse sera o nosso fluxo,
adaptado para um repositorio individual.

## 2. Inicializacao do repositorio

Antes do primeiro push sera feita uma revisao local:

1. Confirmar que a pasta correta e a do desafio.
2. Conferir os tres CSVs fornecidos e a ausencia de arquivos pessoais.
3. Criar `.gitignore`, `.env.example` e estrutura inicial.
4. Criar um ambiente virtual documentado.
5. Executar uma verificacao de importacao e um teste minimo.
6. Revisar o conteudo com `git status` e `git diff --cached`.
7. Inicializar o repositorio local.
8. Fazer o primeiro commit de bootstrap.
9. Criar o repositorio remoto com descricao, topics e README.
10. Fazer o primeiro push apenas depois da revisao de seguranca.

O repositorio sera publico quando estiver apto a ser examinado. O fato de ser
publico nao autoriza publicar credenciais ou resultados que nao possam ser
distribuidos.

## 3. Branches

### Branch principal

- `main`: versao estavel e executavel.

### Branches de trabalho

Cada fase sera desenvolvida em uma branch separada, criada a partir de `main`:

- `codex/phase-0-bootstrap-contract`
- `codex/phase-1-eda-quality`
- `codex/phase-2-modeling-evaluation`
- `codex/phase-3-training-artifact`
- `codex/phase-4-api-docker-observability`
- `codex/phase-5-lifecycle-stakeholders`
- `codex/phase-6-optional-explainability`
- `codex/phase-7-final-review`

Se uma fase exigir correcao posterior, sera criada uma branch de correcao
especifica, como `codex/fix-temporal-split`.

Nao serao misturadas alteracoes de fases diferentes na mesma branch sem uma
justificativa registrada.

## 4. Commits

As mensagens usarao uma forma consistente inspirada em Conventional Commits:

```text
tipo(escopo): resumo curto no imperativo
```

Tipos previstos:

- `feat`: funcionalidade nova;
- `fix`: correcao de comportamento;
- `test`: inclusao ou ajuste de testes;
- `docs`: documentacao;
- `refactor`: reorganizacao sem mudanca de comportamento;
- `chore`: configuracao ou manutencao;
- `ci`: automacao de integracao continua;
- `exp`: experimento de modelagem claramente identificado.

Exemplos adequados:

```text
feat(data): validate zipcode merge cardinality
test(data): cover unknown zipcode handling
exp(model): compare temporal split candidates
docs(model): explain baseline and selection criteria
feat(api): add validated single prediction endpoint
fix(api): reject negative living area values
```

Quando a mudanca exigir contexto, o corpo do commit deve registrar:

```text
Motivo: por que a mudanca foi necessaria.
Alteracao: o que foi modificado.
Verificacao: quais testes ou comandos foram executados.
```

Um commit deve ser pequeno o bastante para ser compreendido e grande o
bastante para permanecer coerente. Exemplos:

- separar contrato de dados e teste do contrato em commits distintos;
- separar implementacao de endpoint e documentacao do endpoint quando isso
  facilitar a revisao;
- incluir uma correcao e seu teste juntos quando o teste depende diretamente
  da correcao;
- nao misturar formatacao geral com uma mudanca de regra de negocio.

Mensagens como `update`, `changes`, `final`, `testando` ou `arrumei` nao serao
usadas.

## 5. Pull requests

Cada fase sera entregue por pull request, mesmo sendo um repositorio pessoal.
Isso cria um registro de revisao e permite avaliar a fase antes de incorporala
ao `main`.

### Titulo

O titulo deve identificar a fase:

```text
feat: establish data contract and project bootstrap
feat: add temporal modeling evaluation
feat: expose model through FastAPI
```

### Corpo

Cada pull request deve informar:

```markdown
## Objetivo
Qual problema esta fase resolve.

## Alteracoes
- arquivos e comportamentos adicionados;
- decisoes relevantes;
- limitacoes conhecidas.

## Verificacao
- comandos executados;
- resultado dos testes;
- resultado da execucao local ou do container.

## Escopo futuro
O que foi deliberadamente deixado para outra fase.
```

Antes do merge, faremos uma revisao como se fossemos o avaliador:

- a mudanca resolve o objetivo da fase?
- o README ou a documentacao foi atualizada?
- ha teste para o comportamento critico?
- existe vazamento de dados ou dependencia implicita?
- a execucao limpa foi verificada?
- a alteracao pode ser revertida sem perder outra funcionalidade?

## 6. Merge e historico

O pull request so sera incorporado quando os testes passarem e a revisao local
estiver concluida. O merge preferencial sera `squash merge` por fase quando os
commits internos forem apenas etapas de uma mesma entrega; os commits e a
discussao continuarao visiveis dentro do pull request.

Se uma fase possuir decisoes independentes que devam permanecer no historico
principal, sera usado merge normal. A escolha sera registrada no pull request.

Depois do merge:

1. conferir o `main` local;
2. executar o teste principal da fase;
3. criar a tag da versao;
4. publicar release notes quando a versao for relevante;
5. excluir a branch de trabalho ja concluida.

## 7. Versoes, tags e releases

As tags marcam estados estaveis do projeto. A numeracao adotada sera:

```text
v0.1.0  bootstrap, contrato e auditoria inicial
v0.2.0  EDA e qualidade dos dados
v0.3.0  baseline, modelos e avaliacao
v0.4.0  pipeline de treinamento, artefato e previsoes
v0.5.0  API, Docker e observabilidade
v0.6.0  deploy documentado, ciclo de vida e stakeholders
v0.7.0  opcionais revisados, se existirem
v1.0.0  entrega final revisada
```

Uma versao de correcao podera usar, por exemplo, `v0.3.1` quando houver um
bug corrigido sem mudanca de escopo. Uma funcionalidade nova dentro da mesma
fase podera incrementar o segundo numero se houver motivo para publicar uma
versao intermediaria.

As releases serao criadas apenas para estados que possam ser executados e
explicados. Cada release deve registrar:

- objetivo da versao;
- principais alteracoes;
- testes executados;
- limitacoes conhecidas;
- como executar aquela versao;
- proximos passos.

O GitHub baseia releases em tags que apontam para pontos especificos do
historico. Isso permite comparar a evolucao e retornar a uma versao anterior.

## 8. Integracao continua

Depois da primeira estrutura funcional, o repositorio tera um workflow em
`.github/workflows/ci.yml` para pull requests e pushes ao `main`.

O CI minimo sera:

1. configurar uma versao de Python fixada;
2. instalar dependencias;
3. validar imports e configuracao;
4. executar testes unitarios;
5. executar verificacao do contrato de dados com amostra controlada;
6. construir o Docker quando a API estiver disponivel;
7. verificar que o container inicia e responde ao health check.

Os notebooks completos nao precisam ser executados em todo push se forem
demorados. Nesse caso, teremos testes de pipeline no CI e uma rotina explicita
para executar e revisar os notebooks antes das releases de modelagem.

O workflow sera simples o suficiente para ser executado por outra pessoa sem
servicos pagos ou credenciais externas.

## 9. Seguranca e limpeza antes do push

Antes de qualquer publicacao:

- verificar `.env`, tokens, chaves, senhas e credenciais AWS;
- conferir que `.gitignore` cobre ambientes virtuais, cache, logs locais e
  arquivos temporarios;
- conferir se o Git nao esta rastreando o arquivo errado por causa do diretorio
  de trabalho;
- procurar strings suspeitas no staged diff;
- verificar tamanho e origem dos arquivos de dados;
- nao usar `git add .` sem revisar o estado do repositorio;
- conferir `git diff --cached` antes do commit e `git log` antes do push.

O push protection do GitHub pode bloquear secrets antes que eles cheguem ao
repositorio, mas isso nao substitui a revisao local. Se um segredo real for
exposto, ele deve ser revogado ou rotacionado, e nao apenas apagado do arquivo.

## 10. Documentacao do repositorio

O repositorio final tera, no minimo:

```text
README.md
CONTEXTO_DESAFIO.md
ESTRATEGIA_EXECUCAO.md
PESQUISA_DIFERENCIAIS.md
PROCESSO_GIT_GITHUB.md
CONTRIBUTING.md
LICENSE ou explicacao de uso do material do desafio
.gitignore
.env.example
.github/workflows/ci.yml
notebooks/
src/
tests/
reports/
diagrams/
artifacts/
```

O README principal deve ser curto o suficiente para leitura inicial e conter:

- problema e objetivo;
- resumo dos resultados;
- arquitetura;
- como instalar e executar;
- como executar testes;
- como chamar a API;
- link para relatorios e diagramas;
- limitacoes;
- distincao entre implementado e proposto;
- versao final e data da revisao.

Documentos longos ficarao em arquivos proprios e serao ligados pelo README.
O GitHub recomenda usar o README para explicar utilidade, inicio rapido,
manutencao e caminhos para documentacao adicional.

## 11. Ordem de trabalho com Git

Para cada fase, seguiremos sempre o mesmo ciclo:

1. Abrir ou atualizar uma issue com objetivo e criterios de aceite.
2. Criar branch a partir do `main` estavel.
3. Implementar uma mudanca pequena e fazer commit descritivo.
4. Executar teste local e atualizar documentacao correspondente.
5. Repetir ate a fase atingir os criterios de aceite.
6. Abrir pull request com resumo, testes e limitacoes.
7. Fazer revisao critica do diff e do resultado executavel.
8. Corrigir observacoes em novos commits.
9. Fazer merge somente quando a fase estiver coerente.
10. Criar tag e release da versao estavel.
11. Excluir a branch concluida e iniciar a proxima a partir do `main`.

## 12. Revisao supervisionada por fase

Cada fase tera uma parada obrigatoria para revisao de Iago antes de ser
considerada concluida. O fluxo sera:

1. concluir a implementacao prevista para a fase;
2. executar testes e verificacoes;
3. preparar um resumo dos arquivos alterados, resultados e limitacoes;
4. apresentar o diff, os comandos executados e as decisoes tomadas;
5. aguardar a revisao e a aprovacao explicita;
6. corrigir os pontos solicitados em novos commits;
7. somente depois fazer merge, criar a tag e iniciar a proxima fase.

Nao faremos merge ou release baseado apenas em uma verificacao automatica. A
revisao supervisionada sera registrada em `docs/reviews/`, com um arquivo por
fase contendo:

- objetivo e criterios de aceite;
- o que foi implementado;
- evidencias de teste;
- decisoes tomadas;
- problemas conhecidos;
- pontos que exigem aprovacao;
- status `aprovada`, `aprovada com ressalvas` ou `precisa de correcao`.

Enquanto a revisao estiver pendente, a fase permanecera aberta e a proxima
branch nao sera iniciada.

## 13. Aplicacao ao nosso desafio

O fluxo concreto sera:

| Fase | Branch | Tag apos aprovacao | Evidencia principal |
| --- | --- | --- | --- |
| 0 | `codex/phase-0-bootstrap-contract` | `v0.1.0` | contrato, estrutura e auditoria |
| 1 | `codex/phase-1-eda-quality` | `v0.2.0` | notebook e relatorio de qualidade |
| 2 | `codex/phase-2-modeling-evaluation` | `v0.3.0` | comparacao e protocolo temporal |
| 3 | `codex/phase-3-training-artifact` | `v0.4.0` | artefato, manifest e previsoes |
| 4 | `codex/phase-4-api-docker-observability` | `v0.5.0` | API executavel e observabilidade |
| 5 | `codex/phase-5-lifecycle-stakeholders` | `v0.6.0` | deploy, ciclo de vida e model card |
| 6 | `codex/phase-6-optional-explainability` | `v0.7.0` | opcionais testados ou decisao de nao incluir |
| 7 | `codex/phase-7-final-review` | `v1.0.0` | entrega final revisada |

Esse processo torna a qualidade observavel sem criar movimentacao falsa. O
avaliador podera ver nao apenas o resultado final, mas tambem a evolucao, as
decisoes e a disciplina de engenharia usada para chegar nele.
