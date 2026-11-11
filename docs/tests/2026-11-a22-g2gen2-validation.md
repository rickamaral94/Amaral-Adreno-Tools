# Validação Snapdragon G2 Gen 2 / Adreno A22 — RG DDS e Pocket G2

Data da preparação: 2026-11-11.  
Baseline do projeto: **Turnip Amaral Standard 5.8.17.1**, Mesa
`fd8ef2befafd01190e33f12dbfd109b924c8ebc3`, Android/KGSL.

Status desta rodada: **cobertura validada em código; hardware e pacote RG DDS
pendentes**. Nenhum ID de GPU foi inventado e nenhum patch de driver foi
adicionado.

## Classificação da evidência

- **Validado em código:** a base Mesa fixada contém as entradas FD735
  `0xffff43030b00` e `0xffff43030e01`; a primeira já inclui o fix upstream
  `9c82a78f18dd60907e380dec60c46336eab64b25` para ignorar somente o speed-bin
  fuse. O patchset Standard não altera essas entradas.
- **Observação externa, não qualificação Amaral:** há relato público de um
  Retroid Pocket G2 com Android 15, firmware
  `RPG2_V1.0.0.176_20260123_181229_user`, Snapdragon G2 Gen 2 / Adreno A22 e
  8 GB LPDDR5X. Isso não fornece o chip ID KGSL nem qualifica nosso binário.
- **Pendente de hardware:** chip ID KGSL, `vendorID`, `deviceID`, identidade
  do driver carregado, métricas Azahar/Eden, temperaturas e clocks de ambos os
  aparelhos.
- **Pendente de pacote:** não foi localizado pacote Turnip público verificável
  específico do RG DDS no centro oficial de firmware até esta revisão.

## O que o wildcard FD735 cobre

No caminho Android/KGSL, Turnip consulta `KGSL_PROP_DEVICE_INFO` e copia
`kgsl_devinfo.chip_id` para `device->dev_id.chip_id`. A seleção da tabela
Freedreno passa por `dev_id_compare()`.

A entrada `0xffff43030b00` usa os bits 47..32 como wildcard de fuse. A entrada
`0xffff43030e01` faz o mesmo para a família `0x43030e01`.

No backend **KGSL** da revisão fixada, `struct kgsl_devinfo.chip_id` é um
`unsigned int` de 32 bits e `tu_knl_kgsl.cc` o copia diretamente para
`device->dev_id.chip_id`. Portanto o valor que esperamos capturar no Android é
a parte `0x43030b00` ou `0x43030e01`; os bits de fuse não vêm nesse campo
KGSL. O wildcard continua casando esses valores porque `dev_id_compare()`
aplica a máscara de fuse ao comparar. O fix `9c82a78f18d` é especialmente
importante para caminhos que fornecem fuse/speed-bin, e mantém o caminho KGSL
sem fuse compatível.

Isso **não** significa que qualquer produto chamado “Adreno A22” seja coberto.
Se RG DDS ou Pocket G2 reportarem outra combinação de core/major/minor/patch,
o resultado deve ser registrado e o menor ID observado deve ser analisado antes
de qualquer patch.

O gate `tools/check_a22_coverage.py` protege essas duas entradas na fonte e no
catálogo gerado. Ele também pode testar um chip ID capturado:

```bash
python3 tools/check_a22_coverage.py work/mesa-standard \
  --catalog dist/GPU_CATALOG_standard.h \
  --chip-id 0xSEU_CHIP_ID --require-chip-match
```

## Matriz de aparelhos

| Aparelho | SoC / GPU anunciado | Sistema / RAM | Firmware da unidade | chip ID KGSL | vendorID / deviceID | Driver runtime | Estado |
|---|---|---|---|---|---|---|---|
| Anbernic RG DDS | Snapdragon G2 Gen 2 (SG6275P) / Adreno A22 | Android 16; 8 ou 12 GB | pendente | pendente | pendente | pendente | hardware pendente |
| Retroid Pocket G2 | Snapdragon G2 Gen 2 / Adreno A22 | Android 15; 8 GB LPDDR5X em relato público | capturar na unidade; referência externa: `RPG2_V1.0.0.176_20260123_181229_user` | pendente | pendente | pendente | pode antecipar a validação |

