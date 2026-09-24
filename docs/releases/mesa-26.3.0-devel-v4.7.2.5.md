# Turnip Amaral 26.3.0-devel v4.7.2.5

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `caf81bd201a84796003adcf00785a2fcda5191a3`
- Mesa HEAD: etnaviv: Clamp out-of-bounds texelFetch coordinates
- Commit anterior: `cdd0cc267728d474d13d30ebc5f345048d77f079`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (24 arquivos)

- `meson.build`
- `src/freedreno/ci/freedreno-a306-fails.txt`
- `src/freedreno/ci/freedreno-a306-skips.txt`
- `src/freedreno/ci/freedreno-a420-fails.txt`
- `src/freedreno/ci/freedreno-a420-skips.txt`
- `src/freedreno/ci/freedreno-a530-fails.txt`
- `src/freedreno/ci/freedreno-a530-skips.txt`
- `src/freedreno/ci/freedreno-a618-fails.txt`
- `src/freedreno/ci/freedreno-a6xx-skips.txt`
- `src/freedreno/common/freedreno_dev_info.h`
- `src/freedreno/common/freedreno_dev_info.py`
- `src/freedreno/common/freedreno_devices.py`
- `src/freedreno/ir3/ir3.h`
- `src/freedreno/ir3/ir3_alias.c`
- `src/freedreno/ir3/ir3_cf.c`
- `src/freedreno/ir3/ir3_compiler.h`
- `src/freedreno/ir3/ir3_compiler_nir.c`
- `src/freedreno/ir3/ir3_legalize.c`
- `src/freedreno/ir3/ir3_lower_parallelcopy.c`
- `src/freedreno/vulkan/tu_clear_blit.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- `src/freedreno/vulkan/tu_device.cc`
- `src/freedreno/vulkan/tu_device.h`
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
