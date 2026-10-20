# Reavaliação da candidata com diagnósticos reais

## Decisão e estado

**2 — ATUALIZAR CONTROLE/EVIDÊNCIAS.** A candidata 5.7.8.1 já existe para avaliação;
os diagnósticos recebidos não justificam outro binário nem promoção para Latest.
Não demonstram defeito novo do Turnip com correção reproduzível. A ausência de
defeito demonstrado também não certifica o driver.

O workflow iniciado anteriormente publicou a candidata em 20/10/2026 às 02:44 UTC,
antes da conclusão desta reavaliação. A partir desta revisão, push executa checks,
mas publicação de candidata exige execução manual. O workflow independente de
build continua disponível. A Latest 4.7.7.2 permanece inalterada.

- [Candidata 5.7.8.1](https://github.com/rickamaral94/Amaral-Adreno-Tools/releases/tag/mesa-27.0.0-devel-v5.7.8.1)
- [CI das quatro compilações e publicação](https://github.com/rickamaral94/Amaral-Adreno-Tools/actions/runs/39360005734)
- Fonte do pacote: `2d9355bcbd7c64592a4de29c98cb1761e064b2e8`.
- Mesa: `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`.
- Fingerprint: `cc52dbd9ae58c1e39089a1277d5e9f39aca9c4fa7d9402e1301456f88d44fce6`.

| Variante | SHA-256 ZIP | SHA-256 ELF |
|---|---|---|
| Standard | `d8a42802cf21a5f1c15bd48239b112be60d6dcd5e8ccf1eecbeab57bbdcc1f03` | `e554cff65c6fdfcb2b4d30275c8a21b6ea3289d01fc4e5e4a3fbbcc1559933e9` |
| OneUI | `23a4bc99a57bc4f50d160d66efd253ce5da8207b8aa0133b9776f9103cd58cca` | `7410ad511d8b6b3bc448b60156a1f38a35ef8a14de1260d4711dfa0741c2ec3f` |

As duas variantes passaram duas compilações independentes e comparação byte a
byte de ZIP/ELF/catálogo na execução acima. CTS, VVL, hardware e A/B da candidata
continuam pendentes. Esta revisão de documentação/ferramentas não troca os assets.

## O que há de novo por família

| Família | Mudança tecnicamente aplicável | Limite da afirmação |
|---|---|---|
| A6xx | Correções upstream de invalidação bindless e caminhos compartilhados Turnip/IR3: push constants, offsets de constantes e ordem do lowering | Correção de código; nenhum ganho de FPS medido em A6xx |
| A7xx, incluindo A740/A750 | Mesmos mecanismos compartilhados; invalidação conserva o caminho anterior a A8xx; escolha GMEM/SYSMEM segue o autotuner upstream | Há motivo para testar compatibilidade; não foi demonstrado melhor uso de recursos no Odin |
| A8xx | Invalidação bindless respeita a distinção de geração; correções compartilhadas de compilador | Não há novo tuning Amaral A8xx nesta revisão |
| A810/A812/A825 | Perfis externos existentes continuam isolados por chip ID | Suporte experimental preservado, não validação nova |
| A840 | Perfis upstream distintos de dois/três slices já estavam na base | Não apresentar suporte já existente como novidade desta candidata |

Referências de implementação:
[bindless](https://gitlab.freedesktop.org/mesa/mesa/-/commit/c88b6ebd3835dfcf0c5764fc7444e6dd2765c08e),
[push constants](https://gitlab.freedesktop.org/mesa/mesa/-/commit/5cf8c6b2fee69fb14ca848c4efce1e38110abebc),
[ordem NIR](https://gitlab.freedesktop.org/mesa/mesa/-/commit/8f491f606a1e5b8d492151c2b1e4d702e264f0bf),
[offset IR3](https://gitlab.freedesktop.org/mesa/mesa/-/commit/2755d64a645bb84926d5c7954c9947e5aea66356).

KGSL MR 44838 já estava incorporada; esta candidata não introduz outra correção
KGSL. OneUI mantém apenas o ajuste UBWC FD740/KGSL documentado; Odin usa Standard.
Não se adicionou política de clocks, PWR_MAX, desativação de atomics ou preferência
global por GMEM/SYSMEM. Os logs A740 não autorizam essas mudanças em outras GPUs.

## Integridade e identidade dos quatro ZIPs

Entradas numeradas conforme os anexos do usuário. Análise offline reproduzível:

```sh
python3 tools/summarize_eden_diagnostics.py \
  /caminho/1-eden-diagnostics-20261018-190237-1964.zip \
  /caminho/2-eden-diagnostics-20261018-204032-7062.zip \
  /caminho/3-eden-diagnostics-20261018-185740-4897.zip \
  /caminho/4-eden-diagnostics-20261018-143900-6562.zip
```

[Resumo estruturado](../../evidence/diagnostics/2026-10-18-eden-summary.json)
preserva hashes dos arquivos de entrada e métricas selecionadas. Logs brutos,
caminhos do aparelho e identificadores de processo não foram publicados.
Manifestos dos anexos 1/2/3 conferem integralmente com o payload; anexo 4 usa schema
1 e não possui manifesto. Hash do arquivo comprova identidade, não autenticidade
da medição nem integridade de uma captura anterior à exportação.

Todos são Little Nightmares no Odin2 Portal/A740, Android 13, FIFO 1920×1080.
Os anexos 1/2/3 carregaram exatamente o ELF Standard da Latest 4.7.7.2,
`2f54e22a9b1868a8c0e2d2af2944fc9689af1c9e9839e2754a030bd8c8fd1a99`.
O anexo 4 registra o mesmo Mesa, mas não fornece hash do ELF carregado.
Nenhum contém execução da candidata 5.7.8.1, A6xx ou A8xx.

| Anexo | Eden | Duração s | FPS médio observado | GPU p50/p99 ms | Clock GPU MHz médio |
|---|---|---:|---:|---:|---:|
| 1 | cd8a63f196 | 122,36 | 34,28 | 19,25 / 36,5 | 401 |
| 2 | 812551b8cb | 458,95 | 45,49 | 12,5 / 30,25 | 680 |
| 3 | cd8a63f196 | 284,87 | 37,47 | 19,5 / 38,25 | 417 |
| 4 | d95a60f58d | 312,40 | 41,23 | indisponível | indisponível |

São observações de cenas/capturas distintas, não um ranking ou A/B de driver.
As capturas 1/3 compartilham o mesmo processo, portanto não são réplicas
independentes. Cache restaurado varia entre 266, 292 e 345 pipelines. Não há
marcadores de cena, ordem balanceada ou cinco repetições controladas.
Percentis GPU são limites de buckets de 0,25 ms; p99 não é o inverso de 1% low.

## O código do Eden explica confundidores importantes

A comparação dos settings 3→2 muda `force_max_clock` de false para true.
O [diff dos dois APKs](https://github.com/rickamaral94/Logs_eden/compare/cd8a63f196...812551b8cb)
contém duas alterações relevantes, inspecionadas no código:

1. `812551b8cb`: habilita clocks máximos por default Android e espaça a renovação
   do pedido turbo em 50 ms, soltando-o após 100 ms sem submits. O salto de clock
   observado é coerente com essa política do emulador. Não é melhoria do Turnip
   nem justificativa para forçar clocks dentro do driver universal.
2. `9dbc077bfc`: marca descontinuidades de captura/pause/resume e rejeita intervalos
   iniciados antes delas. O intervalo de 13.290,801 ms do anexo 1 atravessava a pausa
   de exportação entre capturas, conforme investigação registrada nessa mudança.
   Não o classificar como hang de GPU. Mantemos o valor original na evidência;
   não recalculamos uma distribuição artificial removendo apenas o pior valor.

Também divide `cache_sync` em `texture_download`, `buffer_download` e
`buffer_write_sync`. A ausência de `cache_sync` no anexo 2 não comprova que uma
otimização de driver eliminou readbacks; a instrumentação e os cenários mudaram.

## Hipóteses sustentadas e o que ainda falta

- Nas três capturas com feedback, houve 82 hits em 82 relatórios válidos de
  criação de pipeline. Isso não significa custo zero: picos de criação ficam
  aproximadamente em 33–45 ms. Pipeline binary segue P1 de pesquisa, mas não é
  solução demonstrada para as maiores travadas dessas sessões.
- Das 24 janelas com intervalos longos, 23 não registraram pipeline cache misses.
  A comparação é por janela de aproximadamente 2 s, não por frame. Procurar
  timeline do emulador, filesystem/serviços, pause/resume e submissão antes de
  culpar shader compilation. Não declarar nenhuma dessas causas comprovada.
- A740 a 401–417 MHz apresenta GPU p50 próximo de 19,5 ms. Investigar margem para
  16,7 ms com resolução/cena constantes; clocks e trabalho por frame precisam ser
  controlados. Em 680 MHz, p99 GPU ainda ultrapassa 16,7 ms.
- Capturas 1/3 registram 30,68/71,56 s de `cache_sync` no total. Waits de threads
  diferentes se sobrepõem: não somar guest_sync e cache_sync para inferir tempo
  GPU ou caminho crítico. A próxima captura deve usar causas discriminadas.
- Temperatura de bateria máxima 28–31 °C e thermal status 0 não provam igualdade
  de temperatura do chip, ausência de limitações do governor ou gate térmico.
- Zero falhas de criação/tradução e encerramento por usuário nas capturas não
  comprovam pixels corretos nem compatibilidade universal. VVL não foi executado.
- Timestamps cobrem quase todos os submits medidos, mas excluem o present blit;
  não são latência até a tela. KGSL busy abrange todos os processos.

## Fontes Cemu e limite de acesso à evidência

Foram consultados código/documentação e relatos públicos do
[Cemu Fork Amaral](https://github.com/rickamaral94/Cemu-Fork-Amaral).
Não foram localizados ZIPs/logs brutos de gameplay na árvore consultada ou nos
comentários examinados. Não declarar nova análise de logs Cemu que não recebemos.

- [PR 26](https://github.com/rickamaral94/Cemu-Fork-Amaral/pull/26) documenta
  timestamps GPU, cobertura e causas de espera vinculados à sessão. Usar esses
  campos na comparação futura, separando submits, readback, CPU e apresentação.
- [PR 3](https://github.com/rickamaral94/Cemu-Fork-Amaral/pull/3) registra fallback
  para FIFO quando Immediate não está disponível. Não inferir present_wait2
  funcional no Android apenas porque o WSI genérico Mesa implementa a extensão.
- [Issue 14](https://github.com/rickamaral94/Cemu-Fork-Amaral/issues/14) e
  [matriz de testes](https://github.com/rickamaral94/Cemu-Fork-Amaral/blob/main/docs/android/TEST_MATRIX.md)
  descrevem OSPanic de XCX e investigação PPC/memória. Isso não fundamenta
  workaround Turnip. Wind Waker HD e Tekken possuem relatos históricos de sessões
  normais; não certificam o novo driver.

## Retirada de patches: risco e isolamento

0004/0005/0006 continuam disponíveis como pesquisa. A retirada de extensões de
profundidade, tuning GCM/subalocação e perfis Zelda da candidata não é um ganho
medido. Os logs de Little Nightmares não qualificam nem refutam os perfis Zelda.
Remover três grupos enquanto se muda Mesa limita atribuição de qualquer diferença.

Manter 5.7.8.1 como experimento composto e a Latest como rollback. Se houver
regressão, produzir controles em branches separadas: mesmo Mesa/toolchain com
patchset anterior, depois retirar um grupo por vez. Não reutilizar o tag ou
sobrescrever assets publicados. Não reativar extensões por flag antes de validar
API/backend/CTS, mesmo para recuperar desempenho aparente de um aplicativo.

## Próximos gates por prioridade

| Prioridade | Trabalho concreto | Critério |
|---|---|---|
| P0 | A/B Latest × candidata no mesmo APK Eden e cena, Standard no Odin | Cinco rodadas balanceadas AB/BA; política de clocks idêntica, aquecimento/gate térmico, cache frio/quente separados, hashes carregados, pixels e crash/device lost |
| P0 | Descontinuidades e hitches periódicos do Eden | Captura com marcadores, intervalos válidos, correlação por monotonic clock; não alterar barreiras sem reprodução |
| P1 | A6xx/A750/A825/A830 | Smoke/CTS dirigido e jogos em cada GPU; A825 experimental; nenhum resultado A740 generalizado |
| P1 | Pipeline binary | API/keys/import-export/CTS antes de exposure; identificar consumidor real, comparar custo de cache hit e criação |
| P1 | KGSL/A8xx upstream | Remover dependência externa somente após equivalência do código e teste por chip; não copiar registradores entre famílias |
| P2 | Readback e presentation | Usar waits discriminados, timestamps/cobertura, modo efetivo e GPU/CPU timelines Eden/Cemu |
| P2/P3 | QCOM image processing / tile / wait queues | Pesquisa de instruções/backend e testes, sem exposure especulativa |

A candidata melhora caminhos concretos de correção upstream e permite medir
defaults conservadores. Os desejos de mais desempenho em A6xx, melhor eficiência
em A7xx e maior compatibilidade A8xx continuam sendo objetivos de validação.
Não há base nesta evidência para anunciar os três como resultados alcançados.
