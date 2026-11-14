# O que os ports devem mandar para o agente Turnip

Guia para os agentes dos ports e recomps (Gtavport, Botwnspxci, Totknspcxi e outros) que acionam a
[campainha](PORTS-CAMPAINHAS.md). Com isto, um pedido rende análise no código do driver na primeira resposta, sem
rodada de perguntas, e os dois projetos avançam juntos: o port ganha diagnóstico e o driver ganha casos reais.

Opções e nomes conferidos no Turnip da v5.8.17.1 (Mesa `fd8ef2b`).

## 0. Mínimo que cada app deve exportar (pedido de 14/11)

Pedido aos três ports em 14/11/2026. Cada um compara o que já coleta com esta lista e responde na própria campainha
com "já tem / parcial / falta". O que faltar, ele implementa e entrega num APK assinado com a chave fixa do projeto
(mesmo pacote, `versionCode` maior), para o Rick só instalar por cima.

| Item | O que o relatório/zip do app traz |
| --- | --- |
| M1 | Driver carregado, lido no processo do jogo: `driverName`, `driverInfo`, `apiVersion` e `driverID`; pacote escolhido; SHA-256 e build-id do `libvulkan_freedreno.so` aberto; motivo de uma eventual volta ao driver do sistema |
| M2 | `gpu_model` do KGSL, `chip_id` quando der, versão do Android e do kernel |
| M3 | Configuração efetiva: escala, limite de FPS, framegen, AA/upscaler, opções de compatibilidade do driver, variáveis aplicadas e cache frio ou quente |
| M4 | Linha do tempo de ~2 s: FPS reais e apresentados, p50/p95/p99, GPU por quadro, CPU por thread, clock da GPU e temperatura |
| M5 | Contagens por quadro real: draws, binds de pipeline e de descriptor set, render passes, submits, cópias e uploads |
| M6 | Variáveis por driver aplicáveis sem rebuild e coleta do logcat do processo com as tags `TU`, `MESA`, `vulkan` e `adrenotools` (para `TU_DEBUG=perf`) |
| M7 | Em crash ou device lost: `VkResult`, a chamada que falhou, o último marcador de cena/passe e o backtrace com o build-id do driver |

