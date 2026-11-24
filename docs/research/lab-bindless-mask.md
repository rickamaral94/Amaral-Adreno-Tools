# Lab: invalidação de descritores bindless por set (A7xx)

Pedido do Rick em 24/11/2026, a partir do caso Botwnspxci. Registro na campainha:
[Botwnspxci #3](https://github.com/rickamaral94/Botwnspxci/pull/3), comentários 7137681944 e 7137734949.

## Problema

A cada `vkCmdBindDescriptorSets` que chega a um draw, `tu6_emit_descriptor_sets` (`tu_cmd_buffer.cc`):

1. regrava a base de todos os sets vinculados;
2. emite `SP_UPDATE_CNTL(.gfx_bindless = 0xff)`, que invalida o cache de descritores dos 8 sets.

Um bind que só muda os **offsets dinâmicos** aloca um set reservado novo, com endereço novo, e paga a invalidação
completa. Os sets de textura e sampler, que não mudaram, também são buscados de novo.

No BOTW (LARecomp, Odin 2 Portal, v5.9.19.1), ~75% dos draws fazem esse bind: as constantes de cada draw vão para um
anel transiente com offset dinâmico novo. O G-buffer parece limitado por draw, não por pixel: o tempo de GPU é o mesmo
a 720p e a 900p, com ~3.000 draws.

## Mudança (só no lab)

`docs/research/lab-bindless-mask.patch`, sobre a série Standard da 5.9.19.1 (Mesa `8e0f6be`). Vale só para A7xx e só
para o ponto de bind gráfico. `TU_LAB_BINDLESS_MASK=0` volta ao comportamento atual, então o mesmo ELF serve para o
A/B.

- **No início de cada subpass:** uma invalidação completa escrita direto no `draw_cs`. Ela roda em todo bin e em
  sysmem, sem depender de visibilidade.
- **Dali em diante, em sysmem:** cada draw state de descriptor sets invalida todo set cuja base já mudou em relação à
  referência tirada na primeira emissão depois desse ponto. A máscara só cresce até o próximo subpass. Se um draw
  state for pulado, o seguinte invalida tudo o que já mudou.
- **Em GMEM e no binning:** continua `0xff`, por um `CP_COND_REG_EXEC` de modo de renderização. No a7xx o binning pode
  rodar em paralelo com a renderização, e não confirmamos se o cache de descritores é compartilhado entre eles.
- **Continuam com `0xff`:** command buffers secundários, o resto de um subpass depois de `vkCmdExecuteCommands`,
  passes retomados sem início de subpass e tudo fora dessa janela.
- **Sem mudança:** os caminhos que já invalidam tudo, como barreira com leitura de descritor e o `SP_UPDATE_CNTL` dos
  blits.

## Verificação

- Build Android Standard (NDK r29, `scripts/build_universal.sh`, série Standard + este patch):
  - ZIP `turnip_amaral_27.0.0-devel_v5.9.19.1_lab-bindmask.zip`, SHA-256
    `900999789d5f1505a6d4c497b83a2d70e46d919bb5ee56bd5b3ed0b4e3f96cc2`;
  - ELF `fd86b831fece4a5cfc2000fcf817f0afae1411f88ad9bc0ea7ec544e63df1495`, build-id
    `5660a37792d4c0ab0eb00865b0badd0d9bbf2536`;
  - patch SHA-256 `5b8af86f47cca65adbd4964f639351f623db5738784fcf86b8783569af3c717f`.
- Host com asserts (Turnip `debugoptimized`, `b_ndebug=false`, drm-shim com `FD_GPU_ID=740`):
  - teste de 3 render passes × 300 draws;
  - cada draw troca o offset dinâmico de um UBO, o set de textura troca a cada 50 draws, e há um
    `vkCmdClearAttachments` no meio do passe;
  - rodou no automático, com `TU_LAB_BINDLESS_MASK=0`, com `TU_DEBUG=sysmem` e com `TU_DEBUG=gmem`, sem assert. O
    tamanho do draw state com os dois ramos condicionais confere;
  - no gdb, o caminho do lab rodou em todos os 900 draws (897 comparações de 8 sets e 3 referências, uma por passe).
  - O drm-shim não executa a GPU: esse teste confere a gravação do command stream, não o resultado na tela.
- **Not-run:** hardware, CTS e VVL.

## A/B pedido no Odin

O mesmo APK, rota e cena, com o lab instalado:

1. `TU_LAB_BINDLESS_MASK=0`, que é o comportamento da 5.9.19.1;
2. sem variável, que é o lab;
3. de novo `TU_LAB_BINDLESS_MASK=0`.

Medir:
- GPU por quadro;
- tempo do G-buffer;
- se possível, o `drawCount` e o tempo por passe no trace (`MESA_GPU_TRACES=print`, `MESA_GPU_TRACEFILE`);
- defeitos de imagem: texturas trocadas ou piscando entre draws.

Critério para entrar numa candidata:
- ganho de GPU reproduzível no A/B/A;
- nenhum defeito visual;
- o mesmo resultado num segundo jogo (TOTK ou um jogo DXVK).
