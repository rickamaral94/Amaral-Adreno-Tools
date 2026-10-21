# Little Nightmares no Odin 2 Portal — outubro de 2026

Hardware: AYN Odin 2 Portal, QCS8550/Snapdragon 8 Gen 2, Adreno 740 (A7xx),
Android 13, KGSL, ARM64. Workload: Little Nightmares `01002FC00412C000` no Eden,
resolução 1× e swapchain 1920×1080 nas capturas documentadas. Estas são
**observações**; não houve sequência balanceada de cinco rodadas na mesma cena.
O [JSON de evidência](../../evidence/hardware-tests/2026-10-odin2-portal-little-nightmares.json)
contém SHA-256 disponíveis, commit Eden, identidade do binário e métricas
selecionadas sem publicar logs brutos.

## Drivers, hipótese e resultado

| Driver Standard | Proposta testada | Resultado no A740 | Decisão |
|---|---|---|---|
| Latest 4.7.7.2 | Controle estável anterior. | Executou o jogo; 34,28–45,49 FPS em capturas com APK/clocks/cenas distintos. | Controle histórico. |
| Candidate 5.7.8.1 | Mesa novo com correções bindless, push constants e IR3; patchset conservador, sem tuning específico do jogo. | 44,27 e 44,89 FPS; uma captura registrou 20.666 esperas `texture_download`. | Manter para comparação, sem ganho certificado. |
| PROFILED Lab 5.7.9.1 | Trocar default do autotuner BANDWIDTH por PROFILED somente no A740/Eden. | 37,77 e 40,80 FPS observados em cargas distintas; melhora não demonstrada. | Não integrar o tuning. |
| Readback Lab 5.7.10.1 | Contar cópias de imagem, fallback por linha e r2d/r3d em lotes de 512 por thread. | 41,28 FPS; 3 esperas `texture_download` em 27 ms; nenhum contador `AMARAL_RB_V1` apareceu. | Instrumentação inconclusiva. |
| Readback Lab 5.7.11.1 | Heartbeat de submissão e contadores cumulativos visíveis mesmo com poucas cópias. | 44,01 FPS em 817,61 s; o ELF correto carregou, mas nenhuma linha `AMARAL_RB_V2` apareceu. | Investigar filtro/log; sem release. |
| Readback Lab 5.7.12.1 | Registrar IDs internos e resultado do filtro antes do gate A740 nas filas A7xx, com log Android direto. | 45 heartbeats revelaram `chip=0x43050a01`, `gpu=6760`, app/engine corretos e `scope=0`. O filtro rejeitou este FD740. | Corrigir somente o gate deste chip; sem conclusão de FPS. |
| Readback Lab 5.7.13.1 | Aceitar os chip IDs FD740 conhecidos no gate diagnóstico mesmo com `gpu_id=6760`; preservar filtro Eden e demais caminhos. | Build Standard reproduzível; teste no Odin pendente. | Lab isolada; verificar `scope=1` e incrementos de cópia antes de qualquer decisão sobre otimização. |

Todos os labs usam o mesmo Mesa `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`
da candidata 5.7.8.1. A Latest usa
`378a5dc61b982b7d36e744cf44407e6b55dc98b7`. Os hashes do ELF carregado
estão no JSON. A OneUI não foi testada no Odin. A8xx e A6xx não receberam teste
físico nesta série; nenhuma conclusão A740 foi estendida a essas famílias.

## Capturas

