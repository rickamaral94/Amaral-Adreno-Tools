# Arquitetura

O repositório separa upstream, build, candidatos e validação para impedir que
um resultado isolado vire comportamento global.

1. `config/mesa-lock.json` fixa exatamente o Mesa.
2. O build usa AArch64/KGSL e apenas compatibilidade necessária ao NDK.
3. Cada mudança não upstream é um patch reversível com estado em `evidence/`.
4. O Driver Lab decide promoção por imagem, estabilidade, frametime e só então
   desempenho.

## Modelo universal

O Mesa identifica a GPU e consulta a device database. O Amaral não escolhe um
perfil global “A6/A7/A8”; ele usa o menor gate que representa a dependência
real:

- chip: configuração A825 e UBWC OneUI da FD740;
- capacidade: GCM quando `reg_size_vec4 >= 96`;
- geração: depth range irrestrito em A7xx+;
- aplicativo: perfis BOTW/TOTK;
- sem gate: mudanças realmente independentes do hardware.

Assim, uma ideia criada para A740 também chega a A6xx ou A8xx quando o caminho
de código e a capacidade são equivalentes. Afinar UBWC, GMEM, caches ou FDM por
analogia de nome de família não é permitido.

## Variantes

- `standard`: Mesa fixado + NDK r29 + A825 + extensões + candidatos portáveis;
- `oneui`: conteúdo Standard + `TP_UBWC_FLAG_HINT` somente nas entradas KGSL
  FD740 `0x43050a01` e `0xffff43050a01`.

Cada variante usa árvores e diretórios de build próprios, impedindo vazamento
do patch OneUI para o pacote Standard.

## Gates atuais

| Recurso | Gate | Motivo |
|---|---|---|
| `VK_EXT_depth_bias_control` | todos | runtime comum; emissão sem ramo por chip |
| `VK_EXT_depth_range_unrestricted` | `chip >= 7` | A6xx clampa no hardware |
| GCM | `reg_size_vec4 >= 96` | limita pressão e spill de registradores |
| suballocadores 512 KiB | todos | alocação preguiçosa, sem dependência de chip |
| BOTW/TOTK | nome do aplicativo | problema/tuning é do workload |
| A825 | `0x44030000` | propriedades de silício ainda fora do upstream |
| OneUI UBWC | FD740/KGSL | valor deve coincidir com drivers do sistema |

## Princípios técnicos

- `-march=armv8-a`, sem `-mcpu` exclusivo de Snapdragon 8 Gen 2.
- backend KGSL/Turnip, sem Gallium/EGL/GLX no artefato.
- autotuner GMEM/SYSMEM upstream preservado fora dos perfis por título.
- nenhuma variável `TU_DEBUG` embutida.
- sem spoof de GPU ou versão Vulkan.
- hacks A8xx globais de FDM/MSAA, NOCB, UBWC e shared memory não entram.
- ZIP Adreno Tools contém `libvulkan_freedreno.so` e `meta.json`.

## Estrutura do repositório

| Caminho | Responsabilidade |
|---|---|
| `config/` | lock reproduzível do Mesa e estado do versionamento |
| `patches/` | alterações aplicadas ao Mesa, em ordem explícita |
| `evidence/` | origem, estado e compatibilidade de cada candidato |
| `scripts/` | build, reprodução e validação dos artefatos |
| `tools/` | decisão de versão e validação estrutural do projeto |
| `tests/` | testes unitários da automação de release |
| `docs/releases/` | notas históricas; não controlam builds atuais |
| `docs/reference/` | material histórico que não é carregado pelo driver |

## Workflows ativos

- `ci.yml`: valida metadados, testes, scripts e aplicação dos patches.
- `build-candidate.yml`: build manual e reproduzível de uma revisão informada.
- `publish-upstream.yml`: atualiza Mesa sobre o patch set aprovado e publica
  Standard/OneUI como `Latest`.
- `publish-candidate.yml`: cria uma pre-release quando muda o patch set Amaral.
- `promote-candidate.yml`: promove exatamente os binários aprovados no A/B.
- `retire-release.yml`: retira uma release sem apagar seu histórico.

Publicadores específicos de versões antigas foram removidos do ramo principal.
As tags e releases históricas continuam sendo a fonte imutável dessas versões.
