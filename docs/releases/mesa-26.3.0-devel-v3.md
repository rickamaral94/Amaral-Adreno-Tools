# Turnip Amaral 26.3.0-devel v3

A v3 atualiza o snapshot completo do Mesa para
`1b2e70de00f68f8cf32dca8cd1a64fba9b6410a8` e revisa o perfil experimental da
Adreno 825 com foco em correção visual, estabilidade e desempenho consistente.

## Drivers

- `turnip_amaral_26.3.0-devel_v3.zip`: variante padrão.
- `turnip_amaral_26.3.0-devel_v3_oneUI.zip`: mesma base, com o ajuste UBWC
  separado para a entrada FD740.

## Atualização do Mesa

O snapshot avança 84 commits em relação à v2 e incorpora, entre outras
correções upstream:

- correção do fence usado nos patchpoints de visibility stream do Turnip;
- correções no lowering de I/O do NIR;
- isolamento correto das condições entre passes de otimização algébrica NIR.

A atualização é cumulativa: contém todo o estado do Mesa até o commit fixado,
mais os patches Amaral listados abaixo.

## Perfil A825 revisado

Os issues do Driver Lab #37 e #38 mostraram o mesmo padrão: ganhos elevados em
compilação de shaders, cena estável e trace misto, mas divergência visual
repetida no GPU Stress. A v3 ataca a hipótese de pressão/layout de GMEM sem
alterar a topologia física da GPU.

| Propriedade | v2 | v3 |
|---|---:|---:|
| Color cache GMEM | HALF / 128 KiB | EIGHTH / 16 KiB |
| Depth cache GMEM | HALF / 128 KiB | FULL / 128 KiB |
| Tile alignment | 64 x 32 | 96 x 32 |
| CCUs / slices | 4 / 2 | 4 / 2 |
| GMEM físico | 2 MiB | 2 MiB |
| Shared memory | 32 KiB | 32 KiB |

Também foram removidos os dois workarounds específicos de pipeline da v2:

- FDM por camada volta ao comportamento normal do Turnip;
- sample interpolation volta a respeitar o estado de MSAA do pipeline.

A v3 deixa de afirmar `shading_rate_matches_vk = true` para a A825 até que VRS
seja validado no hardware. Isso não falsifica capabilities nem copia CCUs,
slices, GMEM ou limites físicos da A830.

## O que não foi incorporado

Continuam fora do pacote universal: GMEM/sysmem forçados globalmente,
`TU_DEBUG=flushall`, detecção UBWC sempre verdadeira, shared memory de 64 KiB,
perfis IR3 artificiais, spoof de GPU/Vulkan e hacks específicos de jogo.

## Validação solicitada

A A825 ainda é experimental. Compare a v3 com a v2 e com o driver Qualcomm nas
mesmas condições, executando ao menos três rodadas. Priorize:

- GPU Stress e checkpoints visuais do Amaral Driver Lab;
- jogos com depth, MSAA, pós-processamento e geometria pesada;
- Eden, Cemu, Vita3K e workloads DXVK/VKD3D;
- crash, GPU hang, device lost, artefatos e frametime.

A v2 permanece publicada como fallback durante toda a validação da v3.
