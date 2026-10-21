# Registro de testes em hardware

Esta seção responde, para cada experimento: **qual binário foi testado, em qual
aparelho, o que a mudança pretendia resolver, o que ocorreu e o que ainda não
podemos concluir**. O [registro de Little Nightmares no Odin 2 Portal](2026-10-odin2-portal-little-nightmares.md)
contém as onze capturas Eden recebidas até 21/10/2026. Os fatos selecionados
ficam também em [JSON estruturado](../../evidence/hardware-tests/2026-10-odin2-portal-little-nightmares.json)
para auditoria e futuras análises.

| Hardware / carga | Drivers observados | Conclusão atual |
|---|---|---|
| Odin 2 Portal, A740, Android 13, Little Nightmares no Eden | Latest 4.7.7.2, Standard 5.7.8.1, Labs 5.7.9.1, 5.7.10.1 e 5.7.11.1 | Há execução real, mas ainda não há ganho de FPS demonstrado por A/B controlado. Meta de 60 FPS pendente. |
| Odin 2 Portal, A740, Little Nightmares | Readback Lab 5.7.11.1 | Binário carregado; nenhum heartbeat V2 apareceu, portanto o caminho de cópia continua sem medição. |
| Odin 2 Portal, A740, Little Nightmares | Readback Lab 5.7.12.1 | 45 heartbeats revelaram `chip=0x43050a01`, `gpu=6760` e `scope=0`: o filtro rejeitou o ID recebido. |
| A6xx, A750, A8xx | — | Nenhum resultado novo de hardware neste registro. |
| Cemu Fork Amaral | — | Código e relatos públicos estudados; nenhum ZIP bruto de gameplay analisado nesta etapa. |

## Como acrescentar um teste

1. Copie [o modelo](TEMPLATE.md). Preencha a proposta **antes** da captura e
   adicione os resultados depois. Use um arquivo por workload/dispositivo/série,
   com uma linha por captura; nunca substitua medições antigas.
2. Registre nome/versão/variante do driver, Mesa SHA, fingerprint do patchset,
   SHA-256 do ELF carregado e do ZIP, APK/commit, aparelho, GPU, Android, API,
   KGSL, título/update, resolução, configurações, cache, cena e duração.
3. Guarde as métricas em suas unidades: FPS, frametime, GPU/CPU, waits, pipelines,
   clocks/temperatura e estabilidade visual. Use `indisponível` para medições
   ausentes; zero significa que o instrumento mediu zero.
4. Explique o método. Para alegar ganho de desempenho, faça cinco rodadas por
   variante em ordem balanceada AB/BA, com rota marcada, aquecimento e gate
   térmico definido previamente. Identidades e configurações iguais não provam
   cenas iguais. Se o método não foi cumprido, classifique como **observação**.
5. Referencie o arquivo de evidência e seu hash. Não publique logcat bruto,
   caminhos do aparelho, IDs de processo ou conteúdo de memória. O repositório
   armazena apenas métricas selecionadas e limitações explícitas.
6. Atualize a tabela acima e, quando houver JSON, rode
   `python3 tools/validate_hardware_tests.py`. CI rejeita registros com IDs
   duplicados, hashes malformados ou resultado físico inventado para uma build
   ainda pendente.

Captura verificada por manifesto significa que os arquivos exportados combinam
com o manifesto. Isso não certifica medição, imagem correta ou comparação A/B.
Build reproduzível confirma artefatos; não certifica compatibilidade no aparelho.
Veja também a [política de evidência](../EVIDENCE-POLICY.md) e o
[plano de validação](../VALIDATION-PLAN.md).