| ID da captura Eden | Driver | Duração | FPS médio | GPU p50 / p90 / p99 ms | Clock médio MHz | Integridade |
|---|---|---:|---:|---|---:|---|
| `20261018-190237-1964` | Latest 4.7.7.2 | 122,36 s | 34,28 | 19,25 / 29,5 / 36,5 | 401 | Manifesto verificado |
| `20261018-204032-7062` | Latest 4.7.7.2 | 458,95 s | 45,49 | 12,5 / 24,25 / 30,25 | 680 | Manifesto verificado |
| `20261018-185740-4897` | Latest 4.7.7.2 | 284,87 s | 37,47 | 19,5 / 27,75 / 38,25 | 417 | Manifesto verificado |
| `20261018-143900-6562` | Mesa informado como Latest; ELF sem hash | 312,40 s | 41,23 | indisponível | indisponível | Sem manifesto |
| `20261020-143555-9611` | Candidate 5.7.8.1 | 162,75 s | 44,27 | 15,75 / 24,75 / 39 | 680 | Manifesto verificado |
| `20261020-152817-1977` | PROFILED Lab 5.7.9.1 | 297,91 s | 37,77 | 15,25 / 27,5 / 35 | 680 | Manifesto verificado |
| `20261020-224224-7212` | PROFILED Lab 5.7.9.1 | 690,03 s | 40,80 | 14,5 / 27,5 / 29,75 | indisponível | Transcrito da revisão anterior¹ |
| `20261020-230715-1086` | Candidate 5.7.8.1 | 784,25 s | 44,89 | 14,75 / 23 / 28,75 | indisponível | Transcrito da revisão anterior¹ |
| `20261021-003041-0627` | Readback Lab 5.7.10.1 | 667,16 s | 41,28 | 14 / 25,5 / 26,5 | 679 | Manifesto verificado |
| `20261021-144443-7278` | Readback Lab 5.7.11.1 | 817,61 s | 44,01 | 14,25 / 25,75 / 27,75 | 680 | Manifesto verificado |
| `20261021-162833-1341` | Readback Lab 5.7.12.1 | 453,98 s | 41,06 | 13,75 / 26,25 / 29,75 | 680 | Manifesto verificado |

¹ O arquivo bruto dessas duas capturas não está disponível no ambiente atual;
identidade e valores foram transcritos da análise anterior. O registro deixa o
hash do ZIP vazio em vez de inventá-lo. Se o arquivo for reenviado, preencher
SHA-256 e revalidar. O quarto anexo de 18/10 não identifica o ELF por hash.

## O que foi aprendido

A comparação Latest 4.7.7.2 entre 18/10 muda também APK e política de clock do
Eden. O APK mais novo manteve 680 MHz; os outros registros ficaram em 401–417 MHz.
Isso não mede ganho do driver. O intervalo isolado de 13,29 s na primeira captura
cruzou pausa/exportação do diagnóstico; não é evidência de hang GPU. Veja a
[auditoria dos anexos](../audits/2026-10-20-diagnostics.md).

