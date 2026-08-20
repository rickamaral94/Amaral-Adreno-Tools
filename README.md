# Amaral Adreno Tools

Projeto do **Amaral Turnip Universal**, driver Vulkan para Android/KGSL
construído a partir do Mesa 3D e orientado à compatibilidade em emuladores.

> Status: `v4.1` é a release estável/latest; `v4` permanece disponível como
> fallback. O perfil da Adreno 825 e a variante OneUI continuam com escopo
> experimental e isolado dentro do pacote universal.

## Variantes da atualização v4.1

| Variante | Arquivo | Uso |
|---|---|---|
| Padrão | `turnip_amaral_26.3.0-devel_v4.1.zip` | Recomendada como ponto de partida |
| OneUI | `turnip_amaral_26.3.0-devel_v4.1_oneUI.zip` | Para sistemas cujo driver proprietário exige o mesmo `TP_UBWC_FLAG_HINT` |

As duas variantes usam o snapshot Mesa e o perfil A825 idênticos. A OneUI
acrescenta somente o ajuste UBWC nas duas entradas KGSL da FD740, sem alcançar
o ID legado `GPUId(740)` nem a Adreno X1-85.

### Compatibilidade FD740 validada no Driver Lab

As duas variantes expõem `VK_EXT_depth_range_unrestricted` e o subconjunto
suportado de `VK_EXT_depth_bias_control` somente nas entradas KGSL
`0x43050a01` e `0xffff43050a01` da FD740. No
[#69](https://github.com/rickamaral94/Amaral-Driver-Lab/issues/69), o Driver Lab
confirmou as duas extensões em runtime, nenhuma capacidade perdida,
compatibilidade 100/100 e zero divergência em 116 comparações.

O caminho de profundidade irrestrita quando explicitamente habilitado pelo
aplicativo continua monitorado em sessões reais do Eden. A mudança permanece no
degrau L0, sem alcançar outras GPUs A7xx/A8xx.

### Perfil experimental da Adreno 825 — atualizado na v4.1

A v4.1 reconhece a A825 pelo `chip_id` KGSL `0x44030000` e mantém sua topologia
real: 4 CCUs, 2 slices e 2 MiB de GMEM. A atualização incorpora ao perfil
isolado as propriedades observadas nos builds comunitários testados em hardware
A825 real, tanto em GMEM quanto em SYSMEM.

Com base nos resultados reproduzidos nos issues
[#37](https://github.com/rickamaral94/Amaral-Driver-Lab/issues/37) e
[#38](https://github.com/rickamaral94/Amaral-Driver-Lab/issues/38), somados à
evidência do [DiskDVD/TurniptoolsA8XX](https://github.com/DiskDVD/TurniptoolsA8XX/releases/tag/tu_A8XX-Y2.5),
o perfil passa a usar:

- color cache GMEM: `HALF / 128 KiB`;
- depth cache GMEM: `HALF / 128 KiB`;
- tile alignment: `64 x 32`;
- shared memory: `64 KiB`;
- caches sysmem e buffers VPC preservados nos limites conhecidos da A825.

As mudanças alcançam somente a A825. O autotuner continua escolhendo GMEM ou
SYSMEM, sem variável forçada. Os hacks comunitários de FDM/sample interpolation,
UBWC global e a afirmação não validada de correspondência VRS/Vulkan não entram.

### Variante OneUI

A OneUI ativa `enable_tp_ubwc_flag_hint` somente na entrada FD740. Use primeiro
a variante padrão e teste a OneUI apenas quando o firmware do sistema apresentar
sintomas compatíveis com divergência UBWC em blits, escala ou texturas.

## Direção do projeto

- **Fonte principal:** Mesa 3D/Freedreno/Turnip, fixado por commit.
- **Alvo:** A6xx, A7xx e A8xx reconhecidas pelo snapshot, mais A825 experimental.
- **Perfil público:** AArch64 `armv8-a`, KGSL e decisões upstream como padrão.
- **Sem atalhos globais:** sem spoof de GPU/Vulkan, `TU_DEBUG` forçado,
  capabilities inventadas ou hacks específicos de jogo.
- **Prioridade obrigatória:** compatibilidade gráfica, estabilidade, frametimes
  consistentes e, por último, desempenho/FPS.
- **Evidência antes do padrão:** otimizações da comunidade, inclusive
  experimentais, só avançam após A/B reproduzível com qualidade visual, crash,
  stutter, temperatura e consumo; mudanças específicas ficam isoladas e
  reversíveis por GPU, família ou aplicativo.

## Baseline

| Item | Valor |
|---|---|
| Revisão Amaral | `v4.1` |
| Mesa | `26.3.0-devel` |
| Commit fixado | `6e41d819219d7f4025a95cbbaddfbe492d210ff3` |
| Backend | Turnip/Freedreno + KGSL |
| ABI | Android AArch64, `armv8-a` |
| API mínima proposta | Android 10 / API 29 |
| Exceção não upstream | Adreno 825, experimental e isolada por `chip_id` |

O número `v4.1` é a revisão Amaral e avança enquanto a versão pública do Mesa
permanece `26.3.0-devel`. A v4.1 é a release estável/latest e a v4 continua
disponível como fallback.

## Compilar

Requisitos: Linux x86_64, Android NDK r29, Python 3, Git, Meson, Ninja, Flex,
Bison, glslang, pkg-config, zip e ferramentas ELF.

```bash
python3 -m venv work/venv
work/venv/bin/pip install --requirement requirements-build.txt

NDK_ROOT=/caminho/android-ndk-r29 \
  DRIVER_VARIANT=standard ./scripts/build_universal.sh

NDK_ROOT=/caminho/android-ndk-r29 \
  DRIVER_VARIANT=oneui ./scripts/build_universal.sh
```

O workflow compila cada variante duas vezes e só mantém candidatos quando ZIP e
ELF são idênticos byte a byte.

## Como uma ideia entra no driver

1. Registrar fonte e hipótese em `evidence/candidates.json`.
2. Reproduzir o problema no driver de referência e no candidato.
3. Isolar a mudança em patch pequeno, reversível e licenciado.
4. Executar o Driver Lab com checagem visual antes da velocidade.
5. Promover somente sem corrupção, crash ou regressão relevante.

Consulte [a política de evidências](docs/EVIDENCE-POLICY.md) e o
[processo de atualização upstream](docs/UPSTREAM-UPDATES.md).

## Referências

- [Mesa 3D](https://gitlab.freedesktop.org/mesa/mesa)
- [whitebelyash/mesa-tu8](https://github.com/whitebelyash/mesa-tu8)
- [Amaral Driver Lab](https://github.com/rickamaral94/Amaral-Driver-Lab)
- [Banners-Turnip](https://github.com/The412Banner/Banners-Turnip)
- [freedreno_turnip-CI](https://github.com/s1mptom/freedreno_turnip-CI)

Este projeto não é afiliado à Qualcomm, Mesa ou aos projetos de emulação.
