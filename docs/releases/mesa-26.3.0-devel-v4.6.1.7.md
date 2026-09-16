# Turnip Amaral 26.3.0-devel v4.6.1.7

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `d0bf12daec6e351dbe0d6349124ee178eb0ac913`
- Mesa HEAD: radv: program PA_SC_HISZ_CONTROL.ROUND also for noop FS
- Commit anterior: `0d355084f070f8de919b9885a1d26296cd1897f6`
- Vulkan headers: `1.4.362`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (9 arquivos)

- `src/compiler/nir/nir_from_ssa.c`
- `src/compiler/spirv/vtn_alu.c`
- `src/compiler/spirv/vtn_variables.c`
- `src/freedreno/vulkan/00-turnip-defaults.conf`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- `src/freedreno/vulkan/tu_drirc_gen.py`
- `src/freedreno/vulkan/tu_pipeline.cc`
- `src/util/register_allocate.c`
- `src/util/register_allocate.h`

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
