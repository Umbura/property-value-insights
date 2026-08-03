# Revisão da Fase 4

Status: pendente de revisão supervisionada.

## Objetivo

Disponibilizar o modelo aprovado por uma API reproduzível, com contratos
explícitos de entrada e saída, isolamento em contêiner, verificação de saúde,
logs estruturados e métricas operacionais.

## Critérios de aceite

- o modelo é carregado e verificado uma vez durante a inicialização;
- predições individuais e em lote reproduzem a saída de inferência versionada;
- campos inválidos e lotes excessivos são rejeitados de forma determinística;
- saúde, metadados do modelo e métricas Prometheus estão disponíveis;
- logs permitem correlacionar requisições sem registrar os dados recebidos;
- a imagem executa sem privilégios e com sistema de arquivos raiz somente
  leitura;
- a CI verifica a qualidade do código e um contêiner em execução.

## Entregas

- fábrica da aplicação FastAPI e ciclo de inicialização;
- schemas Pydantic estritos para as 18 features de produção;
- `/health`, `/model-info`, `/predict`, `/predict/batch` e `/metrics`;
- identificadores de requisição e logs JSON da aplicação;
- registro Prometheus isolado e inferência em lote limitada;
- imagem Docker em múltiplos estágios e serviço Docker Compose;
- teste de fumaça do contêiner no GitHub Actions;
- contrato público da API e instruções de execução local.

## Evidências de verificação

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
docker compose config
docker build --tag property-value-insights:phase4 .
```

Resultados observados localmente:

- Ruff: aprovado;
- pytest: 49 testes aprovados;
- construção da imagem: aprovada;
- tamanho final da imagem: aproximadamente 163 MB;
- saúde do contêiner: `healthy`;
- usuário de execução: `app`;
- sistema de arquivos raiz somente leitura: verificado;
- saúde, metadados, predição e métricas: HTTP 200;
- primeiro exemplo futuro: 372.953,43, igual à saída em lote versionada.

## Decisões

- o artefato permanece incluído na imagem para uma avaliação determinística;
- um processo da aplicação é suficiente, pois o modelo é imutável e o desafio
  não define requisitos de tráfego de produção;
- o tamanho do lote é configurável e limitado para proteger memória e latência;
- os logs da aplicação são estruturados e não incluem os corpos das requisições;
- cada instância da aplicação possui seu próprio registro de métricas, mantendo
  testes isolados e evitando coletores duplicados.

## Limitações conhecidas

- autenticação, TLS, limites de tráfego e monitoramento persistente não integram
  a execução local;
- as métricas Prometheus são reiniciadas com o processo;
- `/health` combina vivacidade e prontidão neste serviço de processo único;
- topologia de deploy e aprendizado contínuo permanecem entregas da Fase 5;
- as limitações registradas no manifesto se aplicam a todo resultado da API.

## Pontos para revisão

- inspecionar o contrato público de entrada e saída;
- confirmar a exposição das métricas de avaliação e das limitações do modelo;
- confirmar o limite padrão de 100 imóveis por lote;
- executar o fluxo Docker e inspecionar `/docs`;
- aprovar ou solicitar correções antes do início da Fase 5.
