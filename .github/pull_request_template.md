## Classificação

**Natureza principal:** <!-- Review | Bug | Improvement | Maintenance | Documentation | Release -->

**Áreas afetadas:** <!-- API | Model | Data | Testing | Docker | CI | Documentation | Governance | Repository | Automation -->

**Ciclo ou milestone:** <!-- Ciclo 1 | Ciclo 2 | Ciclo 3 | manutenção fora dos ciclos | outro aprovado -->

**Prioridade:** <!-- High | Medium | Low -->

<!--
Use uma natureza principal. Copilot, integrações com IA, templates, automações,
CI e governança do repositório devem ser classificados como Maintenance quando
não alterarem funcionalmente o produto.
-->

## Contexto

<!-- Explique por que esta alteração é necessária e de onde surgiu a demanda. -->

## Problema atual ou evidência

<!--
Descreva o comportamento, limitação, decisão ou evidência que fundamenta a PR.
Para Bug, inclua reprodução. Para Review, registre o que foi observado sem
transformar recomendações em requisitos. Para Improvement, cite a aprovação.
-->

## Objetivo

<!-- Descreva o resultado esperado de forma objetiva e verificável. -->

## Implementação

<!-- Liste as mudanças realizadas e como elas atendem ao objetivo. -->

## Decisões técnicas

<!-- Registre escolhas relevantes, alternativas consideradas e justificativas. -->

## Arquivos e componentes alterados

<!-- Indique arquivos, módulos, endpoints, documentos, artefatos ou automações afetados. -->

## Backward compatibility

<!-- Marque exatamente uma opção. -->

- [ ] A alteração preserva endpoints, schemas, campos, versões e comportamentos documentados.
- [ ] A alteração incompatível foi explicitamente aprovada, versionada e possui plano de migração e rollback.
- [ ] Não se aplica porque a mudança não afeta contratos ou consumidores existentes.

<!-- Descreva impactos sobre API, modelo, artefatos, dados, automações e consumidores. -->

## Validações executadas

<!--
Registre somente verificações realmente executadas. Adicione ou remova linhas
conforme o escopo. Não declare como aprovado algo que não foi executado com
sucesso.
-->

| Verificação | Comando ou evidência | Resultado |
|---|---|---|
| <!-- teste, inspeção ou check --> | <!-- comando, link ou evidência --> | <!-- aprovado, falhou ou observação --> |

## Validações não executadas

<!--
Liste comandos, cenários ou ambientes relevantes que não foram verificados e o
motivo. Remova esta instrução somente depois de registrar a situação real.
-->

## Resultados observados

<!-- Registre métricas, respostas, artefatos ou comportamentos verificáveis quando aplicável. -->

## Riscos e limitações

<!-- Declare riscos residuais, limitações conhecidas e condições não cobertas. -->

## Fora do escopo

<!-- Liste itens relacionados que foram intencionalmente deixados de fora. -->

## Revisão solicitada

<!-- Indique os pontos que merecem atenção especial durante a revisão. -->

## Issue relacionada

<!--
Use `Closes #<número>` somente quando esta PR concluir integralmente a Issue.
Quando houver relação sem fechamento automático, use `Relacionado a #<número>`.
Inclua todas as Issues necessárias para rastrear origem e dependências.
-->

## Checklist final

- [ ] A natureza, as áreas, o ciclo e a prioridade foram registrados.
- [ ] O escopo da Issue foi respeitado e não houve expansão silenciosa.
- [ ] Reviews registram evidências sem implementar automaticamente achados fora do escopo.
- [ ] Manutenções de IA, templates e automações foram classificadas como Maintenance quando aplicável.
- [ ] A opção correta de backward compatibility foi marcada e justificada.
- [ ] Testes de regressão foram adicionados para bugs quando necessários.
- [ ] Validações executadas e não executadas foram registradas separadamente.
- [ ] A documentação corresponde ao comportamento implementado.
- [ ] Artefatos, manifests, versões e hashes permanecem consistentes quando aplicável.
- [ ] Nenhum segredo, caminho local, log sensível ou arquivo temporário foi incluído.
- [ ] Arquivos textuais foram preservados em UTF-8, sem corrupção de caracteres.
- [ ] `Closes` é usado somente para Issues integralmente concluídas por esta PR.
