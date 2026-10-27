# Candidata de teste 5.7.16.1 — registro de integração

O par físico do A840 (SM8850) no Eden/MUA3 favorece o tratamento de
layout/modifier dos handles SnapAlloc no fallback do u_gralloc
(T-a840-pixelation, finding e9bd; registro em
[docs/tests](../../tests/2026-10-sm8850-a840-marvel-ultimate-alliance-3.md)).
Com o mesmo hash de ajustes (`01faf495…`), a 5.7.14.1 tem ruído em colunas e o
lab 5.7.14.1 + MR !44464 dá imagem nítida. O Rick relata o lab sem erros na
sessão inteira, e o controle Qualcomm também é nítido. Não há observação direta
do modifier nem do ramo executado. Rival residual: interação de cena ou estado,
ou do patch completo do lab. Proposta: `collab/channel` d14b, com review do
`chatgpt` pendente. Não é merge no PR #27 nem release.

## Integração

- Base: integração da 5.7.15.1 (`112a1e9` sobre `c1977d6`).
- Commit local de integração: `3951b69`, exportado em
  [`integration.patch`](integration.patch) (`git am` sobre `112a1e9`).
- Mudança: `patches/upstream-mr44464-snapalloc-34ints.patch` (SHA-256
  `50b63df53873104ec3ed38e552dcc2892227603c3e0a6a0996f784da842b389b`), idêntico a
  [`docs/tests/labs/candidate-snapalloc-34ints.patch`](../../tests/labs/candidate-snapalloc-34ints.patch),
  na lista `standard` de `config/patches.json`. Versão 5.7.16.1, conforme o
  `release_version.py` (patchset novo, A+1). Notas da versão incluídas.
- Mesa: `69f1f21f0258a77046dbaeb8ed7a8ad37a683006` (inalterado).
- Patchset fingerprint: `e43c4b354f18e9390d1f221dce53b1462b8c53caf6cf830ada6837ad9a311f1c`.
- Diferença para o lab testado: o lab tinha o MR completo (layouts de 34 e 33
  ints); esta candidata tem só o de 34 ints. Pela descrição da MR, é o caminho
  esperado no A840, mas os ZIPs do lab não registram qual ramo rodou.
- O patch não tem gate de chip: o fallback roda em qualquer GPU com gralloc
  sem `gmsm`. Ele só aceita handles com a forma exata SnapAlloc e stride
  coerente, mas isso não prova, sozinho, que outras famílias ficam intactas.

## Artefatos

| Variante | ZIP SHA-256 | ELF SHA-256 |
|---|---|---|
| Standard | `3b27ca71d5719edf16ed746755cf2cf82f075e16c034be602124a1f03ea38792` | `af80c8847a613da7bc4daf413a0cf5d20e5a5b34535fc99331fe568faea64486` |
| OneUI | `9f01edf8f83580d20287e94247447fba1d7ff0eabcbf485b0811b4af068b93b7` | `28cea848c357623b646e614a29104ee8d692c2e96dbdcd4ad1e8a2f492af3da0` |

## Gates

| Gate | Status |
|---|---|
| Patches aplicam sobre 69f1f21 (Standard e OneUI) | pass |
| Build Standard e OneUI (NDK r29) | pass |
| `validate_artifact.sh` nas duas variantes | pass |
| Catálogo de GPUs Standard e OneUI igual ao da 5.7.15.1 | pass |
| `validate_project.py`, unittest | pass |
| `git diff --check` de config e docs da integração | pass |
| Reprodutibilidade em dupla build, Standard e OneUI | pass: 2 builds independentes por variante, ZIP idêntico |
| Hardware A840, perfil SGSR+FXAA (OneUI) | observado: captura `20261027-145905-6375`, gameplay nítido; travadas em parte na criação de shaders |
| Hardware A840, Bilinear/None (par com o lab) | not-run |
| Execução A740 (Odin 2 Portal), MUA3 SGSR+FXAA, Standard | observado: captura `20261027-184302-0705` (ZIP SHA-256 `cc7500ab4a8365674ae60b430a66d38ce42b6110b26f41c3591415743c18f0b1`, ELF `af80c884…` confirmado), 923 s a 29,8 FPS, GPU p50/p90/p99 19,8/20,5/30,0 ms: execução sustentada sem erro registrado; pixels não confirmados (sem fotos). Pausas de até 577 ms sem compilação, causa aberta. Não é a regressão pareada ([relatório](../../tests/2026-10-odin2-portal-marvel-ultimate-alliance-3.md)) |
| Regressão A740 pareada (mesmo Eden e ajustes, 5.7.15.1 `6755` × 5.7.16.1 `0705`) | observado: métricas equivalentes (29,73 × 29,75 FPS, pacing p99 34,25 ms nas duas, sem erro); faltam a foto da 5.7.16.1 e minimizar/retomar |
| A6xx, CTS, VVL | not-run |
