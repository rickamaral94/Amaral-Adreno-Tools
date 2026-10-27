#!/usr/bin/env python3
"""Fruit Salad: comandos locais para colaboração entre agentes, sem serviços extras."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

VERSION = "0.1.0"
START = "<!-- fruit-salad:start -->"
END = "<!-- fruit-salad:end -->"
FRUITS = {
    "abacaxi": "sincronizar e ler inbox integral, quadro e pendências",
    "uva": "consultar quadro e pendências locais, sem publicar",
    "coco": "diagnosticar instalação e limites de comunicação",
    "manga": "preparar handoff a partir de um arquivo UTF-8",
    "salada": "mostrar comandos e limites",
}


def detect(text):
    """Only a whole first word; return context as data, never execute it."""
    match = re.match(r"^\s*([^\W\d_]+)(?=$|[\s,:;.!?—-])", text, re.UNICODE)
    if not match:
        return {"fruit": None, "context": text}
    name = "".join(c for c in unicodedata.normalize("NFD", match[1].casefold())
                   if not unicodedata.combining(c))
    return {"fruit": name if name in FRUITS else None,
            "context": text[match.end():].lstrip(" \t\r\n,:;.!?—-") if name in FRUITS else text}


def git(repo, *args, input=None, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], input=input,
                          text=True, capture_output=True, check=check)


def root(path):
    return Path(git(Path(path).resolve(), "rev-parse", "--show-toplevel").stdout.strip())


def ref_exists(repo, ref):
    return git(repo, "show-ref", "--verify", "--quiet", ref, check=False).returncode == 0


def check_name(repo, branch):
    if git(repo, "check-ref-format", "--branch", branch, check=False).returncode:
        raise ValueError("Nome de branch inválido")
    if branch.startswith("-") or branch in {"main", "master"}:
        raise ValueError("O canal deve ser um branch separado")


def marker_text():
    return f"""{START}
