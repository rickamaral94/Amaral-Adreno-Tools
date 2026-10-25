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


def validate(items=None):
    items = load_all() if items is None else items
    known = agents()
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
            row["owner"], row["status"] = m["from"], "reservada"
            row["lease_until"] = created + dt.timedelta(hours=int(m["lease_hours"]))
        elif m["type"] == "status" and m["from"] == row["owner"] and row["lease_until"]:
            hours = int(m.get("lease_hours", "24"))
            row["lease_until"] = max(row["lease_until"], created + dt.timedelta(hours=hours))
        elif m["type"] == "handoff":
            row["owner"] = m["to"].split(",")[0].strip()
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
    for key in ("title", "reply_to", "priority", "verdict", "lease_hours", "needs_human", "refs"):
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
    extra = " ".join(f"{k}={m[k]}" for k in ("title", "priority", "verdict", "reply_to", "lease_hours", "needs_human") if m.get(k))
    print(f"### {m['id']}  {m['from']} -> {m['to']}  [{m['type']}] {m['thread']} {extra}")
    if full:
        print(m["body"])
        print()


def cmd_inbox(a):
    items = load_all()
    seen = seen_ids(a.agent)
    new = [m for m in items if m["id"] not in seen and m["from"] != a.agent
           and (a.agent in [t.strip() for t in m["to"].split(",")] or m["to"] == "all")]
    print(f"{len(new)} mensagem(ns) nova(s) para {a.agent}\n")
    for m in new:
        show(m)
    if items:
        print(f"Depois de ler e responder: collab.py seen --agent {a.agent}")


def cmd_seen(a):
    items = load_all()
    if not items:
        return
    STATE.mkdir(parents=True, exist_ok=True)
    ids = sorted(seen_ids(a.agent) | {m["id"] for m in items})
    cursor_path(a.agent).write_text("\n".join(ids) + "\n", encoding="utf-8")
    print(f"{a.agent}: {len(ids)} mensagens marcadas como lidas")


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
        assert rows[0]["status"] == "reservada" and rows[0]["owner"] == "codex"
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
    MESSAGES = original
    print("selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("--from", dest="sender", required=True)
    n.add_argument("--to", required=True, help="agente, lista separada por vírgula, ou all")
    n.add_argument("--type", required=True)
    n.add_argument("--thread", required=True)
    for key in ("title", "reply-to", "priority", "verdict", "lease-hours", "needs-human", "refs", "body"):
        n.add_argument(f"--{key}", dest=key.replace("-", "_"))
    for name in ("inbox", "seen"):
        s = sub.add_parser(name)
        s.add_argument("--agent", required=True)
    sub.add_parser("board")
    t = sub.add_parser("thread")
    t.add_argument("thread")
    sub.add_parser("validate")
    sub.add_parser("selftest")
    a = p.parse_args()
    {"new": cmd_new, "inbox": cmd_inbox, "seen": cmd_seen, "board": cmd_board,
     "thread": cmd_thread, "validate": cmd_validate, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    main()