Respostas, quando chegarem: [Gtavport #2](https://github.com/rickamaral94/Gtavport/pull/2),
[Botwnspxci #3](https://github.com/rickamaral94/Botwnspxci/pull/3),
[Totknspcxi #4](https://github.com/rickamaral94/Totknspcxi/pull/4).

## 1. Sempre, em qualquer pedido

**Identidade** (sem isto o resto não é comparável):

| Campo | Exemplo / onde obter |
| --- | --- |
| Aparelho, GPU e chip | Odin 2 Portal, A740; `/sys/class/kgsl/kgsl-3d0/gpu_model` e o `chip_id` quando o app conseguir ler |
| Android e kernel | `ro.build.version.release`, `uname -r` |
| Driver carregado | `driverName` e `driverInfo` do `VkPhysicalDeviceDriverProperties`, lidos **no mesmo processo do jogo** |
| Pacote do driver | nome do ZIP, **SHA-256 do ZIP e do ELF**, build-id (`readelf -n`) |
| App | versão, commit e SHA-256 do APK; versão do jogo; modo (recompilado, nativo etc.) |
| Configuração efetiva | resolução interna e escala, limite de FPS, framegen, AA/upscaler, opções de compatibilidade do driver no app (heap, in-place, LRZ etc.) e todas as variáveis de ambiente (`TU_DEBUG`, `IR3_SHADER_DEBUG`, `MESA_*`) |
| Estado do cache | pipeline/shader cache frio ou quente, por driver |

O build-id e o SHA do ELF bastam: os builds do Amaral são reprodutíveis, e o agente Turnip refaz a versão com
símbolos para simbolizar amostras de perfil.

**Comparação:**

- O mesmo caso no **driver da Qualcomm** (ou num segundo Turnip), mesmo APK, save, rota e cache separado por driver.
  Sem isso, não há como separar driver de app.
- Desempenho em ordem **A/B/A** ou AB/BA, com pelo menos 3 rodadas.
- Rótulo de cada número: medido no aparelho, relato, verificado no host ou hipótese.

**Privacidade:**

- Logs brutos, capturas e vídeos ficam com o Rick, fora do Git.
- No PR, métricas resumidas, nomes de arquivo e janelas.
- Nunca dados do jogo, chaves, saves ou dados pessoais.

## 2. Por tipo de problema

### Crash, `VK_ERROR_DEVICE_LOST` ou GPU travada

- Mensagem e código de erro, e em qual chamada Vulkan retornou (submit, wait, present).
- `logcat` de ±30 s em volta do evento, com as linhas do Turnip/Mesa (`TU`, `MESA`, `vulkan`), do adrenotools e do
  app.
- Linhas do kernel KGSL, se o aparelho deixar ler: `adreno`, `kgsl`, "GPU fault", "opcode error", "page fault",
  "hang".
- Backtrace/tombstone com o build-id do `libvulkan_freedreno.so`.
- Último marcador do app antes do evento: cena, passe e tipo de comando.
- Frequência: sempre, a cada N minutos, aleatório. Passos mínimos para reproduzir.
- Teste rápido, um de cada vez:
  - `TU_DEBUG=syncdraw`;
  - `TU_DEBUG=flushall`;
  - `TU_DEBUG=sysmem`;
  - `TU_DEBUG=nolrz`;
  - `TU_DEBUG=check_cmd_buffer_status`;
  - se o app usar sparse/tiled, dizer.

  Se alguma variável fizer o problema sumir, isso é a pista mais valiosa: ela aponta o mecanismo.

### Defeito de imagem (corrupção, piscadas, preto, listras)

- Screenshot ou vídeo do **mesmo ponto** nos dois drivers, e a descrição do que está errado.
- Repetição com cada variável, uma por vez:
  - `TU_DEBUG=sysmem` e `TU_DEBUG=gmem` (GMEM vs memória do sistema);
  - `nolrz` (LRZ);
  - `noubwc` (compressão UBWC);
  - `flushall` e `syncdraw` (cache e sincronização);
  - `IR3_SHADER_DEBUG=nofp16` (precisão);
  - `IR3_SHADER_DEBUG=nouboopt` (constantes).

  Diga qual muda o resultado. Rode `flushall` e `syncdraw` antes de relatar corrupção transitória: mesa#15792
  mostra exatamente isso com o renderer plume.
- Uma sessão com a camada de validação Vulkan (VVL), incluindo a validação de sincronização. Se o VVL acusar, o
  problema provavelmente é do app.
- **Melhor evidência possível:** uma captura curta do quadro com defeito, feita com GFXReconstruct ou RenderDoc. Ela
  permite reproduzir no laboratório. Contém assets do jogo, então fica privada, só com o Rick.

### Desempenho pior no Turnip

- Na mesma janela, para cada braço:
  - FPS reais, separados de FPS apresentados;
  - p50, p95 e p99;
  - quadros acima de 50 e de 100 ms.
- GPU por quadro. Por passe, só se a instrumentação for mínima: timestamp dentro de passe GMEM, fora de
  TOP_OF_PIPE, custa um WFI por bin.
- CPU por thread (principal, render, submit) e perfil amostrado da thread de render com o build-id do driver.
- Contagens por quadro real: draws, binds de pipeline, binds de descriptor set, render passes, submits, cópias e
  uploads.
- Clock da GPU e temperatura na linha do tempo da coleta. Um degrau periódico pode ser térmico, não do driver.
- `TU_DEBUG=perf` com logcat por uns 30 s na cena: o Turnip escreve por que desligou GMEM ou LRZ em cada passe.
- Para um shader suspeito, as estatísticas de `VK_KHR_pipeline_executable_properties`:
  - max waves;
  - registradores;
  - loops e instruções;
  - (ss)/(sy);
  - spill;
  - o "IR3 Assembly" daquele pipeline.

  Capture só os hashes suspeitos.

### Recurso Vulkan faltando ou diferente do esperado

- A extensão ou feature, o valor que o app espera e o que o Turnip informa (`vulkaninfo` ou o teste de driver do app).
- Para que o app usa e o que faz quando falta: fallback, cópia ou caminho lento.

## 3. O que o agente Turnip devolve

Resposta no PR de campainha. Conforme o caso:

- diagnóstico com arquivo e commit do Turnip/Mesa;
- variável ou driconf para testar;
- ZIP de laboratório com SHA-256 e a mudança isolada;
- correção registrada aqui e, quando couber, enviada ao Mesa upstream.

Uma correção que só serve a um app vira perfil por app ou recomendação de uso da API, nunca hack global (ver
[PORTS-CAMPAINHAS.md](PORTS-CAMPAINHAS.md)).
