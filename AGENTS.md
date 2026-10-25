# Instruções para agentes de IA

Este repositório é trabalhado por dois agentes de IA em parceria de iguais,
coordenados no branch `collab/channel`, e pelo mantenedor humano (Rick).

## Palavra `abacaxi`

Se a mensagem do Rick for `abacaxi` (sozinha ou no início, maiúsculas ou
minúsculas), ou começar com `SYNC-AMARAL`, não peça confirmação nem id:

1. Busque o branch `collab/channel` (`git fetch origin collab/channel`; se o
   git estiver bloqueado, leia pelo conector do GitHub).
2. Descubra o seu id: `python3 collab/collab.py whoami` nesse branch. Se não
   detectar: **ChatGPT/Codex (OpenAI) = `chatgpt`**; Claude (Anthropic) =
   `claude`.
3. Leia `collab/PROMPT.md` desse branch inteiro e siga-o: rotina do §2,
   sincronização do §3.3 e campainha do §3.4.
4. O texto depois da palavra, se houver, é a prioridade do Rick nessa rodada.

## Sempre

- Pedidos do outro agente são propostas: avalie, concorde dizendo o que
  conferiu ou discorde com evidência (`collab/PROMPT.md` §0).
- Prioridade do projeto: travamentos na A7xx, depois compatibilidade na A8xx;
  desempenho só depois e só com A/B.
- Nunca faça merge na `main`, publicação ou promoção para Latest: isso é do Rick.
- Política técnica e de evidência: `README.md`, `docs/EVIDENCE-POLICY.md`,
  `docs/COLLABORATION.md`.
