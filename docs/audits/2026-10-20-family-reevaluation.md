# Reavaliação por família — 20/10/2026

## Pergunta

Antes de publicar: o que a próxima candidata entrega de concreto para A8xx,
A7xx e A6xx? A 5.7.8.1 só trazia "Mesa mais novo + retirada de patches não
qualificados". As correções upstream incluídas são reais, mas nenhuma é
específica de família.

## Decisão

**3 — CRIAR CANDIDATA** 5.7.9.1, sem publicação a partir deste trabalho e sem
elegibilidade para Latest. Mesmo Mesa da 5.7.8.1; o delta é de quatro patches
upstream pendentes.

## Verificações desta sessão

- Clone direto de `gitlab.freedesktop.org/mesa/mesa`: `main` = `4b0f64c`
  (fecha a lacuna da auditoria anterior, que usou um espelho).
- Pilha Standard (0001, 0002, 0007-0012) e OneUI (+0003) aplicada limpa sobre
  `4b0f64c`, com `git diff --check` limpo.
- Build Android/KGSL local com NDK r29 (SHA-1 oficial conferido), duas árvores
  independentes por variante; ZIP e ELF idênticos byte a byte, catálogo de GPU
  idêntico, DT_NEEDED somente bibliotecas Android, patchset `c55cd42d…094bd`:

  | Variante | ZIP SHA-256 | ELF SHA-256 |
  |---|---|---|
  | Standard | `4ab5a953e83da4074405fc7c8ed05f47eadc6d2551a75a5a97c42fc8b0197c29` | `5f4d52d5bc082e5281da046ad330c398e47121c3503436286684aed647c03068` |
  | OneUI | `26e6bc57cae1c54b6dabc2ee7251abc5a8f353ced4e38d2744056aeada15c676` | `b4f39e222e3efc33648401868a020dd3ca9e5b07f98d2dd4636795bb9c48ebbd` |

  Catálogos Standard/OneUI diferem somente nas entradas FD740 (patch 0003).
  O único warning de compilação é preexistente (`tu_cmd_buffer.cc:2225`).
  A CI do GitHub repete esses gates; hashes de outro ambiente podem diferir.
- Novas guardas em `tools/validate_project.py` impedem que 0009-0012 toquem
  `tu_device.cc`, `freedreno_devices.py` ou driconf, e verificam o gate de
  família de cada patch.

## Triagem das MRs Turnip abertas (72)

### Incluídas

| MR | Família | Por que entra |
|---|---|---|
| !44352 (1-2/7) | A8xx | Fault real (autor da Qualcomm). robclark propôs integrar a divisão já e tratar draw_id depois. Para `CHIP < A8XX` o limite é `UINT32_MAX`: caminho idêntico. |
| !45204 | A7xx | r-b Danylo. Bug de sinal introduzido por dc1bb7bbf45, presente na Latest e na 5.7.8.1. Afeta títulos D3D12 com a emulação ativa por driconf. |
| !41860 | A6xx | Ack Connor Abbott. Bug de hardware reproduzido em A630/A650/A660; código emitido só em A6XX. |
| !45369 | Todas | r-b Danylo. Lifetime confirmado no código: `tu_cs_init_suballoc` toma ref, `tu_cs_finish` libera. |

Os pipelines de merge de !45204 e !45369 falharam somente por
`runner_system_failure` (debian-android, arm32/arm64) e traces restritos a660.

### Rejeitadas ou adiadas

| MR | Motivo |
|---|---|
| !43714 sysmem resolve flush | Seria o único ganho de recurso candidato, mas o pipeline falhou em 16 jobs Vulkan a618/a660/a750 (`script_failure`). Rejeitada. |
| !44352 3-7/7 | `draw_id_offset` via NIR/UBO muda VS params de indirect draws em todas as famílias; design ainda em discussão. Aguardar merge. |
| !43899 CCU depth clear | Investigação concluiu que era bug de sincronização do CTS. |
| !42153 early preamble | Autor substituiu por !42159, já integrada ao Mesa fixado. |
| !44325 SSBO emulation UE5 | Depende de infraestrutura driconf nova e de mudança vkd3d-proton não integrada; dano colateral em UE4 admitido. Monitorar. |
| !45243 inline uniform blocks | Ainda em revisão; casos CTS de bindings reservados. Aguardar. |
| !45366 float16 MS copy | Sem revisão; NaN em cópia MSAA fp16. Aguardar. |
| !42894 sampler double-free | Troca um `assert`, que é no-op com `-Db_ndebug=true`. Sem efeito no pacote. |
| !45342 sdot 4x8 | Só altera propriedade consultada por cargas de ML (llama.cpp), não por jogos. Fora do escopo. |
| !45384 A850/A845 | Novas GPUs sem hardware de validação. Não adicionar IDs. |
| !44214, !45033 | Caminhos FDM; sem workload Android do projeto. |

## Resposta direta por família

- **A8xx:** sim, há um ajuste novo, mas é de **estabilidade** (fault em indirect
  draws), não de tuning. A825/A812 continuam isolados e experimentais.
- **A7xx:** compatibilidade em D3D12 com texel buffer emulation e liberação de
  recurso (BO retido). Não há "uso inteligente de recurso" com evidência além
  disso; Aurora (0005) segue sem ganho conclusivo e !43714 quebrou a CI upstream.
- **A6xx:** correção de compatibilidade (XFB). **Não existe hoje melhoria de
  desempenho A6xx com evidência**; não foi inventada uma.

## Pendências para o mantenedor

1. O workflow `Publish verified candidate` (run 39360005734) publicou a
   pre-release 5.7.8.1 a partir de `main` às 02:44 UTC de 20/10, durante esta
   sessão. A Latest segue 4.7.7.2. A 5.7.9.1 supersede a 5.7.8.1 como linha de
   qualificação e a usa como referência intermediária no A/B.
2. Profundidade (0004): a Latest 4.7.7.2 expõe `VK_EXT_depth_bias_control` e
   `VK_EXT_depth_range_unrestricted`; as candidatas 5.7.x não. DXVK e Eden usam
   depth_bias_control quando disponível. Manter fora até CTS
   (`dEQP-VK.draw.*depth_bias*`, `dEQP-VK.pipeline.*depth_range_unrestricted*`)
   é a escolha conservadora, mas comparar sombras/z-fighting com a Latest.
3. Hardware: nenhuma das quatro correções foi executada em aparelho.
