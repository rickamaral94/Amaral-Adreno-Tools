# BOTWRecomp no A740: avaliação e plano de melhoria

**Conclusão:** manter LRZ e autotune upstream; priorizar medição correta, constantes/descriptors e dependências explícitas no app. Os anexos não justificam ainda um patch universal de registradores, UBWC, LRZ ou submit. Há execução real da 5.7.13.1; não há teste BOTWRecomp da 5.7.16.1 neste lote. Este relatório é uma análise de código e observações, não uma qualificação de release.

Análise solicitada por Rick em 31/10/2026, thread `T-botwrecomp-a740`. Fonte: ZIP SHA-256 `bf459f1da63787a36be6d7979115553cb3403f5b59ca968e50f36131cd21035f`, dois textos enviados e relatórios nele contidos. Logs brutos permanecem fora do git. A [extração selecionada](../../evidence/analysis/botwrecomp-2026-10-31.json) foi gerada por [analyze_botw_diagnostics.py](../../tools/analyze_botw_diagnostics.py); 60 membros `.txt`, 16 duplicados byte a byte, sete grupos de resumos distintos. Grupos não são rodadas A/B independentes. Não existe manifesto autenticado de captura neste ZIP; o hash identifica os bytes recebidos.

Código público consultado: Mesa **4b0f64ceac6a86af38c1e69cd38cf29f84ba611d** (baseline anunciada pelo driver medido), e **69f1f21f0258a77046dbaeb8ed7a8ad37a683006** (base da candidata). Arquivos `src/freedreno` e IR3 foram baixados dos snapshots upstream. A referência abaixo usa o snapshot medido; isso não reconstitui automaticamente todos os patches do pacote binário. Build-id observado do Turnip: `56becd8cf1d7c217e30cb37c4f5dd4814677e68b`. Sem ELF não stripado correspondente, os offsets do perfil **não foram simbolizados**.

## O que os logs sustentam — e o que precisam corrigir

| Sessão observada | Configuração | FPS reais relatados | GPU ms/quadro real relatados | CPU render ms/apresentação | CPU render ms/quadro real aproximados |
|---|---|---:|---:|---:|---:|
| Amaral 5.7.13.1 | LRZ on, 1× | 28,00 | 14,89 | 6,01 | 10,59 |
| Amaral 5.7.13.1 | LRZ off, dinâmica 0,55 | 28,79 | 16,53 | 6,07 | 12,02 |
| Turnio 26.2 R4 | LRZ on, 1× | 15,65 | 17,15 | 7,18 | 14,19 |
| Qualcomm | LRZ off, dinâmica 0,50 | 14,83 | 17,67 | 10,94 | 19,08 |

A última coluna calcula `CPU_percent × CPU_observed_seconds × 10 / (duration_seconds × real_fps)`. É aproximada: as janelas de CPU e FPS podem não ser idênticas. Não se deve multiplicar simplesmente por dois: 2× framegen não garante duas apresentações por quadro real em toda a janela, e menus/transições contam diferentemente. O JSON mantém o valor original e o denominador explícito.

- Os ~1,7 ms de driver são uma estimativa por apresentação (`28% × ~6 ms`), não um orçamento demonstrado por quadro real. Sampling por tempo de CPU também não atribui tempo bloqueado. Não somar percentuais de stacks/chamadores que se sobrepõem.
- No Turnio, `run 24,87 ms/frame` é tempo de parede na categoria do app, não tempo provado dentro do driver. A diferença para `7,18 ms/frame` de CPU pode conter bloqueio no kernel, preempção e espera não instrumentada. Amostras em `ioctl` não medem sozinhas sua duração nem identificam qual ioctl. Precisamos medir entrada/saída, request, fila e fence.
- O comparativo LRZ mudou resolução, duração (120 s contra 60 s) e temperatura: SoC 43–51 °C versus 47–66 °C relatados. Preserva a observação de imagem correta relatada, mas não isola ganho de LRZ. A redução nominal de 1,64 ms não é ganho atribuível ao LRZ.
- Resolução menor sem redução de tempo **não prova** custo independente de pixels quando o governador reduz frequência. Separar geometria/CP, largura de banda, shaders e DVFS exige frequência/contadores ou condição de energia reproduzível.
- Valores A830 (~2 µs/draw, 20–40 µs/passe, UBWC 16×4) vêm do relato; não extrapolar como medições A740. Multiplicar 2.100×2 µs ou 175×20 µs soma custos possivelmente sobrepostos e não produz previsão de ganho.
- Os 14,89 ms são o valor do diagnóstico, cuja instrumentação deve ser auditada. Não somar automaticamente 4–5 ms de LSFG: verificar se as submissões LSFG já entram na união. A soma poderia contar trabalho duas vezes.

