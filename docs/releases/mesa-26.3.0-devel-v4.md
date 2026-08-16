# Turnip Amaral 26.3.0-devel v4

A v4 atualiza a base completa do Mesa para
`f0bcf54488119f97502da9f4cca87a214e502a3e`, 356 commits após a base da v3.
Ela é publicada primeiro como pré-release para validação comunitária; a v3
permanece como release estável/latest e fallback.

## Drivers

- `turnip_amaral_26.3.0-devel_v4.zip`: variante padrão.
- `turnip_amaral_26.3.0-devel_v4_oneUI.zip`: mesma base, com ajuste UBWC
  separado para as entradas KGSL da FD740.

## O que mudou

- atualização cumulativa do Mesa/Freedreno/Turnip até o commit fixado;
- manutenção do perfil experimental A825 da v3, isolado no `chip_id` KGSL
  `0x44030000`;
- correção do escopo do patch OneUI: `TP_UBWC_FLAG_HINT` agora alcança somente
  `0x43050a01` e `0xffff43050a01`, sem alterar `GPUId(740)` ou Adreno X1-85;
- duas compilações independentes por variante, com comparação byte a byte do
  ZIP e do ELF.

## Política desta pré-release

A atualização não incorpora `force_sysmem`, `force_gmem`, `TU_DEBUG` global,
spoof de GPU/Vulkan, `-O3`, ThinLTO, perfis IR3 artificiais ou hacks específicos
de aplicativo sem evidência reproduzível. Compatibilidade gráfica, estabilidade
e frametimes consistentes têm precedência sobre FPS máximo.

## Validação solicitada

Compare a v4 com a v3 nas mesmas condições e em pelo menos três rodadas. Registre
GPU, dispositivo, Android, emulador e jogo, verificando:

- corrupção visual, texturas, depth, MSAA, pós-processamento e blits;
- crash, GPU hang, device lost e regressões de inicialização;
- média e percentis de frametime, stutter e FPS;
- temperatura, throttling e consumo quando houver medição confiável.

Comece pela variante padrão. Use a OneUI somente quando houver sintomas
compatíveis com divergência UBWC no firmware do sistema.