Na comparação 5.7.8.1 × PROFILED Lab, a captura inicial da Lab tinha cerca de
65% mais draws por quadro, cache diferente e outra trajetória. A diferença de
FPS não mede o efeito causal do autotuner. A captura posterior também não trouxe
AB/BA. O perfil permanece fora do driver universal. Veja o
[protocolo e análise da Lab](https://github.com/rickamaral94/Amaral-Adreno-Tools/pull/25).

A Standard 5.7.8.1 registrou 20.666 esperas `texture_download` somando cerca de
212 s na captura 230715. Na Readback Lab 5.7.10.1, apenas três esperas somaram
27 ms, mas o jogo ficou em 41,28 FPS. Isso mostra que as esperas rotuladas
`texture_download` não explicam, sozinhas, os 40–45 FPS observados. Os tempos de
threads se sobrepõem e o fence pode esperar trabalho anterior. As cenas diferem;
não é prova de otimização. O contador V1 não confirmou se houve cópia por linha.
A [Lab V2](https://github.com/rickamaral94/Amaral-Adreno-Tools/pull/26) foi
preparada para medir isso no próximo diagnóstico.

## Captura V2 de 21/10 às 14:44 UTC

O ZIP `20261021-144443-7278` passou na verificação dos hashes do manifesto;
SHA-256 do arquivo: `b1295d18f1ddd1b150d1e59657c2bd9d3d36af400b4e4cdc76949b04bf18b723`.
O ELF carregado tem SHA-256
`dd8472af1125fc9295fc1b433eedfbe94694cd0232f171600e538312e56e8f47`,
exatamente o Standard 5.7.11.1 da build reproduzível. Eden commit
`6b592ecbeaac9631ffef1cb5735931ed1083189b` e hash efetivo de settings
`1337a7f3ed7ba6f34966a9a3f4a1dbdaaa09f2f8b80f3c8bd56007b8057b5406`.
O cache restaurou 372 pipelines e não houve novas criações; a captura terminou
por ação do usuário, sem falhas de criação/tradução registradas.

O jogo registrou 44,01 FPS, GPU p50/p90/p99 de 14,25/25,75/27,75 ms, 591,0
draws e 116,9 passes por quadro. Foram 240 esperas `texture_download`, somando
3,29 s; `guest_sync` somou 433,76 s em outra thread, sem adição entre threads.
O coletor capturou 27 linhas, informou zero descartes e **não registrou nenhum
`AMARAL_RB_V2`**. O Eden reportou 155.736 chamadas de submit durante a captura;
elas não provam quais callbacks Turnip foram executados. A ausência do heartbeat
impede interpretar os contadores: o gate de ID, o callback efetivo ou o destino
do log ainda precisam ser isolados. Não declarar ausência de cópias nem bug de
readback a partir disso.

O relógio GPU reportou 680 MHz nas 407 amostras, bateria até 31 °C e thermal
status 0. Não há temperatura interna do chip nem cena marcada. A diferença
entre 44,01 FPS desta Lab e 41,28/44,89 FPS de outras capturas não é efeito
causal demonstrado: a carga e a instrumentação diferem. Nenhuma melhoria de
desempenho foi qualificada.

## Captura V3 de 21/10 às 16:28 UTC

O ZIP `20261021-162833-1341` passou no manifesto; SHA-256
`980c156cbcc264ebcc86be30b4c6757bbc4c88de91f404c5288808e46c42c4bb`.
O ELF carregado `b3aa76d16b409bded16c8c6d083b12b006f0c71c8933d0d89cc7bef5edc447cc`
confirma a Standard Lab 5.7.12.1. Mesmo commit Eden e hash efetivo de settings
das capturas recentes. Em 453,98 s, houve 41,06 FPS, GPU p50/p90/p99 de
13,75/26,25/29,75 ms, 557,4 draws/quadro e 20 pipelines novos. Uma espera
`texture_download` somou 7,4 ms. Nenhum desses valores forma A/B com as outras
cenas ou permite atribuir o FPS à mudança diagnóstica.

O logcat registrou **45 linhas `AMARAL_RB_V3`**, sem descarte. Todas mostraram
`path=graphics`, `gpu=6760`, `chip=43050a01`, `app_match=1`, `engine_match=1`
e `scope=0`. O perfil Mesa FD740 reconhece esse chip ID KGSL, mas a função
`amaral_readback_gpu` da Lab aceitava esse chip apenas se o campo `gpu_id`
fosse 0 ou 740. O valor recebido foi 6760. Isso explica por que V1/V2 não
contaram cópias nem emitiram heartbeat V2. Os campos `regions=0` são resultado
do filtro rejeitado; **não provam ausência de cópias de imagem**. A próxima Lab
deve aceitar somente os chip IDs FD740 já conhecidos independentemente do
campo legado `gpu_id`, mantendo o caso `gpu_id=740, chip_id=0` separado. A
[Lab 5.7.13.1](https://github.com/rickamaral94/Amaral-Adreno-Tools/pull/26)
faz essa correção apenas no filtro diagnóstico. O CI compilou a Standard duas
vezes e confirmou ZIP e ELF idênticos; SHA-256 do ELF:
`eb5d61626888b414d0a2a003a68440a961685f0739fbfeaf1b6d46e9ee988975`.
Ainda não existe captura de hardware V4.

Nenhum teste CTS/VVL ou inspeção visual sistemática acompanhou estas capturas.
Não há 1% low verdadeiro nem temperatura interna da GPU. Timestamps GPU não
incluem o blit de apresentação; p99 do histograma não equivale a 1% low. Não
interpretar KGSL busy repetido como capacidade ociosa, nem somar waits de
threads diferentes. As capturas ainda não justificam Latest, ganho de FPS ou
ajuste global de GMEM/SYSMEM.

Decisão atual: **2 — atualizar controle/evidências**. Próximo teste: instalar a
Standard Lab 5.7.13.1 no Odin e verificar se `scope=1` e os contadores
de cópia aumentam. Só então investigar alinhamento ou tempo GPU. Para uma afirmação de ganho,
repetir 5.7.8.1 contra uma candidata com cena marcada, cinco rodadas balanceadas,
clocks/cache/temperatura controlados e verificação visual.
