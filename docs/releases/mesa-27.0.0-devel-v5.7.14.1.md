# Turnip Amaral 27.0.0-devel v5.7.14.1 Candidate

**Candidata de avaliação, não Latest.** Stable 4.7.7.2 e candidata anterior
5.7.8.1 permanecem como controles. O número de revisão Amaral avança até 14
para não reutilizar os identificadores 9–13 empregados pelas Labs A740.

## Base e escopo

- Mesa `69f1f21f0258a77046dbaeb8ed7a8ad37a683006`, 22/10/2026 05:47:33 UTC,
  216 commits após o lock anterior `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`.
- Vulkan headers 1.4.363; Android API 29; NDK r29; arm64-v8a; KGSL.
- Standard mantém comportamento conservador. OneUI acrescenta exclusivamente o
  hint UBWC FD740/KGSL já isolado.
- O patch externo A825 continua experimental e foi somente reposicionado após
  a entrada A830 upstream; seus parâmetros não foram expandidos para outras GPUs.

## Correções upstream que justificam a candidata

- A6xx: `GRAS_MODE_CNTL` corrigido para um caso A650 reproduzido de hang e
  renderização incorreta com draws instanciados e sample mask; invalidação de
  constantes compartilhadas antes de desativá-las ao trocar pipelines.
- Turnip: verificação sem sinal do limite de texel buffer emulado, evitando
  acesso antes da view com offset negativo; liberação de referência local a BO
  nos patchpoints de visibility stream.
- A8xx: divisão de draws indiretos grandes em múltiplos pacotes quando podem
  causar GPU fault, com continuidade de `DrawID` via alterações coordenadas
  Turnip/IR3/NIR. Não habilita A8xx globalmente nem valida novos IDs por si só.
- Vulkan comum/NIR: prevenção de afinidade CPU herdada pela thread de submit,
  tratamento de loads especulados e correção de coordenada em cooperative
  matrix. Impacto no Android/Turnip deve ser medido, não presumido.

Veja a [auditoria dos commits](../audits/2026-10-22-mesa-rebase.md) e o
[registro de hardware](../tests/2026-10-odin2-portal-little-nightmares.md).

## Gates e limites

O patchset Standard/OneUI e as verificações estruturais A840/Vulkan aplicaram
ao Mesa proposto no [CI de rebase](https://github.com/rickamaral94/Amaral-Adreno-Tools/actions/runs/39765675756).
Patches 0004–0006 são referências fora dos pacotes e mantêm o SHA de verificação
histórico: não foram apresentados como testados neste Mesa.

Build dupla, ZIP/ELF byte a byte, validação do pacote, CTS/VVL e teste de
hardware precisam ser registrados separadamente. As observações de Little
Nightmares no A740 não demonstram que estes commits elevem FPS; o experimento
readback ainda aponta a necessidade de cena marcada e correlação no Eden.
Para A6xx, reproduzir o caso sample mask e trocas de pipeline; para A8xx,
testar draws indiretos/`DrawID` em hardware real. Não promover para Latest
nem afirmar compatibilidade universal com base apenas na build.
