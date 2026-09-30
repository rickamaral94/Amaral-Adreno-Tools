# Turnip Amaral 26.3.0-devel v4.7.3.4

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `cec59b299704edc442d930ea9e06ab2edcf5ad7b`
- Mesa HEAD: mesa/st: use nir_trim_vector
- Commit anterior: `c4eb475c289b71292696f176e852eb2deb52b9fc`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (16 arquivos)

- `src/freedreno/ci/freedreno-a618-fails.txt`
- `src/freedreno/ci/freedreno-a660-fails.txt`
- `src/freedreno/ir3/ir3_delay.c`
- `src/freedreno/ir3/ir3_postsched.c`
- `src/freedreno/qrisc/disasm.c`
- `src/freedreno/qrisc/emu.c`
- `src/freedreno/qrisc/util.c`
- `src/freedreno/qrisc/util.h`
- `src/freedreno/vulkan/00-turnip-defaults.conf`
- `src/freedreno/vulkan/tu_clear_blit.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.h`
- `src/freedreno/vulkan/tu_lrz.cc`
- `src/freedreno/vulkan/tu_lrz.h`
- `src/freedreno/vulkan/tu_shader.cc`
- `src/util/blob.h`

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
