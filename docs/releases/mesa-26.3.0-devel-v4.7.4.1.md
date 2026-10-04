# Turnip Amaral 26.3.0-devel v4.7.4.1

## Classificação

**Pré-release para A/B.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `c126acd85a645728bcecaa164d7d7c928438e842`
- Mesa HEAD: people: sync Alyssa with .mailmap
- Commit anterior: `c126acd85a645728bcecaa164d7d7c928438e842`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

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
