# Gtavport: travadas de compilação de pipeline no Turnip (18/11)

Pedido do Gtavport pela campainha (sessão do agente do port, 18/11). No Odin, cada `vkCreateGraphicsPipelines`
monolítico (VS+PS) leva 4–11 ms no Turnip 5.9.18.1, compilado na hora do desenho. Numa área nova chegam ~100 de uma
vez: travada de ~0,5 s. O port usa `VkPipelineCache` persistente. Perguntas: estabilidade e custo do
`VK_EXT_graphics_pipeline_library` (GPL), opções de compilação e clock da GPU.

## Leitura do código (Mesa `a6aacf6`)

- **Chave do cache de shaders** (`tu_hash_shaders`, `tu_pipeline.cc`): layout do pipeline, módulo SPIR-V,
  especialização e chave do shader **de todos os estágios juntos**, mais o estado de biblioteca e as flags do ir3.
  - Não entram formato do alvo, blend, layout de vértice, depth/stencil nem topologia.
  - O cache de cada estágio usa o hash do pipeline inteiro mais o estágio, então trocar o VS parceiro recompila
    também o FS.
- **GPL:** `graphicsPipelineLibrary` e `graphicsPipelineLibraryFastLinking` anunciados sem condição.
  - A biblioteca de pré-raster ou de fragment shader compila o ir3 do próprio estágio na criação.
  - Sem `LINK_TIME_OPTIMIZATION`, o link só reaproveita os shaders das bibliotecas.
  - Com LTO, recompila a partir do NIR retido (`RETAIN_LINK_TIME_OPTIMIZATION_INFO`).
  - `75f94f4dd9f` (junção de set layouts de bibliotecas) já está na 5.8.17.1 e na 5.9.18.1.
- **Cache de disco do Mesa:** desligado por padrão no Android (`disk_cache_os.c`).

## Medidas (reprodução local, host x86, A740 via drm-shim, sem caches)

Shader de teste: o par do pipeline #37 (`AADF8B05B210DF1B` + `EFEADDD82B576B06`, SPIR-V da pre4, o caso extremo de
~8000 instruções). Valem as proporções; os tempos absolutos são do host. Três processos por modo.

| Operação | Tempo |
| --- | --- |
| Monolítico (VS+FS), frio | 805–1205 ms |
| Mesmos shaders, outro formato/blend/vértice/depth/topologia, mesmo processo | 0,09–0,15 ms |
| Mesmo FS com outro módulo de VS | 949–1126 ms (recompila tudo) |
| Outra spec constant | 1063–1124 ms |
| Biblioteca: vertex input / fragment output | 0,02–0,06 ms |
| Biblioteca: pré-raster (VS) | 7–9 ms |
| Biblioteca: fragment shader (FS) | 828–940 ms |
| **Fast-link das 4 bibliotecas** | **0,074–0,078 ms** |
| Link com LTO | 776–885 ms |

O cache de disco do Mesa ligado (`MESA_SHADER_CACHE_DISABLE=false` + diretório) não evita a recompilação ao trocar o
VS parceiro. Ele só repete o papel do `VkPipelineCache` do app entre execuções.

## Parecer

1. **O GPL resolve o caso.** Cada estágio é compilado uma vez, numa biblioteca, e reaproveitado com qualquer parceiro
   e estado. No desenho sobra o fast-link, ~0,1 ms. Use o mesmo `VkPipelineLayout` completo em todas as bibliotecas;
   não precisa de `INDEPENDENT_SETS`.
2. **Custo do fast-link na GPU:** sem otimização entre estágios, o VS exporta todos os varyings que declara, mesmo os
   que o FS não lê. O padrão recomendado é usar o fast-link na hora e compilar em segundo plano a versão com LTO, ou a
   monolítica, para trocar quando ficar pronta. Medir o custo de GPU com o fast-link antes de decidir se a troca vale.
3. **Opções de compilação:** nenhuma opção do Turnip ou do ir3 reduz o tempo sem custo no shader. O ganho está em não
   recompilar.
4. **Clock da GPU:** a 30 fps, com ~73% de uso e só 6 travadas por espera da GPU em 10 min, o governador está correto.
   Restringir o nível de energia por contexto no KGSL só gastaria bateria e calor; o Turnip não expõe isso e não há
   ganho medido.

Estabilidade do GPL no A740 com esta build: o código está exposto e com a correção de layouts. CTS de GPL: **not-run**
aqui. O port deve manter a volta automática para o monolítico e uma opção para desligar, como planejado. Primeiro
teste no aparelho: a mesma rota de 10 min, A/B com o GPL ligado e desligado, contando travadas >100 ms e novos
pipelines.
