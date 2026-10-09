# Vulkan Roadmap 2026 — matriz Amaral Adreno Tools

Data da auditoria: 2026-10-09  
Mesa fixado: `a51a418991f883413f10f66cd52398d590a8257b`  
Contexto de build: Android / KGSL / AArch64

Esta matriz acompanha a evolução da API Vulkan antes de ela aparecer como
mudança prática no Turnip. O objetivo é distinguir especificação, toolchain,
infraestrutura genérica do Mesa, implementação Turnip/IR3 e suporte real do
hardware.

## Fontes de primeira linha

Além do Mesa/Freedreno/Turnip, o projeto acompanha:

- KhronosGroup/Vulkan-Docs — especificação e propostas;
- KhronosGroup/Vulkan-Profiles — `VP_KHR_roadmap_2026`;
- KhronosGroup/Vulkan-Headers — registry e headers;
- KhronosGroup/VK-GL-CTS — conformidade;
- KhronosGroup/Vulkan-ValidationLayers — VUIDs e validação;
- KhronosGroup/SPIRV-Tools e SPIRV-Headers — SPIR-V;
- KhronosGroup/glslang — frontend GLSL/SPIR-V.

A presença de uma extensão nesses projetos **não autoriza** expô-la no driver.
O Amaral continua proibindo spoof de capability.

## Estado estratégico no Turnip fixado

| Feature | Estado no Turnip | Android Amaral | Próxima ação |
|---|---|---|---|
| `VK_KHR_fragment_shading_rate` | implementada e gateada por propriedades da GPU | disponível quando o device profile declara suporte | CTS + device query em A740/A750/A830 |
| `VK_KHR_present_id2` | código existe sob `TU_USE_WSI_PLATFORM` | não tratar como exposta no caminho Android atual | estudar integração Android/WSI |
| `VK_KHR_present_wait2` | código existe sob `TU_USE_WSI_PLATFORM` | não tratar como exposta no caminho Android atual | estudar integração Android/WSI |
| `VK_KHR_present_mode_fifo_latest_ready` | WSI genérico conhece o modo; Turnip não anuncia a extensão | ausente | validar suporte de surface/present Android; não habilitar por flag |
| `VK_KHR_pipeline_binary` | ausente | ausente | desenhar implementação Turnip; estudar ANV/RADV/NVK |
| `VK_KHR_shader_untyped_pointers` | ausente | ausente | auditar NIR/IR3 e CTS |
| `VK_KHR_cooperative_matrix` | ausente | ausente | pesquisa de hardware + lowering IR3, inicialmente A8xx |
| `VK_KHR_copy_memory_indirect` | ausente | ausente | pesquisa |
| `VK_KHR_shader_maximal_reconvergence` | ausente | ausente | auditar controle de fluxo NIR/IR3 |

### O que já está melhor do que parecia

O Turnip atual já implementa uma parte relevante do Roadmap 2026: compute shader
derivatives, dynamic rendering/local read, fragment shading rate, robustness2,
shader clock, maintenance 7/8/9, shader subgroup rotate, quad control quando
suportado pelo hardware, vertex attribute divisor e outras capacidades. Não há
motivo para criar patches Amaral duplicando essas features.

Para A740, `a7xx_base` declara attachment shading rate e `a7xx_gen2` declara
primitive shading rate. O driver expõe as features por propriedade real, não por
nome da GPU. A validação funcional continua necessária; o próprio Turnip mantém
`layeredShadingRateAttachments=false` por falhas CTS conhecidas em A7xx.

## Oportunidades avaliadas

### 1. Pipeline binary — maior oportunidade para emulação, mas não é patch curto

`VK_KHR_pipeline_binary` permite capturar e reutilizar binários de pipelines,
reduzindo recompilação e potencial micro-stutter. Isso é atraente para
Eden/Citron/Cemu e principalmente DXVK/VKD3D.

O Turnip já tem peças úteis como `VK_EXT_shader_module_identifier`,
`VK_EXT_graphics_pipeline_library`, pipeline cache UUID e cache de shaders,
mas não implementa a API KHR. No mesmo Mesa, ANV, RADV e NVK já possuem suporte,
então servem como referência arquitetural. Ainda assim, copiar o flag de
extensão seria incorreto: faltam criação/destruição de objetos binários, chaves,
serialização/restauração e integração com os pipelines Turnip.