Cada resultado deve carregar o nome do aparelho. Resultado do Pocket G2 não é
automaticamente resultado do RG DDS.

## Drivers de referência

### Qualcomm nativo

Controle do mesmo aparelho e firmware. Não reutilizar identidade ou versão de
outro produto. O controle deve ser executado no mesmo aplicativo/cena.

### Amaral Standard 5.8.17.1

- Mesa: `fd8ef2befafd01190e33f12dbfd109b924c8ebc3`
- ZIP Standard:
  `030e901d428203ea92e463cf2cd9acd88f4e81885161e848070c4342b0e2e092`
- ELF Standard:
  `e64f5306c5c8f52f013f01f3d2627a81704f07ba71ab9518c27be2b209863a96`
- backend: Android ARM64 / KGSL
- API mínima do pacote Amaral: 29

Esse é o binário a validar primeiro; esta rodada não cria um novo ZIP porque não
há correção de driver sustentada por hardware.

### Turnip Anbernic RG DDS

**Pendente.** A página oficial do RG DDS anuncia alternância entre Qualcomm e
Turnip, mas o centro oficial de firmware consultado em 2026-11-11 ainda não
oferecia uma entrada RG DDS com ZIP de driver verificável.

Quando surgir, registrar antes de testar:

- URL e firmware de origem;
- SHA-256 do ZIP e do ELF;
- `meta.json`, ABI e `minApi`;
- Build ID, SONAME e `DT_NEEDED`;
- versão/commit Mesa quando identificável;
- `VkPhysicalDeviceDriverProperties` em runtime.

### G1 GEN2 v17 / RG 55G1

Serve **somente como referência de empacotamento**. A análise pública do
TheGammaSqueeze identifica Mesa 26.1.1, package v17, `minApi 34`, KGSL e um
Turnip essencialmente upstream; o diff relatado contra a mesma revisão não
encontrou patch secreto da Anbernic. Isso não prova a composição do futuro
pacote do RG DDS.

## Fontes consultadas nesta preparação

- RG DDS oficial:
  https://anbernic.com/products/rg-dds
- Centro oficial de firmware:
  https://win.anbernic.com/download_data/
- Referência G1 GEN2 v17:
  https://github.com/TheGammaSqueeze/sd-tools/blob/main/docs/09-gpu-driver-comparison.md
- Observação pública Pocket G2:
  https://github.com/eden-emulator/Issue-Reports/issues/557
- Commit upstream de wildcard FD735:
  https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/45682
- Exemplo público de probe KGSL read-only via adb shell:
  https://github.com/Droid-Deck/DroidDeck/issues/245

A página oficial brasileira ainda classificava o RG DDS como pré-venda, com
início de envios previsto para 10/12/2026. Por isso a ausência de hardware de
varejo e de pacote público nesta data não é tratada como regressão.

## Coleta de identidade sem root

Para obter o mesmo `KGSL_PROP_DEVICE_INFO` usado pelo Turnip, compile primeiro
o probe ARM64 read-only. Ele só abre `/dev/kgsl-3d0` e executa GETPROPERTY; não
aloca memória nem submete comandos:

```bash
$NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android29-clang \
  -O2 -Wall -Wextra tools/a22_kgsl_probe.c -o /tmp/a22_kgsl_probe
```

O coletor sanitizado roda via ADB e empurra/remove esse binário em
`/data/local/tmp`:

```bash
python3 tools/collect_a22_android_probe.py \
  --serial <serial-adb> \
  --driver-label amaral-5.8.17.1-standard \
  --kgsl-probe /tmp/a22_kgsl_probe \
  --driver-zip /caminho/turnip_amaral_27.0.0-devel_v5.8.17.1.zip \
  --driver-elf /caminho/libvulkan_freedreno.so \
  --runtime-json /caminho/runtime-vulkan.json \
  --output /caminho/rgdds-amaral.json
```

Para o Qualcomm nativo, omita `--driver-zip` e `--driver-elf`. Use uma cópia
de `docs/tests/a22-runtime-template.json` para o `--runtime-json`.

