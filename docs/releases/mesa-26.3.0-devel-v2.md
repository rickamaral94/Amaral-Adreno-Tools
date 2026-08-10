# Turnip Amaral 26.3.0-devel v2

Esta atualização mantém o snapshot Mesa `26.3.0-devel` no commit
`32fab1ad098a393ffa40dce8e5272f52aa0ff70a` e passa a produzir duas variantes
do Amaral Turnip Universal.

## Drivers desta atualização

- `turnip_amaral_26.3.0-devel_v2.zip`: variante padrão.
- `turnip_amaral_26.3.0-devel_v2_oneUI.zip`: mesma base, com a compatibilidade
  UBWC para OneUI adicionada ao final da nomenclatura.

## Suporte experimental à Adreno 825

As duas variantes incluem suporte comunitário à Adreno 825 pelo `chip_id` KGSL
`0x44030000`:

- identificação explícita da GPU;
- configuração própria de GMEM, CCU, VPC, slices e alinhamento;
- entrada no DRM shim para validação;
- desativação de FDM por camada e sample interpolation forçado somente quando o
  dispositivo detectado é exatamente a A825.

O port foi derivado do fork `whitebelyash/mesa-unified`, mas não incorpora o
fork inteiro. Foram excluídos perfis IR3 globais, aumento global de shared
memory, alterações compartilhadas por várias A8xx e a condição defeituosa que
fazia o caminho da A830 ser tratado como sempre verdadeiro.

O suporte A825 ainda não faz parte do snapshot oficial do Mesa desta revisão e
não foi validado em uma matriz física completa. Ele permanece **experimental**
até receber logs e comparações reproduzíveis da comunidade.

## Variante OneUI

A variante OneUI altera somente a entrada FD740 para ativar
`enable_tp_ubwc_flag_hint`. Esse bit precisa coincidir com o valor do driver
proprietário do sistema para evitar incompatibilidades UBWC em blits, escala e
texturas.

A OneUI não é uma versão de desempenho geral e não modifica GPUs A8xx. A
variante padrão continua sendo a primeira recomendação de teste.

## Validação antes da pré-release

O CI compila as variantes padrão e OneUI separadamente, duas vezes cada, e
exige ZIPs e ELFs idênticos byte a byte. A publicação da pré-release depende da
conclusão desse gate e da geração dos respectivos checksums.
