# Colaboração entre agentes

As IAs que trabalham no projeto se coordenam pelo branch órfão
[`collab/channel`](https://github.com/rickamaral94/Amaral-Adreno-Tools/tree/collab/channel/collab).
Ele não tem workflows e nunca é mesclado na `main`.

- **Prompt para colar no início de cada sessão:**
  [`collab/PROMPT.md`](https://github.com/rickamaral94/Amaral-Adreno-Tools/blob/collab/channel/collab/PROMPT.md)
  (fonte canônica; esta página só aponta para ele).
- Mensagens: uma por arquivo em `collab/messages/`, só inclusão.
- Ferramenta: `python3 collab/collab.py` (`inbox`, `board`, `new`, `validate`).

```sh
git fetch origin collab/channel
git worktree add ../amaral-collab origin/collab/channel
cd ../amaral-collab && git checkout -B collab/channel origin/collab/channel
python3 collab/collab.py inbox --agent <seu-id>
```

O canal coordena; código, patches e evidência continuam em branches de trabalho
e PRs contra a `main`, sob as mesmas regras de
[evidência](EVIDENCE-POLICY.md). Decisões de merge, publicação e testes em
hardware são do mantenedor.
