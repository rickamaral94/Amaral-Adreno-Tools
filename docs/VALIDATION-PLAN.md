# Qualificação 5.7.9.1

Controle A: Latest 4.7.7.2. Candidata B: 5.7.9.1 Standard; OneUI em Samsung afetado.
Referência intermediária: 5.7.8.1 (mesmo Mesa, sem 0009-0012). Ela isola o
efeito dos patches novos: diferença A×5.7.8.1 = Mesa e retirada de 0004/0005/0006;
diferença 5.7.8.1×5.7.9.1 = patches 0009-0012.

1. Validar instalação, identidade, extensions/features e hashes. Confirmar que
   0009-0012 não alteram extensions, features ou limites em relação à 5.7.8.1.
2. CTS dirigido (herdado): descriptors/invalidação, push constants graphics/
   compute/GPL, constantes indiretas e offsets próximos de 511; IR3 int64.
3. A8xx (0009): `dEQP-VK.draw.*indirect*` e `*multi_draw*`; draw indirect e
   indirect count com `drawCount`/`maxDrawCount` acima de
   `((1<<20)-1)*4/stride`; confirmar ausência de fault e registrar o efeito em
   `gl_DrawID`. Cobrir A830 (issue #5, TOTK) e A825 (issue #12) quando houver.
4. A7xx (0010): Spider-Man Remastered e Ratchet & Clank Rift Apart via
   Winlator/vkd3d-proton (texel buffer emulation ativa por driconf); reproducer
   Amber da MR !45204 quando houver Amber Android.
5. A6xx (0011): `dEQP-VK.transform_feedback.*` com queries; Risk of Rain 2 via
   DXVK. Em A7xx/A8xx o código é idêntico ao anterior: rodar só o subset rápido.
6. Lifetime (0012): sessão longa com command buffers SIMULTANEOUS_USE em GMEM;
   memória do processo estável. Teardown sem device lost.
7. Regressão KGSL: wait-any/all, timeout zero, TS/FD mistos, submit, readback,
   teardown e device lost. MR 44838 permanece upstream.
8. A740/Odin 2 Portal Standard: Eden/Citron MK8D, BOTW/TOTK; Cemu Amaral Wind
   Waker HD, BOTW, readback e muitas draws; DXVK/VKD3D reproduzíveis.
9. Samsung FD740: Standard/OneUI, compositor/UI, textura/blit/escala.
10. AB/BA balanceado, cinco rodadas por cenário, cache frio/quente separados,
   temperatura/clocks controlados e gate térmico pré-definido. Nenhum patch novo
   é de desempenho; A/B serve para detectar regressão, não para alegar ganho.

Sem CTS, VVL e aparelho nesta preparação: status not-run. Não há ganho FPS alegado.
RPCSX/Xenia/Xeo entram apenas com cenas reproduzíveis e ambiente de execução real.
