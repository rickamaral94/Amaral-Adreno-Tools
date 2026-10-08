# Auditoria upstream e roteiro por família — 8 de outubro de 2026

Base comparada: Mesa fixado `c126acd85a64` (v4.7.4.1) × Mesa `main`
`5a2730169b75`, com 233 commits de diferença. Os patches foram aplicados nas
duas árvores e a device database do Freedreno foi gerada em cada uma.

## 1. Quebra encontrada e corrigida

O commit upstream `17ca6174dcc` ("freedreno: Drop magic_regs") removeu o
argumento `magic_regs` de `A6xxGPUInfo`. Os patches continuavam passando em
`git apply --check`, mas o gerador Python falhava no build:

| Patch | Erro no Mesa main |
|---|---|
| `0002` (perfil A825) | `TypeError: unexpected keyword argument 'magic_regs'` |
| `0003` (OneUI) | `NameError: name 'a740_magic_regs' is not defined` |

Sem correção, o `publish-upstream` diário pararia na próxima atualização do
lock. Correções:

- `0002`: o perfil A825 só passa `magic_regs` quando o gerador da árvore ainda
  aceita esse argumento. Funciona antes e depois de `17ca6174dcc`.
- `0003`: deixa de duplicar o bloco upstream da FD740. A variante copia o perfil
  upstream já resolvido das duas entradas KGSL e liga somente
  `enable_tp_ubwc_flag_hint`. A cópia antiga ficava congelada e, mesmo sem a
  quebra, divergiria em silêncio de qualquer ajuste upstream na FD740.

Verificação feita com `scripts/check_device_table.sh`:

- no Mesa fixado, Standard e OneUI geram uma database idêntica, registro a
  registro (89/89), à da revisão anterior dos patches;
- no Mesa main, a OneUI difere da Standard só em
  `enable_tp_ubwc_flag_hint=True` em `0x43050a01` e `0xffff43050a01`;
  `GPUId(740)` e X1-85 continuam sem alteração.

O CI ganhou essa geração no SHA fixado e o job `upstream-canary`. O canary
aplica o patch set no `mesa/main` atual e mostra quebras desse tipo no PR,
antes da automação diária. Ele não bloqueia merge.

## 2. O que chega no próximo snapshot upstream, sem patch Amaral

| Commit | Efeito | Famílias |
|---|---|---|
| `19c877f9b75` | suporte inicial a A735 e A753 | A7xx |
| `1887da10a6e` | corrige a checagem invertida de descriptor variável em `can_speculate_descriptor_load` (leitura além do set) | todas |
| `f7ca1f55151` | `SP_CHICKEN_BITS_2` b30 somente para Half-Life: Alyx na A750 (+2,4% nesse título; outros títulos pioram, por isso fica preso ao app) | A750 |
| `5cea3f8fb30` | QCTDD04536579 vira quirk real (RB_DBG_ECO_CNTL em blit 2D) | dispositivo afetado |
| `5622c8717a7`, `bb79ed7b74d` | input attachment via intrinsics de coordenada | todas |
| `9ce7a2ef35a`, `ee29d6c94cd` | correção de CSE de texturas no NIR | todas |

Esses itens seguem o canal `Latest` por serem Mesa puro. O padrão do
`f7ca1f55151` (ganho real, mas preso ao título porque regride outros) é o
mesmo que o projeto já usa para BOTW/TOTK.

## 3. Simplificação possível nos aliases KGSL

`dev_id_compare()` (regra c) faz OR de `0x0000ffff00000000` no chip_id vindo do
kernel antes de comparar. Assim, a entrada `0xffff44010200` já reconhece o
KGSL `0x44010200`. Os aliases sem `0xffff` em `0002` (A810, A812) e `0011`
(A840v2) são redundantes. Não causam dano, mas aumentam a superfície de
patch. A remoção deve ser feita com cuidado, porque `validate_project.py`
afirma esses textos.

## 4. Roteiro recomendado

Na ordem do projeto: compatibilidade, estabilidade, frametime e desempenho.

### 4.1 Levar os patches de estabilidade ao Mesa

`0007` (lifetime/erro), `0009` (merge TS/FD) e `0010` (poll KGSL com timeout
zero) ainda aplicam limpo no main. Ou seja, não estão upstream. Abrir MRs no
Mesa traz revisão dos mantenedores do Turnip, que é a melhor validação
disponível. Também reduz o patch set e deixa a correção para todos os drivers
derivados. Quando o MR entra, o patch sai daqui.

### 4.2 Medir o compilador sem aparelho, em todas as famílias

A dúvida sobre GCM (`0005`) é se A6xx gen3/gen4 (`reg_size_vec4 = 64`) ganham
ou sofrem spill. Isso pode ser medido offline e de forma determinística:

1. capturar bancos Fossilize dos jogos/emuladores do Driver Lab;
2. reproduzir em x86 com o Turnip sobre o drm-shim do Freedreno
   (`freedreno_noop`), trocando o GPU ID por família;
3. comparar as estatísticas de `VK_KHR_pipeline_executable_properties`
   (instruções, spills, registradores, waves) com `GCM=0` e `GCM=1`.

O resultado não substitui o A/B de frametime, mas define o gate do GCM por
evidência em vez de inferência. Também serve para qualquer patch futuro do
ir3. Antes de usar, confirmar que o modo noop do drm-shim cobre o caminho de
compilação do Turnip no SHA fixado.

### 4.3 Exercitar as extensões expostas

O `depth-extensions` foi medido só com a extensão desligada (Driver Lab #69).
Antes de promover, rodar subconjuntos do dEQP-VK em uma GPU por família:

- `dEQP-VK.draw.*depth_bias*` e os testes de `depth_bias_control`;
- testes de `depth_range_unrestricted` (A7xx+);
- `dEQP-VK.synchronization.*` e `dEQP-VK.api.external.semaphore.sync_fd.*`
  para `0009`/`0010`.

### 4.4 Desempenho de CPU do driver (hipótese)

Emuladores fazem muitos draws, então o overhead de CPU do Turnip pesa no
frametime. ThinLTO (`-Db_lto=true`) com o NDK r29 é uma hipótese razoável de
ganho sem tocar no comportamento da GPU. É mudança de toolchain, portanto entra
como candidata, com A/B de P95/P99 e conferência da reprodutibilidade byte a
byte, que o LTO pode afetar.

### 4.5 Cobertura de família

| Família | Situação | Próximo passo |
|---|---|---|
| A6xx | upstream completo; GCM fora em gen3/gen4/gen1_low | decidir GCM pelo item 4.2 |
| A7xx | upstream completo; A735/A753 chegam no próximo snapshot | registrar A735/A753 na matriz de teste |
| A8xx | A810/A830/A829/A840 upstream; A812/A825/A840v2 Amaral | A812 sem teste em hardware; priorizar relatório real |

## 5. Não recomendado

Continuam rejeitados pelas razões já registradas: forçar GMEM/SYSMEM, spoof de
vendor/versão, driconf amplo por emulador, hacks globais A8xx de
FDM/MSAA/UBWC/shared memory e cache de shader gigante sem A/B.
