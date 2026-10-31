# BOTWRecompAndroid no Odin 2 Portal (A740): avaliação do Turnip (31/10/2026)

Status: **análise e lab de teste**. Nada aqui foi promovido. Base: `AVALIACAO-TURNIP-2026-10-31.md`,
`PROMPT-TURNIP-GPU.md` e os logs `logs-botwrecomp-2026-10-31.zip` enviados pelo Rick. Os logs brutos ficam fora do
repositório.

## 1. Qual driver foi medido

O "turnip_amaral 27.0.0-devel v5.7.13.1" da avaliação é a **Readback Lab 5.7.13.1** do PR #26 (Mesa `4b0f64ceac`),
um build de diagnóstico, não uma candidata. Recompilei o head `3bbbdee` do PR #26 e o resultado é bit a bit o driver
medido:

| | Build ID | SHA-256 do ELF |
|---|---|---|
| Driver do log | `56becd8cf1d7c217e30cb37c4f5dd4814677e68b` | — |
| Recompilação local (Standard) | `56becd8cf1d7c217e30cb37c4f5dd4814677e68b` | `eb5d61626888b414d0a2a003a68440a961685f0739fbfeaf1b6d46e9ee988975` (o mesmo do registro do Little Nightmares) |

Com isso os endereços da amostragem viraram nomes de função (seção 3). Os contadores da lab só ligam para FD740 com
o Eden; no BOTW o filtro fica desligado.

## 2. Onde está o limite nesse trecho

Números do `perf-diag` de 30/10 23:16 (LRZ ligado, 1x, framegen 2x).

- **GPU:** 14,9 ms por quadro real, mais ~4–5 ms do LSFG, ≈ 19–20 ms. A 28 quadros reais/s, o quadro real dura
  ~35,7 ms, então a GPU fica ocupada pouco mais da metade do tempo. Isso bate com os ~70% de ocupação a clock reduzido.
- **Thread de render:** 31,5% do tempo ociosa (`render-idle`) e 29% bloqueada dentro do `vkQueuePresentKHR`
  (média de 5,9 ms; p95 de 22,7 ms). Esse bloqueio é a contrapressão do FIFO no BufferQueue do Android, não o Turnip.
- **Thread principal do jogo (t80):** metade do tempo em `svc-block` (ArbitrateLock, WaitForAddress).

**Leitura (hipótese):** se o alvo de quadros reais é 30, nesse trecho nem a GPU nem a thread de render são o
gargalo, e um ganho de driver não sobe a média de 28 FPS. O ganho de driver aparece nos trechos pesados, onde a GPU
chega a 23–27 ms mais o LSFG, ≈ 30 ms, já no limite de 33,3 ms, e em consumo e temperatura.

- **Rival:** a meta do app é 60 quadros reais. Aí a GPU já seria o limite em todo trecho.
- **Teste:** confirmar a meta de quadros reais no app.

## 3. CPU dentro do Turnip (thread de render)

O Turnip responde por 27,7% das 2.144 amostras. Endereços traduzidos com o binário recompilado; as funções são as
variantes A7xx (`chip 7`):

| Onde | Amostras | O que é |
|---|---:|---|
| `memcpy` chamado por `tu_CmdBindPipeline` | 3,9% | cópia de `tu_program_state` (10.096 bytes) a cada bind de pipeline |
| `tu_bind_descriptor_sets<A7XX>` e o `memcpy` que ela chama | 2,3% + 2,1% | cópia de cada descritor dinâmico a cada bind |
| `tu_update_descriptor_sets`, `tu_AllocateDescriptorSets`, `tu_ResetDescriptorPool` | 2,4% | sets novos por desenho (chamados pelo app) |
| `tu_CmdBindPipeline` (código próprio) | 1,8% | estado dinâmico do pipeline |
| `__aarch64_ldadd4_relax` | 1,6% | incremento atômico; chamador ainda não identificado |
| `tu_barrier`, `tu_setup_dynamic_render_pass`, `tu6_emit_lrz`, `tu6_draw_common` | ~2% | por passe e por desenho |

Conclusão: cerca de metade do tempo do Turnip nessa thread é **bind de pipeline e de descriptor set**. Uma parte
disso é cópia que o driver não precisava fazer (lab da seção 5), e a maior parte vem do padrão do app de alocar e
gravar um set por desenho (seção 4).

## 4. Os pontos da avaliação, contra o código

