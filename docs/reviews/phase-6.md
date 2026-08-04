# Revisão da Fase 6

Status: pronta para revisão supervisionada.

## Objetivo

Adicionar análise de incerteza e explicabilidade ao modelo físico sem modificar
o artefato aprovado ou o contrato da API.

## Critérios de aceite

- calibração do intervalo não consulta o período diagnóstico;
- cobertura e largura são apresentadas juntas, inclusive por faixa de preço;
- limitações temporais impedem promessa de cobertura em produção;
- SHAP explica somente as features do modelo físico;
- explicações locais reconciliam baseline, contribuições e previsão;
- associação não é descrita como causalidade;
- dependências opcionais permanecem fora da imagem de serving;
- artefatos são reproduzíveis e testados;
- revisão supervisionada ocorre antes da Fase 7.

## Fora do escopo

- alteração da API ou do modelo promovido;
- garantia formal de cobertura sob mudança temporal;
- adaptador generativo ou provedor externo;
- publicação, merge final ou release.

## Entregas

- protocolo de avaliação e referências metodológicas;
- intervalo empírico calibrado em cinco janelas temporais;
- diagnóstico geral e por quartil com cobertura e largura;
- explicações SHAP globais nas 100 linhas futuras;
- explicações locais para previsões baixa, mediana e alta;
- CSVs, JSONs e figuras reproduzíveis;
- relatório opcional e atualização do model card;
- comandos `property_value_insights.uncertainty` e
  `property_value_insights.explainability`;
- testes de integridade, aditividade, rastreabilidade e isolamento do runtime.

## Evidências de verificação

```powershell
.\.venv\Scripts\python.exe -m property_value_insights.uncertainty --project-root .
.\.venv\Scripts\python.exe -m property_value_insights.explainability --project-root .
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
docker compose config --quiet
```

Resultados observados localmente:

- Ruff: aprovado;
- pytest: 75 testes aprovados;
- dependências: consistentes;
- configuração do Docker Compose: válida;
- regeneração integral de CSVs, JSONs e PNGs: reproduzível e sem diff;
- figuras inspecionadas sem sobreposição de texto;
- aditividade SHAP: erro máximo de `1,40e-9`;
- cobertura diagnóstica: 89,40% para nível nominal de 90%;
- dependências de explicabilidade: ausentes do runtime de serving;
- build da imagem não repetido nesta revisão porque o Docker Desktop estava
  desligado;
- GitHub Actions: jobs `quality` e `container` aprovados;
- CI remoto: imagem construída, API saudável e endpoints públicos verificados.

## Decisões

- o intervalo é diagnóstico e não oferece garantia conformal em produção;
- cobertura e largura permanecem inseparáveis na comunicação;
- a menor cobertura em Q1 e Q4 é apresentada sem suavização;
- SHAP explica comportamento em relação ao baseline, não causalidade;
- o baseline usa 50 linhas históricas determinísticas;
- explicabilidade não cria endpoint nem altera a resposta da API;
- o adaptador generativo permanece excluído;
- publicação, merge e release permanecem sob responsabilidade do autor.

## Pontos para revisão

- avaliar cobertura geral e por quartil;
- conferir largura e utilidade prática dos intervalos;
- revisar baseline e estabilidade das explicações SHAP;
- confirmar isolamento das dependências opcionais;
- decidir pela aprovação ou remoção de cada opcional separadamente.
