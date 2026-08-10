# Amaral Adreno Tools

Projeto do **Amaral Turnip Universal**, driver Vulkan para Android/KGSL
construído a partir do Mesa 3D e orientado à compatibilidade em emuladores.

> Status: `v2` em pré-release de validação comunitária. O suporte à Adreno 825
> e a variante OneUI são experimentais.

## Variantes da atualização v2

As duas variantes usam o mesmo snapshot Mesa, a mesma revisão Amaral e o mesmo
suporte experimental à Adreno 825. A variante OneUI acrescenta somente a
compatibilidade UBWC descrita abaixo.

| Variante | Arquivo | Uso |
|---|---|---|
| Padrão | `turnip_amaral_26.3.0-devel_v2.zip` | Recomendada como ponto de partida |
| OneUI | `turnip_amaral_26.3.0-devel_v2_oneUI.zip` | Para sistemas cujo driver proprietário exige o mesmo `TP_UBWC_FLAG_HINT` |

### Suporte experimental à Adreno 825

A variante padrão e a OneUI reconhecem a Adreno 825 pelo `chip_id` KGSL
`0x44030000`. O port comunitário adiciona uma configuração própria de
GMEM/CCU/VPC e mantém os dois workarounds de pipeline condicionados diretamente
a esse ID. Assim, eles não alteram A810, A829, A830, A840 nem outras GPUs do
pacote Universal.

Esse suporte deriva do fork
[`whitebelyash/mesa-unified`](https://github.com/whitebelyash/mesa-unified/tree/turnip/gen8),
mas o fork completo não foi incorporado. Perfis globais de compilação IR3,
aumento global de shared memory e alterações conjuntas para várias A8xx ficaram
de fora. A A825 ainda não está definida no snapshot oficial do Mesa usado por
esta revisão e não possui validação CTS ou matriz física completa; por isso seu
suporte deve ser considerado **experimental**.

### Variante OneUI

A OneUI é o mesmo driver padrão com `enable_tp_ubwc_flag_hint` ativado somente
na entrada FD740. O Mesa documenta que esse bit precisa coincidir com o driver
proprietário do sistema; quando há divergência, podem ocorrer falhas em blits,
escala e texturas. Ela não é um perfil de desempenho geral para aparelhos
Samsung e não altera a configuração das GPUs A8xx.

Use primeiro a variante padrão. Teste a OneUI quando o firmware/driver do
sistema apresentar sintomas compatíveis com a divergência de UBWC.

## Direção do projeto

- **Fonte principal:** Mesa 3D/Freedreno/Turnip, fixado por commit.
- **Alvo de validação:** Adreno A6xx, A7xx e A8xx reconhecidas pelo snapshot,
  mais a A825 em suporte comunitário experimental.
- **Um perfil público:** AArch64 `armv8-a`, KGSL e decisões upstream como padrão.
- **Sem atalhos globais:** nada de spoof de GPU/Vulkan, recursos inventados,
  `TU_DEBUG` forçado ou hack específico de jogo no pacote universal.
- **Evidência antes de otimização:** mudanças novas ficam isoladas por variante
  ou por `chip_id` e só são promovidas após teste A/B e validação visual.

## Baseline

| Item | Valor |
|---|---|
| Revisão Amaral | `v2` |
| Mesa | `26.3.0-devel` |
| Commit fixado | `32fab1ad098a393ffa40dce8e5272f52aa0ff70a` |
| Backend | Turnip/Freedreno + KGSL |
| ABI | Android AArch64, `armv8-a` |
| API mínima proposta | Android 10 / API 29, pendente de matriz completa |
| Exceção não upstream | Adreno 825, experimental e isolada por `chip_id` |

O arquivo canônico é [`config/mesa-lock.json`](config/mesa-lock.json). O número
`v2` é a revisão Amaral: ele avança enquanto a versão do Mesa for a mesma e
volta para `v1` quando a versão do Mesa mudar. O commit completo permanece no
lock e nos checksums, não no nome público.

## Compilar

Requisitos: Linux x86_64, Android NDK r29, Python 3, Git, Meson, Ninja, Flex,
Bison, glslang, pkg-config, zip e ferramentas ELF.

```bash
python3 -m venv work/venv
work/venv/bin/pip install --requirement requirements-build.txt

# Variante padrão
NDK_ROOT=/caminho/android-ndk-r29 \
  DRIVER_VARIANT=standard ./scripts/build_universal.sh

# Variante OneUI
NDK_ROOT=/caminho/android-ndk-r29 \
  DRIVER_VARIANT=oneui ./scripts/build_universal.sh
```

Para o gate de reprodutibilidade, execute cada variante duas vezes:

```bash
NDK_ROOT=/caminho/android-ndk-r29 \
  DRIVER_VARIANT=standard ./scripts/check_reproducibility.sh
NDK_ROOT=/caminho/android-ndk-r29 \
  DRIVER_VARIANT=oneui ./scripts/check_reproducibility.sh
```

O workflow executa a mesma matriz e só mantém candidatos quando ZIP e ELF são
idênticos byte a byte. Os artefatos temporários ficam disponíveis por 14 dias;
o workflow de candidatos não cria release automaticamente.

## Como uma ideia entra no driver

1. Registrar a fonte e a hipótese em `evidence/candidates.json`.
2. Reproduzir o problema no driver de referência e no candidato.
3. Isolar a mudança em patch pequeno, reversível e licenciado.
4. Executar a matriz do Driver Lab com checagem visual antes da velocidade.
5. Promover somente se não houver corrupção, crash ou regressão relevante.

Os critérios completos estão em [`docs/EVIDENCE-POLICY.md`](docs/EVIDENCE-POLICY.md).

## Atualizações do Mesa

A automação semanal somente detecta um novo `main` e abre um relatório. A troca
do snapshot exige auditoria de **todo o intervalo**, duas compilações idênticas e
nova validação no Driver Lab. Consulte
[`docs/UPSTREAM-UPDATES.md`](docs/UPSTREAM-UPDATES.md).

## Referências

- [Mesa 3D](https://gitlab.freedesktop.org/mesa/mesa)
- [whitebelyash/mesa-unified](https://github.com/whitebelyash/mesa-unified/tree/turnip/gen8)
- Repositórios privados Amaral Adreno 6xx/7xx/8xx (histórico técnico)
- [Amaral Driver Lab](https://github.com/rickamaral94/Amaral-Driver-Lab)
- [freedreno_turnip-CI](https://github.com/s1mptom/freedreno_turnip-CI)

Este projeto não é afiliado à Qualcomm, Mesa ou aos projetos de emulação.
