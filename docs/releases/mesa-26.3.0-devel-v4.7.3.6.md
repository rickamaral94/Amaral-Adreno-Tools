# Turnip Amaral 26.3.0-devel v4.7.3.6

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `e8e6cf93eac7dfc294088b986bb09c7eed12b409`
- Mesa HEAD: llvmpipe: test min and max with denormals in lp_test_arit
- Commit anterior: `8ea6e9dd417b99ef2e368436bfd567c81f23b0b2`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (14 arquivos)

- `src/compiler/nir/nir_intrinsics.py`
- `src/compiler/spirv/vtn_variables.c`
- `src/freedreno/ci/freedreno-a306-fails.txt`
- `src/freedreno/ci/freedreno-a306-flakes.txt`
- `src/freedreno/ci/freedreno-a530-fails.txt`
- `src/freedreno/ci/freedreno-a618-fails.txt`
- `src/freedreno/vulkan/tu_device.cc`
- `src/util/blend.h`
- `src/util/driconf.h`
- `src/util/meson.build`
- `src/util/os_misc.c`
- `src/util/u_pack_color.h`
- `src/vulkan/runtime/vk_debug_utils.c`
- `src/vulkan/runtime/vk_debug_utils.h`

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
