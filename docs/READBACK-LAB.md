# A740 Readback Lab 5.7.10.1

Objetivo: identificar o caminho de cópia antes de otimizar. Base exata 5.7.8.1
Standard, Mesa 4b0f64ceac6a86af38c1e69cd38cf29f84ba611d. Não inclui o patch
PROFILED da Lab 5.7.9.1. Não altera barreiras, comandos GPU, UBWC, extensões,
precisão, clocks ou a escolha dos caminhos de cópia. Não é build de performance.

## Evidência e hipótese

Na captura 230715, 5.7.8.1 carregou corretamente e registrou 44,89 FPS contra
40,80 da captura Lab 224224. Os workloads e readbacks diferem; não é um A/B
qualificado. PROFILED permanece fora do main sem benefício demonstrado.

A captura 230715 registrou 20.666 esperas texture_download, 212 s de wall time
na thread GPU. Esses 212 s não são duração exclusiva de cópias nem tempo que
pode ser removido: o fence espera trabalho anterior também. Os tempos de threads
se sobrepõem. Não se conclui que banda de memória ou o blitter seja o gargalo.

No APK 6b592ecbea, TextureCache::DownloadMemory pode copiar imagens completas e
chamar runtime.Finish() por imagem antes de SwizzleImage no CPU. Existem outros
chamadores de Finish; o rótulo texture_download não identifica o chamador.
Em tu_copy_image_to_buffer, pitch ou endereço desalinhado a 64 bytes exige
cópias por linha, com possível operação adicional no limite MAX_VIEWPORT_SIZE.
O caminho geral usa r2d; certos formatos usam r3d. Os diagnósticos anteriores
não registram qual desses caminhos realmente ocorreu.

Referências:
- https://github.com/rickamaral94/Logs_eden/blob/6b592ecbeaac9631ffef1cb5735931ed1083189b/src/video_core/texture_cache/texture_cache.h
- https://github.com/rickamaral94/Logs_eden/blob/6b592ecbeaac9631ffef1cb5735931ed1083189b/src/video_core/renderer_vulkan/vk_texture_cache.cpp
- https://github.com/chaotic-cx/mesa-mirror/blob/4b0f64ceac6a86af38c1e69cd38cf29f84ba611d/src/freedreno/vulkan/tu_clear_blit.cc

## Instrumentação

Gate: IDs A740 conhecidos e app/engine exatamente yuzu Emulator. Contadores
thread-local, sem locks, alocação dinâmica ou waits. Uma linha AMARAL_RB_V1 a cada
512 regiões de cópia gravadas por thread. Não registra endereços ou conteúdo.

Campos:
- regions: regiões gravadas no lote, normalmente 512;
- layers: camadas processadas;
- row_layers: camadas que entraram no fallback por linha;
- runs: chamadas reais a ops->run, incluindo sobras de linha;
- requested_bytes: bytes lógicos das regiões após conversão de blocos comprimidos,
  excluindo padding; não mede tráfego de memória, compressão ou bytes concluídos;
- r3d_regions: regiões que usaram o caminho r3d;
- dominant_vk_format / dominant_regions: formato VkFormat mais frequente entre
  os enums 0..255 nesse lote e sua contagem;
- other_format_regions: enums fora de 0..255, contados sem indexar o array.

São contagens de gravação do command buffer, não de execução GPU: um buffer
reutilizado pode executar mais vezes; um buffer descartado pode não executar.
Lotes parciais ficam fora do log. As mensagens podem chegar depois do trabalho
que descrevem e parte do lote pode anteceder a captura. Não calcular banda ou
correlação por frame com esses totais. Threads diferentes não compartilham lote.

Log periódico evita depender da mensagem de inicialização que o APK atual perde.
O custo de contagem/log é diagnóstico e pode afetar desempenho; não usar FPS
desta build como resultado de uma otimização. Testes cobrem scope, soma, reset e
formatos fora do intervalo. Compilação/reprodutibilidade não substituem CTS.

## Teste no Odin sem APK novo

1. Baixar verified-standard da execução lab-readback.yml e extrair o ZIP externo.
2. Importar o ZIP interno 5.7.10.1 no Eden e selecionar apenas em Little Nightmares.
3. Reiniciar o processo, percorrer o trecho e aquecer o cache normalmente.
4. Iniciar diagnóstico e jogar 3–5 minutos na rota com quedas; exportar o ZIP.
5. Procurar AMARAL_RB_V1 em logs/driver_logcat.txt. Com poucas cópias ou lotes
   incompletos pode não haver linhas; isso não é prova de zero readbacks.
6. Voltar à 5.7.8.1 Standard após a investigação. Não usar OneUI no Odin.

O APK não envia o título ao Vulkan: instalação global também afeta outros jogos
Eden/yuzu no A740. Outros IDs/engines não entram na contagem. Nenhuma mudança no
Eden foi feita; o coletor existente pode capturar as mensagens periódicas.

## Decisão após a captura

- Muitos row_layers/runs: investigar alinhamento de staging/stride e custo do
  fallback antes de propor uma alternativa com resultados equivalentes.
- Predomínio de cópias alinhadas r2d: não otimizar um fallback que não ocorre;
  medir execução GPU das cópias e trabalho anterior ao fence.
- r3d relevante: identificar formato/aspecto e exigências de correção antes de
  mudar engine de cópia.
- Nenhum caso autoriza remover Finish, waits, flushes ou barreiras por flag.

Para decompor o fence futuramente, o Eden precisará registrar chamador, tamanho,
formato, número de imagens e duração separada de cópia GPU, espera e swizzle CPU.
Essa instrumentação será proposta ao dono antes de alterar o APK.

Branch de laboratório somente, com duas builds por variante e sem publicação
ou promoção automática. Meta de 60 FPS continua pendente.
