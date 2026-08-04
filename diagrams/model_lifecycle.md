# Ciclo de vida do modelo

```mermaid
flowchart TD
    Labels["Novas vendas com preço observado"] --> Ingest["Ingestão imutável e versionada"]
    Ingest --> Contract{"Contrato e qualidade aprovados?"}
    Contract -- "Não" --> Quarantine["Quarentena e investigação"]
    Contract -- "Sim" --> Candidate["Treinar challenger reproduzível"]
    Candidate --> Temporal["Cinco janelas temporais completas"]
    Temporal --> Segments["Erro geral, faixa superior, tempo e CEP"]
    Segments --> Gates{"Gates de promoção aprovados?"}
    Gates -- "Não" --> Archive["Registrar rejeição e evidências"]
    Gates -- "Sim" --> Registry["Registrar artefato, hash, lineage e métricas"]
    Registry --> Staging["Staging, contrato e shadow"]
    Staging --> Human{"Aprovação humana?"}
    Human -- "Não" --> Archive
    Human -- "Sim" --> Canary["Canary controlado"]
    Canary --> Production["Alias champion"]
    Production --> Monitor["Monitoramento operacional, funcional e preditivo"]
    Monitor --> Incident{"Incidente ou degradação?"}
    Incident -- "Técnico" --> Rollback["Restaurar champion anterior"]
    Incident -- "Preditivo" --> Review["Revisar dados, segmentos e hipótese"]
    Incident -- "Não" --> Monitor
    Rollback --> Monitor
    Review --> Candidate
```

Nenhum drift isolado promove ou substitui um modelo. A automação prepara
evidências e bloqueia candidatos inválidos; a mudança do champion exige os
critérios documentados e aprovação humana.

O procedimento detalhado está em
[`docs/CONTINUOUS_LEARNING.md`](../docs/CONTINUOUS_LEARNING.md).
