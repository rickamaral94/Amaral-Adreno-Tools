# Amaral Adreno Tools

Projeto do **Amaral Turnip Universal**, um único pacote de driver Vulkan para
Android/KGSL, construído a partir do Mesa 3D e orientado a compatibilidade em
emuladores.

> Status: estrutura inicial de desenvolvimento. Ainda não há release universal
> recomendada para uso diário.

## Direção do projeto

- **Fonte principal:** Mesa 3D/Freedreno/Turnip, fixado por commit.
- **Alvo inicial de validação:** Adreno A6xx, A7xx e A8xx reconhecidas pelo
  snapshot do Mesa. Suporte real depende também do aparelho, firmware, Android
  e emulador.
- **Um perfil público:** AArch64 `armv8-a`, KGSL e decisões upstream como padrão.
- **Sem atalhos globais:** nada de spoof de GPU/Vulkan, recursos inventados,
  `TU_DEBUG` forçado ou hack específico de jogo no pacote universal.
- **Evidência antes de otimização:** relatos da comunidade, issues de emuladores,
  repositórios antigos e Amaral Driver Lab alimentam candidatos isolados; não
  viram patch ativo sem teste A/B e validação visual.

## Baseline inicial

| Item | Valor |
|---|---|
| Revisão Amaral | `v1` |
| Mesa | `26.3.0-devel` |
| Commit fixado | `32fab1ad098a393ffa40dce8e5272f52aa0ff70a` |
| Backend | Turnip/Freedreno + KGSL |
| ABI | Android AArch64, `armv8-a` |
| API mínima proposta | Android 10 / API 29, pendente de matriz completa |
| Hacks de execução ativos | nenhum |

O arquivo canônico é [`config/mesa-lock.json`](config/mesa-lock.json). O padrão
curto de identificação é:

- nome: `Turnip Amaral 26.3.0-devel v1`;
- arquivo: `turnip_amaral_26.3.0-devel_v1.zip`;
- descrição: `Turnip Amaral 26.3.0-devel v1 · Vulkan 1.4.xxx`.

O número `v1` é a revisão Amaral. Ele avança (`v2`, `v3`...) enquanto a versão
do Mesa for a mesma e volta para `v1` quando a versão do Mesa mudar. O commit
completo continua no lock e nos checksums, não no nome público.

## Começar

Requisitos: Linux x86_64, Android NDK r29, Python 3, Git, Meson, Ninja, Flex,
Bison, glslang, pkg-config, zip e ferramentas ELF.

```bash
python3 -m venv work/venv
work/venv/bin/pip install --requirement requirements-build.txt
NDK_ROOT=/caminho/android-ndk-r29 ./scripts/build_universal.sh
```

O build usa apenas o commit fixado, aplica a compatibilidade necessária ao NDK
r29, valida o ELF e gera ZIP + `SHA256SUMS.txt` em `dist/`.

Para o gate de reprodutibilidade usado antes dos testes:

```bash
NDK_ROOT=/caminho/android-ndk-r29 ./scripts/check_reproducibility.sh
```

Ele faz duas compilações isoladas e só mantém o candidato quando ZIP e ELF forem
idênticos byte a byte. O workflow envia o resultado como artefato temporário por
14 dias; ele não cria release.

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
- Repositórios privados Amaral Adreno 6xx/7xx/8xx (histórico técnico)
- [Amaral Driver Lab](https://github.com/rickamaral94/Amaral-Driver-Lab)
- [freedreno_turnip-CI](https://github.com/s1mptom/freedreno_turnip-CI)

Este projeto não é afiliado à Qualcomm, Mesa ou aos projetos de emulação.
