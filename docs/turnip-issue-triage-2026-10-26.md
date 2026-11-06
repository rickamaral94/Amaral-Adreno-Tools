# Triagem de issues Turnip externos — 26/10/2026

Esta triagem identifica testes e hipóteses para o patchset da candidata 5.7.14.1
(Mesa `69f1f21`). Os relatos abaixo são de terceiros. Nenhum foi reproduzido
com o ZIP/ELF Amaral; CTS, VVL e hardware para esses casos estão **not-run**.
Uma issue externa não demonstra que a falha existe em nossa build nem que um
patch comunitário a corrige. A prioridade segue a política de
`docs/EVIDENCE-POLICY.md` e a separação por chip/caminho.

| Prioridade de investigação | Relato e evidência disponível | Hipóteses concorrentes | Próximo teste decisivo / decisão atual |
| --- | --- | --- | --- |
| P0, A830 hang | [DroidDeck #1472](https://github.com/Droid-Deck/DroidDeck/issues/1472): Cyberpunk 2077 trava ao descer do telhado para a rua, com espera de fence de ~10 s por quadro, em quatro combinações Proton/Turnip; logs anexos. O autor relata que `TU_DEBUG=flushall` **ou** `syncdraw` evita o hang; `sysmem` ficou ligado em todas as tentativas. A issue nomeia WN-Turnip-1.19-b e Mesa v27.0.0-20261024-r2-A8xx, mas não seus commits Mesa. | Regressão após [9931034 / !40550](https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/40550), que retirou o `flushall` A8xx forçado e passou a esperar explicitamente; draw indireto grande sem [!44352](https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/44352), mesclada em 22/10; bug em vkd3d/barreira incorreta; ou timing mascarado pelos flags. O Mesa `69f1f21` já força `TU_CMD_FLAG_WAIT_FOR_ME` para `TU_STAGE_BV_CP` (`tu_cmd_buffer.cc:6287–6303`) e divide draws indiretos grandes, portanto os flags isolados não provam qual ramo falhou. | **Primeiro:** obter commit/fingerprint Mesa dos dois drivers e conferir se contêm !44352 e 9931034; data ou rótulo v27 não prova ancestralidade. Depois repetir cena com binário/ELF identificado, submit/fence, dump de comandos, barreira Vulkan e producer/consumer. Variar um controle por vez (`sysmem` on/off; indirect; flags), com retorno à base. Só testar wait em lab se trace mostrar lacuna; jamais globalmente. |
| P0, A725 device lost | [MrPurple #38](https://github.com/MrPurple666/purple-turnip/issues/38): T30-toasted perde o dispositivo de forma intermitente no ARMSX2; T29-toasted teria ficado estável por mais de 3 h com aparelho/app/configuração iguais. Há erro `VK_ERROR_DEVICE_LOST`, mas sem fault KGSL ou diff isolado. Os ZIPs oficiais foram identificados e os ELFs inspecionados abaixo; o repositório só contém README e tags T29/T30 no mesmo commit, sem janela de fonte. | Regressão entre patchsets T29/T30, variação térmica/firmware ou bug do emulador dependente de timing. | Obter o ref Mesa e os patches de ambos os binários, então comparar com nossa base. Repetir A/B/retorno à base sob mesma carga com fault KGSL se surgir suspeito aplicável ao `69f1f21`; nenhum patch agora. |
| P0/P1, A830 device lost | [DroidDeck #1009](https://github.com/Droid-Deck/DroidDeck/issues/1009): UE5/vkd3d cai 10/10 após New Game, `VK_ERROR_DEVICE_LOST`, contador KGSL `gpufault_procs` aumenta; logs anexos. Outros drivers/runtimes não eliminaram, `TU_DEBUG=sysmem` ficou constante. | Falha de acesso/sincronização em Turnip; tradução vkd3d, workload UE5 ou ambiente Linux/Proton. | Antes de atribuir ao driver, obter endereço/tipo de fault KGSL, breadcrumbs do comando e A/B com `sysmem` desligado na mesma pilha. Comparar build Amaral apenas se o caminho Android Vulkan for equivalente. |
| P1, A750/A830 corrupção | [MrPurple #31](https://github.com/MrPurple666/purple-turnip/issues/31): corredor de BotW 1.6.0 corrompe apenas com câmera em movimento em renderizadores Yuzu; Kenji-NX, BotW 1.0 e driver Qualcomm são controles limpos. Relator resume diferenças no submit 2 em blits/CCU/f16 e oferece RD dump; outro usuário relata versão antiga limpa no A740, porém com crashes. O ref comunitário citado (`whitebelyash/mesa-unified` `7fdde2f8`) data de 30/06; isso não demonstra qual patchset entrou no binário. | Interação query/LRZ/Z-mode; cópia/blit f16 ou sequência de frames do emulador. A correção upstream [64245a2](https://gitlab.freedesktop.org/mesa/mesa/-/commit/64245a20b78) preserva NaNs em cópia MSAA f16, mas só é relevante se o trace passar nesse ramo. | **Primeiro:** obter commit/patchset do binário, RD dumps bruto e cena reproduzível. Comparar query, barrier, blit f16 e LRZ em submit correto/corrompido; testar 64245a2 isolado apenas se ocorrer cópia MSAA f16. O Mesa da candidata já contém guardas `occlusion_query_may_be_running` em `tu_query_pool.cc`, `tu_cmd_buffer.cc` e `tu_pipeline.cc`; sua existência não valida a hipótese. |
| P1, A840 imagem errada | [Registro Amaral A840](tests/2026-10-sm8850-a840-marvel-ultimate-alliance-3.md) e [issue Amaral #12](https://github.com/rickamaral94/Amaral-Adreno-Tools/issues/12), A825: artefatos descritos em aparelhos diferentes, sem controle comum/ELF exato na issue #12. [MrPurple #35](https://github.com/MrPurple666/purple-turnip/issues/35) também relata MUA3 com artefatos no A740/T30; o controle `sysmem,nolrz` sugerido não ajudou, segundo o autor. | Importação de imagem/Gralloc, UBWC, estado Gen8, escala ou app/emulador; mesmo jogo em outro chip/build não prova causa comum. | Prosseguir com etapa 0 A840 aprovada em `T-a840-pixelation`: mesma cena MUA3 em Standard Nearest/Bilinear e Qualcomm Nearest, mais outro jogo como controle global, hash completo do ELF. Não inferir causa comum com A825/A740 antes de reprodução e matriz por chip. |
| P2, A710 cobertura | [MrPurple #8](https://github.com/MrPurple666/purple-turnip/issues/8): Citron/Winlator com pixels azuis/amarelos ou tela preta em A710; há uma segunda pessoa com sintomas similares, mas sem hashes, trace ou controles. | Suporte/perfil A710, app/emulador, importação de imagem. | Solicitar versão e ELF exatos, cena, log, controle Qualcomm e comparação de formato/layout; manter A710 separado do A840 e do A825. |
| Fora do driver Android atual | [lfdevs #99](https://github.com/lfdevs/mesa-for-android-container/issues/99): A740 em KGSL/Termux:X11, corrupção com `FD_MESA_DEBUG=sysmem` em glmark2; [PR #96](https://github.com/lfdevs/mesa-for-android-container/pull/96) mesclado, junto de correção Termux:X11, elimina o sintoma relatado. Há custo de 48–61% em microbenchmark reportado; forçar `enable_tp_ubwc_flag_hint=1` falhou e causou flashing em outro workload. | Caminho de present fence OpenGL/Termux versus nosso Vulkan Android; correção conjunta impede atribuir efeito ao PR #96 isoladamente. | Não portar #96 nem ativar flag UBWC por este relato. Só reabrir se captura no caminho Vulkan Android mostrar a mesma ausência de espera e medição A/B do custo. |
| Configuração do frontend, sem patch Turnip | [DroidDeck #1293](https://github.com/Droid-Deck/DroidDeck/issues/1293): HITMAN A830 falha quando ambiente força feature level 12_2/DXR apesar de `maxRayRecursionDepth=0`; `nodxr` + 12_1 permite iniciar. | Exposição incorreta criada pelo frontend, não defeito demonstrado da capability Turnip. | Usar como controle de triagem: verificar flags efetivas da camada de tradução antes de alterar capabilities do driver. |
| Capacidade já exposta na árvore Amaral | [MrPurple #39](https://github.com/MrPurple666/purple-turnip/issues/39) atribui um crash no FFVII Rebirth/A740 à ausência de `shaderInt16`/`shaderFloat16`. No nosso Mesa `69f1f21`, `tu_device.cc:491,533` define ambas como `true`. | Build/wrapper carregado difere, outra feature ou formato falta, ou a mensagem de vkd3d não identifica o `VkResult` causal. `shaderFloat64` e recursos de armazenamento 8-bit estão desligados nesta árvore, mas o issue não os aponta; são alternativas não priorizadas. | Capturar `vkGetPhysicalDeviceFeatures2` do ELF realmente carregado, SPIR-V/PSO e `VkResult`; não habilitar flags por inferência do issue. |

Também foram vistos [ilhan #34](https://github.com/ilhan-athn7/freedreno_turnip-CI/issues/34),
que alega correções A740 de câmera/GMEM e pede testadores, e repositórios de
binários como StevenMXZ e Banners. Não apareceu nessa rodada um issue com
reprodução e código suficientes para importar uma dessas alterações. A fonte
primária de qualquer fix continua sendo Mesa; um issue de empacotamento,
Termux/X11 ou frontend não equivale ao caminho do nosso driver Android.

Proveniência verificada de #38: os ZIPs das releases oficiais
[T29](https://github.com/MrPurple666/purple-turnip/releases/tag/vturnip_mrpurple_T29-toasted.adpkg)
e [T30](https://github.com/MrPurple666/purple-turnip/releases/tag/vturnip_mrpurple_T30-toasted.adpkg)
têm SHA-256 `606d5c1d7fa3e54467972d1813682e914565fe6ef8ff4000e320e6ed1a261d05`
e `f65b2d3353fd4aa7190bb5426b94468e99ffea7a58a830bc0c4651db89353227`,
respectivamente, iguais aos digests publicados pelo GitHub. Os ELFs
`vulkan.purple.so` têm SHA-256
`0a6032a0c99fd0cbbbdef9ff87adb89ba0bf9c634b4b56b1eb21a2d2b02f4b45`
(T29) e `1d80dfa019659b008e4669311db5b1e4a02af59ff1d5458a98e2f5fe18ed013b`
(T30). As strings embutidas registram `26.2.0-devel (git-3858275f00)` e
`26.3.0-devel (git-62ac221a33)`; nenhum desses dois hashes resolve no
espelho Mesa consultado. A diferença de versão delimita os artefatos, mas não
revela quais mudanças de fonte causaram o relato.

Um suspeito upstream a investigar para #38, **sem atribuição causal**: em
13/07, `e1b839d` passou a usar `load/store_global_offset` no rebaixamento de
endereços SSBO do Turnip; em 17/09, `16f569e` corrigiu a interpretação
assinada de offsets constantes grandes nesse caminho. A candidata `69f1f21`
contém o uso dos novos intrinsics em `tu_shader.cc` e `uint32_t`/
`nir_src_as_uint` em `ir3_a6xx.c`, isto é, já contém a correção. O cálculo
assinado original é de 05/05 (`c784af5`), anterior à release T29; a mudança
de julho pode ter aumentado a exposição, mas não há shader, endereço da fault
KGSL ou fonte dos forks T29/T30 que ligue esse defeito ao ARMSX2. A issue
também não identifica jogo/cena para um ensaio físico comparável. Primeiro
obter esses dados; um teste negativo em A740 não falsificaria a A725.

Próxima decisão: cruzar esta matriz com a revisão independente do Claude em
`T-a8xx-strategy`, escolher um único caso P0 reproduzível e registrar previsão,
contraexemplo, hash do artefato e teste mínimo antes de construir lab. A
candidata #27 e Latest permanecem sem mudança por esta triagem.
