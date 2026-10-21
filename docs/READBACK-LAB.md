# A740 Readback Lab 5.7.11.1 — V2

Base Standard 5.7.8.1, Mesa 4b0f64ceac6a86af38c1e69cd38cf29f84ba611d.
Autotuner original, sem PROFILED. Diagnóstico, não otimização de desempenho.
Barreiras, comandos GPU, extensões, clocks e seleção do caminho de cópia preservados.

## Por que revisar

A 5.7.10.1 não produziu AMARAL_RB_V1 na captura 003041. Seu limiar de 512 regiões
por thread e ausência de heartbeat tornaram o resultado inconclusivo. Ver
[resultado anterior](READBACK-FIRST-RESULT.md). Não concluir que não houve cópias.

## V2

O callback queue_submit registra AMARAL_RB_V2 na primeira entrada e, enquanto
houver novas submissões, no máximo uma vez a cada 10 segundos. O heartbeat roda
somente nos IDs A740 conhecidos, mesmo quando o filtro de aplicativo falha.
Não depende de atingir um número mínimo de cópias. As chamadas de cópia usam o
mesmo filtro A740 e app/engine exatamente yuzu Emulator da V1.

Campos:
- gpu / chip: identificação numérica recebida pelo driver;
- app_match / engine_match: resultado de cada comparação, sem registrar nomes;
- submit_entries: entradas no callback de submissão A740, não submissões concluídas;
- regions, layers, row_layers, runs: regiões gravadas, camadas, camadas com fallback
  por linha e chamadas a ops->run;
- requested_bytes: bytes lógicos, excluindo padding; não são tráfego de memória;
- r3d_regions: regiões gravadas pelo caminho r3d;
- last_vk_format: último formato observado, não formato dominante do intervalo.

Contadores cumulativos compartilhados por todas as threads e unidades C++ da
biblioteca. Contam dispositivos elegíveis do processo em conjunto; não são
separados por dispositivo. Só se admite interpretar uma captura de um único
processo/dispositivo. Usam atomics relaxed lock-free; a leitura dos vários campos
não é uma transação. Campos podem refletir instantes ligeiramente diferentes.

Para avaliar a janela, subtrair snapshots consecutivos do mesmo processo, nunca
somar snapshots nem usar o primeiro total como atividade da captura. Copias
anteriores à captura entram no total. Lotes com uma única região são visíveis;
o final após o último heartbeat pode ficar fora do log. Sem submissões posteriores,
não há flush final. Command buffers reutilizados/descartados não equivalem a
execuções GPU. Não calcular banda ou duração GPU com estes contadores.

Clock de CPU é consultado em cada entrada A740 para limitar logs. Atomics,
clock e logging adicionam custo. Não usar o FPS da Lab como ganho ou regressão
de tuning. Nenhuma espera GPU, barreira ou lock de diagnóstico foi adicionado.

## Teste no Odin

1. Baixar verified-standard, extrair ZIP externo e importar o ZIP interno 5.7.11.1.
2. Selecionar somente no Little Nightmares e reiniciar o processo Eden.
3. Aquecer o cache, capturar 3–5 minutos no trecho problemático e exportar ZIP.
4. Esperar linhas AMARAL_RB_V2 em logs/driver_logcat.txt a aproximadamente cada
   10 segundos enquanto houver submissões. Não precisa de APK novo.
5. Voltar à 5.7.8.1 Standard depois do diagnóstico.

O APK usa identidade Vulkan genérica: instalação global alcança outros jogos
Eden/yuzu no A740. OneUI não é a variante para o Odin.

## Interpretação e próximo gate

- Heartbeat ausente: verificar logging, IDs e callback; resultado inconclusivo.
- app_match ou engine_match igual a 0: filtro não atendeu à identidade efetiva;
  não interpretar regions=0 como ausência de cópias.
- Matches=1 e regions sem aumento: nenhuma nova região elegível observada entre
  snapshots; não prova ausência de outros tipos de transferência.
- row_layers/runs crescendo muito: investigar alinhamento/stride antes de tuning.
- Cópias alinhadas: investigar duração GPU e trabalho anterior às esperas.

Esta versão ainda não separa tempo GPU de render passes e cópias. Essa etapa
exigirá instrumentação de timestamps apropriada, potencialmente no Eden, que
será apresentada ao proprietário antes de alterar o APK. Não remover fences ou
Finish, não forçar GMEM/SYSMEM e não anunciar 60 FPS com base nestes contadores.

Testes locais executam o header real do patch, filtros positivos/negativos,
intervalo do heartbeat, contagens concorrentes e estado compartilhado entre
unidades de compilação. CI exige duas builds independentes por variante e
comparação ZIP/ELF. Compatibilidade em hardware e CTS continuam pendentes.
