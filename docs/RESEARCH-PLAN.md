# Pesquisa e conhecimento externo

Fonte principal: Mesa/Freedreno/Turnip/IR3/NIR; spec/CTS/VVL Khronos como contratos.
A auditoria de 20/10/2026 registra fixes upstream reais e rejeições comunitárias.
Nenhuma quantidade de commits ou propaganda de FPS substitui teste.

P0: estabilidade da candidata, qualificação de capacidades e relatos A825/A830.
P1: pipeline_binary em branch separada: API Create/Destroy/GetKey/GetData/
ReleaseCapturedData; chaves por build/dispositivo, capture/import/export, lifetime,
OOM/dados inválidos, compute/graphics/GPL e CTS round-trip. Reutilizar runtime e
serialização Turnip, com reupload correto; não persistir endereços GPU. API desligada
até completa. Benefício depende da adoção pelos aplicativos.
P1: manter KGSL upstream e avaliar A8xx por mecanismo/ID; reduzir stack externa.
P1: acompanhar MR !44352 3-7/7 (draw_id_offset); quando integrada, trocar 0009
pelo upstream e remover a limitação de gl_DrawID nos draws divididos em A8xx.
P2: MR !44325 (SSBO emulation para UE5 em A7xx) depois do lado vkd3d-proton;
MR !43714 (flush de resolve sysmem) só se o upstream corrigir a CI.
P2: image_processing3: provar GatherH2/V2/D/4x1 versus SAMGP por disassembly e hardware;
implementar VTN/NIR/IR3 e format flags apenas com evidência. Toolchain não prova GPU.
P2: present_id2/present_wait2/fifo_latest_ready: validar Android/WSI de ponta a ponta.
P3: tile shading, cooperative matrix e multiple wait queues; capacidade real primeiro.

Fontes monitoradas: Khronos Vulkan-Docs/Profiles/Headers, VK-GL-CTS, VVL,
SPIRV-Tools/Headers, glslang; whitebelyash, StevenMXZ, K11MCH1, MrPurple,
Balemuni, Banners e WinNative. Diferenciar pacotes proprietários de código Turnip.

Decisões comunitárias atuais:
- whitebelyash gen8: rejeitar condição `chip_id == X || constante` e desativações
  globais de FDM/MSAA. Manter perfis externos isolados, sem importar stack inteira.
- WinNative: UBWC FD740/X1-85 é mais amplo que OneUI Amaral; não portar ao Standard.
  Atomics desativados por substituição global e PWR_MAX/governor são hipóteses de
  diagnóstico, não defaults universais.
- Banners/Steven: baselines e integração por variante; build sem aparelho não prova
  compatibilidade. WSI Wayland/Linux não demonstra exposição Android AdrenoTools.
- Balemuni/MrPurple: binários como comparadores; não importar alegações sem fonte/teste.

Patches 0004/0005/0006 preservados como referência, sem distribuição. Pesquisa deve
seguir spec → backend → teste → hardware → A/B → revisão, nunca exposure por flag.
