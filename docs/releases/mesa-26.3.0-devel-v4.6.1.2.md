# Turnip Amaral 26.3.0-devel v4.6.1.2

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `8355a57771bc94b7dbea6b496805a40751056508`
- Mesa HEAD: radv/ci: update list of expected failures for HAWAII/POLARIS10
- Commit anterior: `cab1821ef75f20338424b8d2c66cdae87b345454`
- Vulkan headers: `1.4.362`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (14 arquivos)

- `src/freedreno/ci/deqp-freedreno-a530-piglit.toml`
- `src/freedreno/ci/freedreno-a306-fails.txt`
- `src/freedreno/ci/freedreno-a530-fails.txt`
- `src/freedreno/ci/freedreno-a530-flakes.txt`
- `src/freedreno/ci/freedreno-a530-skips.txt`
- `src/freedreno/common/freedreno_dev_info.py`
- `src/freedreno/common/freedreno_devices.py`
- `src/freedreno/ir3/ir3.c`
- `src/freedreno/ir3/ir3.h`
- `src/freedreno/ir3/ir3_compiler.c`
- `src/freedreno/ir3/ir3_compiler_nir.c`
- `src/freedreno/ir3/ir3_nir_lower_io_offsets.c`
- `src/freedreno/ir3/ir3_ra.c`
- `src/freedreno/vulkan/tu_query_pool.cc`

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
