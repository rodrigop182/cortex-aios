#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
atualizar.py — motor da skill /atualizar do CORTEX OS.

Troca SO a camada de PRODUTO (skills, nucleo, refs genericas) por uma versao nova,
PRESERVANDO o DADO DO USUARIO (memoria, voz, nicho, contexto, projetos preenchidos).

Fonte da versao nova: pasta ja descompactada (--novo) OU download automatico do GitHub
(--github-repo + --github-token). A fronteira produto/dado vem do MANIFESTO-UPDATE.md.

DUAS etapas:
  1. Atualiza a PASTA-FONTE (--instalado): o espelho do zip que o usuario guardou
     (a pasta que tem _claude_global/ e memoria/).
  2. DEPLOY opcional pros lugares VIVOS (--claude-dir / --cortex-dir): copia os
     hooks/skills atualizados pra ~/.claude e pra pasta CORTEX, que e o que o Claude
     Code de fato carrega. Sem isso, a pasta-fonte fica nova mas o sistema vivo, velho.

Uso:
  python atualizar.py --instalado <raiz-instalada> --novo <raiz-do-zip-novo> [opcoes]
  python atualizar.py --instalado <raiz-instalada> --github-repo owner/repo --github-token TOKEN [opcoes]

  --dry-run            so mostra o que faria, nao escreve nada (DEFAULT recomendado primeiro)
  --yes                aplica sem perguntar (use depois de conferir o dry-run)
  --permitir-remocao-produto
                       permite remover somente caminhos listados em REMOVER_PRODUTO
  --permitir-sobrescrever-produto
                       permite sobrescrever produto existente diferente sem ledger
  --claude-dir <dir>   tambem faz deploy de _claude_global/* pra esta pasta (ex: ~/.claude)
  --cortex-dir <dir>   tambem faz deploy das skills do motor (memoria/.claude/*) pra esta pasta
  --github-repo        repo no formato owner/repo (ex: rodrigo/cortex-aios)
  --github-token       Personal Access Token com permissao repo (leitura). Alternativa: var
                       de ambiente CORTEX_GITHUB_TOKEN.

Falha segura: qualquer erro antes de aplicar aborta sem tocar no instalado.
Deploy nunca apaga dado nem quebra placeholder ja resolvido (ver _deploy_destino).
"""
import argparse
import fnmatch
import re
import shutil
import sys
import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path


def carregar_manifesto(raiz_novo: Path):
    """Le MANIFESTO-UPDATE.md e extrai PRODUTO, DADO e remocoes explicitas."""
    man = raiz_novo / "MANIFESTO-UPDATE.md"
    if not man.exists():
        sys.exit(f"ERRO: MANIFESTO-UPDATE.md nao encontrado em {raiz_novo}. "
                 "A versao nova precisa trazer o manifesto.")
    texto = man.read_text(encoding="utf-8")
    produto, dado, remover_produto = [], [], []
    alvo = None
    for linha in texto.splitlines():
        s = linha.strip()
        if s.startswith("## PRODUTO"):
            alvo = produto
            continue
        if s.startswith("## REMOVER_PRODUTO"):
            alvo = remover_produto
            continue
        if s.startswith("## DADO"):
            alvo = dado
            continue
        if s.startswith("## "):
            alvo = None
            continue
        if alvo is not None and s and not s.startswith("```") and not s.startswith("#"):
            alvo.append(s)
    if not produto:
        sys.exit("ERRO: manifesto sem caminhos de PRODUTO. Abortado.")
    return produto, dado, remover_produto


def casa_padrao(rel: str, padroes) -> bool:
    """rel casa com algum padrao (suporta ** e * estilo glob).
    Case-insensitive nos dois SOs (vies seguro: protege DADO igual no Win e Linux).
    Padrao de substring SEM barra (ex '*token*') casa o BASENAME, nao o caminho
    inteiro, pra um diretorio 'auth-token/' nao ser confundido com arquivo-segredo."""
    rel = rel.replace("\\", "/").lower()
    base = rel.rsplit("/", 1)[-1]
    for p in padroes:
        p = p.replace("\\", "/").lower()
        if p.endswith("/**"):
            raiz = p[:-3]
            if rel == raiz or rel.startswith(raiz + "/"):
                return True
        elif "**" in p:
            regex = re.escape(p).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
            if re.fullmatch(regex, rel):
                return True
        elif "/" not in p:
            # substring/glob sem barra: casa o nome do arquivo, nao o caminho
            if fnmatch.fnmatchcase(base, p):
                return True
        elif fnmatch.fnmatchcase(rel, p):
            return True
    return False


def eh_produto(rel, produto, dado, produto_exatos):
    """Classifica um caminho. Produto EXATO (sem glob) vence glob de DADO, pra um
    arquivo de produto dentro de pasta-dado (ex memoria/projects/README.md) nao ser
    engolido. Fora isso, DADO vence (na duvida, preservar)."""
    rel = rel.replace("\\", "/")
    if rel.lower() in produto_exatos:
        return True
    if casa_padrao(rel, dado):
        return False
    return casa_padrao(rel, produto)


def listar_produto_no_novo(raiz_novo: Path, produto, dado):
    """Todos os arquivos da versao nova que sao PRODUTO (e nao DADO)."""
    produto_exatos = {p.replace("\\", "/").lower() for p in produto
                      if "*" not in p}
    out = []
    for f in raiz_novo.rglob("*"):
        if not f.is_file():
            continue
        rel = str(f.relative_to(raiz_novo)).replace("\\", "/")
        if any(seg in (".git", "__pycache__") for seg in f.parts):
            continue
        if eh_produto(rel, produto, dado, produto_exatos):
            out.append(rel)
    return out


# ---------------------------------------------------------------------------
# DEPLOY pros lugares vivos (~/.claude, pasta CORTEX) — fecha o gap "atualizei
# a pasta-fonte mas o sistema vivo continua velho".
# ---------------------------------------------------------------------------

# placeholders REAIS do CORTEX (o que o instalador resolve). Distingue de '{{' literal de
# codigo (f-strings, regex) pra nao classificar mal arquivos que so MANIPULAM placeholders.
_PH_RE = re.compile(r"\{\{(CAMINHO|REPO|PASTA)_[A-Z]+\}\}")


def _linhas_norm(txt):
    """Linhas do texto sem as vazias do FINAL — tolera trailing newline que editores e o
    Set-Content do PowerShell adicionam. splitlines ja normaliza CRLF vs LF."""
    linhas = (txt or "").splitlines()
    while linhas and linhas[-1] == "":
        linhas.pop()
    return linhas


def _ler_txt(p: Path):
    # utf-8-sig tolera BOM (alguns editores/Set-Content gravam com BOM). Sem isso o BOM vira
    # ﻿ na 1a linha e a comparacao acha que "a logica mudou", re-introduzindo placeholder
    # por cima de um arquivo que ja estava resolvido. Funciona igual em arquivos sem BOM.
    try:
        return p.read_text(encoding="utf-8-sig")
    except Exception:
        return None


def _so_placeholder_difere(novo_txt: str, vivo_txt: str) -> bool:
    """True se o vivo e o template novo com cada {{PLACEHOLDER}} trocado por algum valor — ou
    seja, a unica diferenca e placeholder-vs-valor-ja-resolvido. Se a LOGICA mudou (linha nova,
    comportamento novo), retorna False (=> precisa ajuste manual). E o que garante que o deploy
    NUNCA quebra uma resolucao que o usuario ja fez.

    Compara LINHA A LINHA (placeholders do CORTEX sao caminhos numa linha so, nunca multilinha):
    linha sem placeholder tem que ser IDENTICA; linha com placeholder casa um regex-coringa SO
    daquela linha. Comparar por linha evita o falso-negativo do coringa global, em que um `.*?`
    consumia texto do segmento seguinte e fazia o deploy achar que a logica mudou sem ter mudado."""
    if novo_txt is None or vivo_txt is None:
        return False
    novo_linhas, vivo_linhas = _linhas_norm(novo_txt), _linhas_norm(vivo_txt)
    if len(novo_linhas) != len(vivo_linhas):
        return False  # numero de linhas diferente => logica mudou de fato
    for ln_novo, ln_vivo in zip(novo_linhas, vivo_linhas):
        if "{{" not in ln_novo:
            if ln_novo != ln_vivo:
                return False
            continue
        regex = ".+?".join(re.escape(seg) for seg in re.split(r"\{\{[^}]+\}\}", ln_novo))
        try:
            if re.fullmatch(regex, ln_vivo) is None:
                return False
        except Exception:
            return False
    return True


def _garantir_gitignore(raiz: Path) -> bool:
    """Se a raiz e um repo git (ex um CORTEX versionado no GitHub), garante que os backups e
    o cache do CORTEX nao sujem o git do usuario. Acrescenta ao .gitignore o que faltar."""
    if not (raiz / ".git").exists():
        return False
    gi = raiz / ".gitignore"
    necessarios = ["_backup-update-*/", "_backup-cortex-*/", "CORTEX.bak-*/",
                   "__pycache__/", "*.pyc"]
    atual = _ler_txt(gi) or ""
    faltam = [p for p in necessarios if p not in atual]
    if not faltam:
        return False
    try:
        with open(gi, "a", encoding="utf-8") as f:
            if atual and not atual.endswith("\n"):
                f.write("\n")
            f.write("\n# CORTEX /atualizar — backups e cache nao versionados\n")
            for p in faltam:
                f.write(p + "\n")
        return True
    except Exception:
        return False


