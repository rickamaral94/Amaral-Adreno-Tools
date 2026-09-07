# Turnip Amaral 26.3.0-devel v4.5.1.2

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `b63bb362308a17316245671f51e2fb5c6637702d`
- Mesa HEAD: pan/bi: Fix binary shader dumps
- Commit anterior: `86158b8c7467cadcd24f8a8cf02aa3bc748f7e3f`
- Vulkan headers: `1.4.359`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (3 arquivos)

- `meson.build`
- `src/compiler/nir/nir_serialize.c`
- `src/vulkan/runtime/vk_image.c`

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
