# Lab A740 PROFILED — primeira captura física

Decisão: **2 — atualizar controle/evidências**. O experimento permanece em
avaliação, sem promoção e sem uma segunda mudança de tuning sobreposta.

## Identidade e integridade

Captura nova: `20261020-152817-1977`, 297,91 s, Little Nightmares, Odin2 Portal,
A740. Todos os tamanhos/hashes de payload listados no manifesto foram conferidos.
ELF carregado `1038279f89312dc7f5a9dedd033000b8ed94ae6e36b878e7ecbe5210695ce077`:
corresponde ao Standard Lab 5.7.9.1 compilado na execução 39443817769.
Comparação observacional com `20261020-143555-9611`, Standard 5.7.8.1.

Mesmo APK `6b592ecbeaac9631ffef1cb5735931ed1083189b`, game build ID, hash de
configurações efetivas, FIFO 1920x1080 e clock GPU reportado de 680 MHz.
Essas igualdades melhoram o controle, mas não fixam o workload ou estado de cache.

## Observações (não são resultado A/B qualificado)

| Métrica | 5.7.8.1 | Lab 5.7.9.1 |
|---|---:|---:|
| Duração s | 162,75 | 297,91 |
| FPS médio | 44,27 | 37,77 |
| GPU p50 ms | 15,75 | 15,25 |
| GPU p90 ms | 24,75 | 27,5 |
| GPU p99 ms | 39 | 35 |
| Draws/quadro | 371,9 | 613,9 |
| Render passes/quadro (workload) | 103,4 | 117,3 |
| Upload solicitado KiB/quadro | 1469,9 | 3016,7 |
| Pipelines restaurados no início do título | 0 | 189 |
| Novos pipelines gráficos na captura | 100 | 85 |
| Maior criação de pipeline ms | 114,326 | 45,954 |
| Intervalos guest de 28–38 ms | 33,4% | 55,5% |

O novo workload tem aproximadamente 65% mais draws/quadro e o dobro de bytes
solicitados para upload. Não inferir aumento de custo por draw, regressão do
patch ou ganho no p99 a partir dessa comparação. Câmera, objetos, shaders e
caminho percorrido influenciam o custo, mesmo com as mesmas configurações.
Não há marcadores de cena ou réplicas AB/BA. O novo registro é game_run 2 no
processo; não é uma execução isolada com estado inicial demonstrado equivalente.

A bateria alcançou 26 °C e thermal status 0 em ambos. São sinais disponíveis,
não prova de equivalência térmica interna. O KGSL busy do controle era suspeito
(25 amostras repetindo exatamente 79,004%); não comparar com os 40,5% novos.

Nenhum erro de criação/tradução, device lost ou crash foi registrado na captura;
ela terminou por ação do usuário. Correção visual e estabilidade prolongada
continuam sem confirmação. O registro de inicialização AMARAL_LAB não está no
logcat da captura: o coletor começa depois da inicialização. Hash confirma o
binário, mas seleção efetiva do algoritmo e modos por passe não foram observados
diretamente. A ativação é esperada pelo gate e pela ausência de overrides
reportados; não tratá-la como medição dos modos executados.

## Travadas e escopo do autotuner

Nove das dez janelas com intervalos longos não registram novos pipelines.
Há quatro janelas aproximadamente em 82,54 / 142,91 / 203,25 / 263,60 s, com
espaçamento próximo de 60,35 s. As respectivas amostras não reportam GC ou
blocking GC e não há linhas de log próximas que identifiquem a causa. Isso é
uma pista temporal, não diagnóstico de filesystem, compilador ou driver.
A maior pausa, ~800 ms, coincide na janela com chamadas de serviços de save;
essa proximidade também não estabelece causalidade.

A distribuição de draws/pass registra ~20,7% de passes com cinco ou mais draws
na Lab, contra ~11,5% no controle. É apenas um teto aproximado da parcela que
pode chegar à seleção complexa do autotuner: outros guards podem escolher o modo
antes. Não representa proporção do tempo GPU. A mudança testada não visa os
passes pequenos, já encaminhados para SYSMEM pelo caminho padrão quando cabível.

O início das capturas contém passes semelhantes (~86–89 por quadro), mas a
trajetória diverge e isso não justifica selecionar pequenos trechos a posteriori
para anunciar vitória. Preservar a captura inteira e repetir uma rota marcada.

## Próximo passo executável

Capturar **5.7.8.1 Standard no trecho desta captura Lab**, mesmo APK e configurações,
com cache aquecido separadamente e processo reiniciado ao trocar driver.
Marcar início/fim de rota; usar a mesma duração e repetir AB/BA em cinco rodadas.
Confirmar visualmente sombras, iluminação, transparências e transições.

Somente depois separar hipóteses: se PROFILED piorar com workload equivalente,
retirar o perfil; se melhorar, medir dispersão/p99 e estabilidade antes de ampliar
escopo. Ainda não há justificativa para forçar SYSMEM, alterar UBWC, precisão de
shaders ou barreiras. A meta de 60 FPS não foi atingida nesta captura.

Para uma futura revisão do APK: preservar logcat de inicialização, registrar
identidade Vulkan app/engine e acrescentar spans de operações periódicas/cache
save/presentation para localizar as pausas. Não atribuir genericamente GMEM ao
modo default. Nenhum código do Eden foi alterado nesta análise.

Evidência selecionada, sem publicar logs brutos:
[JSON reproduzível](../evidence/diagnostics/2026-10-20-ln-lab-first-result.json).
