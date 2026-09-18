# Turnip Amaral 26.3.0-devel v4.7.1.1

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `f1b6a86974b06ddec7adbf6afcfc8df15a93ff49`
- Mesa HEAD: dri: allocate MSAA color buffers for drisw image loader buffers
- Commit anterior: `972675794391a60f6f6f20a3a39d1cb0aecd7af4`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (13 arquivos)

- `include/vulkan/vulkan_core.h`
- `src/compiler/nir/nir_builder.h`
- `src/compiler/nir/nir_builtin_builder.c`
- `src/compiler/nir/nir_lower_input_attachments.c`
- `src/compiler/nir/nir_lower_subgroups.c`
- `src/compiler/nir/nir_lower_tex.c`
- `src/freedreno/ci/freedreno-a702-fails.txt`
- `src/freedreno/ir3/ir3_a6xx.c`
- `src/freedreno/ir3/ir3_nir.c`
- `src/freedreno/vulkan/tu_descriptor_set.cc`
- `src/freedreno/vulkan/tu_descriptor_set.h`
- `src/freedreno/vulkan/tu_device.cc`
- `src/vulkan/registry/vk.xml`

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Atualizações exclusivas do Mesa upstream podem avançar para Latest depois dos
gates de compilação, aplicação dos patches, validação do pacote e
reprodutibilidade byte a byte. Mudanças próprias do Amaral permanecem como
pré-release até aprovação em testes A/B.

Não há `TU_DEBUG=sysmem` forçado nos perfis Zelda. O autotuner continua livre
para escolher GMEM/SYSMEM, com a preferência por GMEM já validada na v4.5.
