# Política de evidência

Uma dica da comunidade é uma hipótese, não uma correção. Para entrar no driver
universal, um hack precisa ter fonte rastreável, licença compatível, mudança
isolada, mecanismo técnico explicável e resultado reproduzível.

A decisão segue sempre esta ordem: compatibilidade gráfica, estabilidade,
frametimes consistentes e desempenho. Ganho de FPS não compensa artefato,
travamento, piora de P95/P99 ou comportamento térmico/energético inadequado.

## Barreiras obrigatórias

- problema reproduzido com logs e identidade do driver confirmada;
- mesma configuração, temperatura e sequência para candidato e referência;
- comparar FPS, P50/P95/P99, stutter, temperatura, consumo, estabilidade e
  qualidade gráfica nas GPUs e nos emuladores alcançados pela mudança;
- pelo menos 5 rodadas por cenário (10 nas decisões de release);
- qualidade visual aprovada antes de considerar FPS/tempo;
- zero crash, `device lost`, corrupção ou recurso Vulkan artificial;
- regressão média não pior que 2% e P95/P99 não piores de forma relevante;
- confiança média ou alta no Driver Lab;
- cobertura de ao menos uma A6xx, uma A7xx e uma A8xx antes de tornar padrão;
- teste nos emuladores afetados e um conjunto de controle.

Resultado específico de jogo pode justificar documentação ou opção de diagnóstico,
mas não um comportamento global. Otimizações específicas devem ficar isoladas
por GPU, família ou aplicativo e manter reversão simples. Spoofing e recursos
não suportados são rejeitados no pacote universal.

## Estados

- `proposed`: hipótese registrada.
- `testing`: patch isolado em avaliação.
- `approved`: passou por todas as barreiras; ainda exige revisão.
- `active`: incluído no build padrão.
- `reference-only`: útil como histórico, não distribuído.
- `rejected`: evidência insuficiente, regressão ou risco incompatível.