def _bkp(dst: Path, bdir: Path, rel: str):
    """Copia o arquivo vivo pro backup datado antes de sobrescrever (reversivel)."""
    try:
        b = bdir / rel
        b.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, b)
    except Exception:
        pass


def _deploy_destino(origem_sub: Path, dst_raiz: Path, restringir=None,
                    aplicar=True, v_inst="0.0.0"):
    """Deploy do PRODUTO de origem_sub (ex novo/_claude_global) pros arquivos VIVOS em
    dst_raiz (ex ~/.claude). Regras de seguranca:
      - arquivo SEM placeholder: copia se mudou (sobrescreve; backup antes).
      - arquivo COM placeholder ja resolvido no vivo e logica igual: PRESERVA (nao toca).
      - arquivo COM placeholder e logica MUDOU, ou arquivo NOVO configuravel: copia o
        template (com placeholder) e marca pra AJUSTE MANUAL (o agente re-resolve).
      - settings.json: NUNCA sobrescreve automatico (pode ter hooks do usuario mesclados).
      - pula seeds cujo CAMINHO contem chaves de placeholder (a pasta-seed de memoria):
        sao seed de dado, nao vao pros hooks vivos.
    'restringir': se setado (ex '.claude'), so deploya o que estiver sob esse subcaminho.
    Retorna (escritos, preservados, ajuste_manual:list, backup_dir|None)."""
    escritos, preservados, ajuste = [], [], []
    carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
    bdir = dst_raiz / f"_backup-update-{v_inst}-{carimbo}"

    for f in sorted(origem_sub.rglob("*")):
        if not f.is_file():
            continue
        if any(seg in (".git", "__pycache__") for seg in f.parts):
            continue
        rel = str(f.relative_to(origem_sub)).replace("\\", "/")
        if rel.endswith(".pyc"):
            continue
        if "{{" in rel:
            continue  # seed de dado (pasta-placeholder), nao vai pro deploy de produto
        if restringir and not (rel == restringir or rel.startswith(restringir + "/")):
            continue

        src = f
        dst = dst_raiz / rel
        novo_b = src.read_bytes()
        novo_txt = _ler_txt(src)
        tem_ph = bool(novo_txt and _PH_RE.search(novo_txt))

        # settings.json: caso especial — nunca sobrescrever (preserva hooks do usuario)
        if rel.endswith("settings.json"):
            if dst.exists():
                if _so_placeholder_difere(_ler_txt(src), _ler_txt(dst)):
                    preservados.append(rel)
                else:
                    ajuste.append(f"{rel} (re-mescle a secao 'hooks' a mao; nao toquei pra "
                                  "nao apagar os seus)")
            else:
                ajuste.append(f"{rel} (copie e resolva os placeholders a mao)")
            continue

        if dst.exists():
            if tem_ph:
                if _so_placeholder_difere(_ler_txt(src), _ler_txt(dst)):
                    preservados.append(rel)   # ja resolvido, logica igual: nao toca
                    continue
                # logica mudou E tem placeholder: atualiza, mas avisa pra re-resolver
                if aplicar:
                    _bkp(dst, bdir, rel)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                escritos.append(rel)
                ajuste.append(f"{rel} (logica nova + placeholder: RE-RESOLVA os {{...}})")
            else:
                # compara por TEXTO normalizado (splitlines tolera CRLF/LF e o utf-8-sig tira BOM),
                # pra nao sobrescrever so por diferenca de encoding/quebra-de-linha.
                vivo_txt = _ler_txt(dst)
                if vivo_txt is None or _linhas_norm(vivo_txt) != _linhas_norm(novo_txt):
                    if aplicar:
                        _bkp(dst, bdir, rel)
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                    escritos.append(rel)
        else:
            # arquivo novo
            if aplicar:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            escritos.append(rel)
            if tem_ph:
                ajuste.append(f"{rel} (NOVO configuravel: resolva os {{...}})")

    return escritos, preservados, ajuste, (bdir if bdir.exists() else None)


