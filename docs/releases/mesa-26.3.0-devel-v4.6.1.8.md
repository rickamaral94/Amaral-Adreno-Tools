# Turnip Amaral 26.3.0-devel v4.6.1.8

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `972675794391a60f6f6f20a3a39d1cb0aecd7af4`
- Mesa HEAD: bin/ci_run_n_monitor: add `--no-new-job-after 12h`
- Commit anterior: `d0bf12daec6e351dbe0d6349124ee178eb0ac913`
- Vulkan headers: `1.4.362`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (7 arquivos)

- `src/compiler/spirv/vtn_bindgen2.c`
- `src/vulkan/wsi/wsi_common_display.c`
- `src/vulkan/wsi/wsi_common_headless.c`
- `src/vulkan/wsi/wsi_common_metal.c`
- `src/vulkan/wsi/wsi_common_wayland.c`
- `src/vulkan/wsi/wsi_common_win32.cpp`
- `src/vulkan/wsi/wsi_common_x11.c`

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
