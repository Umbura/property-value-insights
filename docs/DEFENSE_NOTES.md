# Notas para defesa técnica

## Qual modelo está servido?

O serving usa `property_value_hist_gradient_boosting_physical 0.4.0-rc1`, com 18 features
físicas e espaciais. O experimento demográfico teve resultado estatístico
competitivo, mas não foi aprovado para serving por ganho marginal, risco de
proxy socioeconômica e ausência de fonte/vintage documentados.

## Por que existem quatro versões/identidades?

- projeto/pacote: `1.0.0`;
- contrato HTTP/OpenAPI: `0.5.0-rc1`;
- modelo treinado: `0.4.0-rc1`;
- artefato: schema `1.0` e SHA-256 `90ffbab62970c805b7fd65a5488fa727026bdc59b81d56726318374cdce8c439`.

O valor `0.1.0.dev0` dentro de `manifest.runtime` registra
o pacote no momento em que o artefato imutável foi criado. Não é a versão atual
da distribuição nem razão para regenerar o modelo apenas por documentação.

## A avaliação possui validação cruzada?

Sim. A seleção usa cinco janelas temporais expansivas no desenvolvimento. O
período mais recente possui 4.640 vendas e é diagnóstico previamente inspecionado,
não holdout final intocado.

## A degradação em imóveis caros é bug?

Não foi encontrado bug funcional. Métricas, artefato e previsões foram
reproduzidos, sem valores negativos ou não finitos. A degradação é progressiva e
compatível com baixa densidade na cauda e regressão ao centro. Ela é comum em
regressão desbalanceada, mas materialmente importante para o negócio.

## Como o uso é controlado?

Não se aplica teto ao preço. Na avaliação, as faixas acima de US$ 1 milhão e
US$ 2 milhões demonstram quando revisão humana e avaliação especializada são
necessárias. Como o preço real é desconhecido na inferência, o gatilho de runtime
não pode usar apenas a previsão pontual; previsão, intervalo, raridade e cobertura
serão combinados na Issue #64. ZIP desconhecido, coordenadas fora da região, ano
futuro e combinações raras também devem receber sinais de cobertura/OOD.

## Por que o registro com 33 quartos não foi corrigido?

É uma anomalia estatística de alta confiança, mas os arquivos não provam se o
valor correto seria 3 ou outro número. Corrigir silenciosamente alteraria o dado
e exigiria nova avaliação e artefato. A verificação externa ficou na Issue #65.

## O projeto está em produção?

Não. Existe runtime containerizado, CI, logs e métricas, mas a arquitetura de
registro, staging, canary e rollback é recomendada. A imagem final de submissão
será consolidada depois da Review #39 e da lapidação final.
