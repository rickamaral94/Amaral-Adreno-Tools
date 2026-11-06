# Fruit Salad Integration

Comandos em português para coordenar ChatGPT/Codex e Claude por git. Python 3.8+
e git 2.31+; sem dependências Python, servidor, conta extra ou credenciais no kit.
Versão **0.1 candidata**. A instalação é local; ativação em outros ambientes
depende de carregar AGENTS.md/CLAUDE.md e dar acesso ao repositório aos agentes.

## Instalar em outro repositório

Copie esta pasta (fruit.py, collab.py e PROTOCOL.md juntos) ou extraia o ZIP.
Na pasta do kit, execute:

```sh
python3 fruit.py init --repo /caminho/do/repositorio --human mantenedor
cd /caminho/do/repositorio
python3 .fruit-salad/fruit.py coco
python3 .fruit-salad/fruit.py salada
```

Use aspas em caminhos com espaços. É necessário um repositório git não bare
com ao menos um commit e identidade git configurada. `init` cria um commit
órfão em `collab/channel`; não altera o índice atual nem faz commit na branch
de código. Instala `.fruit-salad/` e acrescenta blocos delimitados às instruções,
preservando o conteúdo anterior. Repetir a mesma instalação é idempotente.
Arquivos diferentes, links simbólicos ou blocos editados são recusados; não há
atualização destrutiva implícita. Faça uma revisão para upgrades.

Depois de revisar os arquivos, faça commit deles na sua branch de trabalho e
push do canal explicitamente. Não mescle o canal na branch de código. Cada
colaborador clona o repo, busca `collab/channel` e usa o kit instalado; o
primeiro comando cria um worktree do canal sob o diretório git comum. Você pode
usar um worktree do canal já existente. `git worktree list` mostra sua localização.

```sh
git push origin collab/channel
python3 .fruit-salad/fruit.py abacaxi --agent chatgpt --fetch
```

`--channel equipe/canal`, `--remote upstream`, `--human ana` e `--doorbell 12`
personalizam a instalação. `--doorbell` só registra o número, não envia
comentários nem testa o provedor. Identidades de conta/conversa não são copiadas.

Para um canal existente compatível, faça fetch antes e use `init --attach`.
Esse modo preserva engine, roster, histórico e PROMPT existentes; o `--human`
do instalador não altera o roster do canal anexado. Não migre o Amaral copiando
mensagens, PR #34 ou automações para outro projeto.

## Usar na conversa

| Escreva | Resultado esperado na sessão ativa |
| --- | --- |
| `abacaxi revisar o PR 12` | Sincronizar o canal e coordenar esse assunto. |
| `uva` | Ver estado curto, bloqueios e próximo passo. |
| `coco` | Ver o que está instalado e o que falta comprovar. |
| `manga passar a revisão ao Claude` | Preparar handoff com contexto e evidência. |
| `salada` | Ver ajuda dos comandos. |

O CLI fornece leitura e criação local de mensagens. Quem interpreta o texto,
responde, revisa e decide próximos passos é o agente. Não existe interpretação
mágica pelo git, nem sessão que fica acordada por instalar arquivos. Use a fruta
nas duas conversas se não houver integração de despertar testada.

Consulte [PROTOCOL.md](PROTOCOL.md) para envio, fechamentos, leases, validação e
teste E2E. `uva` não publica; `manga` não faz push; `abacaxi` não marca inbox
como lida automaticamente. Comandos sempre mostram se o estado é local.

## Testar e remover

```sh
python3 -m unittest discover -s tests -v
```

Testes usam repositórios temporários e remote bare local. Não dependem de
GitHub nem enviam mensagens. O motor deriva de collab.py do Amaral (origem
c529ef6; snapshot do canal 46749cc4799996679be3b4ed6d62cbc01fc0cc6b), com
papel humano genérico e relatório sem famílias de GPU. A cópia é versionada;
atualizações do canal original não são importadas automaticamente.

Para remover, preserve primeiro o histórico do canal. Retire somente os blocos
entre `fruit-salad:start/end` de AGENTS.md/CLAUDE.md e os arquivos instalados em
`.fruit-salad`. Remova o worktree com git somente quando limpo. Não apague o
branch do canal ou mensagens sem decisão explícita do mantenedor.
