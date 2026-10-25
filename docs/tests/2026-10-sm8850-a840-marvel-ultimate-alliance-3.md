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
2. Labs de diagnóstico L0 (chip `0x44050a31`), uma mudança por build:
   `noubwc` (sem compressão UBWC) e `sysmem` (sem GMEM). Se um deles corrigir a
   imagem, o mecanismo fica isolado para investigar uma correção real. Nenhum
   lab é release.
3. Jogos acima de 30 FPS (MK8D, BOTW, TOTK) com cena marcada, e DX12 via
   Winlator/GameHub para exercitar draws indiretos grandes.
