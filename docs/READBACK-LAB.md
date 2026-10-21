# A740 Readback Lab 5.7.13.1 — V4

Base Standard 5.7.8.1, Mesa `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`,
autotuner original. Diagnóstico, não build de performance. Sem alteração de
comandos GPU, barreiras, caminhos de cópia, clocks ou capabilities Vulkan.

## Por que a V4 existe

A [captura V3](READBACK-THIRD-RESULT.md) identificou no Odin `gpu=6760` e
`chip=0x43050a01`, com app/engine Eden corretos, mas `scope=0`. As V1–V3 exigiam
que `gpu_id` fosse 0 ou 740 mesmo quando o chip ID exato FD740 estava presente.
O Mesa já reconhece 0x43050a01 como FD740 KGSL. Essa premissa adicional impediu
as contagens e o heartbeat da V2; não foi uma medição de zero readbacks.

A V4 reconhece **apenas** 0x43050a01 e o fallback 0xffff43050a01 como FD740,
independentemente do valor legado `gpu_id`, e conserva o caso `gpu_id=740` com
`chip_id=0`. Os demais chip IDs não passam no gate, mesmo dentro da família
A7xx. O filtro de app/engine `yuzu Emulator` continua obrigatório para contar.
O chip ID comprovado no hardware, não uma suposição para toda A7xx, fundamenta
a correção. Nada muda em A6xx/A8xx.

## Mensagens e limites

Como na V3, os callbacks `queue_submit` e `queue_submit_sparse` em Android
registram `AMARAL_RB_V3` com tag `AmaralRB` quando a geração real do perfil é 7.
O log direto precede o filtro A740, até uma linha por processo a cada dez
segundos. Campos: `path`, `gpu`, `chip`, `app_match`, `engine_match`, `scope`,
`queue_entries`, `regions`, `layers`, `row_layers`, `runs`, `requested_bytes`,
`r3d_regions` e `last_vk_format`. Esperamos `scope=1` no Odin; verificar no ZIP,
não supor.

Os totais são cumulativos de gravação de comandos, não execuções GPU nem tempo.
Subtrair duas linhas consecutivas para estimar atividade na janela. Os campos
são atomics relaxed e não formam snapshot transacional. Bytes solicitados não
são tráfego efetivo. O último formato não é histograma. Buffers reutilizados ou
descartados não se traduzem diretamente em número de execuções. A consulta ao
relógio, atomics e log criam overhead; não comparar FPS da Lab como otimização.
O logger de geração A7xx pode emitir mensagem para outros jogos A7xx se a Lab
for instalada globalmente, mas os contadores continuam gated no FD740/Eden.

## Teste no Odin

1. Baixar `verified-standard`, extrair o ZIP externo e importar o ZIP interno
   5.7.13.1 apenas para Little Nightmares. Reiniciar o processo Eden.
2. Aquecer e capturar 3–5 minutos na rota com quedas. O Eden Diagnostics atual
   basta; exportar o ZIP completo.
3. Em `logs/driver_logcat.txt`, verificar `AMARAL_RB_V3` e `scope=1` antes de
   interpretar incrementos de `regions`, `row_layers`, `runs` ou `r3d_regions`.
4. Voltar à 5.7.8.1 Standard depois. OneUI não é a variante do Odin.

Se `scope=1` e `regions=0` entre snapshots, isso significa que nenhuma nova
região elegível foi gravada nesse intervalo, não ausência de outras
transferências. Se houver muitas camadas no fallback por linha, investigar
alinhamento/stride e tempo GPU antes de propor tuning. Não remover fences,
Finish ou barreiras por causa destes contadores. CTS/validade visual e tempo GPU
por operação ainda não foram medidos nesta Lab.

Testes locais exercitam o header C++ real, inclusive o chip ID visto no Odin,
IDs negativos, contagem concorrente e estado entre unidades. CI exige aplicação
no Mesa fixado e duas compilações independentes por variante com ZIP/ELF iguais.