As referências de código são da Mesa `69f1f21`, a base da 5.7.14.1 e posteriores. Onde a `4b0f64ceac` é diferente,
isso está dito.

1. **Timestamps.**
   - `tu_CmdWriteTimestamp2` (`tu_query_pool.cc`) só emite WFI quando o estágio não é top-of-pipe.
   - `VK_PIPELINE_STAGE_2_NONE` vale 0, então não tem WFI. O contador é lido quando o CP chega ao comando, que pode
     ser antes do fim do trabalho anterior. O spec permite isso.
   - `ALL_COMMANDS` emite WFI e depois lê `CP_ALWAYS_ON_COUNTER`. Na mesma fila, ele não pode sair antes do fim do
     trabalho anterior.
   - O fim de uma submissão dentro de outra indica **outra fila ou outro `VkDevice`**: cada um tem o seu contexto
     KGSL, e eles se intercalam. O Turnip expõe uma única fila gráfica.
   - Hipótese: o LSFG usa um device próprio.
   - Teste: marcar cada intervalo com a fila ou o device. Para medir uma submissão com exatidão, usar `ALL_COMMANDS`
     no início também: custa um WFI por submissão, ~9 por quadro. A união dos intervalos continua correta.
2. **UBWC em A2B10G10R10.** O defeito foi visto na **A830 com o Turnip 26.3-devel**, que é o caminho A8xx
   experimental.
   - O padrão de blocos 16x4 é o bloco UBWC de 32 bpp. Isso sugere ler dado comprimido sem a decodificação dos
     metadados.
   - No A740 não foi testado.
   - Teste: religar a compressão dessas imagens no A740 com a 5.7.16.1 e comparar com a imagem sem compressão. Se
     aparecer, entra em T-a8xx-compat/T-a7xx com reprodução mínima.
3. **LRZ.**
   - O Turnip desliga o LRZ por desenho, e diz o motivo, quando o fragment shader descarta ou escreve profundidade,
     quando o teste é ALWAYS/NOT_EQUAL, quando a direção muda e com blend.
   - `TU_DEBUG=perf` escreve no logcat "Disabling LRZ because …" e "Disabling gmem due to …".
   - É o teste mais barato para saber quais passes perdem o LRZ, sem build novo.
4. **Feedback loop em `GENERAL`, sem a extensão.**
   - O Turnip expõe `VK_EXT_attachment_feedback_loop_layout` (`attachmentFeedbackLoopLayout = true`). Com ela, o
     driver força sysmem só no passe que tem o loop (`tu_pipeline_update_rp_state`).
   - Isso não custa nada aqui, porque o autotune já escolhe sysmem. Também não muda o UBWC da imagem: não há caso
     especial em `tu_image.cc`.
   - Ganho: o caso fica definido pelo spec em vez de depender do comportamento atual.
   - Com loop de profundidade, o Turnip troca para `EARLY_Z_LATE_Z`.
5. **Constant buffers de 16 bytes por desenho.** Na A7xx, os push constants vão como **shared consts**: escrita
   direta em `SP_SHARED_CONSTANT_GFX`, dentro do draw state (`tu6_emit_shared_consts`), sem buscar memória. Hoje:
   - cada bind de set novo faz o CPU alocar e gravar o set e copiar os descritores dinâmicos;
   - na GPU, `SP_UPDATE_CNTL` invalida o cache de bindless de **todos** os sets gráficos (`gfx_bindless = 0xff`).

   16 bytes cabem com folga nos 256 de `maxPushConstantsSize`. A promoção de UBO para registradores do ir3
   (`ir3_nir_analyze_ubo_ranges`) só pega faixas de offset constante, o que explica `nouboopt` não mudar nada.
6. **`maxStorageBufferRange` de 128 MB.**
   - O limite vem de `max_storage_buffer_range_bytes = 1 << 27` na A7xx (`freedreno_devices.py`).
   - Já existe a opção driconf `tu_enable_ssbo_emulation`, presente na 5.7.13.1 e na `69f1f21`. Ela sobe o limite para
     2 GB − 1 baixando os SSBOs para acesso global com checagem de limites (`nir_lower_ssbo`).
   - O driconf aceita sobrescrita por variável de ambiente com o mesmo nome (`xmlconfig.c`).
   - O upstream liga essa opção para jogos UE5 em `a799b0baca9`.
   - Custo: ALU de checagem por acesso. Alternativa: `bufferDeviceAddress`, que gera o mesmo `ldg` sem a checagem.
   - Medir antes de adotar.
