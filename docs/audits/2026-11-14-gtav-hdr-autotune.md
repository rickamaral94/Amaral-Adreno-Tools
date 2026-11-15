# Gtavport: passe HDR lento só no Turnip (A740), 14/11/2026

Chamado pela [campainha do Gtavport](https://github.com/rickamaral94/Gtavport/pull/2#issuecomment-6873765591).
Resposta do agente Turnip:
[comentário](https://github.com/rickamaral94/Gtavport/pull/2#issuecomment-6873781917).

## Evidência (medida no Odin 2 Portal pelo Rick, relatório do Gtavport v0.3.0-pre1)

Mesmo APK (`f76fbb1f…186c`), mesmo ponto e mesmas opções, sem variáveis de driver:

| | Turnip Amaral 5.9.18.1 (build-id `e6bfc6bd…`) | Driver do sistema (Qualcomm 69e13475cb) |
| --- | --- | --- |
| FPS | 21,6 | 59,9 |
| p95 / p99 do frametime | 300,7 / 305,2 ms | 20,5 / 22,3 ms |
| Quadros > 100 ms em 60 s | 140 | 0 |
| GPU por quadro (média / p95) | 42,0 / 299,8 ms | 12,4 / 13,0 ms |
| Passe 1280x721 RGBA16F + depth (6 passes) | 3,36 → 83,66 ms | 2,41 → 2,66 ms |

No Turnip, a GPU ficou a 680 MHz, 61–64 °C, sem estado térmico. O padrão é por fases: ~14 s a 60 fps e depois
blocos de quadros de ~300 ms. A Mesa `fd8ef2b` (5.8.17.1) já mostrava o mesmo comportamento.

## Hipótese (verificada no código; não testada no aparelho)

O autotune padrão (`bandwidth`, `tu_autotune.cc`, `bandwidth_algo::get_optimal_mode`) usa uma média móvel de
*samples passed*:

- o custo estimado de SYSMEM recebe o termo dos desenhos inteiro;
- o de GMEM recebe só 1/10 dele.

Uma contagem enorme na média força GMEM até ela decair. O [mesa!45904](https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/45904)
(aberto) mostra exatamente essa corrupção num passe GMEM preemptado entre tiles: a diferença `end - start` volta curta
ou dá a volta para ~2^64. No Android, o compositor preempta.

Num alvo de ~11 MB (RGBA16F + depth), GMEM vira dezenas de bins e cada desenho é reexecutado por bin. A medição da
Qualcomm, a ~2,5 ms, é coerente com renderização direta.

**Hipótese rival:** o passe é caro em GMEM e o autotune passa a escolher GMEM depois do aquecimento, sem contagem
corrompida.

## Evidência nova: "Isolar o passe HDR" (14/11, medido no Odin pelo Gtavport)

Tabela completa na [campainha do Gtavport](https://github.com/rickamaral94/Gtavport/pull/2). Turnip v5.9.18.1,
cada um dos 24 pixel shaders do passe desligado, um por vez:

- p95 continua entre 237 e 242 ms em todos os braços;
- o maior alívio vem do `6A497187391DEA22` (54 desenhos por quadro): GPU média de 59 para 44 ms, p95 ainda em 240;
- a linha do tempo repete as fases: 60 fps até ~14 s e, a partir de ~16 s, quadros de ~300 ms, com GPU a 680 MHz e
  58 °C (não é limitação térmica nem clock baixo);
- driver do sistema: 60 fps cravados em todos os braços.

Leitura: nenhum shader explica o custo. Um custo que escala com o número de desenhos, e não com um shader, é o que
se espera de GMEM com muitos bins, em que cada desenho é reexecutado por bin. A transição depois de um aquecimento
fixo combina com a média móvel do autotune. Isso reforça a hipótese principal sem descartar a rival; os testes abaixo
seguem necessários.

## Rodada do Rick, 14/11 04:15–05:25 (logs enviados no chat, medição no aparelho)

Zip recebido: SHA-256 `98ef10ed7053f5bd9a46538dcf825242533e94707595e2a3a5b2e1f8b14af509`. Ele fica com o Rick; aqui só
os resumos do `perf-diag` do Gtavport (Odin 2 Portal, A740v2, Android 13, kernel 5.15.123; 1280x720, 60 fps, vsync,
FXAA, SGSR1). Mesma cena e configuração em todos os braços.

| Hora | Driver (ELF conferido) | Janela | FPS reais | p95 / p99 (ms) | GPU/quadro | `TU_DEBUG` |
| --- | --- | --- | --- | --- | --- | --- |
| 04:15 | 5.9.18.1 Standard, `7b8ff2f8…` (= manifesto da release), build-id `e6bfc6bd…` | 60 s | 21,6 | 300,7 / 305,2 | 42,0 ms | nenhum |
| 04:20 | sistema (Qualcomm) | 60 s | 59,9 | 20,5 / 22,3 | 12,4 ms | — |
| 04:34 | 5.9.18.1 Standard, `7b8ff2f8…` | 600 s | 13,2 | 239,9 / 242,1 | 72,0 ms | nenhum |
| 05:10 | sistema (Qualcomm) | 600 s | 60,0 | 20,7 / 22,2 | 12,6 ms | — |
| 05:25 | lab !45904, `9f01e24c…`, build-id `8b0b742d…` (= este lab) | 60 s | 23,0 | 247,7 / 249,9 | 39,0 ms | nenhum |

O `perf-diag` registra só `ODIN2_VK_DRIVER`, `TU_DEBUG`, `MESA_VK_ABORT_ON_DEVICE_LOSS` e `FD_DEV_FEATURES`
(`odin2/perf/odin2_perf.cpp` do Gtavport). `TU_AUTOTUNE_ALGO` não aparece no relatório, então não dá para afirmar
se alguma rodada usou essa variável.

Leitura:

1. **O lab !45904 não muda nada** (p95 de 248 contra 240–300 ms). A contagem de amostras corrompida por preempção,
   na forma que o MR corrige, não explica este caso. A hipótese "autotune enganado por contagem corrompida" cai; a
   de "GMEM escolhido e caro" continua aberta.
2. **A virada aos ~16 s é troca de cena, não necessariamente aquecimento do autotune.** O passe de 4 alvos
   `1280x721 4c fmt 20 +depth` (G-buffer) só existe nas janelas lentas (0 → 1,8 ms). Antes de ~16 s o jogo não
   desenha o mundo deferred.
3. **O custo está no passe HDR** `1280x721 1c fmt 10 (RGBA16F) +depth`, 6 por quadro: de ~3 ms para ~80 ms por
   quadro, na média da janela.
4. **O tempo dos quadros lentos é quase fixo** (238–244 ms na rodada de 600 s, ~300 ms na de 04:15) e não acompanha a
   carga. Desligar shaders mexe na média, não no p95. Isso se parece mais com uma espera ou um custo fixo por passe do
   que com custo de shader.
5. **As esperas do processador de comandos são consequência.** No Turnip, o processador de comandos do Gtavport
   esgota a espera de 100 ms (`gtav_native_fence_wait_ms`) milhares de vezes: 4851 vezes em 600 s, contra 7 no driver
   do sistema. É a thread do jogo esperando o renderer gravar o quadro, enquanto o renderer espera a GPU (~290 ms).
   Não é uma espera da GPU por algo da CPU.

Pendente: o mesmo trecho com `TU_DEBUG=sysmem` e com `TU_DEBUG=gmem`. As duas aparecem no relatório e respondem
direto se o custo depende do modo de renderização. Pedido ao Gtavport: incluir `TU_AUTOTUNE_ALGO`,
`TU_AUTOTUNE_FLAGS`, `IR3_SHADER_DEBUG` e `MESA_*` na lista de variáveis registradas.

## Rodada do Rick, 14/11 21:50–21:55: modo de renderização (medição no aparelho)

Zip: SHA-256 `275070732e34a920622c307a7dbf5a21c0825a350579e798f99cd37867e126b2`. O driver usado foi o lab !45904 (ELF
`9f01e24c…`, build-id `8b0b742d…`, conferido no relatório), em vez da 5.9.18.1 pura. Como o lab não mudou nada na rodada
anterior, os dois servem como base equivalente para este teste. As variáveis aparecem no relatório e no logcat.

| `TU_DEBUG` | FPS reais | p95 (ms) | GPU/quadro | Antes de ~16 s | Passe HDR, janela lenta |
| --- | --- | --- | --- | --- | --- |
| nenhum (rodada anterior, lab) | 23,0 | 247,7 | 39,0 ms | 60 fps | 81 ms |
| `sysmem` | 21,9 | 289,0 | 41,3 ms | 60 fps | 96 ms |
| `gmem` | 19,7 | 251,1 | 49,2 ms | ~49 fps | 57 ms |
| `sysmem,nolrz` | 22,0 | 286,5 | 41,0 ms | 60 fps | 88 ms |

Nenhuma mensagem do Turnip no logcat além do gralloc.

**Conclusão:** o problema **não depende do modo** (GMEM ou SYSMEM) nem do LRZ. A hipótese de autotune/GMEM está
**refutada**: forçar SYSMEM não cura. O `gmem` só deixa a cena inicial mais lenta, o custo normal de GMEM.

Hipóteses que restam (todas no passe RGBA16F + depth):

1. **Execução de shader no ir3:** spill, memória privada (arrays indexados vindos do endereçamento relativo do Xenos)
   ou poucas waves. Um passe de tela cheia em resolução fixa dá exatamente um custo fixo por quadro.
2. **Amostragem cara:** formato, tiling linear ou anisotropia 16x numa textura que o Turnip amostra devagar.
3. **Custo fixo por desenho:** flush/WFI por barreira entre luzes. Isso não escala com pixels.

Testes que separam as três (pedidos na campainha):

- render scale 0,5: o custo cai ~4x se for por pixel (1 ou 2); fica igual se for por desenho (3);
- anisotropia 1: separa 2;
- estatísticas de `VK_KHR_pipeline_executable_properties` dos 24 pixel shaders do passe e dos vertex shaders (instruções,
  max waves, registradores, spill, memória privada) e o IR3 dos 3 mais desenhados. Separa 1. O agente do port coleta
  isso sem o Rick.

## Culpado confirmado, 15/11 (medição no aparelho, números do Gtavport na campainha)

- **Custo por pixel:** com render scale 0,5, o passe fica ~3× mais barato. A anisotropia não muda nada.
- **Estatísticas de pipeline no Turnip.** O fragment shader `EFEADDD82B576B06` foge do padrão:
  - ~8000 instruções e 1 laço;
  - 48 registradores full (o teto do ir3) e 4 waves;
  - ~400 STP e ~640 LDP de spill.

  Em 10 min ele tem ~2170 desenhos, para 2135 quadros acima de 100 ms. Ficou fora do rodízio dos 24 (27º lugar).
- **Teste de exclusão no Odin** (lab 5.9.18.1):

  | Braço | FPS | p95 | Passe HDR | Quadros >100 ms |
  | --- | --- | --- | --- | --- |
  | `GTAV_NATIVE_SKIP_PS=EFEADDD82B576B06` | 60,0 | 20,8 ms | 3,6 ms (igual ao driver do sistema) | 0 |
  | controle `311BC83470B3F7A2` | 21,1 | 357 ms | até 111 ms | — |

**Mecanismo provável (hipótese, pelo código do XenosRecomp):** quando o shader Xenos tem salto incondicional ou para
trás, o tradutor gera o shader inteiro como máquina de estados (`while (true) { switch (pc) { ... } }`). Todo valor
que atravessa um `case` fica vivo no laço inteiro, a pressão passa do teto de 48 registradores e o spill cai dentro do
laço. O driver da Qualcomm executa o mesmo SPIR-V em ~2,5 ms.

Próximo passo:

- Ler localmente o IR3 do pipeline #36 (zip do Rick de 15/11). O assembly é derivado do jogo e **não** entra em
  repositório; aqui ficam só números agregados.
- Separar o que é padrão de entrada (correção no tradutor do port, vale para qualquer driver) do que é perda evitável no
  NIR/ir3: switch → cadeia de `if` com phis, recarga de constantes de UBO com índice dinâmico, escolha de spill dentro do
  laço. Só a segunda parte vira lab aqui, e só se aparecer no assembly.

## Por que o driver da Qualcomm não trava no `EFEADDD82B576B06` (15/11, leitura local do zip do Rick)

Zip: SHA-256 `333f231cfc25b6da9f901fdeeb2fbbb03418818f4a3a6192aec123d1a510bd56`. O `pipeline-stats.txt` trouxe as
estatísticas e só a primeira representação ("NIR from SPIRV") de cada executável; o "Final NIR" e o "IR3 Assembly", que
o Turnip também expõe (`tu_pipeline.cc`), não vieram. Leitura local; nenhum trecho do shader entra aqui.

**Verificado no NIR (pipeline #36, FS):**

- **Máquina de estados.** Um único `loop` envolve o shader inteiro. No topo há um despacho por `pc`: 89 comparações
  `ieq pc, k` em cadeia de `if`, ou seja, o caso 4 do XenosRecomp.
- **~184 valores escalares (≈46 vec4) carregados pela volta do laço** (phis do cabeçalho). O ir3 tem 48 vec4 (192
  escalares) por fibra. Só o estado carregado ocupa ~96% do teto antes de qualquer temporário de um `case`.
- **Resultado no Turnip** (estatísticas do executável): 8089 instruções, 48 registradores, 4 waves, 400 STP e 636 LDP
  (spill), 2454 MOVs. Ciclos de espera estimados em `(sy)`: 7570. O spill fica dentro do laço, então se repete a cada
  volta e em cada pixel.

**Por que a Qualcomm não sofre (hipótese, sem acesso ao binário dela):**

- O compilador proprietário (de base LLVM) tem passes que desfazem máquinas de estado em laço, como o jump threading
  sobre `switch`. Com eles, cada valor só fica vivo no trecho em que é usado, não no laço inteiro, e a pressão cai
  abaixo do teto.
- Ele também pode escolher spill e rematerialização de outro jeito, ou trocar waves por registradores.

O ir3 não tem um passe que reestruture esse padrão. Ele aloca o laço como está e faz spill. A medida do port (passe
HDR com 3,6 ms sem o shader e ~2,5 ms no driver do sistema) mostra que o mesmo SPIR-V cabe num driver bom.

**Caminhos:**

1. **No port (mais eficaz e vale para qualquer driver):** o tradutor estrutura o fluxo em vez de gerar
   `while/switch(pc)`, ou ao menos tira do estado carregado os registradores que cada trecho não usa.
2. **No driver (pesquisa aqui):**
   - reproduzir o pipeline #36 fora do aparelho: Turnip com drm-shim emulando o A740 e o SPIR-V do pipeline vindo do zip
     do Rick, só local;
   - medir duas melhorias universais no NIR/ir3: (a) desfazer o despacho por `pc` quando o destino de cada volta é
     conhecido (jump threading); (b) spill dos valores carregados que o `case` atual não usa, fora do caminho quente.

   Entra como lab só se reduzir spill e tempo sem regressão no shader-db.

## Testes pedidos (só variáveis, 120 s cada)

1. `TU_AUTOTUNE_ALGO=prefer_sysmem`. Previsão: 60 fps estáveis, sem fases.
2. `TU_DEBUG=gmem`. Previsão: lento desde o início.
3. `TU_DEBUG=sysmem`.
4. `TU_AUTOTUNE_ALGO=profiled`.

Como ler o resultado:

- Se 1 cura e 2 é lento desde o início, a decisão do autotune é a causa.
- Separar "contagem corrompida" de "heurística" pede o lab abaixo, **sem** variável. Previsão: com o lab, o passe
  fica rápido também no Automatic.

## Lab

`lab-mr45904-gmem-preemption-sample-counts.patch`: os três commits do MR (`539aeb46233`, `5ee487f9fd2`,
`292918f6727`), aplicados limpos sobre a série Standard da 5.9.18.1.

- Pacote: `turnip_amaral_5.9.18.1_lab-mr45904.zip`, SHA-256
  `9d5b2e084f6516cf47fa474daeec872d3e5e091b53b18ceb4f6492fb955d7109`.
- ELF: `9f01e24ce29d7e1c2eb54b9607ef32963da16f03345fc79dcef70c894d55a1f7`, build-id
  `8b0b742dbc303c3dcfda8dad1bd65c7f9e2d0a15`, versão `git-306739e220`.
- Build local, não do CI. Not-run: CTS de occlusion query e hardware.

Se confirmado, o caminho universal é acompanhar o !45904 upstream, que corrige também occlusion queries de
qualquer app. Um driconf `prefer_sysmem` por app fica como contorno temporário, só se o lab não bastar.
