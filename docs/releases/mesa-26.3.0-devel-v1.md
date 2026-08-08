# Turnip Amaral 26.3.0-devel v1

Primeira versão universal do Amaral Adreno Tools, criada para oferecer uma base
única de compatibilidade para GPUs Adreno reconhecidas pelo Mesa nas famílias
A6xx, A7xx e A8xx.

## O que mudou

- Atualização para o snapshot Mesa `26.3.0-devel` no commit
  `32fab1ad098a393ffa40dce8e5272f52aa0ff70a`.
- Base mais recente que o snapshot A7xx usado como referência, incorporando 201
  commits upstream do intervalo auditado.
- Runtime Vulkan mais robusto ao encontrar itens inválidos no cache de shaders:
  o Mesa agora descarta o item que falhou na desserialização, evitando manter um
  cache problemático.
- `VK_KHR_maintenance9` marcado como concluído para o Turnip no upstream.
- Otimizações internas no NIR que reutilizam estruturas temporárias durante a
  propagação de cópias, ajudando a reduzir trabalho interno da compilação de
  shaders sem alterar a renderização esperada.
- Ajustes de robustez e manutenção do Freedreno incluídos pelo snapshot atual.

## Melhorias do Amaral

- Um único build universal AArch64 `armv8-a` com backend KGSL.
- API mínima Android 29 para ampliar o alcance, ainda dependente do aparelho,
  firmware e emulador.
- Autotuner GMEM/SYSMEM original do Mesa preservado.
- Nenhum spoof de GPU ou Vulkan, recurso artificial, `TU_DEBUG` forçado ou hack
  global específico de jogo.
- Compatibilidade de build com Android NDK r29.
- ZIP e ELF produzidos por duas compilações independentes e confirmados como
  idênticos byte a byte.

## Vulkan

Compilado com headers **Vulkan 1.4.358**. Esse número identifica a revisão dos
headers usada no build; os recursos realmente disponíveis continuam dependendo
da GPU, firmware, Android e emulador.

## Ganhos esperados

O foco desta versão é melhorar previsibilidade, compatibilidade e manutenção:
base Mesa mais atual, tratamento mais seguro do cache de shaders e um perfil
universal sem ajustes agressivos que favoreçam um jogo e prejudiquem outro.

Não anunciamos ganho percentual de FPS porque esta versão ainda não passou pela
matriz completa de testes físicos. Desempenho pode variar conforme o aparelho e
o emulador.

## Status e testes

Esta é uma **pré-release de validação comunitária**. O build, o formato do ZIP,
o ELF AArch64, os metadados, o hardening e a reprodutibilidade foram validados.
Ainda precisamos ampliar os testes reais nas famílias A6xx, A7xx e A8xx.

Compartilhe logs, capturas e comparações reproduzíveis no repositório. Esses
retornos serão usados para as próximas revisões Amaral.

## Integridade

- Arquivo: `turnip_amaral_26.3.0-devel_v1.zip`
- SHA-256 do ZIP: `6a7ce670ee78069adecbca291e7fd74b55071e88039b3dffc691de814aae14e5`
- SHA-256 do ELF: `4b6f973bc072bce6040d310a0675a7d67e1696f90bb50b6bc66f2ae22090d010`

