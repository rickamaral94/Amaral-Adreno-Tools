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

O pacote universal não seleciona perfis por família. O próprio Mesa usa a
identificação real da GPU e sua device database. Novas GPUs só entram no escopo
quando reconhecidas pelo snapshot upstream e quando houver validação real.

## Princípios técnicos

- `-march=armv8-a`, sem `-mcpu` específico e sem ThinLTO na referência.
- backend KGSL, somente Turnip/Freedreno, sem Gallium/EGL/GLX no artefato.
- autotuner GMEM/SYSMEM upstream preservado.
- nenhuma variável `TU_DEBUG` embutida.
- sem spoof de nome, modelo, extensões ou versão Vulkan.
- ZIP simples para Adreno Tools: `libvulkan_freedreno.so` e `meta.json`.

