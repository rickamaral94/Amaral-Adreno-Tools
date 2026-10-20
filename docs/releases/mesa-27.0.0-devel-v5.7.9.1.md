# Turnip Amaral 27.0.0-devel v5.7.9.1 Candidate

**Pré-release para A/B.**

Controle: Latest 4.7.7.2 permanece inalterada. Esta candidata substitui a
5.7.8.1 como linha de qualificação. Não há CTS, VVL ou aparelho executados
nesta preparação; não há promessa de ganho de FPS.

## Base rastreável

- Mesa `27.0.0-devel`, commit `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`
  (HEAD de `main` confirmado no GitLab oficial em 20/10/2026)
- Vulkan headers `1.4.363`; NDK r29, API 29, ARM64 `armv8-a`, KGSL
- Mesmo Mesa da 5.7.8.1: o delta desta revisão é só o patchset

## O que esta versão melhora, por família

Cada item é uma correção upstream revisada por mantenedores do Turnip e ainda
não integrada ao `main`. Todas ficam presas à família afetada, menos a correção
de lifetime, que é universal por natureza.

| Família | Patch | Problema real | Escopo |
|---|---|---|---|
| A8xx | 0009 (MR !44352, 1-2/7) | GPU fault em `vkCmdDraw*Indirect`/`*IndirectCount` grandes: o CP só busca `(1<<20)-1` dwords por pacote | Só `CHIP >= A8XX`; A6xx/A7xx emitem os mesmos pacotes |
| A7xx | 0010 (MR !45204) | Bounds check com sinal na emulação de texel buffer: offset negativo escrevia antes da view | Emulação só existe em gen 7 e só liga por driconf (Spider-Man Remastered, Ratchet & Clank: D3D12/vkd3d-proton) |
| A6xx | 0011 (MR !41860) | Dados de transform feedback corrompidos com draw XFB dentro de query XFB (Risk of Rain 2; DXVK usa XFB para stream output) | Só `CHIP == A6XX`; reproduzido em A630/A650/A660 |
| Todas | 0012 (MR !45369) | Referência de BO nunca liberada nos patchpoints de visibility stream: o BO do suballocator fica retido | Command buffers SIMULTANEOUS_USE em GMEM com binning |

Herdado da 5.7.8.1 (upstream em `4b0f64c`): sequência de invalidação bindless,
coleta completa de push constants, ordem de vector shrinking/int64 e offsets de
constantes IR3 por componente. KGSL MR 44838 e A840 com dois/três slices
seguem upstream.

## O que esta versão não faz

- **Nenhum tuning de desempenho.** Não existe hoje uma melhoria de desempenho
  para A6xx ou A7xx com evidência. A MR !43714 (cortar flushes de resolve
  sysmem vazios) foi rejeitada: o pipeline upstream falhou em todos os jobs
  Vulkan a618/a660/a750.
- Nenhuma extensão, feature, limite ou ID de GPU novo. `tu_device.cc` e
  `freedreno_devices.py` não são tocados pelos patches novos.
- A8xx continua experimental. A825/A812 seguem isolados por chip ID; A850/A845
  (MR !45384) não entram sem hardware.
- Profundidade (0004), GCM/suballocadores (0005) e perfis Zelda (0006) continuam
  fora do pacote, como na 5.7.8.1. Essa retirada pode mudar comportamento em
  relação à Latest; compare antes de concluir.

## Limitação conhecida (A8xx)

Os commits 3-7 da MR !44352 (`draw_id_offset`) ficaram de fora porque alteram
os VS params de indirect draws em todas as famílias e seguem em revisão. Por
isso, em A8xx, `gl_DrawID` reinicia em 0 a cada pacote **somente** nos draws que
excedem o limite. Antes, esses mesmos draws terminavam em GPU fault.

## Variantes

- Standard: universal; variante do Odin 2 Portal/A740.
- OneUI: mesmo código, mais o TP_UBWC_FLAG_HINT restrito às duas entradas KGSL
  da FD740. Os patches 0009-0012 são idênticos nas duas.

## Instalação e avaliação

Importar o ZIP no AdrenoTools ou no emulador compatível. Preservar o ZIP Latest
para rollback. Registrar hash e identidade efetiva do driver. Protocolo:
[VALIDATION-PLAN.md](../VALIDATION-PLAN.md).
