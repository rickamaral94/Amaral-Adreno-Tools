# Turnip Amaral 26.3.0-devel v4.7.2.6

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `434a909bae5c738d48201d7a75a185dfe23832b8`
- Mesa HEAD: anv: choose correct pipeline mode for Xe2 query result copy
- Commit anterior: `caf81bd201a84796003adcf00785a2fcda5191a3`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (11 arquivos)

- `meson.build`
- `src/freedreno/common/freedreno_devices.py`
- `src/freedreno/ir3/ir3_compiler.c`
- `src/util/format/u_format_fxt1.c`
- `src/util/format/u_format_other.c`
- `src/util/meson.build`
- `src/util/rust/bitview.rs`
- `src/util/rust/lib.rs`
- `src/util/rust/meson.build`
- `src/util/texcompress_astc.cpp`
- `src/util/u_pack_color.h`

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
