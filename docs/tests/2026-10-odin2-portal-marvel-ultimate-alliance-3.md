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
| `20261027-195410-6755` | 5.7.15.1 Standard (controle), `5dc729c6a0ba605c3fd5d31b9cd80d5ca48107e5dfd1d5354c3f6cff0da874ec` | 795,53 s | 29,73 | 20,3 / 23,0 / 30,5 | Hashes do manifesto verificados |

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

## Controle 5.7.15.1 (mesma configuração)

A captura `20261027-195410-6755` usa o mesmo Eden e o mesmo hash de ajustes
(`991ea2e0…`) da 0705, com a 5.7.15.1 Standard no lugar da 5.7.16.1.

| Métrica | 5.7.15.1 (6755) | 5.7.16.1 (0705) |
|---|---:|---:|
| FPS médio | 29,73 | 29,75 |
| Intervalo p50/p99 | 33,5 / 34,25 ms | 33,5 / 34,25 ms |
| Intervalo máximo | 200,5 ms | 577,5 ms |
| GPU p50/p90/p99 | 20,3 / 23,0 / 30,5 ms | 19,8 / 20,5 / 30,0 ms |
| Pipelines criadas em runtime | 0 | 0 |
| Erros registrados | nenhum | nenhum |

Nesta carga não há sinal de regressão da 5.7.16.1. A pausa maior da 0705 foi
única, no início, sem compilação e logo depois de um `trim_memory`; com uma
única ocorrência, não se atribui ao patch. A foto do controle (EXIF 20:00:28Z)
mostra gameplay nítido. Limites: a rota não foi marcada, a 5.7.16.1 não tem
foto e minimizar/retomar não foi registrado em nenhuma das duas.

## Próximos testes

1. 5.7.16.1 com foto e com minimizar/retomar, no mesmo trecho do controle.
2. Para as pausas: marcar a cena e repetir o trecho inicial sem limpar o cache.
