# Turnip Amaral 26.3.0-devel v4.4

## As extensões de profundidade saem do gate por `chip_id`

Até a v4.3, `VK_EXT_depth_bias_control` e `VK_EXT_depth_range_unrestricted` só
ligavam em dois `chip_id` — as entradas KGSL da FD740. Esse gate não descrevia
nenhuma dependência técnica: descrevia **onde estava a evidência**. Um Adreno
750, 830 ou X1-85 rodando este driver não recebia as extensões, sem razão de
hardware.

A v4.4 troca cada gate pela dependência real, e ela é **diferente para cada
extensão**:

| extensão | v4.3 | v4.4 | por quê |
|---|---|---|---|
| `VK_EXT_depth_bias_control` | 2 `chip_id` | **todas as famílias** | não há dependência de geração |
| `VK_EXT_depth_range_unrestricted` | 2 `chip_id` | **a7xx+** | no a6xx o hardware clampa sozinho |

Somos, até onde consegui verificar, a **única build que entrega estas duas
extensões**: o Mesa `main` de hoje não as expõe no Turnip, e o Turnip é o único
driver Mesa grande sem a `depth_bias_control` — `radv`, `nvk`, `panvk`, `hk` e
`venus` já a têm.

### `depth_bias_control` — sem gate, e o motivo é verificável

O runtime comum do Vulkan já faz o trabalho inteiro: lê
`VkDepthBiasRepresentationInfoEXT` e fornece `vkCmdSetDepthBias2EXT`. Do lado do
driver, `tu6_emit_depth_bias()` é um `template <chip CHIP>` que escreve
`GRAS_SU_POLY_OFFSET_SCALE`, `_OFFSET` e `_OFFSET_CLAMP` **sem nenhuma
ramificação por chip** — os três valores chegam aos registradores sem folga
somada, em qualquer geração. Faltava só o driver declarar.

**Suporte parcial, declarado como tal.** O Adreno deriva o menor valor
representável do formato e não expõe chave para forçar interpretação UNORM num
`D32_SFLOAT` — não há equivalente do `POLY_OFFSET_DB_FMT_CNTL` do RDNA nem do
`SET_DEPTH_BIAS_CONTROL` da NVIDIA. Por isso:

| feature | valor |
|---|---|
| `depthBiasControl` | **true** |
| `depthBiasExact` | **true** |
| `leastRepresentableValueForceUnormRepresentation` | false |
| `floatRepresentation` | false |

Com as duas últimas em `false`, a única representação pedível é
`LEAST_REPRESENTABLE_VALUE_FORMAT` — exatamente o que o hardware faz
nativamente. A extensão separa isso em quatro bits justamente para permitir
declarar suporte parcial com honestidade.

### `depth_range_unrestricted` — a7xx+, e este gate é de silício

O clamp em [0,1] no a7xx **não vem do silício**: vem do Turnip ligando
`z_clamp_enable` incondicionalmente para sustentar `VK_EXT_depth_clamp_zero_one`.
O comentário do próprio upstream diz:

```c
/* A7XX+ doesn't clamp to [0,1] with disabled depth clamp, to support
 * VK_EXT_depth_clamp_zero_one we have to always enable clamp and manually
 * set range to [0,1] when rs->depth_clamp_enable is false. */
```

No a6xx o hardware clampa por conta própria, então a extensão **não teria como
ser honrada** — declará-la ali seria mentir. Daí `chip >= 7`: dependência de
silício, não de evidência.

`tu_force_zero_one_depth_clamp()` consulta a extensão **habilitada pelo
aplicativo**, não o gate. Quem não a habilita recebe o código emitido idêntico
ao de antes. Se o aplicativo habilitar as duas ao mesmo tempo,
`depth_clamp_zero_one` vence — as duas pedem coisas opostas e a garantia de
[0,1] é a mais restritiva.

## Estado da validação — leia isto antes de instalar

A corrida que existe é do laboratório, no **FD740** (Driver Lab
[#69](https://github.com/rickamaral94/Amaral-Driver-Lab/issues/69)): as duas
extensões expostas em runtime, `capability_diff` **+2/−0**, nada perdido, nenhum
limite alterado, compatibilidade **100/100** e **zero divergência de pixel em
116 comparações**.

O que essa corrida prova é que o driver **renderiza idêntico para quem não
habilita a extensão**. O caminho novo — extensão *habilitada* — nunca foi
exercitado, porque nenhuma cena do laboratório a habilita.

**Generalizar de um `chip_id` para uma família é passo de degrau no mecanismo,
não na medição.** O mecanismo está lido no código e no XML de registradores; a
evidência em aparelho continua sendo de um único modelo. Está publicada como
`latest` por decisão de distribuição, não porque a validação tenha sido feita.

Se aparecer artefato de profundidade que a v4.3 não tinha — z-fighting novo,
geometria sumindo perto do plano distante — **o suspeito é o `0004`**, e o teste
é rodar a v4.3 no mesmo lugar.

## Também nesta versão

**Correção de defeito no workflow.** O filtro de caminhos que dispara a
reconstrução listava apenas `patches/0005-...`. Mudar qualquer outro patch não
disparava build, e a release ficaria com um binário que não corresponde ao que o
repositório diz. Passou a ser `patches/**`.

## Base e conteúdo

Mesa `26.3.0-devel`, commit `451e4a46` — a mesma da v4.3. A mudança desta versão
é nossa, não do upstream.

| patch | escopo |
|---|---|
| `0001` NDK r29 | build |
| `0002` A825 | um `chip_id` |
| `0003` UBWC OneUI | variante OneUI, FD740 |
| `0004` extensões de profundidade | **todas** / **a7xx+** |
| `0005` afinação Aurora | GCM: `reg_size_vec4 >= 96`; suballocadores: todas |
| `0006` perfil de emuladores | todas, por nome de aplicação |

Padrão: `turnip_amaral_26.3.0-devel_v4.4.zip` ·
OneUI: `turnip_amaral_26.3.0-devel_v4.4_oneUI.zip`