## Prioridades P0: correção e medição

| Item | Onde no código | Ganho GPU/CPU estimado | Driver ou app | Risco |
|---|---|---|---|---|
| Corrigir denominadores e auditar timestamps | `tu_query_pool.cc:tu_CmdWriteTimestamp2`, `emit_counter_barrier`; `runtime/diag.c` do app (fonte não fornecida) | Ganho de execução não medido; evita escolher otimização errada. Instrumentação menos frequente pode reduzir waits, magnitude desconhecida | App primeiro; driver só se reproduzido erro de query | Médio: medir muda a carga |
| Formalizar feedback loop | `tu_device.cc`, `tu_pipeline_update_rp_state` em `tu_cmd_buffer.cc`; pipeline/rendering/image flags do app | Correção; ganho pode ser zero ou negativo | App | Alto se ler dados escritos pela mesma draw sem ordenação válida |
| Não generalizar workaround UBWC A830 | `tu_image.cc:ubwc_possible`, `tu_image_init`; `tu_formats.cc`; `fdl/fd6_view.c` | Sem ganho A740 demonstrado | Reprodutor app + eventual fix driver | Alto: remover compressão pode piorar banda |

## Prioridades P1: melhores experimentos de desempenho

| Item | Onde no código | Ganho GPU/CPU estimado | Driver ou app | Risco |
|---|---|---|---|---|
| Separar 16 B mutáveis do bloco grande | `tu_CmdPushConstants2KHR`, `tu6_emit_per_stage_push_consts`; `ir3_nir_analyze_ubo_ranges.c` | Pode remover grande parte dos bytes copiados atribuíveis ao delta; ms ainda não medidos. 2.100×16 B ≈ 33,6 KB não equivalem a remover todos os 15 MB | Tradutor/app; IR3 só com caso mínimo | Médio/alto: semântica de snapshot e leituras indiretas |
| Reutilizar sets e recursos estáveis | `tu_descriptor_set.cc:tu_AllocateDescriptorSets`, `tu_UpdateDescriptorSets`; `tu_bind_descriptor_sets`, `tu6_emit_descriptor_sets`, `tu6_draw_common` | CPU potencial dentro da parcela de descriptors; percentuais fornecidos não são ganho realizável | App primeiro; depois driver com perfil simbolizado | Médio: lifetime, update-after-bind e invalidation |
| Dependências precisas e menos fronteiras de passe | `tu_flush_for_access`, `tu_flush_for_stage`, `tu6_emit_flushes`, `tu6_sysmem_render_begin/end` | Desconhecido; remoção da barreira inicial já foi relatada sem ganho | App primeiro | Alto: visibilidade, layout e read-after-write |
| Diagnóstico de submit 26.2×27 | `tu_queue.cc`, `tu_knl_kgsl.cc:kgsl_queue_submit`, merge/wait de syncobj | Sem ganho adicional provado no Amaral atual | Instrumentar app/driver de laboratório | Médio; não retirar esperas sem contrato |

## Prioridades P2: dependem de caso mínimo

