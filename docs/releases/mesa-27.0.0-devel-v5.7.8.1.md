# Turnip Amaral 27.0.0-devel v5.7.8.1 Candidate

**Pré-release para A/B.**

Controle: Latest 4.7.7.2 permanece inalterada. Esta candidata não tem CTS, VVL
ou hardware executados nesta preparação; não há promessa de ganho de FPS.

## Mudanças que justificam a candidata

Mesa fixado em `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`, headers registrados
1.4.363, NDK r29, API 29, ARM64/KGSL. A versão 27 não é o motivo da atualização.

- `c88b6ebd3835`: sequência correta de invalidação de descriptors bindless,
  com tratamento específico anterior a A8xx.
- `5cf8c6b2fee6`: coleta completa de intervalos de push constants.
- `8f491f606a1e`: ordem segura de vector shrinking em relação ao lowering int64.
- `2755d64a645b`: evita overflow de offsets de constantes por componente no IR3.
- KGSL MR 44838 e A840 dois/três slices permanecem upstream.

## Defaults conservadores e risco de regressão

Os patches de pesquisa 0004/0005/0006 deixam de ser aplicados: não expor extensões
Amaral de profundidade sem CTS; restaurar GCM/suballocadores e perfis Zelda upstream.
Essa retirada pode mudar comportamento em jogos que dependiam dos patches. Compare
pixels, compilação e frametimes com 4.7.7.2; bisectar alterações se surgir diferença.
Nenhum relato antigo é declarado corrigido sem reprodução.

A810/A812/A825 externos seguem isolados por chip ID e experimentais. Os quatro fixes
comunitários de lifetime/OOM e a remoção do spoof MGS4 permanecem. OneUI acrescenta
somente UBWC FD740/KGSL; Standard é a variante do Odin 2 Portal.

## Instalação e avaliação

Importar o ZIP no emulador/AdrenoTools compatível. Usar Standard por padrão;
OneUI apenas em firmware que precisa desse ajuste. Preservar o ZIP Latest como
rollback. Separar testes de cache frio e quente e registrar hash/identidade efetiva.

Artefatos: ZIP Standard/OneUI, SHA256SUMS, relatórios byte a byte, manifestos de
build, ambiente e catálogo de GPUs. Logs completos na execução GitHub Actions.
Build/reprodutibilidade não demonstram conformidade nem compatibilidade universal.

Protocolo: [VALIDATION-PLAN.md](../../docs/VALIDATION-PLAN.md).
Pipeline binary, image_processing3 e outras extensões de pesquisa não são expostas.
