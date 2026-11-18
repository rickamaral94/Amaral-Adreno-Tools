# Turnip Amaral 27.0.0-devel v5.9.19.1

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `27.0.0-devel`
- Mesa commit: `8e0f6be8759fa657e80f6cade416970097df1c81`
- Mesa HEAD: panvk/utrace: Lazily allocate copy buffer heap
- Commit anterior: `a6aacf6b0fb0468b1dbe57fa34a0bba7c5ee2413`
- Vulkan headers: `1.4.368`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Mudanças em relação à 5.9.18.1

Candidata pedida pelo Rick em 18/11/2026: Mesa upstream de hoje com o patchset atual e a correção de captura de
representações internas (`0010`). Os headers Vulkan continuam em `1.4.368`.

**Mesa `a6aacf6` (14/11) → `8e0f6be` (18/11).** 314 commits no total, 36 em `src/freedreno`. Os de Turnip e ir3:

- `1446d7f9e75`, `2bbd85f5484`, `79cb5065125` ir3: não cria alias (`alias.tex`) para fontes de array e confere as
  flags das fontes de collects com alias. Corrige erro de validação em Enshrouded (vkd3d). Vale para todas as famílias
  com `alias.tex`.
- `50623f710a3` tu: LRZ desligado em imagens de depth importadas (AHB ou DMA-BUF com layout externo). Antes, os
  metadados de LRZ podiam escrever além da alocação. Mesmo comportamento do driver proprietário.
- `6d453f2636f` tu: volta a aceitar import de AHB `S8_UINT`; o suporte passa a vir do gralloc.
- `6f26f219568` tu: reduz o tamanho dos acessos a UBO antes de rebaixar inline uniform blocks. Corrige uma assertiva
  com `shaderInt64`.
- `55cfd6e78cb`, `650e49e4f5f` tu/ir3: passam a anunciar `storagePushConstant8/16` e, onde suportado,
  `uniformAndStorageBuffer8/16BitAccess`. São features de extensões que o Turnip já expunha.
- `c035bdfaa1f` vulkan/android: AHB de depth com compressão desligada passa a ser linear.
- O restante em `src/freedreno` é A2xx/A5xx, decodificador e CI.

**Revisão contra o patchset Amaral:**

| Patch | Arquivos tocados pelo upstream no intervalo | Resultado |
| --- | --- | --- |
| `0001` NDK r29 | `vk_android.c` (`c035bdf`, outra função) | aplica; independente |
| `0002` A8xx | nenhum | aplica |
| `0007` estabilidade | `tu_shader.cc` (`6f26f21`, outra função) | aplica; independente |
| `0008` vendor spoof | nenhum | aplica |
| `0009` program state | nenhum | aplica |
| `upstream-mr44464` SnapAlloc | nenhum (depende do `0001`) | aplica; o MR segue sem equivalente no upstream |
| `0010` captura de IR | nenhum | aplica |
| `0003` OneUI | nenhum | aplica |

Nenhuma mudança upstream duplica ou contradiz um patch nosso. `check_mesa_policy --patched` passa nas duas variantes.

**Patch novo:**

- `0010-tu-capture-ir-cache-dedup.patch`: com `VK_PIPELINE_CREATE_CAPTURE_INTERNAL_REPRESENTATIONS`, o Turnip mantém o
  shader recém-compilado em vez de uma cópia igual que já estava no pipeline cache (por exemplo, importada do cache
  do app), que não tem IR.
  - Antes, a captura só expunha "NIR from SPIRV".
  - Pipelines sem a flag seguem exatamente o mesmo código.
  - Achado no caso Gtavport de 15/11 e validado na reprodução local: de 1 para 3 representações com o cache do app
    quente; estatísticas e acerto de cache iguais sem a flag.

## Validação

- `validate_project`, testes, `check_a840_topology` e `check_vulkan_roadmap --fail-on-new-support`: OK.
- Série Standard e OneUI aplicam sobre `8e0f6be`; `check_mesa_policy --patched` OK nas duas.
- Build Standard e OneUI, dupla build reproduzível, `validate_artifact` e catálogo de GPUs: ver o PR de integração e a
  execução do workflow de publicação.
- **Hardware desta Mesa: not-run em qualquer família.**
- Teste pedido antes de qualquer promoção:
  - **A740, Odin 2 Portal:** BOTW, TOTK, GTA V (Gtavport) e um jogo do Eden, contra a 5.8.17.1, com atenção a
    travamentos, device lost e defeitos de imagem (mudança no alias do ir3).
  - **A840, SM-F971B:** MUA3/Eden.
  - Ferramentas de perfil: uma rodada do Gtavport com `GTAVPORT_PIPELINE_STATS=1` e o cache do app quente deve trazer
    as três representações.
- CTS e VVL: **not-run**.

Ela só vira Latest pelo fluxo de promoção, com qualificação em hardware vinculada a estes hashes (ver a seção de
promoção abaixo).

## Promoção por exceção do dono

Em 18/11/2026 o Rick validou esta versão no Odin 2 Portal (A740) com o Gtavport e pediu a promoção a Latest
([relato](../tests/2026-11-18-v5.9.19.1-owner-smoke.md)).

A promoção usou a exceção do dono do `promotion_gate`, registrada em `evidence/qualifications/5.9.19.1.json`.

- **Dispensados, e registrados como not-run:** CTS, VVL, regressões formais, A/B de 5 rodadas e cobertura A6xx/A8xx.
- **Cumpridos:** identidade exata dos artefatos, CI, dupla build reproduzível e hardware A7xx relatado pelo dono.

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Toda mudança passa por candidata. Promoção exige evidência vinculada ao SHA Mesa, fingerprint e hashes Standard/OneUI.
Build reproduzível não prova compatibilidade, conformidade ou ganho de desempenho. Defaults de compiler, suballocadores
e perfis por título permanecem upstream; patches de pesquisa não são aplicados aos pacotes distribuídos.
