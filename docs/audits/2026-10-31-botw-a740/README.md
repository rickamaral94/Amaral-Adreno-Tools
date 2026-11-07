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

- **GPU:** o diagnóstico informa 14,9 ms por quadro real. Não se sabe se as submissões do LSFG (~4–5 ms) já entram
  nessa conta, e a união de timestamps é um envelope, não ocupação provada (ver PR #38). Mesmo somando as duas, ≈ 20 ms
  contra ~35,7 ms por quadro real a 28 quadros/s.
- **Thread de render:** 31,5% do tempo de parede ociosa (`render-idle`) e 29% dentro do `vkQueuePresentKHR`
  (média de 5,9 ms por apresentação; p95 de 22,7 ms). Os valores "por frame" do diagnóstico são **por apresentação**:
  o PR #38 estima ~10,6 ms de CPU de render por quadro real. Esse bloqueio é a contrapressão do FIFO no BufferQueue do Android, não o Turnip.
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
   - O fim de uma submissão dentro de outra não deveria acontecer na mesma fila.
   - **Hipótese:** outra fila ou outro `VkDevice` (o LSFG), cada um com o seu contexto KGSL, que se intercalam.
   - **Rival** (PR #38): reuso ou reset de slot de query antes da leitura no `diag.c`.
   - Teste que separa as duas: marcar cada intervalo com fila/device, serial de submissão e geração do slot.
   - Para medir uma submissão com exatidão, usar `ALL_COMMANDS` no início também. Isso custa um WFI por submissão,
     ~9 por quadro. A união dos intervalos é envelope, não ocupação.
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
   - `VK_KHR_performance_query` exige `TU_DEBUG=perfc` **e** `is_perf_cntr_selectable`, que é `false` no backend
     KGSL. Então não está disponível no Odin.
   - O `CP_ALWAYS_ON_COUNTER` é um relógio fixo de timestamps, não a frequência do núcleo.
   - Sem contador de frequência confiável, fixar o modo de energia e registrar a temperatura.

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
- **Previsão:** a fatia do `memcpy` chamado por `tu_CmdBindPipeline` (3,9%) some. (Escrevi antes "o Turnip cai
  ~3–4 pontos"; estava errado, porque esse `memcpy` é contado no módulo `libc.so`, não no Turnip.) Tempo de GPU e FPS sem mudança fora do ruído, porque a thread de render não está saturada (seção 2).
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

## 7. Resultado do A/B (31/10, 09:17 e 09:25)

O Rick rodou as duas no Odin, com LRZ ligado, 1x, framegen 2x e `perf-diag` de 60 s: primeiro a lab, depois a
5.7.16.1. Cada `libvulkan_freedreno` carregado foi traduzido com o próprio binário.

| | Lab bindpipeline | 5.7.16.1 |
|---|---:|---:|
| Desenhos / binds de pipeline / sets por 2 s (média na janela) | 90.655 / 21.818 / 73.645 | 97.864 / 24.266 / 79.258 |
| Temperatura do SoC | 39–55 °C | 51–69 °C |
| CPU da thread de render por apresentação | 5,35 ms | 6,07 ms |
| `tu_CmdBindPipeline` (código próprio) | 1,06% | 1,73% |
| `memcpy` etc. chamados de `tu_CmdBindPipeline` | 0,81% | 3,19% |
| **Total ligado ao bind de pipeline** | **1,87%** (37 amostras) | **4,92%** (102 amostras) |
| Fatia do módulo `libvulkan_freedreno.so` | 28,3% | 26,9% |

- **Mecanismo confirmado; magnitude preliminar.**
  - A remoção da cópia está demonstrada pelo código e pelo disassembly.
  - A queda de ~60% por `vkCmdBindPipeline` é uma estimativa. As amostras vêm só dos blocos de 5 s com a amostragem
    ligada, e a contagem de binds é da janela inteira; CPU e carga também diferiram.
  - Na lab, o que ainda aparece como chamador em `tu_CmdBindPipeline` é a chamada de
    `vk_cmd_set_dynamic_graphics_state`, um custo separado. A cópia de `0x2770` bytes não está mais lá.
  - Em tempo, ~0,3 ms → ~0,1 ms por apresentação. Não converti para quadro real: 2x de framegen não garante duas
    apresentações por quadro real.
- **O que não dá para atribuir à lab:** FPS (29,20 × 27,24), GPU por quadro real (14,65 × 8,14 ms) e a CPU total da
  thread. As janelas diferem em carga (+8% de desenhos e +11% de binds na 5.7.16.1) e em temperatura, e a da 5.7.16.1
  inclui uma parada de ~3 s por compilação de shaders do app (cache de pipeline vazio).
  - A métrica de GPU também é inconsistente entre as duas: 3.828 intervalos contados e 8.430 aninhados na 5.7.16.1,
    contra 7.928 e 4.856 na lab.
- **Estabilidade:** a sessão da lab durou ~7,5 min sem device lost nem erro registrado. A conferência visual é do
  Rick.
- **Para fechar o gate de desempenho:** AB/BA com cache de pipeline aquecido, mesma cena e o aparelho na mesma
  temperatura, em cinco rodadas por variante, medindo o custo por bind e a CPU da thread de render.

## 8. Revisão do ChatGPT (4b6b, 31/10)

**Aprovada no escopo de laboratório isolado**, sem inclusão nem release. Revisão estática; build, CTS e VVL do
revisor ficaram not-run. Antes de qualquer inclusão, testar:

- pipeline de biblioteca (GPL) depois de destruir as bibliotecas;
- secondary command buffer e rebind no primary;
- alternância gráfico/compute;
- tessellation e FDM;
- trace `draw` ativo.

Para uma proposta upstream: deixar o membro `const` e corrigir a assinatura da tracepoint (hoje `char *`). Levar ao
upstream só depois da validação e com autorização do Rick.