| Item | Onde no código | Ganho GPU/CPU estimado | Driver ou app | Risco |
|---|---|---|---|---|
| Heap 3 GB por BDA | `tu_device.cc:tu_get_properties`, `common/freedreno_devices.py`, `tu_shader.cc`, `ir3_compiler_nir.c` | Pode eliminar seleção de janelas; pode aumentar custo 64-bit e reduzir robustez. Sem previsão de FPS | App/tradutor | Alto: bounds, alignment, lifetime |
| Descriptor buffer/push descriptors | `tu_GetDescriptorEXT`, `tu_CmdBindDescriptorBuffersEXT`, `tu_CmdSetDescriptorBufferOffsets2EXT` | Menos alocação/update de sets possível; bindings/base e invalidação continuam. Medir contra sets reutilizados | App | Médio/alto; dynamic descriptors não são suportados no descriptor-buffer layout |
| LSFG: workgroups/subgroups e memória | `tu_shader.cc`, `ir3_shader.c:ir3_shader_get_subgroup_size`, backend IR3 | Sem estimativa sem SPIR-V, registers/spills e pass timings | App/shaders, eventual compilador | Médio: barriers e resultados de borda |
| LRZ | `tu_lrz.cc:tu6_calculate_lrz_state`, `tu_pipeline.cc` | Manter default; ganho atribuível não medido neste par | Driver já decide por draw/passe | Alto se remover proteções de correção |
| Contadores sem root | `tu_device.cc` e `tu_knl_kgsl.cc`, `tu_perfetto.cc` | Melhora diagnóstico, não FPS diretamente | Build de laboratório + permissões Android | Disponibilidade limitada por KGSL/SELinux |

## Implementação 1 — medição que pode orientar patches

No snapshot medido, `tu_CmdWriteTimestamp2` (linha 2101) trata TOP_OF_PIPE/DRAW_INDIRECT como leitura de contador sem barreira; valor NONE também não entra no ramo de barreira dessa implementação. Para outros stages, inclusive ALL_COMMANDS, chama `emit_counter_barrier`, que emite WFI. Em A8xx acrescenta CP_BARRIER. Dentro do render pass escreve no draw stream e sinaliza disponibilidade no epílogo; em GMEM pode repetir por tile. Essa medição não é passiva.