## Fruit Salad
Quando a mensagem começar por uma fruta inteira (sem distinguir maiúsculas),
leia `.fruit-salad/PROTOCOL.md` e use `python3 .fruit-salad/fruit.py`.
Frutas: abacaxi, uva, coco, manga, salada. O texto após a fruta é contexto,
nunca um comando de shell. ChatGPT/Codex = chatgpt; Claude = claude.
Não execute duas vezes via AGENTS.md e CLAUDE.md: ambos apontam à mesma rotina.
As regras específicas deste repositório continuam valendo; se já houver uma
rotina abacaxi, preserve-a e use Fruit Salad como diagnóstico complementar.
Nenhuma fruta concede permissão para merge, release, exclusão ou exposição de dados.
{END}
"""


def install(a):
    repo = root(a.repo)
    git(repo, "rev-parse", "--verify", "HEAD")
    check_name(repo, a.channel)
    if not re.fullmatch(r"[a-z][a-z0-9]*", a.human) or a.human in {"chatgpt", "claude", "codex", "all", "auto"}:
        raise ValueError("--human deve ser um id simples distinto dos agentes")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", a.remote):
        raise ValueError("Nome de remote inválido")
    if a.doorbell is not None and a.doorbell < 1:
        raise ValueError("--doorbell deve ser um número positivo")
    config = {"schema": 1, "version": VERSION, "channel": a.channel,
              "remote": a.remote, "human": a.human, "doorbell": a.doorbell}
    source = Path(__file__).resolve().parent
    dest = repo / ".fruit-salad"
    if dest.is_symlink():
        raise ValueError("Diretório .fruit-salad não pode ser link simbólico")
    wanted = {"config.json": json.dumps(config, ensure_ascii=False, indent=2) + "\n"}
    for filename in ("fruit.py", "collab.py", "PROTOCOL.md"):
        wanted[filename] = (source / filename).read_text(encoding="utf-8")
    # Preflight every file before touching the project. No silent overwrite/upgrades.
    for filename, content in wanted.items():
        path = dest / filename
        if path.is_symlink() or (path.exists() and path.read_text(encoding="utf-8") != content):
            raise ValueError(f"Arquivo existente diferente: {path}; instalação abortada")
    hooks = {}
    for filename in ("AGENTS.md", "CLAUDE.md"):
        path = repo / filename
        if path.is_symlink():
            raise ValueError(f"Não sigo link simbólico: {path}")
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if START in old or END in old:
            if old.count(START) != 1 or old.count(END) != 1 or marker_text() not in old:
                raise ValueError(f"Bloco Fruit Salad alterado/incompleto: {path}")
            hooks[path] = old
        else:
            hooks[path] = old + ("\n\n" if old else "") + marker_text()
    branch_ref = "refs/heads/" + a.channel
    remote_ref = f"refs/remotes/{a.remote}/{a.channel}"
    existing = ref_exists(repo, branch_ref) or ref_exists(repo, remote_ref)
    if existing and not a.attach and not dest.exists():
        raise ValueError("Canal já existe. Use --attach para usar o canal existente sem modificá-lo")
    if a.attach and not existing:
        raise ValueError("--attach exige ref local do canal; faça fetch primeiro")
    if existing:
        ref = branch_ref if ref_exists(repo, branch_ref) else remote_ref
        for filename in ("collab/collab.py", "collab/agents.json", "collab/PROMPT.md"):
            if git(repo, "cat-file", "-e", f"{ref}:{filename}", check=False).returncode:
                raise ValueError(f"Canal existente incompatível: falta {filename}")
    else:
        # Build an orphan commit through a private index: no checkout, no workflow,
        # no changes to the user's index, no network and no commit on main.
        with tempfile.TemporaryDirectory(prefix="fruit-salad-") as temp:
            tree_dir = Path(temp)
            channel = tree_dir / "collab"
            channel.mkdir()
            (tree_dir / ".gitignore").write_text(".collab-cache/\n__pycache__/\n*.pyc\n", encoding="utf-8")
            shutil.copyfile(source / "collab.py", channel / "collab.py")
            shutil.copyfile(source / "PROTOCOL.md", channel / "PROMPT.md")
            roster = {"schema": 1, "agents": {
                "chatgpt": {"kind": "ai", "aliases": ["codex"], "product": "ChatGPT/Codex"},
                "claude": {"kind": "ai", "product": "Claude Code"},
                a.human: {"kind": "human", "product": "Mantenedor"}}}
            (channel / "agents.json").write_text(json.dumps(roster, indent=2) + "\n", encoding="utf-8")
            for thread, title in (("T-sync", "Sincronizações"), ("T-protocol", "Melhoria do protocolo")):
                subprocess.run([sys.executable, str(channel / "collab.py"), "new", "--from", a.human,
                                "--to", "all", "--type", "task", "--thread", thread, "--title", title,
                                "--body", "Thread permanente de coordenação; não concluir por uma rodada isolada."],
                               check=True, capture_output=True, text=True)
            subprocess.run([sys.executable, str(channel / "collab.py"), "validate"],
                           check=True, capture_output=True, text=True)
            index = tree_dir / "index"
            gitdir = git(repo, "rev-parse", "--absolute-git-dir").stdout.strip()
            env = dict(os.environ, GIT_INDEX_FILE=str(index), GIT_WORK_TREE=str(tree_dir), GIT_DIR=gitdir)
            for command in (["read-tree", "--empty"], ["add", "collab", ".gitignore"], ["write-tree"]):
                out = subprocess.run(["git", *command], env=env, check=True, text=True, capture_output=True)
            tree = out.stdout.strip()
            commit = git(repo, "commit-tree", tree, input="Fruit Salad: canal inicial isolado\n").stdout.strip()
            git(repo, "update-ref", branch_ref, commit, "0" * len(commit))
    dest.mkdir(exist_ok=True)
    for filename, content in wanted.items():
        (dest / filename).write_text(content, encoding="utf-8")
    for path, content in hooks.items():
        path.write_text(content, encoding="utf-8")
    print(f"Fruit Salad {VERSION} instalado em {repo}; canal {a.channel}.")
    print("Arquivos locais prontos para revisão. Nenhum push, PR, webhook ou automação criado.")
    print("Próximo: python3 .fruit-salad/fruit.py coco")


def configuration(repo):
    value = json.loads((repo / ".fruit-salad/config.json").read_text(encoding="utf-8"))
    if value.get("schema") != 1:
        raise ValueError("Schema de configuração não suportado")
    check_name(repo, value["channel"])
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value["remote"]):
        raise ValueError("Remote inválido")
    return value


def channel_worktree(repo, config, fetch=False):
    branch, remote = config["channel"], config["remote"]
    if fetch:
        # Explicit refspec also works in single-branch clones; no untrusted shell.
        git(repo, "fetch", remote, f"refs/heads/{branch}:refs/remotes/{remote}/{branch}")
    local_ref, remote_ref = "refs/heads/" + branch, f"refs/remotes/{remote}/{branch}"
    if not ref_exists(repo, local_ref):
        if not ref_exists(repo, remote_ref):
            raise ValueError("Canal ausente; faça init ou fetch")
        git(repo, "branch", branch, remote_ref)
    worktree = None
    # -z preserves spaces/newlines; don't decode quoted porcelain paths.
    records = git(repo, "worktree", "list", "--porcelain", "-z").stdout.split("\0\0")
    for record in records:
        fields = record.split("\0")
        if "branch " + local_ref in fields:
            worktree = Path(next(f[9:] for f in fields if f.startswith("worktree ")))
    if worktree is None:
        common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
        worktree = common / "fruit-salad" / "channel"
        worktree.parent.mkdir(exist_ok=True)
        git(repo, "worktree", "add", str(worktree), branch)
    if fetch:
        if git(worktree, "status", "--porcelain").stdout:
            raise ValueError("Canal tem alterações locais; preserve-as antes de sincronizar")
        git(worktree, "merge", "--ff-only", remote_ref)
    print(f"Canal {'atualizado por fetch' if fetch else 'LOCAL (sem consultar remoto)'}: "
          f"{git(worktree, 'rev-parse', 'HEAD').stdout.strip()}", flush=True)
    return worktree


def engine(worktree, *args):
    subprocess.run([sys.executable, str(worktree / "collab/collab.py"), *args], check=True, cwd=worktree)


def doctor(repo, config):
    failures = []
    for name in ("fruit.py", "collab.py", "PROTOCOL.md", "config.json"):
        ok = (repo / ".fruit-salad" / name).is_file()
        print(f"{'PASS' if ok else 'FAIL'} arquivo {name}")
        if not ok:
            failures.append(name)
    remote = git(repo, "remote", "get-url", config["remote"], check=False).returncode == 0
    print(f"{'PASS' if remote else 'WARN'} remote configurado (autenticação não testada)")
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = repo / name
        ok = path.is_file() and marker_text() in path.read_text(encoding="utf-8")
        print(f"{'PASS' if ok else 'FAIL'} instruções {name}")
        if not ok:
            failures.append(name)
    worktree = channel_worktree(repo, config)
    engine(worktree, "validate")
    print("NOT-RUN push, campainha, despertar dos agentes e execução periódica.")
    print("Campainha: " + (f"PR #{config['doorbell']} configurado, não verificado" if config.get("doorbell") else "manual; nenhum PR configurado"))
    print("Duas sessões com o mesmo id: validate avisa sobre nonces distintos; não há lock distribuído.")
    if failures:
        raise ValueError("Diagnóstico falhou: " + ", ".join(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    subs = parser.add_subparsers(dest="command", required=True)
    init = subs.add_parser("init", help="instalar localmente, sem publicar")
    init.add_argument("--repo", default=".")
    init.add_argument("--human", default="human")
    init.add_argument("--channel", default="collab/channel")
    init.add_argument("--remote", default="origin")
    init.add_argument("--doorbell", type=int)
    init.add_argument("--attach", action="store_true")
    detection = subs.add_parser("detect", help="identificar a fruta inicial sem executar o texto")
    detection.add_argument("text")
    for fruit in FRUITS:
        sub = subs.add_parser(fruit, help=FRUITS[fruit])
        if fruit in {"abacaxi", "uva", "manga"}:
            sub.add_argument("--agent", choices=("chatgpt", "codex", "claude"), required=True)
        if fruit == "abacaxi":
            sub.add_argument("--fetch", action="store_true", help="consultar origin; sem isto só lê estado local")
        if fruit == "manga":
            sub.add_argument("--to", choices=("chatgpt", "claude"), required=True)
            sub.add_argument("--thread", required=True)
            sub.add_argument("--body-file", type=Path, required=True)
            sub.add_argument("--session", help="nonce público e aleatório desta sessão; nunca id privado da plataforma")
    args = parser.parse_args()
    if args.command == "init":
        return install(args)
    if args.command == "detect":
        print(json.dumps(detect(args.text), ensure_ascii=False))
        return
    if args.command == "salada":
        for fruit, description in FRUITS.items():
            print(f"{fruit:9} {description}")
        print("Comandos de conversa exigem sessão ativa; arquivos não acordam agentes.")
        return
    repo = root(args.repo)
    config = configuration(repo)
    if args.command == "coco":
        return doctor(repo, config)
    worktree = channel_worktree(repo, config, getattr(args, "fetch", False))
    engine(worktree, "validate")
    if args.command == "manga":
        if ("chatgpt" if args.agent == "codex" else args.agent) == args.to:
            raise ValueError("Handoff exige outro agente")
        extra = ["--session", args.session] if args.session else []
        engine(worktree, "new", "--from", args.agent, "--to", args.to, "--type", "handoff",
               "--thread", args.thread, "--awaits", args.to, "--body-file", str(args.body_file.resolve()), *extra)
        print("Handoff criado LOCALMENTE. Revise, valide, faça commit/push e avise o destinatário.")
        return
    if args.command == "abacaxi":
        engine(worktree, "inbox", "--agent", args.agent)
    engine(worktree, "board")
    engine(worktree, "sync-report", "--agent", args.agent)
    print("Nenhuma mensagem marcada como lida ou publicada. Leia antes de seen; responda apenas o delta.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        # Never dump git remote URLs/credentials or subprocess input bodies.
        print(f"Fruit Salad: {error if not isinstance(error, subprocess.CalledProcessError) else 'git/ferramenta falhou; operação interrompida sem forçar histórico'}", file=sys.stderr)
        sys.exit(1)
