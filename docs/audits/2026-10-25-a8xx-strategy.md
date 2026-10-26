# A8xx: estratégia de suporte e revisão de fontes — 25/10/2026

O método recomendado é **Mesa fixado + diferenças pequenas por mecanismo +
validação por chip**, com revisão independente antes de incorporar cada diferença.
A melhor fonte depende do problema: upstream para correções gerais, comunidade
para hipóteses reproduzíveis e perfis ainda ausentes. Não existe evidência de que
uma stack comunitária inteira seja superior para toda a família.

Esta rodada foi pedida por Rick e coordenada com Claude em `T-a8xx-strategy`, no
branch `collab/channel`. ChatGPT auditou os projetos comunitários e implementou o
gate de perfis; Claude ficou com Mesa/MRs e propostas de correção em branch própria.
O acordo não autoriza release nem afirma que o problema visual A840 foi resolvido.

## Bases e evidência

- Projeto: `main` `a41737adfa99c40bfadfcf9a7cffcfe9871477e8`, Mesa
  `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`.
- Candidata #27: `c1977d6557630527ac56e686c29b949f2a793b1c`, Mesa
  `69f1f21f0258a77046dbaeb8ed7a8ad37a683006`.
- GitHub e os clones funcionaram. O GitLab oficial retornou CONNECT 403 nesta
  sessão de ChatGPT; as árvores completas dos dois SHAs foram obtidas pelo
  [espelho](https://github.com/chaotic-cx/mesa-mirror). Isso permite verificar
  conteúdo e aplicar patches, mas não confirma o HEAD oficial mais recente.
- Leitura de código, expansão do banco de GPUs e aplicação de patches são
  verificações locais. Relatos de jogos abaixo são dos autores, não reproduções
  nossas. CTS, VVL e aparelho nesta rodada: **not-run**.

## Fontes comparadas, fixadas por commit

| Fonte | Snapshot | O que foi conferido |
|---|---|---|
| [whitebelyash/mesa-unified](https://github.com/whitebelyash/mesa-unified/tree/9c7e022677dfa3abb356c2b6732cbd2e25783d01) | `9c7e022677df` | HEAD gen8 e stack preservada pelos empacotadores; ajustes A810/A812 e hacks de amplo alcance |
| [StevenMXZ](https://github.com/StevenMXZ/Adreno-Tools-Drivers/tree/b3b32ad30e7d7b4bd897e678af064036eeb9df09) | `b3b32ad30e7d` | `build_turnip.sh`: Patchs1 aplica WinNative 0001–0006; Patchs2 aplica gen8, shared memory global e A840v2 |
| [Banners](https://github.com/The412Banner/Banners-Turnip/tree/9ce33d486961d873b4a3931b298b35581e3b02de) | `9ce33d486961` | gen8, scripts, patches WinNative 0001–0005 e aplicação por variante; 0006 foi retirado |
| [WinNative](https://github.com/WinNative-Emu/Drivers/tree/c71f600a2977a141f21a922c9ed2e14fb09b13d3) | `c71f600a2977` | README Linux e código do cache IB 0006; limites do ensaio Rebirth/A840v2 |
| [Droid-Deck](https://github.com/Droid-Deck/Drivers/tree/de8bba431f1c8dd96b61c403262cf74f7756ef19) | `de8bba431f1c` | continuação Max/WinNative; retirada do cache, perfis, LRZ/resolve/hysteresis, gralloc e workaround cat4 A845/A850 |

Steven e Banners compartilham código whitebelyash/WinNative: não contam como
confirmações independentes do mecanismo. Builds Android/bionic e Linux/glibc não
são binários intercambiáveis. Um relato no Linux não qualifica Android/AdrenoTools.
Repositórios de binários sem fonte correspondente servem de controle físico,
não de origem para portar uma correção verificável.

## Decisões por mecanismo

| Item | Código e risco encontrados | Decisão e validação necessária |
|---|---|---|
| Bindless A8xx | WinNative 0004 usa registradores de invalidação A8xx; nossa base já contém `c88b6ebd3835` | Manter upstream, não duplicar; CTS descriptors e regressões |
| KGSL waits TS/FD e timeout zero | Correções da MR !44838 já estão nas bases; scripts comunitários às vezes ainda carregam patches antigos | Manter upstream; submit, waits mistos, timeout zero, teardown |
| Cube directions, WinNative 0003 | Quirk em `a8xx_base`; NIR troca NaNs por zero, limita infinitos, troca vetor zero por +Z e preserva camada de cube array | Candidato isolado a laboratório; apply-check passa em 69f1f21. Exigir teste NIR, cube/cube-array, gradientes/LOD, 16/32 bits e reprodução do hang antes de distribuição |
| IB virtual alias, 0005 | A8xx + sparse + `TU_BO_ALLOC_NO_32B_ROLLOVER`; novo VBO, bind, IOVA, unbind e free. Erros de teardown e kernels diferentes exigem atenção | Laboratório separado; apply-check passa. Stress de alocação, OOM, device lost, destruição, relaunch e longa sessão KGSL; não misturar com correção visual GMEM |
| IB cache, 0006 | Reuso com mutex, flags/tamanho/alinhamento; limite de 256 MiB de armazenamento **ocioso**, sem limitar BOs vivos; ao encher volta ao free original | **Não portar agora**: evidência contraditória e retirada posterior por regressão A840 |
| Mesh emulado, 0001 | Compute escreve em ring e VS consome; render passes com mesh usam sysmem; gate permite A7xx+, não só A8xx | Pesquisa separada; CTS mesh, task, indirect/count, sincronização, OOM e invariantes de ring. Não expor extensão para dizer que há mais suporte |
| Half-wave/subgroup32, 0002 | `minSubgroupSize` depende de `has_getfiberid`; também atinge A7xx e partes A6xx. Altera lowering de vários intrinsics e propriedades | Pesquisa separada, CTS subgroups e required subgroup size, estágios, votação/shuffle/ballot; não é ajuste exclusivo A8xx |
| Gen8 em bloco | Em Banners `a8xx_gen8.patch`: `chip_id == 0xffff44050000 || 0x44050001` é sempre verdadeiro; há `nocb` global e leitura de handle fora da guarda `gmsm` | **Rejeitar importação em bloco**; recuperar só mudanças isoladas após revisão |
| Shared memory global | `a8xx_shared_mem.py` substitui todo `32 * 1024` por `64 * 1024` no campo, incluindo outras famílias | **Rejeitar**. Capacidade exposta precisa corresponder ao chip; o novo gate detecta essa contaminação |
| Perfis Droid-Deck | A810/A829 ganham `disable_gmem`; A825 usa tile width 96 e 32 KiB shared, diferentes de Amaral (64/64 KiB); A845/A850 são aliases da A840 de 3 slices | Não escolher valores por popularidade nem copiar registradores por analogia; requer identificação de chip/topologia, fonte e testes GMEM/SYSMEM por aparelho |
| Cat4 repeat A845/A850 | `de8bba431f1c` desliga repetição SFU para IDs `0x44041430` e `0x44051431`, citando dessaturação DXVK/Unity | Pista L0, não correção A840. Confirmar fonte/topologia dos novos chips e reprodução; sem adicionar aliases automaticamente |
| LRZ color mask/flush, resolve CR e hysteresis | Droid-Deck escreve mask por MRT, zera LRZ após flush, acrescenta resolve CR=1 e SP hysteresis constants; escopo A8xx amplo | Avaliar contra MRs upstream, caminho e captura antes de portar. Escrita de registro aparentemente plausível não é evidência de raiz |
| Gralloc UBWC | Droid-Deck mantém `numInts >= 2` mas remove identificação `gmsm`; stack gen8 antiga remove também a guarda da leitura. Na build Android NDK atual, IMapper4/5 não é compilado e o backend qcom requer gralloc1 legado, ausente no Android 17: o fallback é o caminho ativo. A MR Mesa !44464 reconhece o handle SnapAlloc por formato e stride, incluindo um ramo heurístico para SM7435/A710 | Não remover a guarda `gmsm` sem identificar o handle. Testar o lab isolado da !44464 na A840; antes de distribuir, revisar o ramo A710 e testar AHB/format/modifier e compositor. A !44888 (draft) trata outro sintoma, falha de opcode CP em A840/KGSL, sem causa ainda demonstrada |

A retirada do cache IB é rastreável no autor: [Droid-Deck 27bf2ac](https://github.com/Droid-Deck/Drivers/commit/27bf2ac1b386ac3399a7a5604ead18f067f652c3),
seguida por [Banners 1c8d3bf](https://github.com/The412Banner/Banners-Turnip/commit/1c8d3bf183b9a863e844a7d666d0c1304be0fd4d).
O relato WinNative de reversão retention-off é útil, mas não supera por si só essa
regressão posterior. Não identificamos a causa exata do defeito kernel/firmware.

## Matriz preservada no projeto

Valores são o contrato de regressão do código atual, **não especificação do
silício nem certificação**. GMEM real vem do kernel; não inventar por nome comercial.

| Modelo / chip KGSL | Origem do perfil | CCU / slices | Tile alinhamento; largura máxima | Shared |
|---|---|---|---|---|
| A810 `44010000` | upstream com alias externo redundante | 1 / 1 | 32×16; 16384 | 32 KiB |
| A812 `44010200` | alias experimental da A810 | 1 / 1 | 32×16; 16384 | 32 KiB |
| A825 `44030000` | externo, propriedades locais | 4 / 2 | 64×32; 16416 | 64 KiB |
| A829 `44030a20` | upstream | 4 / 2 | 64×32; 16384 | 32 KiB |
| A830 `44050000` / `44050001` | upstream, revisão preservada | 6 / 3 | 96×32; 16416 | 32 KiB |
| A840 `44050a21` | upstream 2 slices | 4 / 2 | 64×32; 16384 | 32 KiB |
| A840 `44050a31` | upstream 3 slices | 6 / 3 | 96×32; 16416 | 32 KiB |

O prefixo `ffff` nos IDs upstream é wildcard do fuse, conforme
`freedreno_dev_info.c:dev_id_compare`; ausência de uma duplicata KGSL literal
não prova falta de suporte. Não confundir `44030a20` com `44030000` nem as duas
A840. A845/A850 permanecem fora do contrato revisado do projeto.

## Melhoria aplicada nesta branch

`tools/check_a8xx_profiles.py` executa os geradores Python de registradores e de
perfis do Mesa em processos separados, com dependências pinadas. Compara os
objetos completos expandidos com a árvore pristine do mesmo `HEAD` (via archive):

- nenhum perfil upstream pode desaparecer ou mudar sem revisão;
- Standard preserva os perfis, OneUI só permite UBWC hint nos dois IDs FD740;
- acréscimos externos ficam na lista conhecida, A812 deve continuar alias A810;
- A825 inteiro deve ser A830/gen1 com os overrides revisados, não só conter
  strings de campos corretos em algum lugar;
- verifica oito IDs/chip revisions, topologias independentes, aliases ambíguos e
  rejeita IDs desconhecidos, incluindo os vizinhos das duas A840.

A CI executa o gate após Standard e após OneUI. Não alteramos a receita de build,
o fingerprint, os binários nem o patchset da candidata para adicionar esse teste.
Mudanças legítimas de perfil devem vir com atualização explícita do contrato e
review. O gate não testa a lógica C de lookup em execução, features Vulkan,
linkage, firmware, hardware nem desempenho. A correspondência de IDs implementa
o ramo chip-id revisado dos dois locks; qualquer alteração upstream desse ramo
exige reavaliar o gate.
O gate usa `tarfile.extractall(filter="data")`; a execução local requer Python
3.12+ (ou 3.11.4+ com o backport do filtro). O job `ubuntu-24.04` usa Python 3.12.

Reprodução (na árvore Mesa com os patches do manifesto aplicados):

```sh
python3 -m venv work/profile-venv
work/profile-venv/bin/pip install Mako==1.3.10 MarkupSafe==3.0.3 PyYAML==6.0.3
work/profile-venv/bin/python tools/check_a8xx_profiles.py /caminho/mesa --variant standard --report /tmp/a8xx.json
python3 -m unittest discover -s tests -v
```

Verificado localmente: main/4b0f64c e candidata/69f1f21, ambas Standard e OneUI;
12 testes negativos/positivos novos; suíte total de 40 testes; metadados,
YAML e `git diff --check`. Patches comunitários 0003/0005: apenas apply-check,
sem inclusão. Nenhuma medição de ganho ou build de driver novo nesta parte.

## Como escolher a próxima correção

1. Classificar reprodução: GPU hang/device lost, erro de imagem, compilação,
   abertura do jogo ou apresentação. Fixar chip ID, kernel, hash ELF, frontend e cena.
2. Procurar equivalente no Mesa fixado e upstream; não reaplicar fix integrado.
3. Revisar diff mínimo com o outro agente: mecanismo, todas as famílias afetadas,
   contratos Vulkan, dependências, falhas de alocação e alcance por chip.
4. Executar apply-check sem fuzz, geração de catálogo, testes direcionados e build
   reproduzível. Preservar controle; uma hipótese por lab.
5. CTS/VVL e hardware: A840 de 2 e 3 slices separadas, A825/A810 se disponíveis,
   regressões A6/A7 quando código compartilhado mudar. Só depois decidir distribuição.
6. Para A840/MUA3, aproveitar a rodada visual já preparada: mesma cena e escala,
   Standard, Bilinear, noubwc, sysmem, gen8state, snapalloc e controle Qualcomm
   identificado. Um resultado visual do lab é hipótese de mecanismo, não validação
   para incluir a MR no patchset distribuído.
   Dois labs corrigirem a imagem não identificam qual commit é a causa.

Novos pedidos físicos precisam de binários/hashes e critérios antes da captura;
a presente auditoria não cria pedido incompleto nem duplica o já aberto.
