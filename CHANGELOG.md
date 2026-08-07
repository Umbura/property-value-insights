# Histórico de versões

Todas as alterações relevantes deste projeto são registradas neste arquivo.

## [Unreleased]

## [1.0.1] - 2026-08-07

Versão final de entrega após a revisão pré-submissão.

### Documentação e governança

- consolidação das reviews de API, modelo, dados, documentação e operação;
- resultados principais, arquitetura e limitações trazidos para a abertura do README;
- dicionário canônico e política explícita de revisão humana;
- documentos históricos organizados em `docs/process/` e `docs/archive/`;
- remoção de arquivos `.gitkeep` residuais em diretórios já preenchidos.

### Release e container

- versão integrada promovida para `1.0.1`, sem alterar API ou modelo;
- workflow de publicação da imagem no GitHub Container Registry;
- tags semânticas `1.0.1`, `1.0`, `1` e `latest`;
- labels OCI, digest de registry e teste da imagem publicada por digest;
- documentação de pull e execução da imagem final.

### Preservado

- modelo físico `0.4.0-rc1`;
- contrato da API `0.5.0-rc1`;
- Joblib, manifesto, hashes, dados brutos e 100 previsões futuras.

## [1.0.0] - 2026-08-04

Primeira versão estável integrada da solução.

### Incluído

- auditoria e contrato dos dados fornecidos;
- análise exploratória reproduzível;
- avaliação temporal, calibração e diagnósticos de equidade vertical;
- modelo versionado com manifesto, hashes e 100 previsões futuras;
- API FastAPI com inferência individual e em lote;
- contêiner Docker sem privilégios e compatível com sistema de arquivos somente leitura;
- logs estruturados, identificadores de requisição e métricas Prometheus;
- documentação de arquitetura, aprendizado contínuo e comunicação com stakeholders;
- análises offline de incerteza temporal e explicabilidade SHAP;
- ambiente bloqueado com `uv`, auditoria de dependências e verificação automatizada.

### Governança

- o modelo aprovado utiliza somente características físicas e espaciais;
- a alternativa demográfica permanece documentada, mas não integra o serving;
- a licença MIT cobre o código original e não relicencia os dados fornecidos;
- limitações, uso pretendido e riscos estão documentados no model card.

## [0.1.0] - 2026-08-02

Versão inicial com a estrutura do projeto, o contrato dos dados fornecidos,
validações de domínio e o primeiro workflow de qualidade.
