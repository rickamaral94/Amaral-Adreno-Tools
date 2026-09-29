# Turnip Amaral 26.3.0-devel v4.7.3.3

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `c4eb475c289b71292696f176e852eb2deb52b9fc`
- Mesa HEAD: radv: switch radv_device_memory to use vk_device_memory
- Commit anterior: `90fae16e42e3f33043f1111b9a69a728241ba0b8`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (8 arquivos)

- `src/vulkan/anti-lag-layer/anti_lag_layer.h`
- `src/vulkan/runtime/vk_android.c`
- `src/vulkan/runtime/vk_android.h`
- `src/vulkan/runtime/vk_graphics_state.c`
- `src/vulkan/runtime/vk_image.c`
- `src/vulkan/runtime/vk_render_pass.c`
- `src/vulkan/runtime/vk_ycbcr_conversion.c`
- `src/vulkan/wsi/wsi_common.c`

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Atualizações exclusivas do Mesa upstream podem avançar para Latest depois dos
gates de compilação, aplicação dos patches, validação do pacote e
reprodutibilidade byte a byte. Correções comunitárias estritas de estabilidade
também podem ser promovidas após revisão de código e esses mesmos gates quando
já são distribuídas em outro driver e permanecem sem correção posterior
conhecida. Tuning, performance e workarounds continuam exigindo testes A/B.

Não há `TU_DEBUG=sysmem` forçado nos perfis Zelda. O autotuner continua livre
para escolher GMEM/SYSMEM, com a preferência por GMEM já validada na v4.5.
