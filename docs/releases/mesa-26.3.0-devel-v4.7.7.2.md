# Turnip Amaral 26.3.0-devel v4.7.7.2

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `378a5dc61b982b7d36e744cf44407e6b55dc98b7`
- Mesa HEAD: etnaviv: blt: Re-validate tile status on full color clears
- Commit anterior: `07ea97900e735afff9bfd59805983912f72f7dfd`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (17 arquivos)

- `meson.build`
- `src/compiler/nir/meson.build`
- `src/compiler/nir/nir.h`
- `src/compiler/nir/nir_constant_expressions.py`
- `src/compiler/nir/nir_lower_alu_width.c`
- `src/compiler/nir/nir_opcodes.py`
- `src/compiler/nir/nir_opt_algebraic.py`
- `src/compiler/nir/nir_opt_uadd_carry.c`
- `src/freedreno/ir3/ir3.c`
- `src/freedreno/ir3/ir3.h`
- `src/freedreno/ir3/ir3_lower_copies_validate.c`
- `src/freedreno/ir3/ir3_lower_parallelcopy.c`
- `src/freedreno/ir3/ir3_ra.h`
- `src/freedreno/ir3/meson.build`
- `src/vulkan/runtime/vk_android.c`
- `src/vulkan/runtime/vk_image.c`
- `src/vulkan/runtime/vk_image.h`

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