7. **`uniformAndStorageBuffer8BitAccess`** está fixo em `false` em `tu_device.cc`. Ligar exige trabalho no ir3; fica
   fora de prioridade.
8. **26.2 "Turnio R4" bloqueando no `ioctl`.** É um build de terceiros sem fonte publicada. Sem a fonte não dá para
   atribuir a causa.
9. **Medição.**
   - `VK_KHR_performance_query` só aparece com `TU_DEBUG=perfc`, e só se o KGSL deixar selecionar contadores.
   - Para separar trabalho de frequência sem root, comparar o `CP_ALWAYS_ON_COUNTER` (relógio fixo) com um contador
     de ciclos do CP no mesmo intervalo.

**Upstream desde a `69f1f21` (main de 31/10, `fd8ef2befaf`):** nada novo sobre custo por desenho ou por passe. O que
importa para o A740 já está na triagem c89d:
- `2fae1d0`: alinhamento de varyings nas a7xx gen1/gen2, que inclui o FD740;
- as melhorias de propagação de BNOT no ir3.

## 5. Lab: `5.7.16.1-botwlab-bindpipeline`

- **Mudança:** `cmd->state.program` passa de cópia (`struct tu_program_state`, ~10 KB) para ponteiro para o
  `program` do pipeline vinculado. O patch tem 22 linhas inseridas e 18 removidas, em `tu_cmd_buffer.{h,cc}` e
  `tu_pipeline.cc` ([patch](lab-tu-program-state-pointer.patch)).
- **Por que é seguro:**
  - Todos os leitores rodam na gravação de um desenho, depois de um bind.
  - O Turnip não tem shader object, então nada mais grava esse estado.
  - O pipeline já precisa viver enquanto os comandos que o usam existirem, como acontece com `cmd->state.shaders`.
  - A tracepoint de desenho copia as hashes com `strcpy`.
- **O upstream ainda copia.** Se o teste confirmar o ganho, isso vira proposta de MR.
- **Build:** só Standard, sobre a integração 5.7.16.1 (`3951b69`) mais este patch.
  - ZIP `d469a1fc118d96a06777f34fd9dcd62a49ad0557973284cb9dc52c0bd690a9b1`.
  - ELF `32c550704520f8bc601a93908cd091be21d7e3e1ba968903743a85eb58177631`, Build ID
    `9c55cbaed1749f6569dcf53c1f540e9a0736f0e4`.
  - `validate_artifact.sh` passou.
  - No disassembly, `tu_CmdBindPipeline` da 5.7.13.1 e da 5.7.16.1 tem a cópia de `0x2770` bytes; a da lab não tem.
  - Não houve dupla build de reprodutibilidade, CTS nem hardware.
- **Referência do A/B:** 5.7.16.1 Standard, ZIP `3b27ca71d5719edf16ed746755cf2cf82f075e16c034be602124a1f03ea38792`.
- **Previsão:** a fatia do `memcpy` chamado por `tu_CmdBindPipeline` (3,9%) some, e o Turnip cai ~3–4 pontos na
  thread de render. Tempo de GPU e FPS sem mudança fora do ruído, porque a thread de render não está saturada (seção 2).
- **O que derruba a hipótese:**
  - a fatia não cair;
  - aparecer qualquer defeito visual ou travamento que a 5.7.16.1 não tem no mesmo trecho.

## 6. Próximos testes (Rick)

1. **A/B de driver, sem mudar o app:** 5.7.16.1 Standard contra a lab, no mesmo trecho do lago, com LRZ ligado, 1x e
   `perf-diag` de 60 s cada.
   - A 5.7.16.1 também serve de referência contra a 5.7.13.1: a base Mesa mudou.
   - Eu tenho o binário com símbolos das duas, então traduzo os endereços.
2. **`TU_DEBUG=perf`** por ~30 s no mesmo trecho, só para o logcat com os motivos de LRZ e GMEM. Nessa execução não
   se mede desempenho, porque o log pesa.
3. **No app (opcional, maior ganho esperado na CPU):**
   - push constants para os 16 bytes por desenho;
   - sets persistentes;
   - pular binds repetidos;
   - a extensão de feedback loop.

   Cada um com o mesmo A/B.
