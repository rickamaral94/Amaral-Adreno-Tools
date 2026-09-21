# Turnip Amaral 26.3.0-devel v4.7.2.2

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `ad9f155a7fdc62a4718fd07d374787eb61fc59a3`
- Mesa HEAD: tu: Bump editorconfig line length
- Commit anterior: `590bf21d918c86908d96d1f4590ecd25b9657171`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (5 arquivos)

- `src/compiler/nir/nir.h`
- `src/compiler/nir/nir_lower_abort.c`
- `src/compiler/nir/nir_lower_tex.c`
- `src/freedreno/vulkan/.editorconfig`
- `src/vulkan/overlay-layer/overlay.cpp`

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
