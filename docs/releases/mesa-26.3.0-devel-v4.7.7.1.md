# Turnip Amaral 26.3.0-devel v4.7.7.1

## Classificação

**Pré-release para A/B.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `07ea97900e735afff9bfd59805983912f72f7dfd`
- Mesa HEAD: freedreno: add 2 slice Adreno 840 chip id
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

## A840v2 correction and publication authorization

Replaces the external A840v2 alias with Mesa MR 45083. Chip 0x44050A21 uses
four CCU, two slices, 64x32 tile alignment and a maximum tile width of 16384.
The three-slice A840 retains its independent upstream profile. The previous
v4.7.6.1 profile is superseded for A840v2 and must not be promoted.

Includes upstream non-uniform acceleration-structure ray-query correction
42d7c3315495a6aee7eca5e87f0a9b4acd6b4311. Existing patches preserve their
behavior; Aurora patch context follows upstream explicit C++ casts.

Latest publication was explicitly requested by the user on 2026-10-14.
Standard/OneUI build, artifact and byte reproducibility gates are mandatory.
Device A/B and CTS have not been executed for this release; no hardware
conformance or performance gain is claimed.
