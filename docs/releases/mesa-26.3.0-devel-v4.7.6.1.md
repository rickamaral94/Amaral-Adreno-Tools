# Turnip Amaral 26.3.0-devel v4.7.6.1

## Classificação

**Pré-release para A/B.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `a51a418991f883413f10f66cd52398d590a8257b`
- Mesa HEAD: tu/kgsl: Handle errors around profiling buffer/ioctls
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

## Revisão KGSL de 8 de outubro

Candidata em preparação; nenhuma release publicada. MR Mesa 44838 incorporada
inteira. Patches 0009 e 0010 retirados; trecho KGSL de 0007 removido porque
o upstream substituiu a alocação dinâmica por profile_obj na pilha.
Os demais quatro fixes comunitários de 0007 são preservados.
Novos IDs upstream: A735 0xffff43030e01 e A753 0xffff43051701.
A825 permanece experimental; OneUI permanece isolado aos IDs FD740.
Sem novos defaults globais, spoofing, mesh shaders, Wave32 ou IB cache.
Builds duplos Standard/OneUI e testes em hardware são gates pendentes.
Latest permanece v4.7.4.1.
