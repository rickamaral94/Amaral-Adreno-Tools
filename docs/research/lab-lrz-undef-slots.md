# Lab: slots de cor sem formato não contam como escrita parcial no LRZ

Pedido do Botwnspxci na campainha ([Botwnspxci #3](https://github.com/rickamaral94/Botwnspxci/pull/3), comentário
7173722397), depois da leitura do trace da Amaral.20 (comentário 7173650893).

## Problema

`tu6_calc_blend_lrz` (`tu_pipeline.cc`) conta os alvos escritos só entre os slots com formato definido, mas compara
essa contagem com `cb->attachment_count`, que também inclui os slots `VK_FORMAT_UNDEFINED`. Um pipeline com um slot
vazio no meio sempre sai como `TU_LRZ_BLEND_READS_DEST_OR_PARTIAL_WRITE`. Assim, todo draw que escreve depth chama
`tu_lrz_disable_write_for_rp("Depth write + blending")`, e o LRZ não é escrito no resto do render pass.

No BOTW (LARecomp), o G-buffer liga albedo e normais em dois slots cada e deixa o duplicado sem view e com formato
`UNDEFINED`. O trace 23410 (v5.9.19.1 padrão) mostra `lrz=true` com `lrzWriteDisableReason="Depth write + blending"`
em todos os passes 1600x900 de 5 e 6 cores. Sem escrita de LRZ, o teste de LRZ do G-buffer não descarta nada.

Um slot sem formato não tem anexo: não é lido nem escrito. Não muda a análise de "lê o destino".

## Mudança (só no lab)

`docs/research/lab-lrz-undef-slots.patch`, sobre a série Standard da 5.9.19.1 (Mesa `8e0f6be`):

- compara os alvos escritos com `total_color_attachments`, os slots com formato, em vez de `cb->attachment_count`;
- `TU_LAB_LRZ_UNDEF_SLOTS=0` volta à comparação atual, então o mesmo ELF serve para o A/B;
- continuam marcando `READS_DEST`: blend ligado, logic op que lê o destino, `write_mask` parcial e
  `colorWriteEnable` desligado em slots com formato;
- vale para os dois pontos de cálculo: o estado de pipeline e o estado dinâmico.

## Verificação

- Build Android Standard (NDK r29, `scripts/build_universal.sh`, série Standard + este patch):
  - ZIP `turnip_amaral_27.0.0-devel_v5.9.19.1_lab-lrzslots.zip`, SHA-256
    `801393f4458b907bd14382691a1386d85c99e96095060064e64ae77081fee114`;
  - ELF `842ffc56faa977908fbd90689bb4f5a463988d1d38a7f9c7a9f5b102efe97570`, build-id
    `d44e0d296a5bcd1f0f05510e36e5ef1adf59a15d`;
  - patch SHA-256 `cc098014aecb5427cbcd57e00122a721825f703d25ed70038397ef99c9365a4b`.
- Host (Turnip `debugoptimized`, `b_ndebug=false`, drm-shim com `FD_GPU_ID=740`, `TU_DEBUG=perf`),
  `tools/research/lab-tests/lrzslots.c`: slots `{RGBA8, UNDEFINED, RGBA8}`, D32 com `LESS` e escrita, 8 draws.

  | Máscara do slot 2 | Lab (sem variável ou `=1`) | `TU_LAB_LRZ_UNDEF_SLOTS=0` |
  | --- | --- | --- |
  | `0xf` (completa) | sem "Depth write + blending" | "Depth write + blending" no draw 1 |
  | `0x7` (parcial) | "Depth write + blending" no draw 1 | "Depth write + blending" no draw 1 |

  O drm-shim não executa a GPU: esse teste confere a decisão do driver, não o resultado na tela.
- **Not-run:** hardware, CTS e VVL.

## A/B pedido no Odin

O mesmo APK, rota e cena (a área densa, com 4.700+ draws), com o lab instalado:

1. `TU_LAB_LRZ_UNDEF_SLOTS=0`, que é o comportamento da 5.9.19.1;
2. sem variável, que é o lab;
3. de novo `TU_LAB_LRZ_UNDEF_SLOTS=0`.

Medir:
- GPU por quadro real e tempo do G-buffer;
- quadros reais/s;
- trace curto (`MESA_GPU_TRACES=print`): `lrzWriteDisableReason` deve sumir dos passes do G-buffer no braço 2. Lembre que o
  `lrzStatus` não é confiável na A7xx (o trace lê só `buffer[0]` e sem flush);
- defeitos de profundidade: objetos sumindo, recortados ou aparecendo atrás de outros.

Critério para entrar numa candidata:
- ganho de GPU reproduzível no A/B/A;
- nenhum defeito visual;
- nenhuma regressão num segundo jogo (TOTK ou um jogo DXVK).
