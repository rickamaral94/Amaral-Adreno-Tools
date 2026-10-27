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
  registram pixels. A captura curta usava `NearestNeighbor` global, mas a
  captura principal de 77 s já usava **SgsrEdge/FXAA** no perfil do jogo; assim,
  Nearest sozinho não explica o relato persistente. Causa não isolada.

## Observação visual adicional — 26/10/2026 (em revisão)

O Rick enviou duas capturas do MUA3 no mesmo aparelho: às 17:56:29, o conteúdo
do jogo aparece preto, com poucos pontos/linhas de ruído na faixa inferior
([imagem](images/a840-20261026/175629-black.jpg), SHA-256
`68f5cf22bcab7387d886a8c7b8f22a5583243885cd0d6dcc204c0c34f4f1df29`);
às 17:56:42, a maior parte da área do jogo mostra ruído denso em colunas
([imagem](images/a840-20261026/175642-noise.jpg), SHA-256
`9e7696a30aa2fb5e224f16578e8f914ed1b766daf83249cb2c1cb24f180bd870`).
Os controles virtuais do Eden permanecem legíveis nas duas; não há cena do jogo
reconhecível no ruído. Uma medição independente do perfil médio de luminância
na região central sem controles (colunas 350–849, linhas 200–499, screenshot
1280×966) encontra período principal de ~16,7 px na captura, equivalente a
~31,9 px no swapchain 2448×1848, com harmônico de ~8,3 px na captura. Isso
é compatível com uma grade no espaço de apresentação, mas não distingue
memória tiled/comprimida de shader em blocos. Essas imagens demonstram
corrupção visual observada, não apenas pixels grandes de NearestNeighbor.
Não há prova de que as duas imagens sejam o mesmo quadro ou de que o jogo já
tivesse terminado de carregar na primeira.

O ZIP de diagnóstico enviado junto (`20261026-205617-7853`, SHA-256
`097ddcc251def60a410814c0afee67d7d68fa06adf28fb2183849b319a697e52`)
passou `unzip -t`; manifesto `complete=true`. Não foi incluído no repositório,
pois contém logs brutos. Campos selecionados do `report.json`/`summary.txt`:

| Item | Valor observado |
|---|---|
| Driver selecionado | Candidate **5.7.15.1 OneUI**, Mesa `69f1f21f02`; não é o controle 5.7.14.1 Standard da etapa 0 |
| ELF realmente carregado | `0f83d311ecebffcf4946f2fa9d797199b8b8d97620f53b5624b62d3083749e4f`, igual ao ELF OneUI 5.7.15.1 entregue; build-id `04bc281f85128874434fd2de7f3e99b21a6ecba9` |
| Eden/jogo | `604cde0b1b964c7bb0092550ec62511545096bc2`, MUA3 `010060700AC50000`, update 4.0.1 (NAND) ativo |
| Configuração | Docked, Res1X, filtro **SgsrEdge**, FXAA, swapchain 2448×1848 RGBA8/FIFO; hash das configurações efetivas `7566b20a7d7707f372b9baa596d67d087730e7d183d471384a35ab39a2825915` |
| Captura | 645,39 s, 1 cena registrada sem marcador manual, ~29,9 FPS, GPU p50/p90/p99 12,8/15,5/21,3 ms, nenhuma falha de dispositivo/pipeline registrada, fim por ação do usuário |

O ZIP não contém imagens dos quadros, nem capturas pareadas com Bilinear,
5.7.14.1 Standard ou Qualcomm. A tela preta e as colunas de ruído podem vir do
jogo/decodificação, de um alvo intermediário do Eden, do filtro/presentação ou
do Turnip; os dados ainda não localizam a etapa defeituosa. Não atribuir raiz a
SnapAlloc, UBWC, GMEM ou aos três backports da 5.7.15.1 sem controle. A
comparação com o Qualcomm chegou depois e mudou a ordem do próximo teste,
descrita abaixo. Os controles pareados ainda não foram executados.

### Controle Qualcomm recebido depois (ainda não pareado)

