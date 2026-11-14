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
