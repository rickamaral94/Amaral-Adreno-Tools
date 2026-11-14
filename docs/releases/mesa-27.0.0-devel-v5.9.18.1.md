# Turnip Amaral 27.0.0-devel v5.9.18.1

## Classificação

**Pré-release (candidata).** A Latest continua sendo a 5.8.17.1.

## Base rastreável

- Mesa: `27.0.0-devel`
- Mesa commit: `a6aacf6b0fb0468b1dbe57fa34a0bba7c5ee2413`
- Mesa HEAD: util: avoid Windows memstream temp file leaks
- Commit anterior: `f4ab1f91b0749f34b6342885bc5ff98a731e92e3`
- Vulkan headers: `1.4.368`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Mudanças em relação à 5.8.17.1

Candidata pedida pelo Rick em 14/11/2026: Mesa upstream de hoje com o patchset
atual. Os headers Vulkan passaram a `1.4.368`, por isso o segundo número da
versão subiu (5.8 → 5.9).

**Mesa `fd8ef2b` (31/10) → `a6aacf6` (14/11).** 74 commits em `src/freedreno`,
54 deles em Turnip, comum, fdl e ir3. Os que mais pesam para o projeto:

A7xx (A740 do Odin):

- `c534b8df833` freedreno: novo valor de `SP_DBG_ECO_CNTL` na entrada do A740,
  igual ao do driver proprietário mais novo. Sem ele, GPUs da mesma entrada
  (Adreno X1-85) travavam de forma aleatória, mas consistente. O upstream não
  viu efeito colateral no A740; marcado para `mesa-stable`. **Mudança no nosso
  chip principal: o teste no Odin é obrigatório.**
- `88b01a7c269` tu: o bind de descriptor set só suja as constantes do shader
  quando os shaders usam os endereços base dos sets. Menos trabalho de CPU para
  apps com muitos binds de set, como os ports NVN.
- `7c9b2268a84`, `bda4a67701d`, `82faea4f58c` tu/autotune: corrida e vida útil
  do histórico que decide GMEM ou SYSMEM por passe.
- ir3: `6259aefccde` (udiv fp32), `9b0a38cabb8` (resultados de 1 bit em
  shfl/movs), `d520ae902ed` (FP32→FP16 com subnormal).
- `91a36b060e9` (scissor com contagem zero), `78fd465cef8` (limpa
  `SP_xS_BASE` sem uso).

A8xx (A840 do SM-F971B):

- `2ce86eedc5d`, `e1852a339be` tu/lrz: fast-clear parcial de LRZ por slice e
  pitch de 32. Corrige corrupção de profundidade (Conan Exiles), relevante para
  o A840 de três slices.
- `5b2db4b8e3e` fdl: descritor de buffer com `NUM_ELEMENTS` de 32 bits. Buffers
  de 1 GiB ou mais deixam de ler zero (UE5 Nanite via vkd3d).
- `1c87c601870` tu: WFI antes de ler registradores recém-escritos (MSAA no
  A830/A840; `store_3d_blit` e XFB em A650).

Todas as famílias:

- `8a494f248a7` tu: emite os flushes pendentes ao terminar um command buffer
  numa cadeia suspend/resume (UE5 via vkd3d, Mortal Shell 2).
- `64adb6a1bf7` tu: passa a anunciar `VK_KHR_shader_maximal_reconvergence` onde o
  perfil da GPU tem `has_getfiberid`. É exposição nova herdada do upstream; o CTS
  `dEQP-VK.reconvergence.maximal.*` está not-run aqui (roadmap atualizado).
- `e4415d24616` tu/kgsl: `VK_KHR_calibrated_timestamps` funcionando no KGSL;
  antes, `vkGetCalibratedTimestampsKHR` caía em `UNREACHABLE`.
- `73196ec50b0`, `a84e5bacf90`: emulação de SSBO e de texel buffer também no
  A6xx (perfis por app de jogos D3D12/UE5).
- `31f1ceddffc` (macrotile do A635 no KGSL), `8c589b897b3` (CCUs do A722),
  `df911094d36` e `cc656a6ce1e` (flags de memória do KGSL e rollover de IB),
  `0f5ba03ea0b` (ordem de bindings), `9296e254129` (blits fora da contagem
  de primitivas geradas).
- `ce116a018ec` tu: remove a invalidação de profundidade no fim da occlusion
  query. Só tem efeito em a7xx gen3 (A750); sem efeito no A740.

**Patches Amaral:**

- `0009-tu-program-state-pointer.patch`: rebase sobre `88b01a7c269`, que
  passou a ler `uses_bindless_base_addrs` do estado do programa no bind de
  descriptor set. Esse caminho pode rodar antes de qualquer pipeline vinculado.
  O ponteiro nulo vale como "não usa", o mesmo resultado da cópia zerada de
  antes. O comportamento do bind de pipeline não muda.
- `0001`, `0002`, `0007`, `0008`, `0003` (OneUI) e
  `upstream-mr44464-snapalloc-34ints.patch` aplicam sem mudança. O MR 44464
  continua aberto no upstream.
- O laboratório de sparse do KGSL (`docs/research/`) **não** entra. Ele não tem
  teste que prove a correção.

## Validação

- Build Standard e OneUI, dupla build reproduzível, `validate_artifact` e
  catálogo de GPUs: ver o registro do PR de integração e a execução do workflow
  de publicação.
- **Hardware desta Mesa: not-run em qualquer família.**
- Teste pedido antes de qualquer promoção:
  - **A740, Odin 2 Portal:** mudança de `SP_DBG_ECO_CNTL`. BOTW, TOTK e um jogo
    do Eden, contra a 5.8.17.1, com atenção a travamentos e device lost.
  - **A840, SM-F971B:** MUA3/Eden e um jogo com a corrupção de profundidade
    antes vista, contra a 5.8.17.1.
  - **0009 rebaseado:** o mesmo smoke do BOTW. Os casos de revisão de 31/10
    seguem not-run.
- CTS e VVL: **not-run**.

Por isso esta versão é pré-release. Ela só vira Latest pelo fluxo de promoção,
com qualificação em hardware vinculada a estes hashes.

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Toda mudança passa por candidata. Promoção exige evidência vinculada ao SHA
Mesa, fingerprint e hashes Standard/OneUI. Build reproduzível não prova
compatibilidade, conformidade ou ganho de desempenho. Defaults de compiler,
suballocadores e perfis por título permanecem upstream; patches de pesquisa
não são aplicados aos pacotes distribuídos.