O JSON de runtime deve vir **da mesma sessão do aplicativo** e ser preenchido a
partir de `VkPhysicalDeviceProperties2` +
`VkPhysicalDeviceDriverProperties`. Vulkan do sistema, `dumpsys` ou strings
do ELF não provam que um driver AdrenoTools foi carregado pelo Azahar/Eden.

O coletor também tenta ler nós KGSL públicos, mas o campo decisivo é
`kgsl.device_info.chip_id`, vindo de `KGSL_PROP_DEVICE_INFO`. Se o probe for
bloqueado pelo firmware/SELinux, registre a falha como pendente; não substitua
por um nome comercial de GPU. Há evidência pública de Android Qualcomm onde o
GETPROPERTY funciona em `adb shell` mesmo com ioctls de alocação bloqueados,
mas cada firmware precisa ser confirmado.

## Protocolo A/B em hardware

### Preparação comum

- carregamento por aplicativo/AdrenoTools, sem root;
- mesmo firmware, emulador, jogo, save, resolução, brilho, fan/power mode e
  conectividade;
- confirmar a identidade Vulkan em **cada** variante;
- registrar temperatura e clocks no início/fim;
- invalidar a rodada se Android atingir thermal status MODERATE ou superior;
- não misturar cache frio e quente;
- cinco rodadas por variante, ordem balanceada:
  `A B B A A B B A A B`.

Primeiro: A = Qualcomm nativo, B = Amaral Standard.  
Quando existir pacote DDS verificável: A = Amaral Standard, B = Anbernic Turnip.

### Azahar — duas telas

Cena proposta: **Mario Kart 7, Time Trials, Toad Circuit**, mesmo save/config e
rota. Interna em **3x**, que corresponde a 1200x720 no topo e 960x720 na tela
inferior, alinhando-se às resoluções físicas anunciadas do RG DDS. Capturar 90 s
a partir do mesmo ponto marcado.

No RG DDS executar dois blocos separados:

1. tela inferior ativa;
2. tela inferior desativada/oculta quando o aplicativo permitir, mantendo 3x e
   todas as demais opções idênticas.

Não atribuir diferença ao driver se a resolução interna, layout ou composição
mudar junto com o estado da segunda tela.

### Eden — shaders e pipelines

Cena proposta: **Mario Kart 8 Deluxe, Mario Kart Stadium, 720p Handheld**, mesma
configuração e trecho de 120 s. Fazer dois conjuntos:

- **cache frio:** limpar somente o cache de shaders/pipelines da variante antes
  de cada rodada;
- **cache quente:** preaquecer uma vez e preservar o cache daquela variante nas
  cinco rodadas.

Exportar os diagnósticos Eden quando disponíveis e processar com:

```bash
python3 tools/summarize_eden_diagnostics.py <diagnostico.zip>
```

Registrar p95/p99 de frametime, stutter, erros visuais,
`VK_ERROR_DEVICE_LOST`, pipeline misses/creation, waits, temperatura e clocks.
Métrica indisponível permanece `null`/“indisponível”.

## Gate para qualquer patch além da A22

Se a investigação futura exigir mudança com alcance A7xx ou maior, antes de
promover a hipótese rode também no Odin 2 Portal/A740:

- BOTWRecomp, mesma rota marcada;
- Wind Waker HD no Cemu Fork Amaral, mesma cena/câmera.

Coletar render CPU, GPU quando disponível, waits/fences, frametime, erros
visuais e device loss. Um ajuste de tela dupla deve continuar L0/L1 e não
atingir A740 sem mecanismo compartilhado demonstrado.

## Decisão desta rodada

**Manter o driver.** A base 5.8.17.1 já contém a correção upstream de
reconhecimento FD735 e não há chip ID físico divergente, pacote DDS verificável
ou falha de renderização reproduzida que sustente um patch adicional.

Próximo evento decisivo: captura do Pocket G2 ou RG DDS com chip ID KGSL +
identidade Vulkan da mesma sessão. Se casar com a tabela existente, avançar
direto para A/B de renderização. Se não casar, abrir uma correção mínima para o
ID realmente observado.
