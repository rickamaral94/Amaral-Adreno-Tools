# Turnip Amaral 26.3.0-devel v4.3

## Compatibilidade primeiro, e para todas as famílias

A v4.3 atualiza a base do Mesa e traz um perfil de compatibilidade para
emuladores de Nintendo Switch. A mudança de método em relação à v4.2 é esta:
**os limites de aplicação foram re-derivados da dependência real de cada
melhoria, em vez de copiados da rotulagem "A740" da origem.**

O resultado é que a maior parte do que veio do [Balemuni's Aurora](https://github.com/Balemuni/Balemunis-Aurora)
não é sobre a A740 — e passa a valer para a6xx, a7xx e a8xx.

## Base

| Item | Valor |
|---|---|
| Mesa | `26.3.0-devel`, commit `451e4a46` (era `6e41d819` na v4.2) |
| NDK | r29, `armv8-a` |
| Backend | KGSL |
| API mínima | Android 10 / 29 |

## A novidade: perfil de compatibilidade para emuladores

Casa `yuzu Emulator`, que é como o yuzu e seus forks — o Eden entre eles — se
identificam em `pApplicationName` e `pEngineName`.

| opção | o que corrige | sintoma |
|---|---|---|
| `tu_dont_care_as_load` | jogos usam `DONT_CARE` esperando que o conteúdo do tile sobreviva; num tiler ele é descartado | blocos pretos, céu piscando, artefatos de terreno |
| `tu_allow_oob_indirect_ubo_loads` | acesso indireto a UBO além do limite declarado | corrupção e **travamento** — o upstream registra laço infinito neste caso |
| `tu_emulate_alpha_to_coverage` | alpha-to-coverage do hardware, que o upstream descreve como algo que *"produz resultados ruins de forma consistente comparado a outros fabricantes"* | folhagem, grama, cabelo |

As duas primeiras são o que o Aurora relata como corretivo para Breath of the
Wild e Tears of the Kingdom. A terceira é acréscimo nosso, por analogia
explícita: o upstream já liga a emulação de alpha-to-coverage para DXVK e
vkd3d-proton, e um emulador é camada de tradução pelo mesmo motivo.

**Alcance universal, verificado no fonte — não suposto.** Nenhuma das três tem
teste de geração:

| opção | onde é lida | tem gate de chip? |
|---|---|---|
| `dont_care_as_load` | `tu_pass.cc`, `attachment_set_ops()` | não, `if` direto |
| `emulate_alpha_to_coverage` | `tu_pipeline.cc` | não, `if` direto |
| `allow_oob_indirect_ubo_loads` | `tu_device.cc` → `compiler_options` | não, `if` direto |

O defeito está no aplicativo e na natureza *tiler* do hardware, que **toda**
Adreno tem. Uma Adreno 660 rodando o mesmo emulador recebe exatamente a mesma
correção que a 740.

**O custo é real e é declarado.** As três desativam uma otimização, e o alcance
é o emulador inteiro, não um jogo — o driver só enxerga o nome do emulador. O
custo do `dont_care_as_load` cresce com o número de tiles, então pesa mais onde
a GMEM é menor. A troca é deliberada: compatibilidade é prioridade 1 do
projeto, desempenho é a 4.

## O que mudou nos limites da afinação Aurora

### GCM: o gate passa a ser o banco de registradores, não a geração

Na v4.2 o GCM ficou em `gen >= 7`, copiando a rotulagem do Aurora. Isso estava
errado. GCM é um passe de NIR, sem dependência de hardware; o que o limita é
**pressão de registrador**, porque hoistar código alonga intervalos de vida e
pode forçar *spill* para memória privada — que custa mais do que o passe
economiza.

E o banco de registradores, no Turnip, vem de `dev_info->props.reg_size_vec4`:
é **por dispositivo, não por família**.

| família | `reg_size_vec4` | GCM na v4.3 |
|---|---:|---|
| a8xx_gen2 | 128 | **ligado** |
| a6xx_gen1, a6xx_gen2 | 96 | **ligado** — era desligado na v4.2 |
| **a7xx inteira, FD740 incluída** | **96** | **ligado** |
| a8xx_base, a8xx_gen1 | 96 | **ligado** |
| a6xx_gen3, a6xx_gen4 | 64 | desligado |
| a6xx_gen1_low | 48 (uma variante 32) | desligado |

A A740 tem **96 — o mesmo que a6xx_gen1 e a6xx_gen2**. Gatear por geração
excluía famílias com orçamento de registrador idêntico ao do alvo onde a
afinação foi testada, e não incluía nada a mais. O gate correto é
`reg_size_vec4 >= 96`.

**Por que a6xx_gen3, a6xx_gen4 e a6xx_gen1_low ficam de fora:** têm de um terço
a metade menos registrador (64, 48, e uma variante com 32). Ali o passe tende a
virar spill, e o remédio fica pior que a doença. Isso inclui Adreno 7c+ Gen 3,
8c Gen 3, 704, 722 e as entradas FD663, FD690, FD702.

Quem quiser medir nessas famílias tem o caminho: `GCM=1` no ambiente liga em
qualquer uma delas, e `GCM=0` desliga em qualquer uma. O override tem
precedência sobre o padrão.

### Suballocadores: agora em todas as famílias

Na v4.2 ficaram em `chip >= 7`. Sem motivo: não há dependência de hardware, e o
custo é limitado. A alocação é preguiçosa (`suballoc->bo = NULL` no init), o
tamanho é `MAX2(pedido, default_size)` e o alocador segura no máximo dois BOs —
o corrente e um em cache. O pior caso é 2 × (512−128) KiB × 2 suballocadores,
cerca de **1,5 MiB**. Passa a valer para a6xx, a7xx e a8xx.

## O que avaliei e deixei de fora

**MR !19316** — limpar o buffer de flags UBWC na transição de `UNDEFINED`.
Corrige travamento por lixo em memória reaproveitada, classe muito relevante
para emulador. Mas é de 2022, toca 8 arquivos e ~490 linhas contra uma base em
que `tu_clear_blit`, `tu_cmd_buffer` e `tu_pass` ainda eram `.c`; hoje são
`.cc`. Portar é reescrita no subsistema de tile, exatamente onde mora a
prioridade 1. Fica para quando houver bancada para validar.

**`tu_restrict_subgroup_size_64`** — o Switch é NVIDIA com warp 32 e a Adreno
expõe 128, então shaders que assumem subgrupo menor podem produzir faixas
verticais e regiões não escritas. É hipótese plausível, **sem evidência
pública** de que atinja emuladores de Switch. Não entra sem medição.

**`disable_conservative_lrz`** — rejeitada: pioraria a correção, que é o oposto
do objetivo desta versão. **`tu_enable_fast_border_color_for_undefined_formats`**
— rejeitada: é otimização para apps que comprovadamente não usam border color.
**Opções de semântica D3D** (`use_tex_coord_round_nearest_even_mode`,
`enable_softfloat32`, emulação de texel buffer e SSBO) — não se aplicam ao
Switch.

## Estado da validação

**Nada da v4.3 foi validado em aparelho.** O que está verificado é o mecanismo:
cada opção foi lida no fonte do Mesa no commit travado, e os seis patches foram
conferidos aplicando contra ele, nas duas variantes.

O `0004` precisou ser **regenerado**: o upstream inseriu `tu_subgroup_size()`
entre `tu_is_vk_1_1()` e `get_device_extensions()`, deslocando as âncoras.
Conferido que as linhas adicionadas e removidas são idênticas às da v4.2
(+47/−5) — só as âncoras mudaram.

Esta release é publicada como **`latest`** — a versão recomendada — por decisão
do mantenedor, e não porque a validação em aparelho tenha sido feita. As duas
coisas não são a mesma, e ficam ditas separadamente:

- **o que está verificado:** cada opção foi lida no fonte do Mesa no commit
  travado; os seis patches aplicam nas duas variantes; cada variante foi
  compilada **duas vezes** e o `.so` saiu byte a byte idêntico, com o relatório
  anexado a esta release;
- **o que não está:** nenhum quadro foi renderizado num Adreno por nós.

Ela substitui a v4.2, que foi retirada de circulação.

Se algo regredir em relação à v4.2, o suspeito tem ordem: primeiro o perfil do
emulador (`0006`), depois o GCM — que agora liga também em a6xx_gen1 e
a6xx_gen2, onde antes não ligava. `GCM=0` no ambiente isola o segundo sem
precisar trocar de driver.

| mudança | teste que a promove |
|---|---|
| perfil do emulador | rodar BOTW/TOTK no Eden: blocos pretos, céu piscando e travamentos devem sumir. Comparar com a v4.2, mesmo trecho |
| GCM em a6xx_gen1/gen2 | `GCM=0` contra padrão no mesmo aparelho |
| suballocadores | cauda de frametime, não média |

## Pacotes

Padrão: `turnip_amaral_26.3.0-devel_v4.3.zip` ·
OneUI: `turnip_amaral_26.3.0-devel_v4.3_oneUI.zip`
