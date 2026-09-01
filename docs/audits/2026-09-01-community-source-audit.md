# Auditoria de fonte comunitária — 1º de setembro de 2026

Esta auditoria compara código, workflows, patches e binários. Afirmações de
README/release foram tratadas como hipótese até encontrar mecanismo verificável.

## Resultado executivo

| Projeto | O que existe de fato | Decisão Amaral |
|---|---|---|
| Mesa main | base reproduzível e 188 commits após v4.4 | atualizar para `eaa8cb690243` |
| Banners A6/A7 | Mesa main limpo, automatizado | controle nightly; nada para portar |
| StevenMXZ A6/A7 | build de Mesa main; patches históricos não compõem a linha atual | baseline; nada exclusivo |
| StevenMXZ Gen8 | empacota `whitebelyash/mesa-unified` | referência A8xx, não fonte independente |
| Balemuni Apex V2 | apenas binários/README; driconf recuperável do ELF | portar somente regras isoláveis BOTW/TOTK |
| MrPurple T30 | binários e changelog, sem fonte/workflow correspondente | A/B externo; não importar |
| whitebelyash gen8 | fonte experimental A8xx com vários hacks globais | manter A825 isolada; rejeitar globais |

## Mesa atualizado

Entre a base v4.4 (`451e4a464788`) e `eaa8cb690243`, foram identificadas
correções relevantes no Turnip/Freedreno:

- feedback de hit do pipeline cache;
- stitching de descriptors em graphics pipeline libraries;
- propriedades/aspectos corretos para imagens esparsas D32S8;
- reserva segura de estado VPC com geometry shader;
- otimização `nir_opt_non_uniform` no IR3;
- refatoração do autotuner e medição GPU tick→ns mais precisa;
- opção experimental upstream `TU_DEBUG=gmem_warmup`, mantida desligada.

O header Vulkan permanece em `1.4.359`; número de API não é usado como ranking.

## Balemuni Apex V2

O repositório público não contém os patches nem workflow reprodutível. Foram
baixados os dois artefatos oficiais e verificados hashes diferentes, confirmando
que Universal e Ultimate são binários distintos. A inspeção do ELF encontrou o
driconf efetivamente embutido:

- regra ampla de engines: fast border color, texcoord round-even, OOB indirect
  UBO e DONT_CARE-as-LOAD;
- BOTW: `tu_autotune_algorithm=prefer_gmem`;
- TOTK: `prefer_gmem` + `tu_ignore_frag_depth_direction`.

As issues públicas sobre água/flicker de BOTW e grama/terreno de TOTK ainda não
contêm confirmação independente suficiente. Por isso, o Amaral não copia a
regra ampla. A v4.5 concentra o conjunto dentro dos dois títulos e só o ativa
quando o frontend revela `botw`/`totk` em `pApplicationName`.

### O que não foi importado

- NDK r28 como suposta otimização: toolchain sozinho não prova frame pacing.
- cache de shader de 4 GiB: não evita compilação inicial e falta A/B.
- `-mcpu`/tuning Cortex-X3: quebraria a proposta universal.
- fingerprint de pacote: melhora identificação no gerenciador, não rendering.
- regra para todos os emuladores: alcance excessivo e risco de regressão.

## whitebelyash / A8xx

O ramo `turnip/gen8` continua útil para pesquisa de A825/A829/A830/A840, mas
contém mudanças que não podem ser generalizadas:

- desativação global de concurrent binning;
- shared memory de 64 KiB aplicada globalmente;
- leitura UBWC global sem a guarda upstream equivalente;
- desativação de FDM/sample interpolation por modelos;
- spoof não conforme de versão Vulkan;
- perfis que forçam modos de memória.

Uma condição no conjunto FDM/MSAA (`chip_id == X || constante`) é sempre
verdadeira em C/C++, ampliando a mudança para alvos não pretendidos. O Amaral
rejeita esse conjunto. O perfil A825 existente permanece isolado pelo chip_id e
sem forçar GMEM/SYSMEM.

## OneUI e portabilidade

`TP_UBWC_FLAG_HINT` não é otimização universal. O próprio Mesa documenta a
necessidade de coincidir com os demais drivers do sistema em hardware afetado.
Portanto a variante OneUI continua limitada à FD740/KGSL; replicá-la por
semelhança em A6xx/A8xx poderia causar corrupção de layout.

## Evidência interna

Os issues recentes do Driver Lab não demonstraram vitória para `force_sysmem`,
perfil Perf amplo nem driconf amplo. Isso sustenta a v4.5 como pré-release e a
v4.4 como controle estável. Promoção exige A/B por família e por título conforme
`docs/EVIDENCE-POLICY.md`.

## Matriz de teste v4.5

| Braço | Comparação | Métricas mínimas |
|---|---|---|
| upstream | v4.4 × v4.5 em jogo sem perfil | pixels, crash, FPS, P95/P99 |
| BOTW | v4.4 × v4.5, mesma cena/cache | água, shrines, flicker, frametime |
| TOTK | v4.4 × v4.5, mesma cena/cache | grama, terreno, profundidade, frametime |
| famílias | A6xx, A7xx, A8xx disponíveis | imagem antes de performance |
| variantes | Standard × OneUI na FD740 | textura/blit/escala e estabilidade |

Se o frontend não expuser o título no nome Vulkan, o perfil Zelda não ativa;
isso deve ser registrado no relatório, e não contornado com regra global.
