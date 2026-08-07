# C1.5 — Auditoria de documentação, versionamento e governança

## Decisão

A documentação principal é consistente com o artefato e o runtime, mas a leitura
inicial não comunicava as evidências e limitações mais importantes. Esta review
corrige apresentação e rastreabilidade sem alterar API, modelo, dados ou artefato.

## Achados e correções

| Tema | Achado | Classificação | Tratamento nesta PR |
| --- | --- | --- | --- |
| README | resultados e riscos apareciam somente em documentos profundos | melhoria de apresentação | resultados, figura, versões, arquitetura e limites na abertura |
| Alto valor | Q4 agregado ocultava a degradação acima de US$ 1M/2M | correção documental | faixas e revisão humana no README, model card e resumo executivo |
| OOD | API aceita ZIP desconhecido, `(0,0)` e ano futuro sem warning | limitação de comunicação | documentada; implementação permanece na #64 |
| Versões | projeto, API, modelo, artefato e metadata histórica podiam ser confundidos | correção documental | matriz explícita e notas para defesa |
| Demografia | relatório histórico ainda usa “modelo promovido” | risco de interpretação | banner reforçado; modelo físico identificado como serving atual |
| Dados | dicionário existente cobria apenas parte dos campos | lacuna documental | `docs/DATA_DICTIONARY.md` criado sem inventar definições ausentes |
| Reviews antigas | snapshots de fases pareciam status atual | registro histórico | índice e banners; caminhos preservados |
| Raiz | quatro documentos históricos competem com o README | limpeza futura | classificados para mudança posterior, sem mover nesta review |

## Identidade verificada

| Componente | Valor |
| --- | --- |
| Projeto em `pyproject.toml` | `1.0.0` |
| Pacote em `__init__.py` | `1.0.0` |
| API | `0.5.0-rc1` |
| Modelo servido | `0.4.0-rc1` |
| Schema do manifesto | `1.0` |
| Artefato | `90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439` |
| Metadata do pacote no build do artefato | `0.1.0.dev0` |

O último valor é histórico e permanece no manifesto imutável. Não existe
divergência de serving: a API usa a identidade do modelo e o pacote instalado
usa a release `1.0.0`.

## Acesso público

- verificações HTTP sem cabeçalho de autorização: `3`;
- todas acessíveis: `True`;
- metadata pública declarou `private=false`: `True`.

Evidência: `evidence/c1-5/public-access.json`. A verificação prova acesso público
no momento da execução do GitHub Actions; disponibilidade futura continua sujeita
à plataforma e às configurações do repositório.

## Links

- arquivos Markdown verificados: `49`;
- links relativos verificados: `67`;
- links relativos quebrados: `0`;
- links externos catalogados: `40`.

A auditoria confirma existência de caminhos relativos, não conteúdo ou
disponibilidade permanente de todos os sites externos.

## Hierarquia documental aprovada

1. artefato e `model_manifest.json` para identidade técnica imutável;
2. `API_CONTRACT.md`, `MODEL_CARD.md` e `DATA_DICTIONARY.md` para contratos atuais;
3. reviews C1 para evidências pré-entrega;
4. relatórios gerados para métricas específicas;
5. `phase-*.md` e `model_comparison.md` como snapshots históricos.

## Política de revisão humana

- uso comum: segunda opinião quantitativa;
- faixas observadas acima de US$ 1 milhão: evidência para revisão humana;
- faixa observada acima de US$ 2 milhões: evidência para avaliação especializada;
- o preço real não existe na inferência; o gatilho da #64 deverá combinar
  previsão, intervalo, raridade e cobertura;
- OOD, ZIP desconhecido, coordenadas fora da região e casos raros: revisão
  obrigatória quando os sinais forem implementados;
- nenhuma trava deve cortar artificialmente o preço previsto.

## Decisões para defesa oral

As respostas consolidadas estão em [`../DEFENSE_NOTES.md`](../DEFENSE_NOTES.md).
Elas cobrem seleção do modelo físico, validação cruzada, período diagnóstico,
degradação na cauda, versões independentes, anomalias e limites de produção.

## Pontos encaminhados

- #64: sinais estruturados de cobertura, OOD, risco e revisão humana;
- #65: fonte primária para anomalias e sensibilidade por chave `id`;
- #62: challengers futuros para a cauda superior;
- lapidação final: mover documentos históricos da raiz, remover residuais,
  atualizar links e preparar a release/imagem final.

## Escopo preservado

Nenhum CSV bruto, código de runtime, schema público, modelo, Joblib, manifesto,
hash ou previsão foi alterado.