def _placeholders_remanescentes(dst_raiz: Path, rels):
    """Varre os arquivos deployados e lista os que ainda tem {{CAMINHO_/REPO_/PASTA_}}
    nao resolvido (pega tambem o caso de o vivo nunca ter sido resolvido)."""
    pend = []
    for rel in rels:
        txt = _ler_txt(dst_raiz / rel)
        if txt and _PH_RE.search(txt):
            pend.append(rel)
    return pend


def _deploy_e_relatar(origem_sub: Path, dst_raiz: Path, restringir, label, dry_run, v_inst):
    if not origem_sub.is_dir():
        print(f"  [{label}] pulado: {origem_sub} nao existe na versao nova.")
        return
    if not dst_raiz.is_dir():
        print(f"  [{label}] pulado: destino {dst_raiz} nao existe (caminho errado?).")
        return
    if not dry_run and _garantir_gitignore(dst_raiz):
        print(f"  [{label}] .gitignore atualizado (backups/cache fora do git).")
    escritos, preservados, ajuste, bdir = _deploy_destino(
        origem_sub, dst_raiz, restringir=restringir, aplicar=not dry_run, v_inst=v_inst)
    pref = "[dry-run] faria: " if dry_run else ""
    print(f"  [{label}] {pref}{len(escritos)} escrito(s), "
          f"{len(preservados)} preservado(s) (ja resolvidos).")
    if bdir:
        print(f"           backup dos sobrescritos em {bdir.name}")
    pend = _placeholders_remanescentes(dst_raiz, escritos) if not dry_run else []
    todos_aj = list(dict.fromkeys(ajuste + [f"{r} (placeholder ainda literal)" for r in pend
                                            if not any(r in a for a in ajuste)]))
    if todos_aj:
        print(f"           AJUSTE MANUAL ({len(todos_aj)}) — resolva placeholders / re-mescle:")
        for a in todos_aj:
            print(f"             ! {a}")


