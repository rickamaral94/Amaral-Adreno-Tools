# Little Nightmares / A740 — experimento de autotuning

**Lab 5.7.9.1, não Latest, sem ganho de FPS demonstrado.**
Objetivo: reduzir o tempo GPU do jogo preservando semântica Vulkan.
60 FPS é a meta; não é um resultado desta preparação.

## Hipótese e única variável

Controle A: 5.7.8.1 Standard, Mesa `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`.
Experimento B: mesmo Mesa, NDK/API e patchset, mais 0009. Troca o default do
autotuner de BANDWIDTH para PROFILED apenas nos IDs A740 documentados e com
application/engine iguais a `yuzu Emulator`. O algoritmo já existe no Mesa:
compara tempos GPU de passes em GMEM/SYSMEM em vez de estimar largura de banda.
Não se alteram thresholds, hash dos passes ou algoritmo de atualização.

Na captura de 20/10, o jogo registra cerca de 103 passes/quadro, 3,6 draws/pass,
37,6% de reabertura do framebuffer e GPU p50/p90/p99 de 15,75/24,75/39 ms.
Isso fundamenta o experimento, não prova que a decisão atual esteja errada.
Passes com menos de cinco draws já recebem SYSMEM por default neste Mesa,
salvo restrições anteriores. Eles continuam sem profiling neste experimento.

Os guards de SINGLE_PRIM_MODE, FDM, MSRTSS, simultaneous-use e demais caminhos
de seleção permanecem upstream. O patch não força GMEM/SYSMEM; não altera
barreiras, extensões, precisão de shaders, UBWC, clocks, resolução ou OneUI.
Variáveis TU_AUTOTUNE_ALGO/FLAGS explícitas e drirc não vazio prevalecem.

## Limite de identificação e instalação

O APK `6b592ecbea` informa `yuzu Emulator` em pApplicationName e pEngineName,
conforme `src/video_core/vulkan_common/vulkan_wrapper.cpp`.
Não informa title ID. **O driver não sabe qual jogo está rodando.**
Selecione este ZIP somente nas configurações por jogo de Little Nightmares.
Se instalado globalmente, o experimento também alcançará outros jogos Eden/yuzu
no A740. Não distribuir como perfil universal, nem integrar este default ao main.
A6xx/A750/A8xx e outros engines mantêm o comportamento anterior.

O log de inicialização deve conter:
`AMARAL_LAB_LN_A740: profiled autotuner; title unknown; per-game test only`.
Essa mensagem indica seleção do algoritmo, não prova que cada passe usou
GMEM ou SYSMEM. O coletor do APK começa no início da captura e pode perder
a mensagem anterior de inicialização: ausência no ZIP não prova falha de
ativação. Conferir hash do ELF e ausência de overrides; confirmar diretamente
a ativação requer preservar o contexto de inicialização em uma futura captura.
Não usar TU_DEBUG=gmem/sysmem nem overrides de autotuner nesta comparação.

Não é necessário mudar o APK para o primeiro A/B. Para uma futura política
automática por título, será necessário um identificador explícito e confiável
enviado pelo emulador; a marca genérica não deve ser silenciosamente ampliada.

## Riscos

- Profiling adiciona timestamps/trabalho de GPU e CPU: pode piorar FPS.
- Exploração inicial de ambos os modos pode piorar frametime.
- Cenas diferentes podem compartilhar uma assinatura de passe e produzir
  decisões menos adequadas; testar mudanças de câmera e transições.
- Comparar com caches igualmente aquecidos: binários diferentes podem mudar UUID.
- Ausência de crashes não certifica pixels, sombras, transparências ou efeitos.

## Protocolo no Odin2 Portal

1. Mesmo APK `6b592ecbea`, jogo/update/save, configurações, resolução, clocks e
   modo do aparelho. Standard nos dois lados.
2. Aquecer separadamente cache e execução de cada driver, percorrendo a mesma
   rota; reiniciar o processo ao trocar. Depois repetir a rota antes da medição
   para permitir convergência do autotuner. Registrar tempo de aquecimento.
3. Cinco rodadas balanceadas A-B-B-A, com a mesma duração e início de cena.
   Resfriar ao mesmo estado de referência; descartar pares que falhem o gate
   térmico/clocks. Bateria não substitui temperatura interna indisponível.
4. Registrar hash carregado, mensagem de ativação, FPS, p50/p90/p99 GPU,
   intervalos de frame, waits, pipelines novos e capturas visuais nos mesmos pontos.
5. Testar também transições de cenário e uma sessão prolongada.

Comparar medianas e dispersão entre rodadas, não escolher a melhor captura.
Sucesso exige melhora repetível de tempo GPU/frametime e ausência de regressões
visuais, crashes/device lost ou deterioração do p99. Se piorar, retirar o perfil.
Se ficar neutro, não publicar nova release por ele.

## Instrumentação Eden desejável depois do primeiro teste

O KGSL busy repetiu 79,004% em 25/81 amostras: tratar como suspeito/intermitente,
registrar leitura/frescor/erros, sem carregar silenciosamente valor antigo.
O relatório não deve chamar o default de “GMEM”: o modo precisa ser medido.
As contagens de reabertura não medem bytes efetivamente carregados/armazenados.
São melhorias recomendadas para o próximo APK, não alterações feitas aqui.

## Build e distribuição

Branch `lab/little-nightmares-a740-profiled`. Workflow `lab-ln.yml` somente gera
artifacts através do build reproduzível existente, duas compilações por variante.
Não publica release ou promove Latest. Usar `verified-standard` no Odin.
Este branch tem controle de versão/fingerprint próprio; nunca sobrescrever
assets 5.7.8.1. Gates de hardware e CTS permanecem pendentes.
