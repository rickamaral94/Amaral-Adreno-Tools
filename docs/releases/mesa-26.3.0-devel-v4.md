# Turnip Amaral 26.3.0-devel v4 — atualização 2026-08-17

Esta atualização substitui os binários anteriores da v4 e avança a base para o
Mesa `dddaef6f8c970770cc60f6bab6ab5392f54e7679`, cabeça do `main` auditada em
17/08/2026. A v4 permanece pré-release; a v3 continua estável/latest e fallback.

## Drivers

- `turnip_amaral_26.3.0-devel_v4.zip`: variante Standard, recomendada para
  começar os testes.
- `turnip_amaral_26.3.0-devel_v4_oneUI.zip`: mesma base e mesmas melhorias,
  mais o ajuste UBWC restrito às entradas KGSL da FD740.

## Auditoria da atualização do Mesa

O Mesa avançou oito commits desde a base anterior `f0bcf544`. Cinco corrigem
encode H.265 no ANV/Intel, um corrige ciclo de vida no Gallivm, um é específico
do RADV e um preserva bits de I/O não interpolado no `nir_opt_varyings` quando o
driver opta pelo novo modo. O Turnip não habilita essa opção hoje. Portanto, a
subida entrega o snapshot upstream mais recente, mas não sustenta alegação de
ganho de FPS na A740.

O Banners-Turnip `20260817-r4` foi usado como referência independente. Sua
variante A6xx/A7xx também é Mesa puro, sem patch de performance; dela aproveitamos
a confirmação da base e das correções necessárias ao NDK r29, não hacks A8xx.

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
