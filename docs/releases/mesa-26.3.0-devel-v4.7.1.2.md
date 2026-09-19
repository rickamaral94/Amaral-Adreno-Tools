# Turnip Amaral 26.3.0-devel v4.7.1.2

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `590bf21d918c86908d96d1f4590ecd25b9657171`
- Mesa HEAD: anv: implement VK_INTEL_device_info
- Commit anterior: `f1b6a86974b06ddec7adbf6afcfc8df15a93ff49`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (3 arquivos)

- `src/util/drirc_gen.py`
- `src/util/xmlconfig.c`
- `src/util/xmlconfig.h`

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
