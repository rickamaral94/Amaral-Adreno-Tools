# Turnip Amaral 27.0.0-devel v5.8.17.1

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `27.0.0-devel`
- Mesa commit: `fd8ef2befafd01190e33f12dbfd109b924c8ebc3`
- Mesa HEAD: asahi: drop NIR_PASS from poly_nir_lower_gs calls
- Commit anterior: `378a5dc61b982b7d36e744cf44407e6b55dc98b7`
- Vulkan headers: `1.4.366`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Mudanças em relação à 5.7.16.1

Atualização pedida pelo Rick em 31/10/2026: trazer a Mesa upstream mais recente
e incluir a melhoria de CPU do bind de pipeline. Esta é a primeira candidata
na `main` depois da 5.7.8.1. Ela inclui também as candidatas de teste 5.7.14.1,
5.7.15.1 e 5.7.16.1, que não chegaram a ser publicadas.

**Mesa `69f1f21` → `fd8ef2b` (main de 31/10/2026).** 29 commits upstream em
Freedreno/Turnip/ir3, entre eles:

- `2fae1d0` tu: alinhamento `QCTDD08049535_numnonposvar_alignment` em a7xx
  gen1/gen2, incluindo o FD740 (no catálogo, 9 perfis a7xx);
- `8aa6218` tu: restaura o workaround de binning predicado para `a630_sqe.fw`
  (8 perfis a6xx);
- `c99d3b50f77` tu: comportamento GL na primitive generated query;
- `a799b0baca9` tu: `tu_enable_ssbo_emulation` para jogos UE5 (driconf);
- `fe3e563ceb3` e `7e29b87af30`: `prefer_gmem` para Sweet Surrender VR e Beat Saber;
- ir3: propagação de `BNOT` como modificador de fonte e correções no a5xx;
- `9c82a78f18d` freedreno: FD735 independente do speed bin.

Os três backports que a 5.7.15.1 trazia (`29db4909d4e`, `64245a20b78` e
`a1e9f888421`) já estão nesta base, e os patches externos saíram. Os headers
Vulkan passaram a `1.4.366`, por isso o segundo número da versão subiu.

**Patches Amaral:**

- `0008-remove-mgs4-vendor-spoof.patch`: rebase de contexto, porque o
  upstream acrescentou perfis ao lado do MGS4. O comportamento não muda.
- **Novo** `0009-tu-program-state-pointer.patch`: `tu_CmdBindPipeline`
  deixa de copiar `tu_program_state` (~10 KB) a cada bind gráfico e passa a
  apontar para o estado do pipeline vinculado. O perfil do BOTWRecomp no
  A740 mostrava essa cópia em ~3,9% das amostras da thread de render.
  - Em um A/B de 60 s no Odin 2 Portal, o custo por bind caiu ~60%. É
    estimativa preliminar, sem efeito atribuível em FPS ou GPU.
  - Revisado pelos dois agentes (T-botwrecomp-a740, 4b6b).
- `upstream-mr44464-snapalloc-34ints.patch` (A840) segue como na 5.7.16.1.
  O MR continua aberto no upstream.

## Validação

- Build Standard e OneUI, dupla build reproduzível, `validate_artifact` e
  catálogo de GPUs: ver o registro do PR de integração.
- **Hardware desta Mesa: not-run em qualquer família.**
- `0009`: not-run para os casos pedidos na revisão (biblioteca GPL destruída,
  secondary + rebind, gráfico/compute, tessellation/FDM, trace ativo), para o
  AB/BA de 5 rodadas, e para A6xx e A8xx.
- 5.7.16.1, ainda pendentes: A840 com Bilinear/AA None e o par A740.
- CTS e VVL: **not-run**.

Por isso esta versão é pré-release. Ela só vira Latest pelo fluxo de promoção,
com qualificação em hardware vinculada a estes hashes.

## Promoção por exceção do dono

Em 31/10/2026 o Rick testou esta versão no Odin 2 Portal (A740: BOTWRecomp e
outros jogos) e no SM-F971B (A840: MUA3/Eden e outros jogos), relatou que está
ok e pediu a promoção a Latest ([relato](../tests/2026-10-31-v5.8.17.1-owner-smoke.md)).

A promoção usou a exceção do dono do `promotion_gate`, registrada em
`evidence/qualifications/5.8.17.1.json`.

- **Dispensados, e registrados como not-run:** CTS, VVL, regressões formais,
  A/B de 5 rodadas e cobertura A6xx.
- **Cumpridos:** identidade exata dos artefatos, CI, dupla build reproduzível e
  hardware A7xx/A8xx relatado pelo dono.

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Toda mudança passa por candidata. Promoção exige evidência vinculada ao SHA
Mesa, fingerprint e hashes Standard/OneUI. Build reproduzível não prova
compatibilidade, conformidade ou ganho de desempenho. Defaults de compiler,
suballocadores e perfis por título permanecem upstream; patches de pesquisa
não são aplicados aos pacotes distribuídos.