def baixar_zip_github(repo, token, tmp_dir):
    """Baixa o zip do ultimo release do repo GitHub privado. Retorna Path da pasta extraida."""
    try:
        import urllib.request
        import json as _json
    except ImportError:
        sys.exit("ERRO: modulos urllib/json nao encontrados (Python padrao, nao deveria falhar).")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # busca o ultimo release
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            release = _json.loads(r.read().decode())
    except Exception as e:
        sys.exit(f"ERRO ao buscar releases do GitHub ({repo}): {e}\n"
                 "Verifique o repo, o token e a conexao.")

    tag = release.get("tag_name", "?")
    zip_url = release.get("zipball_url")
    if not zip_url:
        sys.exit(f"ERRO: release '{tag}' nao tem zipball_url. Repo sem releases publicados?")

    print(f"GitHub: baixando release {tag} de {repo}...")
    req2 = urllib.request.Request(zip_url, headers=headers)
    zip_path = os.path.join(tmp_dir, "cortex-novo.zip")
    try:
        with urllib.request.urlopen(req2, timeout=60) as r, open(zip_path, "wb") as f:
            shutil.copyfileobj(r, f)
    except Exception as e:
        sys.exit(f"ERRO ao baixar zip: {e}")

    # extrai
    extract_dir = os.path.join(tmp_dir, "extraido")
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

    # o GitHub cria uma subpasta com nome owner-repo-hash — pega a primeira
    subdirs = [d for d in os.listdir(extract_dir)
               if os.path.isdir(os.path.join(extract_dir, d))]
    if not subdirs:
        sys.exit("ERRO: zip extraido vazio ou sem subpasta esperada.")

    raiz = Path(os.path.join(extract_dir, subdirs[0]))
    print(f"GitHub: extraido em {raiz} ({tag})")
    return raiz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instalado", required=True, help="raiz do CORTEX ja instalado (espelho do zip)")
    ap.add_argument("--novo", default="", help="raiz da versao nova (zip descompactado). Alternativa: --github-repo")
    ap.add_argument("--dry-run", action="store_true", help="so mostra, nao aplica")
    ap.add_argument("--yes", action="store_true", help="aplica sem perguntar")
    ap.add_argument("--permitir-remocao-produto", action="store_true",
                    help="remove apenas caminhos listados em REMOVER_PRODUTO no manifesto")
    ap.add_argument("--permitir-sobrescrever-produto", action="store_true",
                    help="sobrescreve produto existente diferente mesmo sem ledger/hash antigo")
    ap.add_argument("--claude-dir", default="", help="tambem deploya _claude_global/* aqui (ex ~/.claude)")
    ap.add_argument("--cortex-dir", default="", help="tambem deploya as skills do motor (memoria/.claude/*) aqui")
    ap.add_argument("--github-repo", default="", help="repo GitHub no formato owner/repo (ex: rodrigo/cortex-aios)")
    ap.add_argument("--github-token", default="", help="Personal Access Token GitHub (ou use env CORTEX_GITHUB_TOKEN)")
    args = ap.parse_args()

    # resolve fonte: --novo ou GitHub
    _tmp_dir = None
    if args.github_repo:
        token = args.github_token or os.environ.get("CORTEX_GITHUB_TOKEN", "")
        if not token:
            sys.exit("ERRO: --github-repo requer --github-token ou variavel CORTEX_GITHUB_TOKEN.")
        _tmp_dir = tempfile.mkdtemp(prefix="cortex-update-")
        try:
            novo_path = baixar_zip_github(args.github_repo, token, _tmp_dir)
            args.novo = str(novo_path)
        except SystemExit:
            shutil.rmtree(_tmp_dir, ignore_errors=True)
            raise
    elif not args.novo:
        ap.error("Informe --novo <pasta> ou --github-repo <owner/repo> (com --github-token).")

    inst = Path(args.instalado).resolve()
    novo = Path(args.novo).resolve()
    if not inst.is_dir():
        sys.exit(f"ERRO: --instalado nao e pasta: {inst}")
    if not novo.is_dir():
        sys.exit(f"ERRO: --novo nao e pasta: {novo}")
    if inst == novo:
        sys.exit("ERRO: instalado e novo sao a mesma pasta.")

    produto, dado, remover_produto = carregar_manifesto(novo)

    # versoes
    def ler_versao(raiz):
        v = raiz / "VERSION"
        return v.read_text(encoding="utf-8").strip() if v.exists() else "0.0.0"

    def parse_semver(s):
        """'1.10.2' -> (1,10,2). Compara como numero, nao como string.
        Parte nao-numerica vira 0 (tolerante a sufixos tipo '1.2.0-beta')."""
        nums = []
        for parte in re.split(r"[.\-+]", s.strip()):
            m = re.match(r"\d+", parte)
            nums.append(int(m.group()) if m else 0)
        return tuple(nums) or (0,)

    v_inst, v_novo = ler_versao(inst), ler_versao(novo)
    print(f"Versao instalada: {v_inst}  ->  versao nova: {v_novo}")
    if parse_semver(v_novo) <= parse_semver(v_inst) and not args.yes:
        print(f"AVISO: versao nova ({v_novo}) nao e maior que a instalada ({v_inst}). "
              "Isso e reinstalacao/downgrade. Use --yes pra forcar.")
        if not args.dry_run:
            sys.exit(1)

    arquivos_novos = listar_produto_no_novo(novo, produto, dado)

    # plano: o que cria e o que sobrescreve.
    a_escrever, pendentes_merge = [], []
    for rel in arquivos_novos:
        dst = inst / rel
        if dst.exists():
            if dst.read_bytes() != (novo / rel).read_bytes():
                if args.permitir_sobrescrever_produto:
                    a_escrever.append(rel)
                else:
                    pendentes_merge.append(rel)
        else:
            a_escrever.append(rel)

    # Produto ausente na nova versao e preservado por padrao. Remocao so entra
    # por REMOVER_PRODUTO + flag explicita, porque sem ledger/checksum nao ha
    # prova de que o arquivo nao foi customizado pelo usuario.
    a_remover = []
    preservar_usuario = []
    set_novos = set(arquivos_novos)
    produto_exatos = {p.replace("\\", "/").lower() for p in produto if "*" not in p}

    # nomes de extensoes customizaveis presentes na versao NOVA.
    def _grupo_customizavel(rel):
        """Se rel esta dentro de skills/<nome>/, agents/<nome> ou hooks/<nome>, devolve
        ('skills'|'agents'|'hooks', <nome>). Senao, None."""
        partes = rel.lower().split("/")
        for marcador in ("skills", "agents", "hooks"):
            if marcador in partes:
                i = partes.index(marcador)
                if i + 1 < len(partes):
                    nome = partes[i + 1]
                    for suf in (".md", ".py", ".ps1", ".sh", ".json"):
                        nome = nome.removesuffix(suf)
                    return (marcador, nome)
        return None

    grupos_novos = set()
    for rel in arquivos_novos:
        g = _grupo_customizavel(rel)
        if g:
            grupos_novos.add(g)

    for f in inst.rglob("*"):
        if not f.is_file():
            continue
        rel = str(f.relative_to(inst)).replace("\\", "/")
        if any(seg in (".git", "__pycache__") for seg in f.parts):
            continue
        if rel.startswith("_backup-"):
            continue
        if not (eh_produto(rel, produto, dado, produto_exatos) and rel not in set_novos):
            continue
        g = _grupo_customizavel(rel)
        if g and g not in grupos_novos:
            # skill/agent cujo nome NAO existe na versao nova: provavel criacao do
            # usuario (ou skill renomeada). Nao apagar — preservar e avisar.
            preservar_usuario.append(rel)
        else:
            a_remover.append(rel)

    obsoletos_preservados = sorted(dict.fromkeys(a_remover + preservar_usuario))
    remocoes_bloqueadas = []
    remocoes_explicitas = []
    if remover_produto:
        for f in inst.rglob("*"):
            if not f.is_file():
                continue
            rel = str(f.relative_to(inst)).replace("\\", "/")
            if any(seg in (".git", "__pycache__") for seg in f.parts):
                continue
            if rel.startswith("_backup-") or rel.startswith("_update-pendente/"):
                continue
            if not casa_padrao(rel, remover_produto):
                continue
            if casa_padrao(rel, dado) and rel.lower() not in produto_exatos:
                remocoes_bloqueadas.append(f"{rel} (bloqueado: classificado como DADO)")
            elif args.permitir_remocao_produto:
                remocoes_explicitas.append(rel)
            else:
                remocoes_bloqueadas.append(
                    f"{rel} (bloqueado: requer --permitir-remocao-produto)")
    a_remover = sorted(dict.fromkeys(remocoes_explicitas))
    preservar_usuario = obsoletos_preservados

    # relatorio
    print("\n=== PLANO DE ATUALIZACAO (pasta-fonte) ===")
    print(f"  PRODUTO a escrever/atualizar: {len(a_escrever)}")
    for r in a_escrever:
        print(f"    + {r}")
    if pendentes_merge:
        print(f"  MERGE MANUAL (existente diferente; original preservado): {len(pendentes_merge)}")
        for r in pendentes_merge:
            print(f"    ! {r}")
    print(f"  PRODUTO a remover (REMOVER_PRODUTO + flag explicita): {len(a_remover)}")
    for r in a_remover:
        print(f"    - {r}")
    if remocoes_bloqueadas:
        print(f"  REMOCAO BLOQUEADA: {len(remocoes_bloqueadas)}")
        for r in remocoes_bloqueadas:
            print(f"    ! {r}")
    if preservar_usuario:
        print(f"  PRESERVADO (produto ausente na nova; update nao apaga por padrao): "
              f"{len(preservar_usuario)}")
        for r in preservar_usuario:
            print(f"    = {r}")
    print("  DADO DO USUARIO: PRESERVADO (intocado)")

    deploy_pedido = bool(args.claude_dir or args.cortex_dir)

    if args.dry_run:
        print("\n[dry-run] Nada foi escrito na pasta-fonte.")
        if deploy_pedido:
            print("\n=== DEPLOY pros lugares vivos (preview) ===")
            if args.claude_dir:
                _deploy_e_relatar(novo / "_claude_global", Path(args.claude_dir).resolve(),
                                  None, "~/.claude (global)", True, v_inst)
            if args.cortex_dir:
                _deploy_e_relatar(novo / "memoria", Path(args.cortex_dir).resolve(),
                                  ".claude", "pasta CORTEX (skills do motor)", True, v_inst)
                _deploy_e_relatar(novo / "memoria", Path(args.cortex_dir).resolve(),
                                  "AGENTS.md", "pasta CORTEX (Codex)", True, v_inst)
        print("\nRode sem --dry-run (com --yes) pra aplicar.")
        return 0

    if not args.yes:
        print("\nUse --yes pra aplicar (depois de conferir o plano acima). "
              "Aplica a pasta-fonte e, se pedidos, os deploys.")
        return 0

    # --- aplicar na PASTA-FONTE ---
    if a_escrever or a_remover or pendentes_merge:
        carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
        bdir = inst / f"_backup-update-{v_inst}-{carimbo}"
        print(f"\nBackup da raiz instalada -> {bdir.name}")
        bdir.mkdir(exist_ok=True)
        for f in inst.rglob("*"):
            if not f.is_file():
                continue
            rel = str(f.relative_to(inst)).replace("\\", "/")
            if rel.startswith("_backup-") or ".git/" in rel or "__pycache__" in rel:
                continue
            d = bdir / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)

        # aplicar: escrever produto novo. Se um write falhar no meio, o instalado fica
        # parcial; o backup ja existe, entao orientar a restauracao em vez de morrer cru.
        for rel in a_escrever:
            dst = inst / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(novo / rel, dst)
            except OSError as e:
                print(f"\nERRO ao escrever {rel}: {e}")
                print("O instalado pode estar PARCIALMENTE atualizado.")
                print(f"RESTAURE copiando o conteudo de {bdir.name} de volta pra raiz.")
                return 2
        for rel in pendentes_merge:
            dst = inst / "_update-pendente" / f"{rel}.new"
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(novo / rel, dst)
            except OSError as e:
                print(f"\nERRO ao preparar merge manual {rel}: {e}")
                print("O original foi preservado. Resolva manualmente ou rode novamente.")
                return 2
        # Remocao so acontece para REMOVER_PRODUTO + flag explicita.
        nao_removidos = []
        for rel in a_remover:
            try:
                (inst / rel).unlink()
            except OSError:
                nao_removidos.append(rel)

        print(f"\nOK: pasta-fonte atualizada pra {v_novo}. {len(a_escrever)} escritos, "
              f"{len(a_remover) - len(nao_removidos)} removidos, "
              f"{len(pendentes_merge)} pendente(s) em _update-pendente. "
              "Dado do usuario intocado.")
        if nao_removidos:
            print(f"AVISO: nao removi {len(nao_removidos)} arquivo(s) (sem permissao?): "
                  f"{nao_removidos}")
        print(f"Reverter pasta-fonte: restaure de {bdir.name}")
    else:
        print("\nPasta-fonte: nada a aplicar (ja estava atualizada).")

    # --- DEPLOY pros lugares vivos ---
    if deploy_pedido:
        print("\n=== DEPLOY pros lugares vivos ===")
        if args.claude_dir:
            _deploy_e_relatar(novo / "_claude_global", Path(args.claude_dir).resolve(),
                              None, "~/.claude (global)", False, v_inst)
        if args.cortex_dir:
            _deploy_e_relatar(novo / "memoria", Path(args.cortex_dir).resolve(),
                              ".claude", "pasta CORTEX (skills do motor)", False, v_inst)
            _deploy_e_relatar(novo / "memoria", Path(args.cortex_dir).resolve(),
                              "AGENTS.md", "pasta CORTEX (Codex)", False, v_inst)
        print("\nDeploy concluido. Se houver AJUSTE MANUAL acima, resolva os placeholders "
              "marcados (o agente do /atualizar faz isso) e de /clear pra recarregar.")

    if _tmp_dir:
        shutil.rmtree(_tmp_dir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
