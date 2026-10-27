# Turnip Amaral 27.0.0-devel v5.7.16.1

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

## Mudanças em relação à 5.7.15.1

Candidata de teste para a corrupção de imagem do A840 (SM8850) no Eden/MUA3.
Mesmo lock Mesa e mesmo patchset da 5.7.15.1, mais um patch:

- `upstream-mr44464-snapalloc-34ints.patch`: MR !44464 (u_gralloc/fallback:
  UBWC em handles SnapAlloc) rebaseado sobre o patch 0001 do NDK, mantendo só
  o layout SnapAlloc display-core de 34 ints por view, o do 8 Elite. O ramo
  de 33 ints (SM7435/parrot) do MR fica de fora: esses handles continuam com
  `DRM_FORMAT_MOD_INVALID`, como hoje. O handle só é aceito se tiver
  exatamente a forma SnapAlloc e o stride bater com o do gralloc; qualquer
  outro mantém o comportamento atual.

Evidência (T-a840-pixelation, finding e9bd), que favorece o tratamento de
layout/modifier sem observar o modifier: no A840, com os mesmos ajustes
(hash `01faf495…`), a 5.7.14.1 mostra ruído em colunas e o lab
5.7.14.1 + MR !44464 mostra imagem nítida. O Rick confirmou o lab sem erros na
sessão inteira. O controle Qualcomm também é nítido. **O lab tinha o MR
completo (34 e 33 ints); esta candidata tem só o caminho de 34 ints, o caminho
esperado no A840 pela descrição da MR (os ZIPs do lab não registram o ramo).**

## Validação

- Build Standard e OneUI, `validate_artifact` e catálogo de GPUs: ver o registro da integração.
- Hardware: A840 desta candidata, A740 (regressão do fallback) e A6xx: **not-run**.
- CTS e VVL: **not-run**.

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Toda mudança passa por candidata. Promoção exige evidência vinculada ao SHA
Mesa, fingerprint e hashes Standard/OneUI. Build reproduzível não prova
compatibilidade, conformidade ou ganho de desempenho. Defaults de compiler,
suballocadores e perfis por título permanecem upstream; patches de pesquisa
não são aplicados aos pacotes distribuídos.
