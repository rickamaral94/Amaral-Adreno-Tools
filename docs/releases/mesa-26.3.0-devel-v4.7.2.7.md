# Turnip Amaral 26.3.0-devel v4.7.2.7

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `82d4f86a0a1e9f76b2de4fa77c6c8e6acaf06aa9`
- Mesa HEAD: jay/nir_lower_fsign: use u2u instead of i2i for downcasts
- Commit anterior: `434a909bae5c738d48201d7a75a185dfe23832b8`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (8 arquivos)

- `meson.build`
- `src/compiler/nir/nir_builder_opcodes_h.py`
- `src/compiler/nir/nir_lower_int64.c`
- `src/compiler/nir/nir_opcodes_c.py`
- `src/compiler/nir/nir_opt_algebraic.py`
- `src/compiler/nir/nir_validate.c`
- `src/freedreno/ir3/ir3.h`
- `src/freedreno/ir3/ir3_compiler_nir.c`

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
