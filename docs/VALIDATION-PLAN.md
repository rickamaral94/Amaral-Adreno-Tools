# Qualificação 5.7.14.1

Controle A: Latest 4.7.7.2. Candidata B: 5.7.14.1 Standard; OneUI apenas em
Samsung afetado. A 5.7.8.1 é controle intermediário. Esta candidata avança o
Mesa, mantém fora do pacote três patches não qualificados e reposiciona o patch
experimental A825 sem mudar seus parâmetros. A/B mede o conjunto; uma diferença
exige bisecção em builds de laboratório antes de atribuir causa.

1. Validar instalação, identidade, extensions/features e hashes. Confirmar retirada
   das duas extensões de profundidade e ausência de perda inesperada adicional.
2. CTS dirigido: descriptors/invalidação, push constants graphics/compute/GPL,
   constantes indiretas e offsets próximos de 511; IR3 int64/vector shrinking;
   `dEQP-VK.tessellation.*` dirigido, incluindo TCS com vértices de saída e pontos
   de controle diferentes (Mesa af60682 / MR !45416). Em A6xx, cobrir
   `dEQP-VK.transform_feedback.*` com queries e alternância de pipelines com e
   sem shared consts (Mesa cadc7e4 / MR !45447); se possível, reproduzir
   Risk of Rain 2 por DXVK. A MR !41860 foi fechada sem merge e seu patch de
   invalidação antes da query não está distribuído.
3. Regressão KGSL: wait-any/all, timeout zero, TS/FD mistos, submit, readback,
   teardown e device lost. MR 44838 permanece upstream.
4. A740/Odin 2 Portal Standard: Eden/Citron MK8D, BOTW/TOTK; Cemu Amaral Wind Waker HD,
   BOTW, readback e muitas draws; DXVK/VKD3D em workloads reproduzíveis.
5. Cobrir A6xx, A750 e A8xx disponíveis; reproduzir issues #12 A825 e #5 A830 com
   versão exata de jogo/emulador. Não concluir correção dos relatos antigos por build.
6. Samsung FD740: Standard/OneUI, compositor/UI, textura/blit/escala, sem generalizar.
7. AB/BA balanceado, cinco rodadas por cenário, cache frio/quente separados,
   temperatura/clocks controlados e gate térmico pré-definido. Registrar métricas
   da política; usar diagnósticos Cemu para separar CPU/GPU/sync/presentation.

Sem CTS, VVL e aparelho nesta preparação: status not-run. Não há ganho FPS alegado.
RPCSX/Xenia/Xeo entram apenas com cenas reproduzíveis e ambiente de execução real.
