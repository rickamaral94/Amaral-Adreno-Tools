# Turnip Amaral 27.0.0-devel v5.7.15.1

## Classificação

**Pré-release para A/B.**

## Base rastreável

- Mesa: `27.0.0-devel`
- Mesa commit: `69f1f21f0258a77046dbaeb8ed7a8ad37a683006`
- Mesa HEAD: tu: upload draw_id_offset through driver_params UBO
- Commit anterior: `378a5dc61b982b7d36e744cf44407e6b55dc98b7`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Mudanças em relação à 5.7.14.1

Pré-release de teste pedido pelo Rick em 26/10/2026. Mesmo lock Mesa e mesmo
patchset da 5.7.14.1, mais três commits upstream já mesclados, aplicados sem
edição (`git format-patch`), revisados em `collab/channel` (T-candidate-5.7.14.1,
propostas fb8a, review e378):

- `29db4909d4e` ir3/ra: corrige o limite do RA no modo `IR3_DOUBLE_ONLY` em
  A6xx gen1_low/gen3/gen4. Sem efeito em A7xx (reg 96) e A8xx (sem double
  threadsize).
- `64245a20b78` tu: reintroduz o caminho 3D f16 nas cópias MSAA, que preserva
  NaN. Todas as famílias.
- `a1e9f888421` tu/kgsl: `MAP_FIXED_NOREPLACE` só quando há endereço de
  capture/replay de BDA. Alocação comum não muda.

Não inclui nenhum lab A840 (SnapAlloc, noubwc, sysmem, gen8state). **Não
corrige a imagem pixelada da A840/MUA3 e não comprova ganho de FPS no A740.**
É a base de correções upstream para a próxima candidata.

## Validação

- Build Standard e OneUI, `validate_artifact` e catálogo de GPUs: ok.
- Reprodutibilidade em dupla build: ver o registro de hashes da integração.
- CTS (copy_image MS f16), VVL e hardware A6xx/A7xx/A8xx: **not-run**.

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Toda mudança passa por candidata. Promoção exige evidência vinculada ao SHA
Mesa, fingerprint e hashes Standard/OneUI. Build reproduzível não prova
compatibilidade, conformidade ou ganho de desempenho. Defaults de compiler,
suballocadores e perfis por título permanecem upstream; patches de pesquisa
não são aplicados aos pacotes distribuídos.
