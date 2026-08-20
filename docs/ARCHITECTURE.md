# Arquitetura

O repositório separa quatro camadas para evitar que um resultado isolado se
transforme em comportamento global:

1. **Upstream fixado:** `config/mesa-lock.json` identifica exatamente o Mesa.
2. **Build:** cross-file genérico AArch64/KGSL e correções estritamente necessárias
   para compilar no NDK escolhido.
3. **Candidatos:** patches de compatibilidade/desempenho vivem isolados e possuem
   estado e evidência em `evidence/candidates.json`.
4. **Validação:** ELF, reprodutibilidade, qualidade visual, estabilidade e A/B no
   Amaral Driver Lab.

O pacote universal não seleciona perfis globais por família. O próprio Mesa usa
a identificação real da GPU e sua device database. A única exceção atual é a
Adreno 825 experimental: sua configuração e seus workarounds são condicionados
ao `chip_id` KGSL `0x44030000`, sem alterar outras GPUs.

O pipeline gera duas variantes a partir da mesma base:

- `standard`: Mesa fixado + compatibilidade NDK + perfil A825 isolado;
- `oneui`: todo o conteúdo de `standard` + `TP_UBWC_FLAG_HINT` somente nas
  entradas KGSL da FD740 (`0x43050a01` e `0xffff43050a01`).

As extensões de profundidade avaliadas no Driver Lab também seguem o degrau L0:
são anunciadas apenas nessas duas entradas KGSL da FD740. A presença de código
genérico no pipeline não amplia o escopo, porque outros dispositivos não podem
habilitar as extensões.

Cada variante usa diretórios de fonte, build e pacote separados para impedir
que o patch OneUI permaneça na compilação padrão.

## Princípios técnicos

- `-march=armv8-a`, sem `-mcpu` específico e sem ThinLTO na referência.
- backend KGSL, somente Turnip/Freedreno, sem Gallium/EGL/GLX no artefato.
- autotuner GMEM/SYSMEM upstream preservado.
- nenhuma variável `TU_DEBUG` embutida.
- sem spoof de nome, modelo, extensões ou versão Vulkan.
- ZIP simples para Adreno Tools: `libvulkan_freedreno.so` e `meta.json`.
- nenhum perfil IR3 global, aumento global de shared memory ou conjunto de hacks
  A8xx do fork comunitário é aplicado; os 64 KiB de shared memory da v4.1 ficam
  exclusivamente na entrada A825 `0x44030000`.
