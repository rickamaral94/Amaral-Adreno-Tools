# A740 Readback Lab 5.7.12.1 — V3

Base Standard 5.7.8.1, Mesa 4b0f64ceac6a86af38c1e69cd38cf29f84ba611d,
autotuner original. Instrumentação para resolver a ausência de heartbeat na V2.
Não é tuning ou build de performance. Barreira, comando GPU, escolha de cópia,
clocks, extensão e precisão preservados.

## Evidência

- [Primeira captura: V1 sem lote de 512](READBACK-FIRST-RESULT.md).
- [Segunda captura: V2 sem heartbeat](READBACK-SECOND-RESULT.md).
- [Registro de testes em hardware](https://github.com/rickamaral94/Amaral-Adreno-Tools/blob/main/docs/tests/2026-10-odin2-portal-little-nightmares.md).

A 5.7.11.1 carregou pelo SHA-256 do ELF, mas não emitiu `AMARAL_RB_V2` em 817 s.
O código da V2 chamava o logger somente após um filtro pelos IDs A740 conhecidos;
o ZIP não revela os IDs internos do Turnip. A V3 remove esse pré-requisito **só
para o heartbeat**. O contador de cópias conserva o mesmo gate A740/Eden.

## Instrumentação V3

No callback `queue_submit` ou `queue_submit_sparse`, uma GPU com geração 7
reporta `AMARAL_RB_V3` diretamente ao logcat Android com tag `AmaralRB`, no
máximo uma vez por processo a cada dez segundos. A geração vem do perfil real
que o driver usa. Reporta `path`, `gpu`, `chip`, `app_match`, `engine_match`,
`scope`, `queue_entries` e acumulados de cópias.

`scope=1` significa que o filtro A740/Eden que protege os contadores passou.
`scope=0` junto de IDs visíveis identifica precisamente qual premissa falhou.
Nenhum nome do aplicativo, endereço de memória ou conteúdo de imagem entra no
log. O heartbeat abrange A7xx apenas nesta build de laboratório; outros jogos
A7xx que carregarem a Lab também verão o log. Instale por jogo no Odin.

`regions`, `layers`, `row_layers`, `runs`, `requested_bytes`, `r3d_regions` e
`last_vk_format` são acumulados de **gravação** do comando elegível, não de
execução GPU. Não usar bytes solicitados como tráfego medido nem somar snapshots.
Subtrair duas linhas consecutivas. São atomics relaxed entre threads: os campos
não formam snapshot transacional e podem variar ligeiramente de instante.
O tempo de consulta do relógio, atomics e log é overhead diagnóstico. FPS da
Lab não certifica ganho nem regressão. Se não houver entradas novas na fila,
não haverá heartbeat posterior ou flush final.

A V3 usa o logger Android diretamente para distinguir a eventual configuração
do logger Mesa. Caso não apareça, o problema pode estar no callback escolhido ou
na coleta Android; a ausência não é evidência de zero cópias. Se o heartbeat
aparecer com `scope=0`, corrigir o gate apenas depois de ler os IDs reais; não
ampliar o filtro por suposição. Se `scope=1` e `regions` crescer, examinar
`row_layers/runs` antes de propor otimização de alinhamento/stride.

## Teste no Odin

1. Baixar `verified-standard`, extrair o ZIP externo e importar o ZIP interno
   5.7.12.1 no Eden apenas para Little Nightmares.
2. Reiniciar o processo, aquecer o jogo e capturar 3–5 minutos na rota com
   quedas, com o Eden Diagnostics atual. Nenhum APK novo é necessário.
3. Procurar `AMARAL_RB_V3` em `logs/driver_logcat.txt`; enviar o ZIP completo.
4. Voltar à 5.7.8.1 Standard após o teste. OneUI não é a variante do Odin.

Testes locais executam o header real, scope positivo/negativo, contagens
concorrentes e estado entre unidades C++; aplicação da patch no Mesa fixado.
CI compila duas vezes cada variante e compara ZIP/ELF. CTS e validação
funcional em hardware desta V3 continuam pendentes.
