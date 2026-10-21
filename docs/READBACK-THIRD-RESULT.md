# Readback Lab V3: captura física 2026-10-21 16:28

Captura Eden `20261021-162833-1341`, Odin 2 Portal/FD740/Little Nightmares.
Manifesto verificado; ZIP SHA-256
`980c156cbcc264ebcc86be30b4c6757bbc4c88de91f404c5288808e46c42c4bb`.
ELF carregado SHA-256
`b3aa76d16b409bded16c8c6d083b12b006f0c71c8933d0d89cc7bef5edc447cc`:
Standard Lab 5.7.12.1. Mesmo Eden commit
`6b592ecbeaac9631ffef1cb5735931ed1083189b` e settings efetivos
`1337a7f3ed7ba6f34966a9a3f4a1dbdaaa09f2f8b80f3c8bd56007b8057b5406`.

453,982 s; 41,06 FPS; GPU p50/p90/p99 13,75/26,25/29,75 ms. 557,4 draws
por quadro; 20 pipelines novos; uma espera texture_download de 7,4 ms. Sem A/B
qualificado ou cena marcada. Estes números não medem ganho de driver.

O logcat registrou 45 `AMARAL_RB_V3`, sem perda: todos `path=graphics`,
`gpu=6760`, `chip=43050a01`, `app_match=1`, `engine_match=1`, `scope=0`.
A entrada FD740 do Mesa usa o chip ID 0x43050a01. A Lab exigia adicionalmente
`gpu_id` 0 ou 740, mas o driver recebeu 6760. Portanto o filtro bloqueou as
contagens de readback e explica as mensagens ausentes da V2. Os campos
`regions=0` não significam zero cópias.

V4 corrige apenas o filtro diagnóstico: os dois chip IDs FD740 conhecidos
(0x43050a01 e fallback 0xffff43050a01) bastam para a identidade, com o caso
legado `gpu_id=740, chip_id=0` preservado. Outros IDs A7xx/A8xx seguem fora da
contagem. Não altera seleção de caminhos de cópia, sincronização ou GPU commands.
Próximo resultado necessário: confirmar `scope=1` no mesmo Odin e calcular
incrementos de `regions`, `row_layers`, `runs` e `r3d_regions` entre heartbeats.

Registro público:
https://github.com/rickamaral94/Amaral-Adreno-Tools/blob/main/docs/tests/2026-10-odin2-portal-little-nightmares.md
