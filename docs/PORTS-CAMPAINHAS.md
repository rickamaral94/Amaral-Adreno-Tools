# Campainhas dos ports e recomps

Orientação do Rick em 14/11/2026: **todo o desenvolvimento do agente Turnip fica neste repositório.** Os
repositórios dos ports e recomps são dos agentes deles. O objetivo continua sendo o melhor Turnip universal possível.
Um port é uma fonte de casos de teste, não um lugar para patch.

## Onde os ports chamam

Cada port tem um PR em rascunho que serve só de campainha. O agente Turnip está inscrito nos três e é acordado por
comentário novo.

| Port | Campainha | Prefixo | Documento no port |
| --- | --- | --- | --- |
| GTA V (Gtavport, Xbox 360 TU27, renderer plume) | [Gtavport #2](https://github.com/rickamaral94/Gtavport/pull/2) | `[gtav]` | `docs/campainha-turnip.md` |
| BOTW (Botwnspxci, NVN → Vulkan) | [Botwnspxci #3](https://github.com/rickamaral94/Botwnspxci/pull/3) | `[botw]` | `docs/logs/CAMPAINHA-TURNIP.md` |
| TOTK (Totknspcxi, NVN → Vulkan) | [Totknspcxi #4](https://github.com/rickamaral94/Totknspcxi/pull/4) | `[totk]` | `docs/logs/CAMPAINHA-TURNIP.md` |

## Regras do agente Turnip

1. **No repositório do port:** só responder no PR de campainha (análise, variável para testar, link para lab ou
   correção daqui) e manter o próprio documento da campainha correto. Nenhum commit de código, patch, build ou
   release lá.
2. **Aqui:** cada pedido que vire trabalho de driver ganha registro em `docs/` (auditoria, lab ou candidata), com a
   referência ao comentário da campainha. Patches entram em `patches/` e candidatos em `evidence/candidates.json`, pelo
   fluxo normal.
3. **Universal primeiro.** Uma correção que só serve a um jogo ou port não entra como hack global. O caminho é:
   - correção do driver que vale para qualquer app;
   - senão, perfil por app (driconf com `application_name_match` / `engine_name_match`) com evidência;
   - senão, recomendação ao port para usar a API corretamente (ex.: `VK_EXT_attachment_feedback_loop_layout`).
4. Testes em hardware continuam com o Rick, pelo modelo de pedido de teste. Merge na `main`, publicação e Latest
   continuam só com pedido dele.

## Identificação das apps (para perfis futuros)

| Port | `pApplicationName` / `pEngineName` | Fonte |
| --- | --- | --- |
| BOTW, TOTK, LAS (runtime LARecomp) | `LARecomp` / `LARecomp` | `runtime/nvn/vulkan/device.c` dos ports |
| UnleashedRecomp (plume) | `plume` (`pApplicationName`) | `thirdparty/plume/plume_vulkan.cpp` |
| Gtavport (plume, via gtav-recomp) | a confirmar no submódulo `upstream` | — |
