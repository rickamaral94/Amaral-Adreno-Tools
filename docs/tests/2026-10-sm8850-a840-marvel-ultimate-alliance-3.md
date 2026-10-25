# Marvel Ultimate Alliance 3 no Samsung SM-F971B (A840) — outubro de 2026

Status: **observado**. Escopo: L0 (este aparelho e chip). Primeira série física
A8xx do projeto.

Hardware: Samsung SM-F971B, SM8850, Adreno 840 de três slices (chip KGSL
`0x44050A31`, 6 CCU, alinhamento de tile 96), Android 17 (API 37), kernel 6.12,
KGSL, ARM64. Workload: Marvel Ultimate Alliance 3 `010060700AC50000` no Eden
`604cde0b1b964c7bb0092550ec62511545096bc2`. O
[JSON de evidência](../../evidence/hardware-tests/2026-10-sm8850-a840-marvel-ultimate-alliance-3.json)
guarda hashes e métricas selecionadas, sem logs brutos.

## Driver e perfil de GPU

| Item | Valor |
|---|---|
| Driver | Candidata 5.7.14.1 **Standard** ([PR #27](https://github.com/rickamaral94/Amaral-Adreno-Tools/pull/27)) |
| Mesa | `69f1f21f0258a77046dbaeb8ed7a8ad37a683006` |
| ELF carregado | `7fcdb9fb922357a04c05e8fa7dad128b8b85de7763b6c90901007c8fc76916ab` |
| Perfil | `GPUId(chip_id=0xffff44050A31)` upstream; nenhum patch Amaral toca este perfil |

**OneUI não se aplica.** Nos catálogos de GPU gerados pelas builds da 5.7.14.1,
só as duas entradas FD740 (`0x43050a01`, `0xffff43050a01`) diferem entre
Standard e OneUI; os perfis A840 `0xffff44050a31` e `0xffff44050a21` são
idênticos. Ser Samsung não muda a variante para esta GPU.

## Capturas

| ID da captura Eden | Duração | FPS | 1% low | Frametime p95/p99 | GPU p50/p90/p99 ms | Configuração | Integridade |
|---|---:|---:|---:|---|---|---|---|
| `20261025-024143-0731` | 1,21 s | 28,62 | indisponível | indisponível | 9,0 / 11,8 / 12,3 | Global: Handheld, NearestNeighbor, dynamic state desligado | Manifesto verificado |
| `20261025-025226-4468` | 77,35 s | 29,87 | 20,77 | 33,76 / 35,32 ms | 12,0 / 16,5 / 20,0 | Perfil do jogo: Docked, SgsrEdge, FXAA, EDS3 | Manifesto verificado |

Clock e ocupação da GPU pelo KGSL: indisponíveis (leitura do sysfs bloqueada).
Bateria até 30,8 °C, estado térmico 0. Sem mensagens do driver, device lost ou
falhas de criação/tradução de pipeline. Um quadro de 116,6 ms em 12,1 s sem
compilação de shader. Memória livre mínima do sistema: 1.368 MiB.

## O que se pode concluir

- **Estabilidade observada** no perfil upstream A840 de três slices nesta carga.
- **Desempenho não testado:** o jogo limita a 30 FPS e as submissões ocupam só
  36,9% do tempo de parede.
- O split de draws indiretos A8xx não é exercitado: o jogo não gera draws
  indiretos grandes.
- **Imagem:** o usuário relata imagem totalmente pixelada. As capturas não
  registram pixels. A configuração global (`NearestNeighbor` ampliando para
  2448×1848) produz pixelização sem envolver o driver; o perfil do jogo usa
  SgsrEdge. Causa não isolada.

## Próximos testes

1. Screenshot da mesma cena com: perfil atual; scaling Bilinear; driver Qualcomm
   do aparelho. Separa escala do Eden, Turnip e o próprio jogo.
2. Labs de diagnóstico, uma mudança por build e destinados só ao teste físico
   na A840 (ver o escopo de código de cada um abaixo). Um resultado positivo
   indica o caminho a bisectar, não a causa raiz. Nenhum lab é release.
3. Jogos acima de 30 FPS (MK8D, BOTW, TOTK) com cena marcada, e DX12 via
   Winlator/GameHub para exercitar draws indiretos grandes.

## Labs de diagnóstico gerados em 25/10/2026

Base: candidata 5.7.14.1 (Mesa `69f1f21`), Standard. Uma mudança por build.
Os binários são destinados só ao teste físico na A840; isso é uma restrição de
distribuição, não do código. Patches em [`labs/`](labs/), fora do patchset
distribuído e do fingerprint; nunca entram em `config/patches.json`. Build única
por lab, com validação de artefato; status **aguardando hardware**.

Escopo de código (revisão do `chatgpt` em T-a840-pixelation, 25/10/2026):

- `noubwc` e `sysmem`: só ativam a flag quando o chip é `0x44050a31`/
  `0xffff44050a31`, mas escrevem em `tu_env`, estado **global** do processo
  (`tu_util.cc`/`tu_util.h` no Mesa 69f1f21). Num aparelho com uma GPU o efeito
  fica nela; num processo com vários dispositivos Vulkan a flag valeria para
  todos.
- `gen8state`: **sem trava por chip.** O 4/7 muda `store_3d_blit` em todas as
  famílias (inclusive A6xx), o 5/7 vale para `CHIP >= A7XX` e só o 6/7 é
  `CHIP >= A8XX`. Instalar apenas na A840.

| Lab | Mudança | ZIP SHA-256 | ELF SHA-256 |
|---|---|---|---|
| `5.7.14.1-a840lab-noubwc` | `TU_DEBUG=noubwc` | `63f545022ab515e234f4d686a9dc2cad0aff2394e5c28eae3256099bd290d710` | `0546fff7f19871a05381df60fd32914cfe92f0838f6b1264b80c2e2baa9e108d` |
| `5.7.14.1-a840lab-sysmem` | `TU_DEBUG=sysmem` | `7e2f65c7f43bd6bfe53cf4707b902103010bb3609709f75546aecd1b1be3eb56` | `ed661f2e84dab5414df1f36aa0410e9bd3d52d3dff32cb7cf1073e5039b624de` |
| `5.7.14.1-a840lab-gen8state` | MR !43940 4/7, 5/7, 6/7 (estado após blit 3D em gen8) | `20fd9db6fb4628603f8ab69b780504ac5ace553e19984e7761fe6c63655e436a` | `2cf55f99dcba098ecd6cf99ae45be57801a39d1610d6d90c2b9d07d51c0e4028` |

Testar os três labs sempre, na mesma cena e com o mesmo critério visual. Cada
flag muda mais de um caminho, então um resultado orienta a bisecção e não prova
a causa:

- `noubwc` corrige: implica o caminho UBWC; isolar formato, imagem e blit.
- `sysmem` corrige: implica o caminho GMEM. Com o `gen8state` também
  corrigindo, os suspeitos são 4/7, 5/7 **ou 6/7**: os dois primeiros só rodam em
  `store_3d_blit` (GMEM), e o 6/7 altera o blit r3d, usado tanto no GMEM quanto em
  sysmem. Separar com um binário por commit.
- Só o `gen8state` corrige: hipótese de 6/7 (`RB_SAMPLE_COUNTER_CNTL` nos blits
  r3d, também em sysmem), não prova; confirmar com binário só do 6/7.
- Nenhum corrige: comparar com o driver Qualcomm para separar Turnip de
  Eden/jogo.

Qualquer correção real exige binários separados por commit, mecanismo
identificado, checagem de A7xx e A/B antes de entrar numa candidata.
