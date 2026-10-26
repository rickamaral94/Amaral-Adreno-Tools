#!/usr/bin/env python3
"""Canal de colaboração entre agentes do Amaral Adreno Tools.

Somente biblioteca padrão (Python 3.8+). O canal é só de inclusão: cada
mensagem é um arquivo novo em collab/messages/, nunca editado depois. O estado
das tarefas (quem trabalha em quê, o que está bloqueado) é calculado a partir
das mensagens, então duas IAs escrevendo ao mesmo tempo nunca geram conflito.

Uso rápido:
  python3 collab/collab.py inbox --agent claude          # o que há de novo
  python3 collab/collab.py board                         # quadro de tarefas
  python3 collab/collab.py thread T-a840-pixelation      # conversa completa
  python3 collab/collab.py new --from claude --to codex --type answer \
      --thread T-a840-pixelation --reply-to <id> --title "..." < corpo.md
  python3 collab/collab.py seen --agent claude           # marca como lido
  python3 collab/collab.py validate                      # antes de todo push
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import secrets
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
MESSAGES = ROOT / "messages"
STATE = ROOT / "state"
AGENTS = ROOT / "agents.json"

TYPES = {
    "hello": "apresentação, capacidades e limites do agente",
    "task": "abre uma thread de trabalho (title obrigatório)",
    "claim": "reserva a thread por lease_hours; outro agente não duplica o trabalho",
    "status": "progresso; renova o lease se o autor for o dono",
    "finding": "fato verificado com evidência (arquivo, hash, commit, log)",
    "proposal": "plano ou patch proposto, aguardando revisão",
    "question": "pergunta para o outro agente",
    "answer": "resposta a uma question (reply_to obrigatório)",
    "review": "revisão de proposta/commit/PR (verdict obrigatório)",
    "handoff": "entrega a thread com todo o contexto para outro agente continuar",
    "release": "libera a reserva sem concluir",
    "blocked": "thread parada por dependência externa",
    "decision-request": "precisa de decisão humana (Rick); needs_human: yes",
    "decision": "decisão humana; somente from: rick",
    "done": "conclui a thread com resultado e links",
    "sync": "resumo padronizado após a palavra SYNC-AMARAL (thread T-sync, ver PROMPT §3.3)",
}
REQUIRED = ("id", "from", "to", "type", "thread", "created")
VERDICTS = {"approve", "changes", "reject"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
ID_RE = re.compile(r"\d{8}T\d{9}Z-[a-z0-9]+-[0-9a-f]{4}\Z")
THREAD_RE = re.compile(r"T-[a-z0-9][a-z0-9.-]{2,60}\Z")


def utcnow():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def new_id(agent):
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%S") + f"{now.microsecond // 1000:03d}Z"
    return f"{stamp}-{agent}-{secrets.token_hex(2)}"


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value):
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def agents():
    return json.loads(AGENTS.read_text(encoding="utf-8"))["agents"]


def names():
    """Mapa nome-ou-apelido -> id canônico (apelidos evitam quebrar mensagens antigas)."""
    out = {}
    for agent_id, info in agents().items():
        out[agent_id] = agent_id
        for alias in info.get("aliases", []):
            out[alias] = agent_id
    return out


def detect_agent():
    """Id do agente atual sem o Rick precisar escolher: COLLAB_AGENT, depois marcadores do ambiente."""
    import os
    forced = os.environ.get("COLLAB_AGENT", "").strip()
    if forced:
        return canonical(forced)
    if os.environ.get("CLAUDECODE") or any(k.startswith("CLAUDE_CODE_") for k in os.environ):
        return "claude"
    if any(k.startswith("CODEX") for k in os.environ):
        return "chatgpt"
    sys.exit("não consegui detectar o agente: defina COLLAB_AGENT=<id> ou passe --agent/--from "
             "(Claude da Anthropic = claude; ChatGPT/Codex da OpenAI = chatgpt)")


def resolve(name):
    return detect_agent() if not name or name == "auto" else canonical(name)


def canonical(name):
    return names().get(name.strip(), name.strip())


def parse(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name}: cabeçalho deve começar com ---")
    head, sep, body = text[4:].partition("\n---\n")
    if not sep:
        raise ValueError(f"{path.name}: cabeçalho sem --- de fechamento")
    meta = {}
    for line in head.splitlines():
        if not line.strip():
            continue
        key, colon, value = line.partition(":")
        if not colon:
            raise ValueError(f"{path.name}: linha inválida no cabeçalho: {line!r}")
        meta[key.strip()] = value.strip()
    meta["body"] = body.strip()
    meta["path"] = path
    return meta


def load_all():
    if not MESSAGES.is_dir():
        return []
    items = [parse(p) for p in sorted(MESSAGES.glob("*.md"))]
    return sorted(items, key=lambda m: (m.get("created", ""), m.get("id", "")))


def closes(m):
    """Ids que a mensagem fecha além do reply_to (campo closes: a,b,c)."""
    return [c.strip() for c in m.get("closes", "").split(",") if c.strip()]


def validate(items=None):
    items = load_all() if items is None else items
    known = names()
    errors, ids, threads = [], set(), {}
    # A validação não depende da ordem: relógios de agentes diferentes divergem.
    all_ids = {m.get("id") for m in items}
    opened = {m.get("thread") for m in items if m.get("type") == "task"}
    for m in items:
        name = m["path"].name
        missing = [k for k in REQUIRED if not m.get(k)]
        if missing:
            errors.append(f"{name}: faltando {missing}")
            continue
        if not ID_RE.fullmatch(m["id"]) or name != m["id"] + ".md":
            errors.append(f"{name}: id inválido ou diferente do nome do arquivo")
        if m["id"] in ids:
            errors.append(f"{name}: id duplicado")
        ids.add(m["id"])
        if m["from"] not in known:
            errors.append(f"{name}: from '{m['from']}' não está em agents.json")
        for target in m["to"].split(","):
            if target.strip() not in known and target.strip() != "all":
                errors.append(f"{name}: destinatário desconhecido '{target}'")
        if m["type"] not in TYPES:
            errors.append(f"{name}: type '{m['type']}' inválido")
        if not THREAD_RE.fullmatch(m["thread"]):
            errors.append(f"{name}: thread '{m['thread']}' inválida (use T-slug-curto)")
        try:
            parse_time(m["created"])
        except ValueError:
            errors.append(f"{name}: created deve ser AAAA-MM-DDTHH:MM:SSZ")
        if m["type"] == "task":
            if m["thread"] in threads:
                errors.append(f"{name}: thread {m['thread']} já foi aberta")
            if not m.get("title"):
                errors.append(f"{name}: task exige title")
            threads[m["thread"]] = m
        elif m["type"] not in {"hello", "decision"} and m["thread"] not in opened:
            errors.append(f"{name}: thread {m['thread']} não foi aberta por um task")
        if m["type"] == "answer" and not m.get("reply_to"):
            errors.append(f"{name}: answer exige reply_to")
        if m.get("reply_to") and m["reply_to"] not in all_ids:
            errors.append(f"{name}: reply_to {m['reply_to']} não existe no canal")
        for closed in closes(m):
            if closed not in all_ids:
                errors.append(f"{name}: closes {closed} não existe no canal")
        if m["type"] == "review" and m.get("verdict") not in VERDICTS:
            errors.append(f"{name}: review exige verdict approve|changes|reject")
        if m["type"] == "claim":
            try:
                if not 1 <= int(m.get("lease_hours", "0")) <= 168:
                    raise ValueError
            except ValueError:
                errors.append(f"{name}: claim exige lease_hours entre 1 e 168")
        if m["type"] == "decision" and m["from"] != "rick":
            errors.append(f"{name}: somente rick emite decision")
        if m["type"] == "decision-request" and m.get("needs_human") != "yes":
            errors.append(f"{name}: decision-request exige needs_human: yes")
        if m.get("priority") and m["priority"] not in PRIORITIES:
            errors.append(f"{name}: priority deve ser P0..P3")
        if not m["body"]:
            errors.append(f"{name}: corpo vazio")
    return errors


def board(items, now=None):
    now = now or utcnow()
    rows = {}
    for m in items:
        t = m["thread"]
        if m["type"] == "task":
            rows[t] = {"thread": t, "title": m.get("title", ""), "priority": m.get("priority", "-"),
                       "status": "aberta", "owner": "-", "lease_until": None,
                       "needs_human": False, "last": m["id"], "last_from": m["from"]}
            continue
        row = rows.get(t)
        if row is None:
            continue
        row["last"], row["last_from"] = m["id"], m["from"]
        created = parse_time(m["created"])
        if m["type"] == "claim":
            row["owner"], row["status"] = canonical(m["from"]), "reservada"
            row["lease_until"] = created + dt.timedelta(hours=int(m["lease_hours"]))
        elif m["type"] == "status" and canonical(m["from"]) == row["owner"] and row["lease_until"]:
            hours = int(m.get("lease_hours", "24"))
            row["lease_until"] = max(row["lease_until"], created + dt.timedelta(hours=hours))
        elif m["type"] == "handoff":
            row["owner"] = canonical(m["to"].split(",")[0])
            row["status"], row["lease_until"] = "entregue", created + dt.timedelta(hours=72)
        elif m["type"] == "release":
            row["owner"], row["status"], row["lease_until"] = "-", "aberta", None
        elif m["type"] == "blocked":
            row["status"] = "bloqueada"
        elif m["type"] == "decision-request":
            row["needs_human"], row["status"] = True, "aguarda Rick"
        elif m["type"] == "decision":
            row["needs_human"] = False
            if row["status"] == "aguarda Rick":
                row["status"] = "reservada" if row["owner"] != "-" else "aberta"
        elif m["type"] == "done":
            row["status"], row["lease_until"] = "concluída", None
    for row in rows.values():
        if row["lease_until"] and row["lease_until"] < now and row["status"] in {"reservada", "entregue"}:
            row["status"] = "lease vencido"
    return list(rows.values())


SHOWN_DIR = ROOT.parent / ".collab-cache"


def shown_path(agent):
    return SHOWN_DIR / f"{agent}.shown"


def cursor_path(agent):
    return STATE / f"{agent}.seen"


def seen_ids(agent):
    # Conjunto de ids lidos, não um máximo: o relógio atrasado de outro agente
    # não pode esconder mensagens atrás do cursor.
    path = cursor_path(agent)
    if not path.is_file():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def cmd_new(a):
    if a.type not in TYPES:
        sys.exit(f"type inválido; opções: {', '.join(TYPES)}")
    body = sys.stdin.read().strip() if not a.body else a.body.strip()
    if not body:
        sys.exit("corpo vazio: passe --body ou envie pelo stdin")
    now = utcnow()
    mid = new_id(a.sender)
    head = {"id": mid, "from": a.sender, "to": a.to, "type": a.type, "thread": a.thread,
            "created": iso(now)}
    for key in ("title", "reply_to", "closes", "priority", "verdict", "lease_hours", "needs_human", "refs"):
        value = getattr(a, key)
        if value:
            head[key] = value
    lines = ["---"] + [f"{k}: {v}" for k, v in head.items()] + ["---", "", body, ""]
    MESSAGES.mkdir(parents=True, exist_ok=True)
    path = MESSAGES / f"{mid}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    errors = [e for e in validate() if e.startswith(path.name)]
    if errors:
        path.unlink()
        sys.exit("mensagem recusada:\n  " + "\n  ".join(errors))
    print(path.relative_to(ROOT.parent))


def show(m, full=True):
    extra = " ".join(f"{k}={m[k]}" for k in ("title", "priority", "verdict", "reply_to", "closes", "lease_hours", "needs_human") if m.get(k))
    print(f"### {m['id']}  {m['from']} -> {m['to']}  [{m['type']}] {m['thread']} {extra}")
    if full:
        print(m["body"])
        print()


def cmd_inbox(a):
    items = load_all()
    me = canonical(a.agent)
    seen = seen_ids(me)
    new = [m for m in items if m["id"] not in seen and canonical(m["from"]) != me
           and (me in [canonical(t) for t in m["to"].split(",")] or m["to"] == "all")]
    print(f"{len(new)} mensagem(ns) nova(s) para {a.agent}\n")
    for m in new:
        show(m)
    # Registra fora de collab/ (não versionado) o que foi mostrado: o `seen`
    # só marca isso, e uma mensagem que chegue entre inbox e seen continua nova.
    SHOWN_DIR.mkdir(parents=True, exist_ok=True)
    shown = shown_path(me)
    previous = set(shown.read_text(encoding="utf-8").split()) if shown.is_file() else set()
    shown.write_text("\n".join(sorted(previous | {m["id"] for m in new})) + "\n", encoding="utf-8")
    if items:
        print(f"Depois de ler e responder: collab.py seen --agent {a.agent}")


def cmd_seen(a):
    items = load_all()
    if not items:
        return
    STATE.mkdir(parents=True, exist_ok=True)
    me = canonical(a.agent)
    shown = shown_path(me)
    shown_ids = set(shown.read_text(encoding="utf-8").split()) if shown.is_file() else set()
    def addressed(m):
        return me in [canonical(x) for x in m["to"].split(",")] or m["to"] == "all"
    # Marca só: o que o inbox mostrou, as próprias mensagens e as que não são
    # para este agente. Mensagem para ele ainda não mostrada continua pendente.
    marked = {m["id"] for m in items
              if m["id"] in shown_ids or canonical(m["from"]) == me or not addressed(m)}
    pending = [m["id"] for m in items if addressed(m) and canonical(m["from"]) != me
               and m["id"] not in marked and m["id"] not in seen_ids(me)]
    ids = sorted(seen_ids(me) | marked)
    cursor_path(me).write_text("\n".join(ids) + "\n", encoding="utf-8")
    print(f"{me}: {len(ids)} mensagens marcadas como lidas")
    if pending:
        print(f"ATENÇÃO: {len(pending)} mensagem(ns) para você ainda não mostrada(s); rode inbox: {', '.join(pending)}")


REQUESTS = {"question", "proposal", "review", "handoff", "task", "decision-request"}


def pending(items, rows, me):
    """Pedidos ainda sem resposta, nos dois sentidos, como pares (mensagem, indício).

    Só fecha um pedido o reply_to (ou o campo closes) vindo de um destinatário
    dele, ou a thread concluída. Mensagem posterior de um destinatário na mesma thread, sem
    reply_to, vira apenas o indício "possivelmente tratado": a ordem depende de
    relógios que divergem e o assunto pode ser outro, então nunca esconde nada.
    """
    closed = {r["thread"] for r in rows if r["status"] == "concluída"}
    everyone = set(names().values())
    def recipients(m):
        if m["to"] == "all":
            return everyone - {canonical(m["from"])}
        return {canonical(t) for t in m["to"].split(",")}
    def status(i, m):
        to = recipients(m)
        if any((x.get("reply_to") == m["id"] or m["id"] in closes(x)) and canonical(x["from"]) in to
               for x in items):
            return None
        return any(j > i and x["thread"] == m["thread"] and canonical(x["from"]) in to
                   for j, x in enumerate(items))
    waiting_me, waiting_other = [], []
    for i, m in enumerate(items):
        if m["type"] not in REQUESTS or m["thread"] in closed:
            continue
        mine = canonical(m["from"]) == me
        if not mine and me not in recipients(m):
            continue
        hint = status(i, m)
        if hint is not None:
            (waiting_other if mine else waiting_me).append((m, hint))
    return waiting_me, waiting_other


def rick_queue(items):
    """Pedidos com needs_human ainda abertos: testes em hardware, decisões.

    Fecha quando o Rick responde (reply_to ou closes) ou quando o próprio autor
    lista o pedido em closes (resultado chegou por outro meio ou foi retirado).
    """
    out = []
    for m in items:
        if canonical(m["from"]) == "rick" or m.get("needs_human") not in {"yes", "true"}:
            continue
        done = any((x.get("reply_to") == m["id"] and canonical(x["from"]) == "rick")
                   or (m["type"] == "decision-request" and x["type"] == "decision"
                       and x["thread"] == m["thread"] and x["created"] >= m["created"])
                   or (m["id"] in closes(x) and canonical(x["from"]) in {"rick", canonical(m["from"])})
                   for x in items)
        if not done:
            out.append(m)
    return out


def sync_pending_lines(pairs, recent_ids, show_all=False):
    """Mostra pedidos novos por extenso e preserva os IDs antigos em aberto."""
    def detail(pair):
        m, hint = pair
        mark = " (possivelmente tratado)" if hint else ""
        return f"- {m['thread']} `{m['id']}` [{m['type']}] {(m.get('title') or m['body'].splitlines()[0])[:90]}{mark}"

    if show_all:
        return [detail(pair) for pair in pairs] or ["- nada"]
    recent = [pair for pair in pairs if pair[0]["id"] in recent_ids]
    older = [pair for pair in pairs if pair[0]["id"] not in recent_ids]
    lines = [detail(pair) for pair in recent]
    if older:
        ids = ", ".join(f"`{m['id']}`" for m, _ in older)
        lines.append(f"- {len(older)} pendência(s) anterior(es) ainda aberta(s): {ids} (detalhes: sync-report --all)")
    return lines or ["- nada"]


def cmd_sync_report(a):
    """Rascunho do corpo da mensagem sync: o mesmo formato para todos os agentes."""
    me = canonical(a.agent)
    items = load_all()
    rows = board(items)
    mine = [r for r in rows if r["owner"] == me and r["status"] in {"reservada", "entregue", "lease vencido"}]
    waiting_me, waiting_other = pending(items, rows, me)
    last_sync = [m for m in items if m["type"] == "sync" and canonical(m["from"]) != me]
    own_sync = [i for i, m in enumerate(items) if m["type"] == "sync" and canonical(m["from"]) == me]
    # A ordem é por horário do canal; relógios diferentes podem deslocar uma
    # mensagem para a seção anterior, mas seu ID nunca desaparece do relatório.
    recent_ids = {m["id"] for m in items[own_sync[-1] + 1:]} if own_sync else {m["id"] for m in items}
    out = ["SYNC-AMARAL", "", f"Agente: {me}. Canal: {len(items)} mensagens.", "",
           "## Estado das frentes (delta desde o último sync; diga sem mudança se aplicável)",
           "- [A7xx-trava]: ", "- [A8xx-compat]: ", "- Outras: ", "",
           "## Em andamento comigo (leases)"]
    out += [f"- {r['thread']}: {r['status']}" + (f" até {iso(r['lease_until'])}" if r["lease_until"] else "") for r in mine] or ["- nada"]
    out += ["", "## Aguardando a minha resposta"] + sync_pending_lines(waiting_me, recent_ids, a.all)
    out += ["", "## Aguardando o outro agente"] + sync_pending_lines(waiting_other, recent_ids, a.all)
    rick = [f"- {m['thread']} `{m['id']}` [{m['type']}] {(m.get('title') or m['body'].splitlines()[0])[:90]}"
            for m in rick_queue(items)]
    out += ["", "## Aguardando o Rick"] + (rick or ["- nada (incluir pedidos de teste em hardware)"])
    out += ["", "## Proposta de próximos passos (quem faz o quê)", "- ", "",
            "## Último sync do outro agente", (f"- `{last_sync[-1]['id']}`" if last_sync else "- nenhum")]
    print("\n".join(out))


def cmd_board(_):
    rows = board(load_all())
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "-": 4}
    rows.sort(key=lambda r: (r["status"] == "concluída", order.get(r["priority"], 4), r["thread"]))
    print(f"{'thread':34} {'pri':3} {'status':14} {'dono':8} {'lease até':20} última")
    for r in rows:
        lease = iso(r["lease_until"]) if r["lease_until"] else "-"
        human = " [Rick]" if r["needs_human"] else ""
        print(f"{r['thread']:34} {r['priority']:3} {r['status']:14} {r['owner']:8} {lease:20} {r['last_from']}{human}")
        print(f"{'':34} {r['title']}")


def cmd_thread(a):
    for m in load_all():
        if m["thread"] == a.thread:
            show(m)


def git_lines(*args):
    out = subprocess.run(["git", "-C", str(ROOT.parent), *args], check=True,
                         capture_output=True, text=True).stdout
    return [line for line in out.splitlines() if line]


def git_blob(ref, path):
    return subprocess.run(["git", "-C", str(ROOT.parent), "show", f"{ref}:{path}"],
                          check=True, capture_output=True).stdout


def cmd_import(a):
    """Traz mensagens de outro ref (PR de um agente sem push no canal), byte a byte."""
    ref = a.ref
    try:
        files = git_lines("ls-tree", "-r", "--name-only", ref, "--", "collab/messages", "collab/state")
    except subprocess.CalledProcessError as error:
        sys.exit(f"ref inválido ou ausente: {ref} ({error.stderr.strip()})")
    written, conflicts, merged = [], [], []
    for rel in files:
        dest = ROOT.parent / rel
        data = git_blob(ref, rel)
        if rel.startswith("collab/messages/") and rel.endswith(".md"):
            if dest.exists():
                if dest.read_bytes() != data:
                    conflicts.append(rel)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            written.append(dest)
        elif rel.startswith("collab/state/") and rel.endswith(".seen"):
            agent = pathlib.Path(rel).stem
            if canonical(agent) == canonical(a.importer):
                continue  # o cursor de quem importa é só dele
            theirs = {l.strip() for l in data.decode().splitlines() if l.strip()}
            ours = seen_ids(canonical(agent))
            if not theirs <= ours:
                STATE.mkdir(parents=True, exist_ok=True)
                cursor_path(canonical(agent)).write_text("\n".join(sorted(ours | theirs)) + "\n", encoding="utf-8")
                merged.append(rel)
    if conflicts:
        for dest in written:
            dest.unlink()
        sys.exit("importação recusada: o ref altera mensagens existentes (só inclusão):\n  " + "\n  ".join(conflicts))
    errors = validate()
    bad = [e for e in errors if any(e.startswith(d.name) for d in written)]
    if bad:
        for dest in written:
            dest.unlink()
        sys.exit("importação recusada, mensagens inválidas:\n  " + "\n  ".join(bad))
    imported = [load_one for load_one in (parse(d) for d in written)]
    senders = sorted({canonical(m["from"]) for m in imported})
    if canonical(a.importer) in senders:
        for dest in written:
            dest.unlink()
        sys.exit("importação recusada: o ref contém mensagens com o seu próprio id; publique-as você mesmo")
    commit = git_lines("rev-parse", ref)[0]
    print(f"importadas {len(written)} mensagens de {', '.join(senders) or '-'}; cursores atualizados: {len(merged)}")
    print(f"origem: {a.source or ref} @ {commit}")
    print(f'commit sugerido: git add collab && git commit -m "collab: import {len(written)} msg de {a.source or ref} @ {commit[:12]} ({a.importer})"')


def cmd_validate(_):
    errors = validate()
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"Canal válido: {len(load_all())} mensagens.")


def cmd_selftest(_):
    import tempfile
    global MESSAGES
    original = MESSAGES
    with tempfile.TemporaryDirectory() as tmp:
        MESSAGES = pathlib.Path(tmp)
        def put(mid, extra, body="x"):
            meta = "\n".join(f"{k}: {v}" for k, v in extra.items())
            (MESSAGES / f"{mid}.md").write_text(f"---\nid: {mid}\n{meta}\n---\n{body}\n")
        put("20260101T000000000Z-claude-0001", {"from": "claude", "to": "all", "type": "task",
            "thread": "T-test", "title": "t", "created": "2026-01-01T00:00:00Z"})
        put("20260101T000100000Z-codex-0002", {"from": "codex", "to": "claude", "type": "claim",
            "thread": "T-test", "lease_hours": "2", "created": "2026-01-01T00:01:00Z"})
        assert validate() == [], validate()
        rows = board(load_all(), now=parse_time("2026-01-01T01:00:00Z"))
        assert rows[0]["status"] == "reservada" and rows[0]["owner"] == "chatgpt"
        rows = board(load_all(), now=parse_time("2026-01-01T05:00:00Z"))
        assert rows[0]["status"] == "lease vencido"
        put("20260101T000200000Z-codex-0003", {"from": "codex", "to": "claude", "type": "decision",
            "thread": "T-test", "created": "2026-01-01T00:02:00Z"})
        assert any("somente rick" in e for e in validate())
        (MESSAGES / "20260101T000200000Z-codex-0003.md").unlink()
        # Relógio do outro agente atrasado: a resposta tem horário anterior à
        # pergunta e ainda assim valida e aparece no inbox.
        put("20251231T235900000Z-codex-0004", {"from": "codex", "to": "claude", "type": "answer",
            "thread": "T-test", "reply_to": "20260101T000000000Z-claude-0001",
            "created": "2025-12-31T23:59:00Z"})
        assert validate() == [], validate()
        assert "20251231T235900000Z-codex-0004" not in seen_ids("claude-selftest")
        # Apelido: mensagem para "codex" chega ao id canônico "chatgpt".
        assert canonical("codex") == "chatgpt" and canonical("chatgpt") == "chatgpt"
        rows = board(load_all(), now=parse_time("2026-01-01T01:00:00Z"))
        assert rows[0]["owner"] == "chatgpt", rows[0]
        # sync-report: só reply_to de um destinatário fecha um pedido; atividade
        # posterior sem referência é indício e nunca remove (review do chatgpt).
        def ids(pairs):
            return {m["id"]: hint for m, hint in pairs}
        put("20260101T000300000Z-codex-0005", {"from": "codex", "to": "claude", "type": "review",
            "thread": "T-test", "verdict": "approve", "created": "2026-01-01T00:03:00Z"})
        put("20260101T000400000Z-claude-0006", {"from": "claude", "to": "chatgpt", "type": "status",
            "thread": "T-test", "created": "2026-01-01T00:04:00Z"})
        items = load_all()
        me_wait, other_wait = pending(items, board(items), "claude")
        assert ids(me_wait) == {"20260101T000300000Z-codex-0005": True}, me_wait
        assert other_wait == [], other_wait  # a task 0001 foi respondida com reply_to em 0004
        # Pergunta seguida de status do destinatário sobre outro assunto continua pendente.
        put("20260101T000500000Z-claude-0007", {"from": "claude", "to": "chatgpt", "type": "question",
            "thread": "T-test", "created": "2026-01-01T00:05:00Z"})
        put("20260101T000600000Z-codex-0008", {"from": "codex", "to": "claude", "type": "status",
            "thread": "T-test", "created": "2026-01-01T00:06:00Z"})
        # Pergunta ao Rick não fecha com mensagem de quem não é destinatário.
        put("20260101T000700000Z-codex-0009", {"from": "codex", "to": "rick", "type": "question",
            "thread": "T-test", "created": "2026-01-01T00:07:00Z"})
        put("20260101T000800000Z-claude-0010", {"from": "claude", "to": "all", "type": "status",
            "thread": "T-test", "created": "2026-01-01T00:08:00Z"})
        # Relógio adiantado: status escrito antes, com horário depois da pergunta.
        put("20260101T000900000Z-claude-0011", {"from": "claude", "to": "chatgpt", "type": "question",
            "thread": "T-test", "created": "2026-01-01T00:09:00Z"})
        put("20270101T000000000Z-codex-0012", {"from": "codex", "to": "claude", "type": "status",
            "thread": "T-test", "created": "2027-01-01T00:00:00Z"})
        items = load_all()
        _, other_wait = pending(items, board(items), "claude")
        assert ids(other_wait) == {"20260101T000500000Z-claude-0007": True,
                                   "20260101T000900000Z-claude-0011": True}, other_wait
        _, other_wait = pending(items, board(items), "chatgpt")
        assert ids(other_wait) == {"20260101T000300000Z-codex-0005": True,
                                   "20260101T000700000Z-codex-0009": False}, other_wait
        # Resposta com reply_to do destinatário fecha; a de um terceiro, não.
        put("20260101T001000000Z-claude-0013", {"from": "claude", "to": "rick", "type": "answer",
            "thread": "T-test", "reply_to": "20260101T000700000Z-codex-0009", "created": "2026-01-01T00:10:00Z"})
        put("20260101T001100000Z-codex-0014", {"from": "codex", "to": "claude", "type": "answer",
            "thread": "T-test", "reply_to": "20260101T000500000Z-claude-0007", "created": "2026-01-01T00:11:00Z"})
        assert validate() == [], validate()
        items = load_all()
        _, other_wait = pending(items, board(items), "chatgpt")
        assert "20260101T000700000Z-codex-0009" in ids(other_wait), other_wait
        _, other_wait = pending(items, board(items), "claude")
        assert "20260101T000500000Z-claude-0007" not in ids(other_wait), other_wait
        # closes: fecha vários pedidos numa mensagem só, sem uma resposta por item.
        put("20260101T001200000Z-codex-0015", {"from": "codex", "to": "claude", "type": "proposal",
            "thread": "T-test", "created": "2026-01-01T00:12:00Z"})
        put("20260101T001300000Z-claude-0016", {"from": "claude", "to": "chatgpt", "type": "status",
            "thread": "T-test", "closes": "20260101T000300000Z-codex-0005,20260101T001200000Z-codex-0015",
            "created": "2026-01-01T00:13:00Z"})
        assert validate() == [], validate()
        items = load_all()
        me_wait, _ = pending(items, board(items), "claude")
        assert not {"20260101T000300000Z-codex-0005", "20260101T001200000Z-codex-0015"} & set(ids(me_wait)), me_wait
        put("20260101T001400000Z-claude-0017", {"from": "claude", "to": "chatgpt", "type": "status",
            "thread": "T-test", "closes": "20260101T000000000Z-nobody-0000", "created": "2026-01-01T00:14:00Z"})
        assert any("closes 20260101T000000000Z-nobody-0000" in e for e in validate())
        (MESSAGES / "20260101T001400000Z-claude-0017.md").unlink()
        # Fila do Rick: qualquer needs_human conta, não só decision-request.
        put("20260101T001500000Z-claude-0018", {"from": "claude", "to": "rick", "type": "status",
            "thread": "T-test", "needs_human": "true", "created": "2026-01-01T00:15:00Z"})
        assert [m["id"] for m in rick_queue(load_all())] == ["20260101T001500000Z-claude-0018"]
        # Resposta de outro agente não fecha; closes do próprio autor fecha.
        put("20260101T001600000Z-codex-0019", {"from": "codex", "to": "claude", "type": "answer",
            "thread": "T-test", "reply_to": "20260101T001500000Z-claude-0018", "created": "2026-01-01T00:16:00Z"})
        assert len(rick_queue(load_all())) == 1
        put("20260101T001700000Z-claude-0020", {"from": "claude", "to": "all", "type": "status",
            "thread": "T-test", "closes": "20260101T001500000Z-claude-0018", "created": "2026-01-01T00:17:00Z"})
        assert rick_queue(load_all()) == []
        # Sync incremental não esconde pedidos antigos ainda abertos.
        older = ({"id": "old", "thread": "T-test", "type": "question", "body": "antigo"}, True)
        recent = ({"id": "new", "thread": "T-test", "type": "proposal", "body": "novo"}, False)
        short = sync_pending_lines([older, recent], {"new"})
        assert "new" in short[0] and "old" in short[1] and "antigo" not in short[1], short
        full = sync_pending_lines([older, recent], {"new"}, show_all=True)
        assert "antigo" in full[0] and "novo" in full[1], full
    MESSAGES = original
    print("selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("--from", dest="sender", default="auto", help="id do agente; padrão: detectado")
    n.add_argument("--to", required=True, help="agente, lista separada por vírgula, ou all")
    n.add_argument("--type", required=True)
    n.add_argument("--thread", required=True)
    for key in ("title", "reply-to", "closes", "priority", "verdict", "lease-hours", "needs-human", "refs", "body"):
        n.add_argument(f"--{key}", dest=key.replace("-", "_"))
    for name in ("inbox", "seen"):
        s = sub.add_parser(name)
        s.add_argument("--agent", default="auto", help="id do agente; padrão: detectado")
    sub.add_parser("board")
    sr = sub.add_parser("sync-report")
    sr.add_argument("--agent", default="auto", help="id do agente; padrão: detectado")
    sr.add_argument("--all", action="store_true", help="mostrar todas as pendências abertas por extenso")
    t = sub.add_parser("thread")
    t.add_argument("thread")
    sub.add_parser("validate")
    sub.add_parser("whoami")
    im = sub.add_parser("import")
    im.add_argument("ref", help="ref git com as mensagens, ex.: origin/pr/28 ou FETCH_HEAD")
    im.add_argument("--importer", default="auto", help="seu id; padrão: detectado")
    im.add_argument("--source", help="descrição da origem, ex.: 'PR #28'")
    sub.add_parser("selftest")
    a = p.parse_args()
    for attr in ("sender", "agent", "importer"):
        if hasattr(a, attr):
            setattr(a, attr, resolve(getattr(a, attr)))
    {"new": cmd_new, "inbox": cmd_inbox, "seen": cmd_seen, "board": cmd_board, "sync-report": cmd_sync_report,
     "thread": cmd_thread, "validate": cmd_validate, "whoami": lambda _: print(detect_agent()), "import": cmd_import, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.stderr.close()  # saída cortada por head/less: não é erro
