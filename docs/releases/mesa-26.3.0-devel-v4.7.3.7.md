# Turnip Amaral 26.3.0-devel v4.7.3.7

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `8fc4981d2d25a32732296a90bf9eaa0371f8c715`
- Mesa HEAD: util: Add p_atomic_dec_not_one helper
- Commit anterior: `e8e6cf93eac7dfc294088b986bb09c7eed12b409`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (11 arquivos)

- `src/freedreno/ci/freedreno-a618-fails.txt`
- `src/freedreno/common/freedreno_dev_info.h`
- `src/freedreno/common/freedreno_devices.py`
- `src/freedreno/decode/cffdec.c`
- `src/freedreno/registers/adreno/a6xx.xml`
- `src/freedreno/tests/reference/crash.log`
- `src/freedreno/tests/reference/crash_prefetch.log`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- `src/util/00-mesa-defaults.conf`
- `src/util/driconf.h`
- `src/util/u_atomic.h`

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
