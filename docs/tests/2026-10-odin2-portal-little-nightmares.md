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
| Readback Lab 5.7.11.1 | Heartbeat de submissão e contadores cumulativos visíveis mesmo com poucas cópias. | **Aguardando captura física.** Duas builds idênticas por variante na CI. | Continuar diagnóstico; sem release. |

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

Nenhum teste CTS/VVL ou inspeção visual sistemática acompanhou estas capturas.
Não há 1% low verdadeiro nem temperatura interna da GPU. Timestamps GPU não
incluem o blit de apresentação; p99 do histograma não equivale a 1% low. Não
interpretar KGSL busy repetido como capacidade ociosa, nem somar waits de
threads diferentes. As capturas ainda não justificam Latest, ganho de FPS ou
ajuste global de GMEM/SYSMEM.

Decisão atual: **2 — atualizar controle/evidências**. Próximo teste: carregar
5.7.11.1 Standard somente neste jogo, aquecer e capturar a mesma rota; analisar
`AMARAL_RB_V2` antes de propor mudança de driver. Para uma afirmação de ganho,
repetir 5.7.8.1 contra uma candidata com cena marcada, cinco rodadas balanceadas,
clocks/cache/temperatura controlados e verificação visual.
