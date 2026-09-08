# Turnip Amaral 26.3.0-devel v4.5.1.3

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `04c9a2eefecff44ea087a445718402e71da4510d`
- Mesa HEAD: anv: Macro out the vid_mem address/attributes boilerplate
- Commit anterior: `b63bb362308a17316245671f51e2fb5c6637702d`
- Vulkan headers: `1.4.359`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (2 arquivos)

- `src/compiler/nir/nir_lower_alu.c`
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
