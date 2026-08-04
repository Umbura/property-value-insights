# Histórico de versões

Todas as alterações relevantes deste projeto são registradas neste arquivo.

## [1.0.0] - 2026-08-04

Primeira versão estável integrada da solução.

### Incluído

- auditoria e contrato dos dados fornecidos;
- análise exploratória reproduzível;
- avaliação temporal, calibração e diagnósticos de equidade vertical;
- modelo versionado com manifesto, hashes e 100 previsões futuras;
- API FastAPI com inferência individual e em lote;
- contêiner Docker sem privilégios e compatível com sistema de arquivos
  somente leitura;
- logs estruturados, identificadores de requisição e métricas Prometheus;
- documentação de arquitetura, aprendizado contínuo e comunicação com
  stakeholders;
- análises offline de incerteza temporal e explicabilidade SHAP;
- ambiente bloqueado com `uv`, auditoria de dependências e verificação
  automatizada da entrega.

### Governança

- o modelo aprovado utiliza somente características físicas e espaciais;
- a alternativa demográfica permanece documentada, mas não integra o serving;
- a licença MIT cobre o código original e não relicencia os dados fornecidos;
- limitações, uso pretendido e riscos estão documentados no model card.

## [0.1.0] - 2026-08-02

Versão inicial com a estrutura do projeto, o contrato dos dados fornecidos,
validações de domínio e o primeiro workflow de qualidade.