**Decisão:** pesquisa de implementação, não expor agora.

### 2. FIFO latest ready — menor superfície de código, mas Android é o bloqueio

O WSI genérico do Mesa já reconhece
`VK_PRESENT_MODE_FIFO_LATEST_READY_KHR`, porém o Turnip não anuncia
`VK_KHR_present_mode_fifo_latest_ready`.

No build Amaral, `-Dplatforms=android` não ativa o caminho
`TU_USE_WSI_PLATFORM` usado para X11/Wayland/KMS. Logo a existência do código
WSI genérico não prova que o modo possa ser exposto corretamente via Android.

**Decisão:** candidato de pesquisa de baixa/média complexidade; primeiro validar
o caminho Android e CTS de surface/present. Não criar extension flag ainda.

### 3. QCOM image_processing3 — melhor alvo Qualcomm específico

O Turnip já implementa `VK_QCOM_image_processing` quando o perfil da GPU
declara `has_image_processing`; A740/A750 possuem essa capacidade na base
auditada. A nova versão 3, porém, adiciona novos gathers SPIR-V, features e
format flags. A proposta Khronos menciona instruções dedicadas nas GPUs Adreno
mais recentes, mas isso não prova que A740 suporte os novos modos.

glslang e SPIRV-Tools já conhecem a nova linguagem/capability, enquanto o Turnip
ainda não implementa a extensão. Há, porém, uma pista concreta no backend:
`ir3-cat5.xml` já define quatro opcodes `samgp0`…`samgp3`. Isso torna plausível
que exista um caminho nativo para os quatro modos de gather da extensão, mas o
mapeamento não está documentado/provado e esses opcodes são antigos — portanto
não devem ser associados aos novos modos apenas pelo nome.

No SHA auditado, `spirv_to_nir.c` ainda reconhece somente as capabilities/ops de
`VK_QCOM_image_processing` original (`SampleWeighted`, `BoxFilter`, `BlockMatch`)
e não trata `OpImageGatherQCOM`. Assim, mesmo que o hardware esteja pronto,
faltam pelo menos VTN/SPIR-V, representação NIR e lowering IR3 verificável.

**Decisão:** prioridade alta de pesquisa. Primeiro provar em shader/disassembly
o mapeamento GatherH2/V2/D/4x1 → SAMGP0..3; depois implementar VTN/NIR/IR3 e só
então expor a extensão atrás de gate de geração e CTS. A8xx é o primeiro alvo
natural se a evidência confirmar que os modos são de hardware recente.

### 4. QCOM tile shading

É conceitualmente muito alinhada ao GMEM/TBDR do Adreno e pode ser estratégica
para performance/potência. A extensão, contudo, envolve render pass, tile
memory, comandos per-tile e SPIR-V. Não é uma otimização simples.

**Decisão:** roadmap de longo prazo; não implementar como hack Amaral.

### 5. QCOM multiple wait queues

É um hint de compilador para esconder latência usando múltiplas filas de espera
no shader. Precisa refletir capacidade real do hardware e do scheduler IR3.

**Decisão:** pesquisa A8xx-first; não expor sem propriedade real
`maxShaderWaitQueues`.

## Gates para uma nova extensão

Antes de uma nova extensão sair como candidata Amaral:

1. implementação real no Turnip/runtime/NIR/IR3, sem spoof;
2. gate pelo mecanismo de hardware real, não por nome comercial;
3. subset CTS específico passando;
4. Validation Layers sem erro novo;
5. A/B funcional em pelo menos um workload que consuma a feature;
6. zero corrupção, device lost ou regressão de P95/P99;
7. expansão para outras famílias somente após evidência.

A matriz estruturada usada pela CI fica em
`evidence/vulkan-roadmap-2026.json`. O script
`tools/check_vulkan_roadmap.py` verifica o estado estrutural contra o Mesa
fixado e sinaliza quando uma feature monitorada aparece no Turnip upstream.
