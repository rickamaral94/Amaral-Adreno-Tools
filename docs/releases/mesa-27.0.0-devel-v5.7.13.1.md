# A740 Readback Lab 5.7.13.1 — gate FD740 corrigido

A captura V3 do Odin mostrou `chip=0x43050a01`, `gpu=6760` e `scope=0`.
V4 aceita os chip IDs FD740 já existentes no Mesa como identidade suficiente
para os contadores de readback, preservando o caso legado `gpu_id=740, chip_id=0`.
O heartbeat direto A7xx permanece para confirmar o resultado em hardware.

Mesmo Mesa/base Standard 5.7.8.1, sem tuning, alteração de comandos GPU ou
promessa de FPS. Somente branch de laboratório, sem promoção/publicação.

[Protocolo](../READBACK-LAB.md) · [evidência V3](../READBACK-THIRD-RESULT.md).
