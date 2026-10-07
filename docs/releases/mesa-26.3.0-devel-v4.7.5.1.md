# Turnip Amaral 26.3.0-devel v4.7.5.1

## Classificação

**Candidata em preparação; nenhuma release publicada.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `7a51c0f5326ee011b16a854499abf1db6f6c8b29`
- Mesa HEAD: kopper: stop including mesa_interface.h from kopper_interface.h
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

## Reparo da atualização Mesa (7 de outubro de 2026)

- Os patches 0002 e 0003 deixam de inserir `magic_regs`, removido do construtor
  upstream em `17ca6174`. O OneUI deixa de referenciar `a740_magic_regs`, também removido.
- O catálogo Standard e OneUI é gerado na CI, além da aplicação dos patches.
  `git apply --check` sozinho não detectava esses erros Python.
- Cada build independente preserva stdout/stderr em `build.log` e mantém o
  status de falha. O workflow de teste envia os logs mesmo quando o build falha.
- Os IDs e parâmetros experimentais A825/840v2 são preservados; somente os dois
  IDs FD740 KGSL diferem entre Standard e OneUI (`enable_tp_ubwc_flag_hint`).
- A base inclui o ajuste posterior de CSE de textura `9ce7a2e` e o gate upstream
  A750/HL: Alyx `f7ca1f5`. Não se declara ganho para outras GPUs/aplicações.
- Mesh shader, Wave32, fixes comunitários A8xx 0003–0005 e IB cache não fazem
  parte desta candidata. Requerem integração e validação separadas.

## Validação

Aplicação sem rejeições dos onze patches e geração dos catálogos Standard/OneUI
verificadas no SHA Mesa fixado. São 89 IDs; as duas variantes diferem somente no
flag UBWC dos IDs `0x43050a01` e `0xffff43050a01`.

Os builds Android duplos e os hashes de ZIP/ELF devem passar na CI antes de
publicar qualquer candidata. A referência estável permanece v4.7.4.1, com seu
fingerprint original; a promoção não está autorizada por esta preparação.
