# Atualizações do Mesa e canais de release

O Mesa `main` é o upstream técnico do projeto. O código upstream e as mudanças
próprias do Amaral seguem canais diferentes.

## Regra de publicação

- **Mesa puro sobre o patch set estável:** build validado e publicado como
  `Latest`.
- **Patch, hack, configuração ou toolchain Amaral:** publicado como
  `pre-release`; só vira `Latest` depois dos testes A/B e da promoção manual do
  mesmo binário.
- **Patch set diferente do estável:** bloqueia a automação upstream. Isso evita
  que uma atualização do Mesa promova indiretamente um hack ainda não testado.

Os dois canais sempre geram Standard e OneUI. Nenhum perfil Zelda força
`TU_DEBUG=sysmem`.

## Versionamento Amaral

O formato público é `M.V.A.U`, por exemplo `4.5.1.3`.

| Campo | Significado | Regra |
|---|---|---|
| `M` | geração Mesa | aumenta quando a versão numérica do Mesa muda |
| `V` | geração Vulkan | aumenta quando a versão dos headers Vulkan muda |
| `A` | revisão Amaral | aumenta quando muda patch/configuração própria |
| `U` | snapshot upstream | aumenta a cada Mesa HEAD publicado |

O sufixo `-devel` não cria sozinho uma geração Mesa nova. A comparação usa a
parte numérica completa: `26.3.0`. Quando `M`, `V` ou `A` muda, `U` reinicia em
`1`.

Exemplos:

- `4.5.1.1` → primeiro snapshot upstream no esquema novo;
- `4.5.1.2` → novo Mesa, mesmos Vulkan e patch set Amaral;
- `4.5.2.1` → alteração própria, publicada inicialmente como pre-release;
- `4.6.2.1` → nova revisão dos headers Vulkan;
- `5.6.2.1` → nova versão numérica do Mesa.

O estado fica em `config/version-state.json`. O lock completo do Mesa continua
em `config/mesa-lock.json`, garantindo a rastreabilidade pelo SHA de 40
caracteres.

## Automação upstream

`.github/workflows/publish-upstream.yml` executa diariamente às 07:07 BRT e
também aceita disparo manual.

1. busca o `mesa/main` atual;
2. confirma que o patch set é exatamente o último aprovado em A/B;
3. resolve as quatro partes da versão;
4. reaplica os patches e valida o diff;
5. compila Standard e OneUI duas vezes;
6. exige ZIP e ELF reproduzíveis byte a byte;
7. valida os pacotes, metadados, ABI e hashes;
8. publica uma tag imutável e a marca como `Latest`;
9. só então persiste o lock, a compatibilidade dos patches e o estado da versão.

Qualquer conflito de patch, falha de compilação ou divergência de hashes
interrompe o fluxo sem publicar.

Se existir um candidato Amaral ainda não promovido, a execução upstream termina
sem erro e registra que foi adiada. Isso mantém o monitoramento saudável sem
misturar uma atualização confiável do Mesa com uma alteração própria pendente.

## Mudanças Amaral e promoção

Alterações em patches, templates, configuração de build ou empacotamento
acionam `.github/workflows/publish-candidate.yml`. O terceiro campo aumenta e a
release nasce como pre-release.

Depois da validação gráfica, estabilidade, frametimes, desempenho, temperatura
e consumo, execute `Promote A/B-approved candidate`. A promoção apenas muda o
canal do artefato já testado e registra seu fingerprint como novo patch set
estável; não recompila o driver.

Não existem publicadores separados por versão antiga no ramo principal. Tags
históricas permanecem disponíveis, mas nunca são reconstruídas a partir do HEAD
atual.
