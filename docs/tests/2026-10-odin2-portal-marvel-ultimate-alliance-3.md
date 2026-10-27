# Marvel Ultimate Alliance 3 no AYN Odin 2 Portal (A740) — outubro de 2026

Status: **observado**. Escopo: L0 (este aparelho e chip). O
[JSON de evidência](../../evidence/hardware-tests/2026-10-odin2-portal-marvel-ultimate-alliance-3.json)
guarda hashes e métricas selecionadas, sem logs brutos.

Hardware: AYN Odin 2 Portal, QCS8550, Adreno 740, Android 13 (API 33), KGSL,
ARM64. Workload: Marvel Ultimate Alliance 3 `010060700AC50000` no Eden
`6b592ecbeaac9631ffef1cb5735931ed1083189b`, Docked, 1×, SgsrEdge, FXAA,
anisotropia 16×, swapchain 1920×1080.

## Captura

| ID da captura Eden | Driver (ELF) | Duração | FPS | GPU p50/p90/p99 ms | Integridade |
|---|---|---:|---:|---|---|
| `20261027-184302-0705` | candidata [5.7.16.1](../candidates/5.7.16.1/README.md) Standard, `af80c8847a613da7bc4daf413a0cf5d20e5a5b34535fc99331fe568faea64486` | 923,06 s | 29,75 | 19,8 / 20,5 / 30,0 | Hashes do manifesto verificados |

Clock da GPU no máximo (680 MHz), ocupação média de 64,5%. O intervalo de
quadro tem p99 de 34,25 ms e 99,3% dos quadros ficam entre 28 e 38 ms. As 260
pipelines foram restauradas do disco: nenhuma foi criada nem esperada durante a
sessão. Não houve device lost, falha de pipeline nem mensagem do driver.

## O que se pode concluir

- **Execução sustentada sem erro registrado** da 5.7.16.1 no A740 nesta carga.
  Isso não confirma pixels, porque não há fotos nem relato visual.
- **Não é a regressão pareada** da candidata: falta a 5.7.15.1 Standard no mesmo
  trecho, com fotos e com o teste de minimizar e retomar.
- **Pausas:** houve duas, de 318,8 ms e 577,5 ms, aos 22,5 s e 23,6 s, sem
  criação de pipeline. Um evento `trim_memory` (running_critical) veio pouco
  antes, aos 21,7 s. A associação é temporal, sem causalidade demonstrada; a
  memória disponível mínima foi de 5.132 MiB e o estado térmico ficou em 0.
  Investigar com uma cena marcada e repetida antes de qualquer patch.
- O gralloc do Odin tem o magic `gmsm`, caminho que o patch SnapAlloc preserva.
  Esta captura não registra o ramo executado.

## Próximos testes

1. Controle 5.7.15.1 Standard no mesmo Eden, ajustes, rota e cache, com fotos e
   minimizar/retomar; depois a 5.7.16.1 no mesmo trecho.
2. Para as pausas: marcar a cena e repetir o trecho inicial sem limpar o cache.