A [especificação de vkCmdWriteTimestamp2](https://docs.vulkan.org/refpages/latest/refpages/source/vkCmdWriteTimestamp2.html) define dependência com comandos anteriores em submission order, limitada pelo stage escolhido. Um timestamp inicial sem dependência não mede necessariamente o início efetivo de trabalho. Mas terminar uma submissão leve antes do término da anterior **não deve ser normalizado como comportamento esperado sem verificar filas, ordem e queries**. No código consultado ALL_COMMANDS espera com WFI; os 5.128 intervalos aninhados entre 7.715 exigem auditoria. Esta análise não demonstrou bug Mesa.

Plano para `runtime/diag.c` (o arquivo não está nos anexos):

1. Cada registro deve guardar frame real, origem jogo/LSFG, queue id, submit serial, query index e geração do slot. Não reutilizar/resetar query antes de conclusão e leitura do uso anterior. Ler disponibilidade, resultados 64-bit, `timestampPeriod` e `timestampValidBits`; tratar wrap.
2. Separar tempo de CPU, parede, submit e present; reportar denominadores: apresentações totais, gameplay presents, quadros reais. Registrar versão do instrumento e hash do APK/ELF.
3. Microteste: uma fila, queries fora de render pass, submissão pesada A e leve B, finais ALL_COMMANDS, inicialmente fence entre A e B; depois repetir sem serialização artificial. Conferir ordem no app. Repetir com múltiplas filas só depois. VVL e teste de query/reset são necessários, não habilitar debug no benchmark final.
4. Medir baseline sem queries e instrumentação amostrada, por exemplo uma janela por N quadros; registrar o N. Não trocar WFI do driver por nada para "acelerar" timestamps.
5. União de intervalos remove sobreposição aritmética, mas **não prova GPU busy**, pois intervalos podem conter espera/ociosos ou domínios não comparáveis. Renomear métrica como envelope/união de timestamps até validar contra contadores. Não subtrair o LSFG sem identidade das submissões.
6. Obter ELF não stripado que corresponda exatamente ao build-id `56becd8cf1d7c217e30cb37c4f5dd4814677e68b` antes de `llvm-symbolizer --obj=<ELF> --inlines 0xc7b480 ...`. Rebuild diferente não valida esses offsets. Sem isso, nomear uma função quente seria invenção.

**Mudança entregue neste PR:** extrator offline com deduplicação, denominadores explícitos e JSON sem logs brutos, acompanhado de testes. Não modifica runtime nem cria métricas ausentes como zero.

## Implementação 2 — constantes pequenas e descriptors estáveis

Não copiar 64 KB por mudança de 16 B se o tradutor puder provar quais bytes cada draw precisa e preservar o valor visto pela draw anterior. O driver recebe snapshots/endereço e não sabe automaticamente que 65.520 B são iguais.

1. Identificar blocos/escritas no tradutor NVN e marcar intervalos sujos. Escolher shader representativo com acessos diretos e outro com índices indiretos. Preservar inicialmente um fallback que copia o snapshot inteiro.
2. Separar valores mutáveis comprovados em push constants (respeitar `maxPushConstantsSize`, ranges e stage flags) ou ring UBO pequeno. Não colocar o bloco inteiro de 64 KB em push constants. Alterar o SPIR-V para buscar o delta separado somente quando a equivalência for provada; com indexação arbitrária no bloco, manter snapshot/fallback ou usar transformação semântica completa.
3. Manter descritores de texturas/heap estáveis e cachear sets por conteúdo e geração; alocar pools por frame em voo e aposentar via fence/timeline. Não sobrescrever memória ainda lida pela GPU. Para upload não coerente, flush respeitando atom size.
4. Comparar três variantes isoladas: sets reutilizados + push constants; ring UBO + offsets dinâmicos; descriptor buffer com descritores persistentes. Não presumir que offset dinâmico é gratuito: `tu_bind_descriptor_sets` copia/ajusta descritores dinâmicos e aloca um set reservado no command stream. Push descriptors também copiam payload; inline uniform block não resolve sozinho a realocação por draw.
5. Turnip já adia emissão de descriptor draw-state para a draw (`tu_dirty_desc_sets`/`tu6_emit_descriptor_sets`). Não propor como novidade o batching que já existe. Uma otimização no driver para binds redundantes exige provar compatibilidade de layout, flags, offsets, descriptors inline e invalidação de estados; só o mesmo handle não basta.
6. IR3 usa `get_ubo_load_range` e `gather_ubo_ranges`: offset constante gera range pequeno; range desconhecido (`~0`) abandona promoção; orçamento de constantes limita o que cabe. UBO de 64 KB não implica carregar 64 KB em const registers. Dump NIR/IR3 deve provar o range antes de alterar o compilador. `nouboopt` sem efeito relatado reduz a prioridade dessa hipótese.

Métricas de aceitação: bytes efetivamente copiados, alocações/updates/binds por quadro real, tempo de CPU por chamada e total, tamanho de command stream e GPU. Pixels e sincronização corretos antes de ganho; executar AB/BA com pelo menos cinco rodadas e temperatura/energia controladas. Não prometer os 10–12% de memcpy ou 12% de descriptors como parcelas integralmente removíveis.

## Implementação 3 — feedback e dependências, antes de remover flushes

O caminho atual em GENERAL sem mecanismo de feedback não torna acessos simultâneos válidos só por mostrar pixels corretos. O [contrato de feedback loop](https://docs.vulkan.org/spec/latest/chapters/renderpass.html#renderpass-feedbackloop) exige layout/estado apropriado; a extensão não ordena arbitrariamente fragmentos que leem/escrevem o mesmo pixel numa draw.

1. Consultar e habilitar `attachmentFeedbackLoopLayout`; Turnip a anuncia no código medido, mas o app precisa habilitar feature/extension. Criar imagens com usage de feedback, layout `ATTACHMENT_FEEDBACK_LOOP_OPTIMAL_EXT` e flags de pipeline de color/depth-stencil feedback, ou estado dinâmico suportado. Usar esse caminho só nas imagens necessárias.
2. Para cada dependência de cor→amostragem, registrar subresource, produtor e consumidor. Exemplo fora de rendering: COLOR_ATTACHMENT_OUTPUT/COLOR_ATTACHMENT_WRITE → FRAGMENT_SHADER/SHADER_SAMPLED_READ. Compute→amostragem requer COMPUTE_SHADER/SHADER_STORAGE_WRITE; uploads exigem TRANSFER_WRITE ou sincronização host conforme a origem. Não trocar tudo por uma barreira fixa. Respeitar as restrições de barreiras dentro de dynamic rendering e as features habilitadas; se necessário, encerrar/reabrir ou usar cópia/ping-pong.
3. Em feedback entre draws, sincronizar a escrita anterior com a leitura; leitura de vizinhança ou conflito dentro da mesma draw pode exigir ping-pong. BY_REGION só quando a dependência for realmente local. Não eliminar barreiras porque GENERAL não muda layout.
4. O Turnip força sysmem quando `pipeline_disable_gmem` indica feedback por textura (`tu_pipeline_update_rp_state`, linha 5571 no baseline). Portanto não promete GMEM barato nem cópia automática para o caminho inválido. Vários passes pequenos já escolhidos sysmem não melhoram simplesmente expondo a extensão.
5. Reduzir fronteiras apenas entre passes semanticamente compatíveis: mesmas attachments/subresources, load/store e hazards preservados. `tu6_sysmem_render_begin/end` e `tu6_emit_flushes` não equivalem a um WFI incondicional por BeginRendering: o estado de cache acumula flushes pendentes e emite os necessários. Medir bits emitidos, WFI/WAIT_FOR_BR e draws por passe em build de laboratório antes de modificar dirty bits.
6. Autotune em `tu_autotune.cc` mantém histórico e algoritmos de estimativa/perfil. Não há um único limiar universal de "175 passes". O modo forçado GMEM pior foi relatado, logo não forçar globalmente GMEM, sysmem nem retirar UBWC.

## Respostas aos demais pontos

**Storage buffers 128 MB e BDA.** `tu_get_properties` obtém `maxStorageBufferRange` da propriedade do chip (A7xx `1 << 27` no catálogo), ou do caminho de emulação SSBO quando habilitado. É um limite exposto pelo caminho de recursos, não tamanho máximo de heap/alocação; não aumentar a constante como workaround. BDA usa endereço global 64-bit (`tu_shader.cc`, `nir_address_format_64bit_global`) e pode endereçar um heap maior sem janela de descriptor, mas requer uso/alocação compatíveis com device address e alinhamento/limites explícitos. O uso de map_memory_placed não habilita automaticamente BDA. Há custo potencial de endereçamento e ausência de proteção equivalente fora de bounds. Testar shader isolado e validar dados; não habilitar SSBO emulation global sem workload discriminante. `uniformAndStorageBuffer8BitAccess=false` é explícito em `tu_device.cc`; shaderInt8/storage8 não tornam UBO byte-addressable. Não alterar feature flag sem implementação/CTS.

**Submit.** `kgsl_queue_submit` mescla waits, monta comandos e chama `IOCTL_KGSL_GPU_COMMAND`; há caminhos de sync FD/timestamp, sparse binds e profiling. Histórico upstream consultado inclui `1da50a1b94027def9d60a08955cd699e382bd3c4` (merge de timestamps e sync files), `2e30bbd3b7d0de6f7f0a72ad40e951411aec5529` (FD-only wait_any), `7e0a2b88e74fd2974a7dd3da0fa9b9e755cdd0b5` (erros queue_submit), `e984ef294eaf5729d8434694f27de32a8922205c` (timeout zero), em 08/10. São candidatos de investigação histórica, **não explicação demonstrada da diferença Turnio→Amaral**. Não temos o source/patchset exato do Turnio R4 nem traces de duração dos ioctls. Reproduzir duas builds de código conhecido, mesmo app/config/energia e sincronização, depois bisectar. Não desabilitar waits ou aumentar frames em voo às cegas.

**LSFG.** Turnip anuncia `shaderStorageImageWriteWithoutFormat` e VulkanMemoryModel no snapshot; isso não promete custo zero nem comprova feature habilitada pelo app. Inspecionar SPIR-V, registros, spills, shared memory e barreiras por dispatch; testar workgroups 64/128/256 invocações apenas se o algoritmo e limites permitirem, sem fixar "melhor" tamanho. `ir3_shader_get_subgroup_size` distingue tamanho base/duplo. Nem int64→32 sem ganho nem `nouboopt` sem ganho justificam patch genérico. Precisamos dos shaders/código LSFG usados para propor mudança compilável; não estão no ZIP.

**LRZ.** Além de writes de profundidade/early tests, stencil, direção do compare, blending/leitura do destino e feedback podem desabilitar teste ou escrita, temporária ou persistentemente. Desabilitar escrita não é igual a desligar todo LRZ. `tu_lrz.cc` mantém esses estados por correção, inclusive "Depth write + blending". Histórico relevante já anterior aos snapshots consultados: `ea3bfc00a4913146697318816fde2dc8bd23820e` (stencil tagging estreito, 29/09), `1f8c5d43b621081330203a76c7698494788e2211` (sticky write-disabled, 29/09), `0cd184e94fc4233d72fba6b9b266a943df4da13a` (partial render area, 24/08), `84d36193fdfe344986fa93f76c67954136803c6d` (depth resolve targets, 24/08). Não são patches novos a acrescentar cegamente à 5.7.13.1. O ganho/defeito particular do jogo precisa de LRZ on/off com resolução fixa e pixels comparáveis.

**UBWC/10-bit.** Investigar criação/view/layout e barriers em `tu_image.cc`, compatibilidade de formatos em `tu_formats.cc`, descritores em `fdl/fd6_view.c` e instruções TEX/SAM/GATHER no IR3. Padrão 16×4 é pista, não diagnóstico automático de UBWC. MUTABLE_FORMAT não é API para desabilitar compressão: o efeito depende da lista de view formats e propriedades do chip (`ubwc_all_formats_compatible`). Reprodutor: clear/draw padrão conhecido em A2B10G10R10, barreira correta, ler por texelFetch/sample/gather e comparar CPU, variando filtros/LOD/component mapping, com/sem compressão comprovada. `textureGather` retorna quatro componentes de vizinhos e não equivale a texelFetch; a tradução precisa validar semântica. Não há, neste lote, shader/reprodutor que demonstre um bug conhecido específico do driver. Manter o workaround localizado já existente no app até esse diagnóstico.

**Contadores sem root.** `KHR_performance_query` só é anunciado com PERFC/PERFCRAW e `is_perf_cntr_selectable`; KGSL define esta propriedade como false no backend consultado. Logo ligar TU_DEBUG=perfc não basta nesse Odin. fdperf é uma ferramenta DRM/MSM, não garantia de funcionamento no KGSL Android. Perfetto de CPU pode ajudar em app debuggable/profileable, conforme permissões; trilha GPU exige build/provedor suportado (`tu_perfetto.cc`/u_trace). Sysfs pode estar bloqueado por SELinux; não tratar clock indisponível como zero. O contador ALWAYS_ON de 19,2 MHz é relógio de timestamps, **não** a frequência do shader core. Sem acesso confiável à frequência, usar modo de energia fixo oferecido pelo aparelho e registrar temperatura; declarar o limite remanescente.

## Entrega e sequência

1. Este PR entrega análise, extrator e resultado sanitizado reprodutível. Testes unitários do extrator e validação documental; nenhum driver foi recompilado, nenhuma feature/versão/patchset alterada.
2. Primeiro obter medição por frame real e baseline sem timestamps intrusivos; depois implementar delta de constantes/descriptors no app, com fallback e imagens.
3. Revisão de shaders, runtime/diag.c e simbolização requer os fontes/ELF exatos. Acesso a esses arquivos não é presumido. O próximo patch Turnip deve responder a caso mínimo e perfil, não ao nome da versão.
4. Candidata 5.7.16.1 e gates MUA3 continuam separados. Não extrapolar BOTWRecomp A740 para A6xx/A8xx, não promover release por esta análise.

Fontes públicas adicionais: [Mesa medido](https://gitlab.freedesktop.org/mesa/mesa/-/tree/4b0f64ceac6a86af38c1e69cd38cf29f84ba611d/src/freedreno), [Mesa candidata](https://gitlab.freedesktop.org/mesa/mesa/-/tree/69f1f21f0258a77046dbaeb8ed7a8ad37a683006/src/freedreno), [IR3 UBO](https://gitlab.freedesktop.org/mesa/mesa/-/blob/4b0f64ceac6a86af38c1e69cd38cf29f84ba611d/src/freedreno/ir3/ir3_nir_analyze_ubo_ranges.c), [timestamps](https://gitlab.freedesktop.org/mesa/mesa/-/blob/4b0f64ceac6a86af38c1e69cd38cf29f84ba611d/src/freedreno/vulkan/tu_query_pool.cc).