Novo ZIP Eden `20261026-211757-8120` (SHA-256
`dc3169ef3b10a3a5ebe559b91a8c269f127ffe7c55826b9f3f704edee12b007c`):
arquivo íntegro, manifesto completo, mesmo Eden/MUA3/update/aparelho. O driver
**realmente carregado** é o Qualcomm do sistema
(`VK_DRIVER_ID_QUALCOMM_PROPRIETARY`), ELF SHA-256
`f7ea5e9121db1e6dc5ca6d09c6f763bff09dfff30e758e8c865f1cc238fec1f9`.
O swapchain continua RGBA8 2448×1848/FIFO com cinco imagens. O teste Qualcomm
usou **Bilinear e AA desligado** (`None`), mantendo Docked/Res1X/EDS3; hash das
configurações efetivas
`01faf4958aca79948c1c856672ef68aa1e95f14bbbcf17535d3a09177aa47f40`.
As duas fotos mostram a cena jogável legível:
[foto 1](images/a840-20261026/qualcomm-gameplay-1.jpg)
(SHA-256 `606cf73d8035871b16ab0221f0d5efc9f965d5f6b57ac0048caa8b54922643e3`)
e [foto 2](images/a840-20261026/qualcomm-gameplay-2.jpg)
(SHA-256 `3ebff4ea11de2350c15a3b0d140439f5141c14845e1dd83f20e5a6297078d422`).

O Rick identificou a [terceira foto](images/a840-20261026/turnip-compiling-noise.jpg)
(SHA-256 `9d9db4910c045a543d3635da88489d121ed50ab4738abd9d9a6112eccafb5c24`)
como teste com nosso driver: há colunas de ruído, mas o overlay indica
“Compilando 78 Shader(s)” e 0 FPS. As fotos não estão dentro dos ZIPs; a
atribuição desta foto a uma captura específica é relato do Rick. As duas
capturas Turnip anteriores, porém, já mostravam o mesmo ruído a ~30 FPS sem
compilação no overlay, e o ZIP Turnip de 645 s registrou zero criação/espera
de pipeline durante a captura: o defeito não se restringe à compilação.

**Naquela rodada ainda não havia A/B de configuração:** o Turnip anterior usou
SgsrEdge/FXAA e o Qualcomm usou Bilinear/AA None. O ZIP Qualcomm registra uma
falha de criação de pipeline compute (`VK_ERROR_UNKNOWN`) ~102 s após o início
e um `VK_ERROR_SURFACE_LOST_KHR` ~303 s após o início, próximo à recriação do
swapchain, mas termina por ação do usuário;
esses eventos isolados não demonstram causa da corrupção Turnip. FPS das duas
sessões não é comparável devido a cache/compilação diferentes.
O Turnip restaurou 33 pipelines do arquivo e a Qualcomm 3; diferenças nas
features `shaderResourceMinLod`/`shaderResourceResidency` são consequência dos
drivers e não podem ser igualadas por ajuste do usuário.

Próximo controle prioritário: no Turnip 5.7.15.1 OneUI, reproduzir **Bilinear
+ AA None** na mesma tela SAVE/menu estável alcançada no Qualcomm (relato do
`claude` em T-a840-pixelation ca82), após terminar o carregamento; se não
conseguir chegar a ela sem imagem, use o mesmo menu de título estável nos dois
drivers. Duas capturas separadas por ≥10 s e ZIP Eden próprio com
driver/configuração confirmados. Gameplay é bônus se ficar navegável.
Se persistir o ruído, a suspeita de caminho específico do Turnip aumenta. Se
limpar, reativar FXAA e depois SgsrEdge um por vez; não instalar labs ainda.

