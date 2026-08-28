> ## ⚠️ Substituída pela v4.3
>
> **Esta versão não é a recomendada.** Use a
> [v4.3](https://github.com/rickamaral94/Amaral-Adreno-Tools/releases/tag/mesa-26.3.0-devel-v4.3),
> que é a `latest`.
>
> A v4.3 traz, sobre esta: base do Mesa mais nova (`451e4a46` contra
> `6e41d819`), um perfil de compatibilidade para emuladores de Switch, e os
> limites do GCM e dos suballocadores re-derivados — nesta versão eles ficavam
> restritos a a7xx+ sem motivo técnico.
>
> Fica publicada por procedência, não por recomendação. O texto abaixo é o da
> publicação original e continua valendo **como descrição da v4.2**.

# Turnip Amaral 26.3.0-devel v4.2

## Afinação A740 no driver universal

Alvo: Qualcomm Adreno 740 / Snapdragon 8 Gen 2 — sem alterar o comportamento
das outras gerações.

A v4.2 traz duas afinações que a comunidade usa na linha A740 para dentro do
driver universal. **As duas são condicionadas à geração do Adreno em tempo de
execução**, então um a6xx recebe exatamente o binário de antes.

| mudança | onde | escopo | estado |
|---|---|---|---|
| GCM (global code motion) ligado por padrão | `ir3_nir.c` | **a7xx+** | mecanismo verificado, **magnitude não medida** |
| `pipeline_suballoc` 128 → 512 KiB | `tu_device.cc` | **a7xx+** | idem |
| `kgsl_profiling_suballoc` 128 → 512 KiB | `tu_device.cc` | **a7xx+** | idem |

O override por ambiente continua valendo e tem precedência: `GCM=0` desliga
mesmo no a7xx. É esse o caminho para isolar o efeito num A/B — mesmo binário,
duas corridas.

## O que esta versão **não** entrega

Esta seção existe porque a redação anterior desta nota afirmava as três coisas
abaixo como entregues. Nenhuma estava.

**Cache de shader de 4 GiB — não entregue, e não entregável hoje.** O Mesa
desliga o cache em disco no Android:

```c
/* src/util/disk_cache_os.c, disk_cache_enabled() */
#if defined(SHADER_CACHE_DISABLE_BY_DEFAULT) || DETECT_OS_ANDROID
   bool disable_by_default = true;
```

Ligar exigiria a propriedade `mesa.shader.cache.disable=false`, que não se
define sem root, e um diretório gravável que um processo de aplicativo não
tem. Enquanto isso valer, **qualquer limite de tamanho é inerte** — inclusive o
`-Dshader-cache-max-size=4G` que a versão anterior passava ao meson. A flag foi
removida por não fazer nada.

**Workarounds de compatibilidade do Zelda — não entregues.** As duas opções
citadas existem no Turnip (`tu_dont_care_as_load` e
`tu_allow_oob_indirect_ubo_loads`, em `00-turnip-defaults.conf`), mas o upstream
as aplica a **Kex Engine, Clausewitz, DXVK e jogos nomeados — nunca a Zelda e
nunca a emulador**. Não existe entrada de Zelda no upstream. Ligá-las para o
emulador inteiro custaria desempenho em **todos** os jogos dele, porque as duas
desativam otimização, e não há medição que justifique a troca. Ficam de fora
até haver corrida no aparelho.

**`profiles/a740/aurora-4.2.conf` não é lido por nada.** Nenhum script de build,
workflow ou o driver consultam `profiles/`. O arquivo foi mantido como registro
de intenção, com o estado real de cada linha anotado nele.

## Estado da validação

**Nada da v4.2 foi validado em aparelho.** As duas mudanças são de desempenho —
prioridade 4 do projeto, atrás de compatibilidade, estabilidade e consistência
de frametime. O mecanismo está lido no código; a magnitude não foi medida.

Por isso esta release sai como **pré-lançamento**, não como `latest`.

O que a promove a estável:

| mudança | teste |
|---|---|
| GCM no a7xx | mesma build, duas corridas: `GCM=0` contra padrão. Diferença abaixo de 3 % não conta |
| suballocadores | idem; observar cauda de frametime, não média |
| portão | sem regressão de compatibilidade — cenas visíveis e ausência de corrupção |

GCM mexe no código gerado dos shaders. Se aparecer corrupção ou travamento que
a v4.1 não tinha, **o suspeito é ele**, e o teste é `GCM=0` no mesmo aparelho.

## Pacotes

Padrão: `turnip_amaral_26.3.0-devel_v4.2.zip`

OneUI: `turnip_amaral_26.3.0-devel_v4.2_oneUI.zip`

Base Mesa `26.3.0-devel`, commit `6e41d819`, conforme `config/mesa-lock.json`.
Patches Amaral existentes mantidos: NDK r29, A825 experimental, extensões de
profundidade FD740 e, na variante OneUI, o hint UBWC.
