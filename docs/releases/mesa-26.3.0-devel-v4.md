# Turnip Amaral 26.3.0-devel v4 — atualização 2026-08-20

Esta atualização substitui os binários anteriores da v4 e avança a base para o
Mesa `c363342a1130b8e00743337492055c71541724af`, cabeça do `main` auditada em
20/08/2026. Após as validações reprodutíveis, a v4 foi promovida a release
estável/latest; a v3 continua disponível como fallback.

## Drivers

- `turnip_amaral_26.3.0-devel_v4.zip`: variante Standard, recomendada para
  começar os testes.
- `turnip_amaral_26.3.0-devel_v4_oneUI.zip`: mesma base e mesmas melhorias,
  mais o ajuste UBWC restrito às entradas KGSL da FD740.

## Auditoria da atualização do Mesa

O Mesa avançou 212 commits desde `dddaef6`. A maior parte pertence a outros
drivers, CI e infraestrutura, mas a auditoria encontrou correções upstream
diretamente relevantes para compatibilidade e estabilidade do Turnip:

- o NIR deixa de achatar `read_invocation` de modo que possa gerar índice não
  uniforme e travar o hardware;
- o IR3 corrige sparse loads de imagens de 64 bits;
- o Turnip passa a enviar os flags `MSM_SUBMIT_SYNCOBJ_*` quando existem apenas
  syncobjs internos nas filas combinadas de gráficos/sparse;
- custom resolve dinâmico deixa de armazenar/limpar attachments antes da hora;
- imagens AHB multicamada com DRM modifier explícito passam a ser importadas no
  gralloc Qualcomm;
- o runtime Vulkan Android corrige a política de tiling para imagens mutáveis,
  preservando optimal tiling no caso UNORM/SRGB e evitando a regressão de
  desempenho observada no ANGLE;
- o suporte upstream reconhece o novo chip-id A830v1.

Também entram correções genéricas de SPIR-V, NIR e comandos Vulkan compartilhados.
Não foi adicionado patch comunitário de FPS nem configuração agressiva: o ganho
esperado desta subida é principalmente compatibilidade, estabilidade e redução
de hangs/regressões, sem promessa de aumento de FPS na A740.

O Banners-Turnip `20260817-r4` permanece como referência independente histórica.
Sua variante A6xx/A7xx é Mesa puro, sem patch de performance; dela aproveitamos
a confirmação da metodologia e das correções necessárias ao NDK r29, não hacks
A8xx. O snapshot `c363342a` desta atualização foi verificado diretamente no
`mesa/main`.

## Melhorias incorporadas do Amaral Adreno Tools IA

O Driver Lab [#69](https://github.com/rickamaral94/Amaral-Driver-Lab/issues/69)
confirmou em runtime duas capacidades novas, sem perdas de extensões, features
ou limites:

- `VK_EXT_depth_range_unrestricted`;
- `VK_EXT_depth_bias_control`, com `depthBiasControl` e `depthBiasExact`; as
  representações que o hardware não garante continuam corretamente desligadas.

O portão gráfico registrou compatibilidade 100/100, sete de sete checks e zero
divergência em 116 comparações. Como a evidência veio da A740 do Odin2 Portal,
o patch produtivo foi reduzido ao degrau L0: somente `0x43050a01` e
`0xffff43050a01`. Outras A7xx/A8xx não anunciam essas extensões nesta v4.

O caminho novo de `depth_range_unrestricted` com a extensão habilitada ainda
precisa ser exercitado no Eden. Procure z-fighting novo, geometria desaparecendo
perto do plano distante ou decalques atravessando superfícies.

## O que foi descartado após os testes

- `force_sysmem`: zero vitórias no Driver Lab #63, P99 0,79 ms pior e dispersão
  130 vezes maior na cena pesada;
- perfil `driconf` de performance: efeito abaixo de 0,25% nas cargas em que foi
  efetivamente ativado (#67), sem ganho comprovado em sessão real do Eden;
- cache de shader em disco: hipótese promissora, mas ainda sem medição entre
  sessões com `force-stop`; fica no laboratório;
- MR !39751: a versão parcial quebrou apresentação, enquanto a completa não tem
  ganho isolado demonstrado contra o upstream; não entra nesta substituição;
- `-O3`, ThinLTO, spoof, `TU_DEBUG` global, GMEM/sysmem forçado e hacks A8xx
  globais.

## Conteúdo preservado

- compatibilidade de build com Android NDK r29;
- A825 experimental e isolada no `chip_id` KGSL `0x44030000`;
- OneUI com `TP_UBWC_FLAG_HINT` apenas nas duas entradas KGSL da FD740, sem
  afetar `GPUId(740)` nem a Adreno X1-85;
- AArch64 `armv8-a`, API 29 e backend KGSL;
- duas compilações independentes por variante, com ZIP e ELF comparados byte a
  byte antes da substituição dos assets.

## Validação solicitada

Compare com a v3 ou com o binário anterior da v4 nas mesmas condições. Comece
pela Standard e use OneUI apenas em firmware Samsung/One UI com sintomas UBWC.
Priorize Eden com jogos que usem depth bias/depth range, registrando correção
visual, crash/device lost, frametimes, stutter, temperatura e consumo.