**Correção relatada pelo Rick:** ele informou que também viu ruído ao testar
nosso driver com **Bilinear e AA desligado**. Isso enfraquece a hipótese de que
SgsrEdge/FXAA sejam condições necessárias para o ruído. O arquivo que ele
reenviou como “segundo diagnóstico do nosso driver”, porém, tem SHA-256
`dc3169ef3b10a3a5ebe559b91a8c269f127ffe7c55826b9f3f704edee12b007c`,
byte a byte igual ao ZIP Qualcomm acima. Nele constam `selection=system`,
`VK_DRIVER_ID_QUALCOMM_PROPRIETARY` e ELF
`f7ea5e9121db1e6dc5ca6d09c6f763bff09dfff30e758e8c865f1cc238fec1f9`.
O ZIP correto do Turnip nessa configuração chegou depois, como registrado abaixo.
O arquivo `8120` continua sendo o controle Qualcomm; não foi reclassificado.

### Turnip Bilinear/AA None — controle de configuração recebido

O ZIP `20261026-215741-1874` (SHA-256
`8ca27e340a5c28e11ea89b7c424214985a7a9eff58e5a481478d3ccabef30655`)
passou `unzip -t` e tem manifesto completo. O driver selecionado é **custom**,
5.7.15.1 OneUI, com `VK_DRIVER_ID_MESA_TURNIP`; o ELF carregado tem SHA-256
`0f83d311ecebffcf4946f2fa9d797199b8b8d97620f53b5624b62d3083749e4f`.
A biblioteca Qualcomm do sistema também aparece mapeada, mas não é o ICD ativo.
O hash das configurações efetivas é
`01faf4958aca79948c1c856672ef68aa1e95f14bbbcf17535d3a09177aa47f40`,
**idêntico ao controle Qualcomm `8120`**: Bilinear, AA `None`, Docked, Res1X,
EDS3 e precisão GPU Low. Mesmo Eden, jogo/update e swapchain RGBA8
2448×1848/FIFO com cinco imagens. A sessão durou 123,3 s, sem device lost ou
erro de pipeline, e terminou por ação do usuário. O FPS da sessão inteira
inclui carregamento e não serve para avaliar a correção da imagem.

Três fotos enviadas pelo Rick mostram a mesma corrupção em colunas:
[30 FPS](images/a840-20261026/turnip-bilinear-noise-30fps.jpg)
(SHA-256 `089fa6c58ad47352f20d60394efcbab53b83348d61aa69f1b020064177c1fe2f`),
[0 FPS](images/a840-20261026/turnip-bilinear-noise-0fps.jpg)
(SHA-256 `a5b3c634582de1b7de7bbbadc1041e5e6d001858d7d0ba3cc426a79fd44a44a3`)
e [compilação](images/a840-20261026/turnip-compiling-noise.jpg). As fotos não
estão dentro do ZIP; a associação à sessão vem do envio do Rick e do overlay.
O ruído a 30 FPS mostra que não depende de uma pausa para compilar shaders.
SGSR e FXAA não são condições necessárias, pois ambos estavam desligados.

Esse par controla driver, configurações efetivas, jogo e swapchain; a imagem
Qualcomm está nítida e a Turnip está corrompida. As fotos Qualcomm registram
gameplay e as Turnip, menu, portanto não há comparação pixel a pixel do mesmo
quadro. O resultado favorece um defeito dependente do driver ou da interação
Eden–driver, mas **não identifica** SnapAlloc, UBWC, GMEM nem shader final.
A grade próxima de 32 px no swapchain é compatível com mais de um desses
mecanismos; seria preciso observar a imagem antes da apresentação ou testar
uma mudança isolada para atribuir causa.

## Próximos testes

1. Antes do lab SnapAlloc já construído sobre 5.7.14.1 Standard, confirmar
   nessa **mesma base** que o ruído se reproduz em Bilinear/AA None na mesma
   tela. Se reproduzir, comparar com o lab SnapAlloc, uma troca por vez, com
   fotos e ZIP Eden. Se a base estiver limpa, não interpretar o lab antigo
   como teste do defeito 5.7.15.1: reconstruir o lab nessa base mais recente.
   Um segundo jogo Eden com o mesmo swapchain ajuda a medir o alcance, mas um
   resultado normal nele não elimina uma interação específica do MUA3.
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
