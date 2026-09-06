# Amaral Adreno Tools

Projeto do **Amaral Turnip Universal**, driver Vulkan para Android/KGSL
construído a partir do Mesa 3D. A ordem de decisão é: compatibilidade gráfica,
estabilidade, frametimes consistentes e desempenho.

> Status: a release marcada como **Latest** no GitHub é a referência estável.
> Atualizações puras do Mesa podem avançar automaticamente; mudanças próprias
> do Amaral continuam em pre-release até aprovação A/B.

## Variantes

| Variante | Arquivo | Uso |
|---|---|---|
| Standard | `turnip_amaral_<mesa>_v<M.V.A.U>.zip` | Ponto de partida para Android/KGSL |
| OneUI | `turnip_amaral_<mesa>_v<M.V.A.U>_oneUI.zip` | Somente quando o firmware OneUI precisar do ajuste UBWC da FD740 |

As variantes têm a mesma base Mesa, suporte às famílias e perfis por
aplicativo. A OneUI acrescenta apenas `TP_UBWC_FLAG_HINT` nas duas entradas
KGSL da FD740; o ID legado `GPUId(740)`, a A825 e a X1-85 não são alterados.

## O que muda na v4.5

- Mesa `26.3.0-devel` atualizado para o commit `eaa8cb690243`, de 1º de
  setembro de 2026.
- Correções upstream novas no pipeline cache, graphics pipeline libraries,
  formatos esparsos D32S8, compilador IR3, autotune e contagem de tempo da GPU.
- Perfis experimentais BOTW/TOTK reconstruídos do binário Balemuni Apex V2,
  isolados por título e disponíveis para A6xx/A7xx/A8xx quando o frontend expõe
  `botw` ou `totk` em `pApplicationName`.
- Remoção do perfil amplo que alterava todos os jogos identificados como
  `yuzu Emulator`; esse alcance não tinha validação A/B e podia causar
  regressões fora de Zelda.

Os perfis Zelda continuam experimentais. Não são promessa de ganho de FPS e
não ativam se o emulador esconder o nome do jogo do Vulkan. A v4.4 é o controle
obrigatório para o A/B.

## Universal não significa forçar tudo em todas as GPUs

Cada mudança é gateada pela dependência real:

| Mudança | Alcance |
|---|---|
| Mesa upstream | GPUs reconhecidas pelo snapshot |
| GCM Aurora | dispositivos com `reg_size_vec4 >= 96` |
| suballocadores de 512 KiB | A6xx/A7xx/A8xx |
| `VK_EXT_depth_bias_control` | todas as famílias |
| `VK_EXT_depth_range_unrestricted` | A7xx+ |
| BOTW/TOTK | aplicação, sem gate por GPU |
| perfil A825 | somente `chip_id 0x44030000` |
| UBWC OneUI | somente FD740/KGSL na variante OneUI |

Uma otimização A740 só alcança outras GPUs quando o código demonstra a mesma
capacidade. Ajustes de UBWC, cache, tile, FDM/MSAA ou registradores ligados ao
silício permanecem isolados.

## Versionamento e canais

O formato novo é `Mesa.Vulkan.Amaral.Upstream`, por exemplo `4.5.1.3`:

- primeiro campo: geração da versão numérica Mesa;
- segundo: geração da versão dos headers Vulkan;
- terceiro: revisão de patches/ajustes próprios;
- quarto: snapshot automático do Mesa upstream.

Mesa upstream sobre o patch set aprovado é publicado como `Latest`. Qualquer
mudança própria aumenta o terceiro campo e permanece como pre-release até os
testes A/B. Consulte o [processo upstream](docs/UPSTREAM-UPDATES.md).

## Baseline de migração

| Item | Valor |
|---|---|
| Esquema inicial | `v4.5.1.0` (o primeiro Mesa novo gera `.1`) |
| Estado exato | `config/mesa-lock.json` e `config/version-state.json` |
| Backend | Turnip/Freedreno + KGSL |
| ABI | Android AArch64, `armv8-a` |
| API mínima proposta | Android 10 / API 29 |
| Exceção não upstream | A825 experimental, isolada por `chip_id` |

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

O pipeline compila cada variante duas vezes e exige ZIP e ELF idênticos byte a
byte antes de publicar.

## Como uma ideia entra no driver

1. Registrar fonte, licença e hipótese em `evidence/`.
2. Ler o código/patch real; texto de release não basta.
3. Separar dependência de hardware, família e aplicativo.
4. Fazer A/B reproduzível com imagem, crash, FPS, frametime/P99, stutter,
   temperatura e consumo.
5. Promover ao padrão somente com ganho comprovado e baixo risco.

Consulte a [política de evidências](docs/EVIDENCE-POLICY.md), a
[auditoria comunitária de 01/09](docs/audits/2026-09-01-community-source-audit.md)
e o [processo upstream](docs/UPSTREAM-UPDATES.md).

Este projeto não é afiliado à Qualcomm, Mesa ou aos projetos de emulação.
