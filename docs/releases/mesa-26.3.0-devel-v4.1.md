# Turnip Amaral 26.3.0-devel v4.1 — A825 refinada

A v4.1 mantém o driver universal para as GPUs A6xx, A7xx e A8xx reconhecidas
pelo Mesa e atualiza apenas o perfil experimental da Adreno 825. A release
continua disponível nas variantes Standard e OneUI e substitui a v4 como
estável/latest; a v4 permanece como fallback.

## Drivers

- `turnip_amaral_26.3.0-devel_v4.1.zip`: variante Standard, recomendada para
  começar os testes.
- `turnip_amaral_26.3.0-devel_v4.1_oneUI.zip`: mesma base e mesmas melhorias,
  mais o ajuste UBWC restrito às entradas KGSL da FD740.

## Perfil A825 atualizado

A evidência comunitária do
[DiskDVD/TurniptoolsA8XX](https://github.com/DiskDVD/TurniptoolsA8XX/releases/tag/tu_A8XX-Y2.5)
mudou a classificação da A825: há aparelhos reais executando os modos GMEM e
SYSMEM. A v4.1 incorpora
somente as propriedades de hardware que podem permanecer isoladas no `chip_id`
KGSL `0x44030000`:

- color cache GMEM: `HALF / 128 KiB`;
- depth cache GMEM: `HALF / 128 KiB`;
- tile alignment: `64 x 32`;
- shared memory: `64 KiB`;
- offsets VPC de `49152 / 24576 / 32768`, já presentes na v4, preservados;
- topologia de 4 CCUs, 2 slices e 2 MiB de GMEM preservada.

O autotuner upstream continua livre para escolher GMEM ou SYSMEM. A release não
força `TU_DEBUG`, não altera outras GPUs e não anuncia capacidade Vulkan sem
validação.

## O que não foi importado

O repositório comunitário também combina alterações globais e experimentais.
Ficaram fora da v4.1:

- desativação de FDM/sample interpolation;
- mudanças UBWC para toda a família A8xx;
- correspondência VRS/Vulkan não comprovada;
- perfis IR3/FP16 gerados sem A/B reproduzível;
- GMEM ou SYSMEM forçado;
- spoof de GPU, versão Vulkan ou Steam Deck.

Essas exclusões preservam a ordem do projeto: compatibilidade gráfica,
estabilidade, frametimes consistentes e desempenho.

## Mesa e Vulkan

A base foi atualizada para o Mesa `26.3.0-devel`, commit
`6e41d819219d7f4025a95cbbaddfbe492d210ff3`, auditado em 20/08/2026. O snapshot
está oito commits à frente da v4; as mudanças intermediárias pertencem a
documentação, CI/CTS, Broadcom, VC4 e Panfrost/PanVK. Portanto, a atualização do
Mesa não traz uma alegação específica de FPS ou correção Turnip nesta release.

O cabeçalho permanece em Vulkan 1.4.359.

## Conteúdo preservado da v4

- compatibilidade de build com Android NDK r29;
- `VK_EXT_depth_range_unrestricted` e o subconjunto validado de
  `VK_EXT_depth_bias_control` apenas nas entradas KGSL da FD740;
- OneUI com `TP_UBWC_FLAG_HINT` somente nas duas entradas KGSL da FD740;
- AArch64 `armv8-a`, API 29 e backend KGSL;
- duas compilações independentes por variante, comparadas byte a byte.

## Validação solicitada

Na A825, compare diretamente v4 e v4.1 com o Amaral Driver Lab e sessões reais
dos emuladores. Registre qualidade gráfica, crash/device lost, FPS, P50/P95/P99,
stutter, temperatura e consumo. Em outras GPUs, a expectativa é comportamento
equivalente à v4, pois o novo perfil não pode ser ativado fora do chip-id A825.
