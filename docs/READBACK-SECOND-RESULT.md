# Readback Lab V2: captura física 2026-10-21 14:44

Captura Eden `20261021-144443-7278`, Odin 2 Portal A740, Little Nightmares.
ZIP SHA-256 `b1295d18f1ddd1b150d1e59657c2bd9d3d36af400b4e4cdc76949b04bf18b723`;
manifesto verificado. ELF carregado SHA-256
`dd8472af1125fc9295fc1b433eedfbe94694cd0232f171600e538312e56e8f47`:
Standard Lab 5.7.11.1 exata. Eden commit
`6b592ecbeaac9631ffef1cb5735931ed1083189b`, hash efetivo de settings
`1337a7f3ed7ba6f34966a9a3f4a1dbdaaa09f2f8b80f3c8bd56007b8057b5406`.

Em 817,607 s: 44,01 FPS, GPU p50/p90/p99 14,25/25,75/27,75 ms, 591,0
draws e 116,9 passes por quadro. Cache restaurou 372 pipelines e nenhum novo
foi criado. 240 esperas texture_download somaram 3,292 s; guest_sync em outra
thread somou 433,76 s. Tempos de threads se sobrepõem. Captura encerrada pelo
usuário, sem falha de pipeline/tradução reportada.

O `logs/driver_logcat.txt` contém 27 linhas e declara zero descartes, mas nenhuma
`AMARAL_RB_V2`. O Eden reportou 155.736 submits; isso não prova qual callback
Turnip foi usado. O filtro de ID A740 da V2 roda antes do log, por isso a
ausência de heartbeat não distingue GPU/chip ID diferente, callback não
atingido ou destino do log. Não concluir que não houve readbacks/cópias por linha.

A V3 registra a identidade recebida pelo Turnip em ambos os callbacks de fila
A7xx, antes do filtro A740/Eden, usando o log Android direto com limite de uma
linha por dez segundos. Os contadores de cópia permanecem gated para A740/Eden.
Se a V3 não registrar nem `AMARAL_RB_V3`, verificar callback ou coleta logcat
antes de outro tuning. Sem medições de tempo GPU por operação, não atribuir os
40–45 FPS às cópias. Não há resultado A/B qualificado ou ganho certificado.

Registro público desta captura:
https://github.com/rickamaral94/Amaral-Adreno-Tools/blob/main/docs/tests/2026-10-odin2-portal-little-nightmares.md
