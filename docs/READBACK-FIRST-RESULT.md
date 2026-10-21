# Readback Lab: captura 2026-10-21 00:30:41

Análise observacional, sem qualificação A/B. Integridade do payload validada pelo
manifesto. ZIP SHA-256: eea1cb04ed5eb98f79e6604f25706c426d7dca32231842281797760685d9e9ad.
ELF carregado: ef52ff521329242cc86ab0da451511b3c6a734a365d728311e99742f017a0abb,
correspondente à Standard Readback Lab 5.7.10.1.

## Resultado

- Duração: 667,159 s; 27.541 quadros completos; 41,28 FPS.
- GPU p50/p90/p99: 14,0 / 25,5 / 26,5 ms. União de timestamps das submissões,
  não tempo exclusivo dos shaders; exclui present blit.
- 44,6% dos intervalos guest estão em 28–38 ms; 55,3% em 12–20 ms.
- 372 pipelines restaurados; nenhuma criação de pipeline durante a captura.
- texture_download: 3 esperas, total 26.891 us; guest_sync: 376,67 s em outra
  thread. Não somar tempos sobrepostos ou interpretar waits como custo removível.
- 526,4 draws, 104,9 passes e 4,0 submits por quadro.
- Bytes de download solicitados: 5,013 MB/quadro; não são tráfego GPU medido.
- Clock médio 679 MHz, máximo 680; bateria máxima 27 °C, status térmico 0.
  Esses indicadores não certificam equivalência térmica.
- Captura encerrada pelo usuário; falhas de pipeline/tradução: zero.

## Comparação e limites

Controle 230715 (5.7.8.1): 44,89 FPS; texture_download ~212 s em 20.666 esperas;
GPU p90 23 ms. Mesmo APK, mesmo hash de configurações efetivas
1337a7f3ed7ba6f34966a9a3f4a1dbdaaa09f2f8b80f3c8bd56007b8057b5406 e mesmo jogo.
Cena/carga/cache não equivalentes: o controle restaurou 322 pipelines, criou 50 e
solicitou aproximadamente o dobro de bytes de download por quadro. O hash de
serialização de settings do sumarizador não é o hash canônico de configurações
efetivas do relatório. A diferença de FPS não prova regressão do driver.

A queda das esperas texture_download sem atingir 60 FPS mostra que elas não
explicam sozinhas o desempenho entre capturas. Não prova otimização pela Lab,
que não muda o caminho de cópia nem remove sincronização.

## Instrumentação inconclusiva

Nenhum AMARAL_RB_V1 no logcat. Coletor disponível, zero linhas descartadas
reportadas. Código do coletor aceita tags Mesa; log INFO é habilitado por padrão
no Mesa fixado. Ainda não foi demonstrado que o gate e o lote de 512 regiões
por thread foram atingidos durante a captura. Bytes de staging solicitados e
quantidade de waits não equivalem à contagem de CmdCopyImageToBuffer.

Sem heartbeat periódico ou contador parcial, ausência de linha não distingue
gate inativo, lote incompleto ou perda no caminho de logging. Não inferir
alinhamento, engine r2d/r3d ou ausência de cópias.

## Próxima investigação

Manter Standard 5.7.8.1 como controle; não promover esta Lab. Antes de outra
rodada, tornar observável a ativação dos contadores e lotes parciais, com
frequência limitada. Para localizar o custo sustentado, separar tempo GPU de
render passes/cópias e duração de gravação/submissão/espera. Preservar barreiras,
defaults e scope A740. Não propor GMEM/SYSMEM global nem novo tuning baseado
somente nesta captura. Qualquer mudança no APK Eden deve ser apresentada ao
proprietário antes da implementação.

Decisão: atualizar controle/evidências; sem nova release de desempenho.
