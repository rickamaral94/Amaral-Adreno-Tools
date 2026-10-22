# Mesa após o lock de 19/10 — revisão de 22/10/2026

O lock atual é `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`. O commit
proposto `69f1f21f0258a77046dbaeb8ed7a8ad37a683006` mantém Mesa
`27.0.0-devel` e está 216 commits à frente, sem divergência de ancestralidade,
no espelho público `chaotic-cx/mesa-mirror` do GitLab Mesa. O workflow
`verify-mesa-rebase.yml` confirmou o SHA no GitLab canônico e aplicou
separadamente Standard e OneUI no
[CI de rebase](https://github.com/rickamaral94/Amaral-Adreno-Tools/actions/runs/39765675756).
O patch experimental A825 exigiu ajuste de contexto porque as entradas A830
foram reorganizadas upstream. Seus valores e chip ID ficaram iguais.

## Mudanças aplicáveis observadas no código upstream

| Commit | Mecanismo e escopo | Qualificação pendente |
|---|---|---|
| [`b35f166`](https://github.com/chaotic-cx/mesa-mirror/commit/b35f16697172b660dadd5b646958c89d8f2ed214) | Turnip troca comparação assinada por não assinada no limite do texel buffer emulado; evita aceitar offset negativo fora da view. | Teste de robustez/CTS e apps que usam essa emulação. |
| [`761d5c8`](https://github.com/chaotic-cx/mesa-mirror/commit/761d5c8a54f93b3d43608f718910ed742983dd0b) | Corrige `GRAS_MODE_CNTL` na A6xx; upstream descreve reproducer A650 com instâncias culled, sample mask e hang/misrender. | Reproduzir em A6xx, conferir A7xx/A8xx via regressão. Não é ganho de FPS A740. |
| [`cadc7e4`](https://github.com/chaotic-cx/mesa-mirror/commit/cadc7e42fb72) | Invalida constantes compartilhadas antes de desligá-las na A6xx; evita carga pendente antiga entre pipelines. | CTS de troca de pipeline e hardware A6xx. |
| [`4f6314d`](https://github.com/chaotic-cx/mesa-mirror/commit/4f6314dc9cb11ee105a1cb6f656b4d1cadc736e4) | Libera referência local de BO após `get_vis_stream_patchpoint_cs`; evita retenção indefinida. | Stress de muitos command buffers e memória. |
| [`14656ce`](https://github.com/chaotic-cx/mesa-mirror/commit/14656cee8c37), [`7638039`](https://github.com/chaotic-cx/mesa-mirror/commit/7638039f12d5) | Divide draws indiretos grandes em pacotes menores **somente A8xx**, para evitar GPU faults reportados upstream. | CTS `DrawIndirect*`, replay de faults e hardware A8xx; suporte A8xx ainda experimental. |
| [`69f1f21`](https://github.com/chaotic-cx/mesa-mirror/commit/69f1f21f0258a77046dbaeb8ed7a8ad37a683006) | Completa continuidade de `DrawID` entre os pacotes indiretos A8xx via IR3/NIR e UBO de parâmetros. | Verificar `gl_DrawID` em multi-draw, especialmente draws com count buffer. |

Também entraram correções NIR de loads especulados e coordenadas de cooperative
matrix, além de evitar afinidade CPU herdada na thread de submit Vulkan. Elas
podem afetar Turnip, mas não são evidência de ganho no Little Nightmares. WSI
X11, Intel e RADV não são melhorias diretas do driver Android/Qualcomm.

**Decisão: 3 — criar candidata para avaliação.** A aplicação dos patches passou;
a versão 5.7.14.1 fica em branch isolado. Builds Standard/OneUI duas vezes,
inspeção do pacote e testes em hardware seguem como gates independentes.
Manter Latest 4.7.7.2 e a Candidate 5.7.8.1 publicadas como controles; não
inferir 60 FPS de um Mesa mais novo.
