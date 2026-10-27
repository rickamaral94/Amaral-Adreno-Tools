# Ensaio de comunicação — 27/10/2026

Ensaio no Amaral Adreno Tools, `collab/channel`, pedido pelo mantenedor durante
a retomada do ChatGPT/Codex. Evidência pública do canal; sem IDs de conversas,
configurações privadas, credenciais ou logs de aparelhos.

| Item | Resultado e alcance |
| --- | --- |
| Identidade | `whoami` retornou `chatgpt`. |
| Ferramenta | `selftest ok`; canal válido com 316 mensagens antes do pong. |
| ChatGPT → Claude → ChatGPT | Token FS-20261027-A retornou com desafio `FS-20261027-A/claude-K7M2`, confirmado em debb. Sessões ativas. |
| Git direto | Fetch, commit e push observados. Avanço concorrente foi recusado; rebase preservou mensagens de ambos. Sem force push. |
| Leitura e fechamento | Inbox antes de seen; resposta com reply_to/closes; corpos via arquivo. |
| Campainha para Claude | Claude relata recebimento dos eventos nesta rodada, aguardando fim de turno; cerca de 4–6 min. Não é garantia de latência. |
| Despertar automático desta sessão ChatGPT | **Não comprovado.** A leitura foi ativa. |
| Agendamento entregando nesta nova conversa | **Observado nesta conversa:** teste único respondeu `FS-DELIVERY-20261027` após leitura de AGENTS.md pelo conector GitHub. Não comprova gatilho por evento GitHub. |
| Dois escritores reais com mesmo id | **Not-run** no canal vivo. Kit testa aviso com dois nonces em repo descartável; não oferece lock. |

Mensagens rastreáveis:

- Ping: `20261027T084147338Z-claude-7ac9`.
- Desafio: `20261027T084143644Z-chatgpt-10f4`.
- Pong e verificações: `20261027T084313008Z-chatgpt-6adb`.
- Token de retorno: `20261027T084811585Z-claude-7dd7`.
- Correção da latência de campainha: `20261027T084904612Z-claude-8481`.
- Confirmação final: `20261027T085204732Z-chatgpt-debb`.

O ping foi publicado às 08:42:08Z conforme relato do Claude, leitura concluída
até 08:42:39Z pelo ChatGPT, pong criado às 08:43:13Z: cerca de 65 s do push ao
pong, nesta observação. O marcador incompleto `08:5xZ` do relato de retorno não
serve para medir latência. Isso não comprova SLA nem despertar com sessão fechada.

Conclusão: o transporte git e o round-trip em sessões ativas funcionam. O modo
portátil básico é manual: mantenedor envia a fruta às sessões. A automação de
despertar é integração opcional por plataforma, a validar separadamente.
