# Teste: <jogo / workload> — <dispositivo / GPU> — <data>

Status: planejado / observado / A-B qualificado / regressão reproduzida.
Escopo: L0 dispositivo, L1 família, L2 mecanismo compartilhado ou L3 universal.
Responsável pela captura: <nome ou pseudônimo>. Evidência pública: <link/issue/PR>.

## Driver e proposta

| Item | Controle A | Candidato B |
|---|---|---|
| Nome, versão, variante | | |
| Commit Mesa | | |
| Patchset fingerprint | | |
| ELF SHA-256 carregado | | |
| ZIP SHA-256 | | |
| O que muda no código | | |

Hipótese concreta: <mecanismo, GPU afetada e efeito esperado>.
Critério de sucesso e regressão: <definir antes de medir>.

## Ambiente e método

Dispositivo, SoC, GPU/chip ID, Android, KGSL, emulador/commit, jogo/build,
resolução, API gráfica, cache, clocks, modo de energia e versões dos patches.
Cena e rota marcadas: <passos e duração>. Aquecimento: <como>. Ordem:
<AB/BA e cinco rodadas por lado, ou explicar por que é só observação>.
Gate térmico: <sensor, limite e regra de descarte definidos antes>.
Verificação visual: <pontos, screenshots comparáveis e resultado>.

## Capturas e resultado

| Rodada / ID | Driver | Duração | FPS | 1% low | Frametime p95/p99 | GPU p50/p90/p99 | CPU / waits | Clock / temperatura | Crash / pixels |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| | | | | | | | | | |

Pipeline/cache, memória, submit e consumo quando medidos: <valores ou
indisponível>. Não derive 1% low de p99 GPU nem some waits de threads diferentes.

## Conclusão e decisão

Resultado no hardware: <fato observado>.
Comparabilidade e limitações: <diferenças de cena, cache, instrumento, duração>.
Inferência sustentada: <o que a evidência permite afirmar>.
Próximo teste: <experimento que diferencia hipóteses>.
Decisão: manter / atualizar controle / criar candidata / elegível para Latest.

Evidência: <hash SHA-256 do arquivo e local privado, se existir; links públicos
apenas para resumo sanitizado>. Campos ausentes são **indisponíveis**, não zero.
