# Candidata de teste 5.7.15.1 — registro de integração

Pedido do Rick em 26/10/2026 (rodada abacaxi). Desenho aprovado pelo `chatgpt`
em `collab/channel` (T-candidate-5.7.14.1, review e378); este diretório leva o
diff e os hashes para a revisão do artefato. Não é merge no PR #27 nem release.

## Integração

- Base: `candidate/5.7.14.1-upstream-review` @ `c1977d6`.
- Commit local de integração: `afa1aa0`, exportado em
  [`integration.patch`](integration.patch) (aplique com `git am` sobre `c1977d6`).
- Mudanças: `patches/upstream-29db4909d4e.patch`, `patches/upstream-64245a20b78.patch`
  e `patches/upstream-a1e9f888421.patch` (`git format-patch` dos commits
  upstream, sem edição), `config/patches.json`, versão 5.7.15.1 em
  `config/mesa-lock.json` e `config/version-state.json`, e notas da versão.
- Mesa: `69f1f21f0258a77046dbaeb8ed7a8ad37a683006` (inalterado).
- Patchset fingerprint: `6405a338a7f6255745534d8c446c6c249f2e936d5d0de677b4ef5a687309f924`.

## Artefatos

| Variante | ZIP SHA-256 | ELF SHA-256 |
|---|---|---|
| Standard | `ee81a3b4762c5173858e96ee163a94d9a4d8952fabc2ef36323b64e2f76ac817` | `5dc729c6a0ba605c3fd5d31b9cd80d5ca48107e5dfd1d5354c3f6cff0da874ec` |
| OneUI | `6eb5905ed2133295d623eccfc4bc0c7052481f95d7e609027b85427ea9777fc6` | `0f83d311ecebffcf4946f2fa9d797199b8b8d97620f53b5624b62d3083749e4f` |

## Gates

| Gate | Status |
|---|---|
| Patches aplicam sem fuzz sobre 69f1f21 + patchset | pass |
| Build Standard e OneUI (NDK r29) | pass |
| `validate_artifact.sh` nas duas variantes | pass |
| Catálogo de GPUs Standard igual ao da 5.7.14.1 | pass |
| `validate_project.py`, unittest, `git diff --check` | pass |
| Reprodutibilidade em dupla build, Standard | em execução |
| Reprodutibilidade em dupla build, OneUI | pendente |
| CTS `copy_image` MS f16, VVL | not-run |
| Hardware A6xx, A7xx (A740), A8xx (A840) | not-run |

Escopo: base de correções upstream A6xx/MSAA/KGSL. **Não resolve a imagem
pixelada da A840/MUA3 e não comprova ganho de FPS no A740.** A etapa 0 da A840
continua com a 5.7.14.1.
