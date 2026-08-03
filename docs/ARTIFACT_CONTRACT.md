# Contrato do artefato de modelo

## Finalidade

O artefato da Fase 3 encapsula o pré-processamento e o estimador aprovados em
um único arquivo carregável. O treinamento e a inferência usam a mesma lista
ordenada de features, evitando diferenças entre notebook, execução em lote e
futura API.

## Arquivos versionados

| Arquivo | Finalidade |
| --- | --- |
| `artifacts/property_value_model.joblib` | pipeline treinado e calibrado |
| `artifacts/model_manifest.json` | proveniência, configuração, hashes e métricas |
| `reports/future_predictions.csv` | previsões dos 100 exemplos futuros |
| `reports/training_summary.md` | resumo legível do treinamento final |

## Modelo empacotado

- algoritmo: `HistGradientBoostingRegressor`;
- features: características físicas, espaciais e `zipcode` categórico;
- alvo: `log1p(price)`;
- calibração: smearing nos 10% finais do treino cronológico;
- versão candidata: `0.4.0-rc1`;
- dados demográficos: excluídos do artefato principal.

O modelo com demografia apresentou MAE média 0,71% menor nas cinco janelas
após a limpeza temporal. O modelo físico foi mantido porque apresentou melhor
MAE e R² no período diagnóstico e evita adicionar proxies socioeconômicas por
um ganho marginal.

## Integridade temporal

O treinamento final exclui 18 registros nos quais `yr_built` ou
`yr_renovated` ocorre depois da data da venda. Os arquivos brutos permanecem
inalterados; a exclusão é reproduzida em código e registrada no manifesto.

## Manifesto

O manifesto registra:

- nome, versão, algoritmo, features e calibração;
- commit usado para gerar o artefato;
- versões do Python e das bibliotecas principais;
- hashes SHA-256 do artefato, dos dados e das previsões;
- quantidade de linhas recebidas, excluídas e utilizadas;
- métricas temporais e limitações conhecidas.

Os hashes dos CSVs normalizam terminações de linha para `LF`. Assim, o mesmo
conteúdo produz o mesmo identificador no Windows e no Linux. O hash binário do
artefato não recebe normalização.

## Geração

Na raiz do repositório:

```powershell
.\.venv\Scripts\python.exe -m property_value_insights.training --project-root .
```

O comando valida os dados, reproduz a avaliação, treina com todo o histórico
válido, salva o modelo, recarrega o arquivo e confirma que as previsões não
mudaram após a persistência.

## Inferência em lote

O arquivo público contém:

- `row_id`: posição do exemplo no arquivo fornecido, iniciada em 1;
- `predicted_price`: preço previsto, arredondado para centavos;
- `model_version`: versão do artefato responsável pela previsão.

Os exemplos futuros não possuem preço observado. Portanto, as previsões não
devem ser apresentadas como métricas de acurácia.

## Segurança e compatibilidade

Arquivos Joblib utilizam serialização baseada em pickle e somente devem ser
carregados de uma origem confiável. O manifesto é obrigatório no carregamento.
O loader verifica o SHA-256 antes de desserializar e, depois, confronta versão
do schema, nome, versão do modelo e ordem das features com o bundle. Qualquer
divergência interrompe o carregamento. A compatibilidade de bibliotecas está
registrada no manifesto e é limitada pelas dependências do projeto.

Um teste de integração executa o treinamento completo em diretório temporário
contendo somente o histórico e os exemplos futuros. Esse teste cobre o comando,
a geração dos quatro arquivos, a recarga do artefato e a independência do CSV
demográfico.
