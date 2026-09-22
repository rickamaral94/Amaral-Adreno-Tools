# Turnip Amaral 26.3.0-devel v4.7.2.3

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `6ac7466d40be92bfec4fe3dfe21376a6af45a8e0`
- Mesa HEAD: vulkan/wsi: support allocating more memory for buffers
- Commit anterior: `ad9f155a7fdc62a4718fd07d374787eb61fc59a3`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (8 arquivos)

- `meson.build`
- `src/compiler/nir/nir_constant_expressions.py`
- `src/compiler/nir/nir_opt_varyings.c`
- `src/compiler/nir/nir_range_analysis.c`
- `src/freedreno/ir3/ir3.c`
- `src/freedreno/ir3/ir3_lower_parallelcopy.c`
- `src/vulkan/wsi/wsi_common.c`
- `src/vulkan/wsi/wsi_common_headless.c`

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
