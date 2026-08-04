# Revisão da Fase 5

Status: pendente de revisão supervisionada.

## Objetivo

Completar os entregáveis de estratégia de deploy, aprendizado contínuo,
governança do modelo e comunicação com stakeholders sem apresentar
infraestrutura proposta como implementada.

## Critérios de aceite

- arquitetura separa estado executável e topologia de produção;
- diagramas cobrem inferência, CI/CD, telemetria, registro e rollback;
- aprendizado contínuo define dados, gatilhos, gates, promoção e incidente;
- model card registra uso, métricas, segmentos, riscos e limitações;
- resumo executivo utiliza somente resultados do modelo físico aprovado;
- números apresentados podem ser reproduzidos por código;
- referências metodológicas e operacionais são verificáveis;
- documentação evita impacto financeiro, SLO ou infraestrutura não observados.

## Entregas

- `diagrams/production_architecture.md`;
- `diagrams/model_lifecycle.md`;
- `docs/CONTINUOUS_LEARNING.md`;
- `docs/MODEL_CARD.md`;
- `docs/REFERENCES.md`;
- `reports/stakeholder_summary.md`;
- gráfico diagnóstico do modelo físico aprovado;
- tabela de desempenho por quartil;
- JSON de métricas e comparação com baseline;
- comando reproduzível `generate-stakeholder-report`;
- teste de consistência entre diagnóstico e manifesto.

## Evidências de verificação

```powershell
.\.venv\Scripts\python.exe -m property_value_insights.stakeholder_reporting --project-root .
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
docker compose config
docker build --tag property-value-insights:phase5 .
```

Resultados observados localmente:

- Ruff: aprovado;
- pytest: 60 testes aprovados;
- dependências: consistentes;
- links e artefatos locais da fase: verificados;
- regeneração de gráfico, CSV e JSON: reproduzível e sem diff;
- construção da imagem: aprovada;
- módulo de reporting importável no runtime sem instalar Matplotlib;
- configuração do Docker Compose: válida.

## Decisões

- o modelo continua físico; demografia permanece apenas como experimento;
- a imagem imutável mantém API e modelo como unidade de implantação;
- registro gerenciado, cloud, TLS e armazenamento são arquitetura proposta;
- drift isolado não aciona promoção nem rollback preditivo;
- thresholds dependentes de tráfego e rótulos serão calibrados com dados reais;
- toda promoção de champion exige aprovação humana;
- o relatório executivo usa um diagnóstico novo do artefato aprovado, pois a
  figura anterior correspondia ao campeão demográfico experimental.

## Limitações conhecidas

- nenhum recurso de produção foi provisionado;
- não há tráfego real, teste de carga nem latência de rótulo observada;
- monitoramento preditivo está desenhado, mas depende de novas vendas;
- o período diagnóstico já foi consultado durante o desenvolvimento;
- o dataset não permite medir equidade entre atributos protegidos;
- explicabilidade opcional permanece reservada à Fase 6.

## Pontos para revisão

- confirmar que a arquitetura é suficientemente clara para discussão técnica;
- revisar gates, responsabilidades e rollback;
- avaliar transparência e linguagem do model card;
- conferir o resumo executivo e a ênfase no quartil superior;
- decidir se a Fase 6 deve implementar explicabilidade ou registrar a decisão de
  não incluir.
