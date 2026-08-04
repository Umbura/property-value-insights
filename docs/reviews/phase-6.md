# Revisão da Fase 6

Status: em desenvolvimento.

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

## Pontos para revisão

- avaliar cobertura geral e por quartil;
- conferir largura e utilidade prática dos intervalos;
- revisar baseline e estabilidade das explicações SHAP;
- confirmar isolamento das dependências opcionais;
- decidir pela aprovação ou remoção de cada opcional separadamente.

