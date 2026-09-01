# Turnip Amaral 26.3.0-devel v4.5 Candidate

Esta é uma **pré-release de validação**. A v4.4 permanece Latest e é o fallback
recomendado.

## Principais mudanças

- Mesa main atualizado de `451e4a464788` para `eaa8cb690243` (01/09/2026).
- Novas correções upstream para cache/pipelines, descriptors, D32S8 sparse,
  geometry shaders, IR3, autotune e temporização da GPU.
- Perfis BOTW/TOTK reconstruídos do comportamento do Balemuni Apex V2 e
  isolados por aplicativo para qualquer A6xx/A7xx/A8xx compatível.
- Removida a regra que aplicava workarounds a todo `yuzu Emulator`.
- Standard e OneUI continuam geradas da mesma fonte; OneUI altera somente
  FD740/KGSL.

## Sobre os perfis Zelda

Eles não são uma promessa de mais FPS. O objetivo é testar correções de água e
flicker em BOTW e de grama/terreno/profundidade em TOTK. O perfil só funciona
quando o emulador/frontend coloca `botw` ou `totk` em `pApplicationName`.

BOTW usa as opções de compatibilidade observadas no Apex V2 e
`prefer_gmem`. TOTK usa o mesmo conjunto mais
`tu_ignore_frag_depth_direction`. Fora desses títulos, o autotuner e o
comportamento upstream permanecem inalterados.

## O que foi deliberadamente recusado

- GMEM/SYSMEM ou `TU_DEBUG` forçado globalmente;
- cache de shader de 4 GiB sem A/B;
- tuning Cortex-X3 em um pacote universal;
- hacks globais A8xx de UBWC, FDM/MSAA, NOCB ou shared memory;
- patches MrPurple sem fonte pública correspondente.

## Base técnica

| Item | Valor |
|---|---|
| Mesa | `26.3.0-devel` |
| commit | `eaa8cb690243d25c9b5ccc40e11a0d0d5a836d0f` |
| Vulkan headers | `1.4.359` |
| NDK | r29 |
| ABI/KMD | arm64-v8a / KGSL |

Arquivos:

- `turnip_amaral_26.3.0-devel_v4.5.zip`
- `turnip_amaral_26.3.0-devel_v4.5_oneUI.zip`

## Validação solicitada

Compare com a v4.4 usando a mesma versão do emulador, save, configuração,
resolução e cache. Registre qualidade gráfica, crashes, FPS, P95/P99, stutter,
temperatura e consumo. Compatibilidade visual tem prioridade sobre qualquer
ganho médio.
