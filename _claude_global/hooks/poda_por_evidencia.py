#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
poda_por_evidencia.py — rodado SOB DEMANDA (skill catch-up / audit / fecha-sessao),
NUNCA como hook automatico. FASE 5, mecanismo 3 (poda) + leitura do mecanismo 2 (eficacia).

Ataca a "torneira aberta": regra que so engorda o acervo. Mas com TRES travas de seguranca
em camada, pra nunca podar regra viva (o erro caro):

  1. PRESENCA NO INDICE (tapa o furo do mec 1): regra com ponteiro no MEMORY.md e VIVA por
     presenca, mesmo que nunca tenha sido aberta via Read. O indice e curado (/lint, /audit),
     entao estar nele = decisao deliberada de manter. Regra injetada via indice no recall nao
     dispara Read, mas tambem nao e morta — esta camada resolve isso sem hook novo nem inflar log.
  2. EFICACIA (mec 2, _eficacia-regras.log): regra que a destilacao marcou 'eficaz' e protegida;
     regra marcada 'reforcar' NAO e podada — vai pra lista A REESCREVER (problema e a redacao, nao
     a existencia). Quem escreve esse veredito e o Claude na destilacao (tem contexto), nao um script.
  3. USO + IDADE + STATUS (logica original): so vira candidata a MORTA quem esta FORA do indice,
     sem leitura recente, com idade > DIAS_MIN_IDADE, e status nao ativo/pausa.

GATE OBRIGATORIO (principio 6): modo padrao SO IMPRIME relatorio. Quem decide e o humano/Claude,
que entao roda --mover <slug...>. Poda = MOVER pra archives/ (reversivel), nunca deletar. Cada
movimento logado. O --mover RE-CHECA indice e maturidade (trava nao some so porque alguem chamou).

MODO CONSERVADOR (anti falso-negativo): "sem uso" so e confiavel apos DIAS_COLETA_MIN dias de
instrumentacao. Abaixo disso, regra orfa sem status 'resolvido' NAO e proposta (status resolvido e
sinal explicito do usuario, dispensa historico de uso).

Uso:
  python -B poda_por_evidencia.py                 -> relatorio (nao move nada)
  python -B poda_por_evidencia.py --mover a.md b.md  -> arquiva esses (gate ja passou)
"""
import sys, os, re, datetime, pathlib

# CONFIGURE: troque {{CAMINHO_MEMORIA}} pelo caminho ABSOLUTO da sua pasta de memoria (a mesma
# que o fecha-sessao usa). O instalador resolve esse placeholder; so ajuste a mao se rodar manual.
MEMORY_DIR = pathlib.Path(r"{{CAMINHO_MEMORIA}}")
LOG_USO = MEMORY_DIR / "_uso-memoria.log"
LOG_EFICACIA = MEMORY_DIR / "_eficacia-regras.log"
LOG_PODA = MEMORY_DIR / "_poda.log"
INDICE = MEMORY_DIR / "MEMORY.md"
ARCHIVES = MEMORY_DIR / "archives"

DIAS_SEM_USO = 60       # regra fora do indice e nao aberta ha mais que isto = candidata
DIAS_MIN_IDADE = 21     # regra criada/mexida nas ultimas 3 semanas: intocavel
DIAS_COLETA_MIN = 30    # instrumentacao precisa deste historico antes de propor poda por uso
DIAS_EFICACIA = 120     # veredito de eficacia (eficaz/reforcar) vale por este periodo


def _agora():
    return datetime.datetime.now()


def _slugs_no_indice():
    """Set de basenames .md linkados no MEMORY.md (com ou sem path no link).
    Camada 1 de protecao: presenca no indice curado = regra viva."""
    try:
        txt = INDICE.read_text(encoding="utf-8")
    except Exception:
        return set()
    return set(re.findall(r"\]\((?:[^)]*[\\/])?([\w.-]+\.md)\)", txt))


def _ler_ultimos_usos():
    """slug -> datetime do ultimo uso (Read), a partir do _uso-memoria.log.
    Tolera formato legado de 2 campos (ts\\tslug) e estendido de 3 (ts\\ttipo\\tslug)."""
    usos = {}
    if not LOG_USO.exists():
        return usos, None
    primeiro = None
    try:
        for linha in LOG_USO.read_text(encoding="utf-8").splitlines():
            partes = linha.split("\t")
            if len(partes) < 2:
                continue
            try:
                dt = datetime.datetime.strptime(partes[0].strip(), "%Y-%m-%d %H:%M")
            except Exception:
                continue
            slug = partes[2].strip() if len(partes) >= 3 else partes[1].strip()
            if not slug.endswith(".md"):
                continue
            if primeiro is None or dt < primeiro:
                primeiro = dt
            if slug not in usos or dt > usos[slug]:
                usos[slug] = dt
    except Exception:
        pass
    return usos, primeiro


def _ler_eficacia():
    """slug -> veredito mais recente ('eficaz' | 'reforcar') dos ultimos DIAS_EFICACIA dias.
    Le _eficacia-regras.log (escrito pela destilacao). Linha: ts\\tslug.md\\tveredito\\tmotivo."""
    vereditos = {}
    if not LOG_EFICACIA.exists():
        return vereditos
    corte = _agora() - datetime.timedelta(days=DIAS_EFICACIA)
    try:
        for linha in LOG_EFICACIA.read_text(encoding="utf-8").splitlines():
            if not linha.strip() or linha.lstrip().startswith("#"):
                continue
            partes = linha.split("\t")
            if len(partes) < 3:
                continue
            try:
                dt = datetime.datetime.strptime(partes[0].strip(), "%Y-%m-%d %H:%M")
            except Exception:
                continue
            if dt < corte:
                continue
            slug = partes[1].strip()
            veredito = partes[2].strip().lower()
            if veredito not in ("eficaz", "reforcar"):
                continue
            if slug not in vereditos or dt > vereditos[slug][1]:
                vereditos[slug] = (veredito, dt)
    except Exception:
        pass
    return {s: v[0] for s, v in vereditos.items()}


def _status_frontmatter(path):
    """Retorna 'ativo'/'pausa'/'resolvido'/None lendo o topo do arquivo."""
    try:
        head = path.read_text(encoding="utf-8")[:600]
    except Exception:
        return None
    m = re.search(r"status:\s*(ativo|pausa|resolvido)", head, re.IGNORECASE)
    return m.group(1).lower() if m else None


def _classificar():
    """Varre as regras e separa em quatro baldes:
      mortas    -> candidatas a arquivar (gate)
      reescrever-> marcadas 'reforcar' pela destilacao (corrigir redacao, nao podar)
      passivas  -> no indice mas sem leitura registrada (info pro /audit revisar o ponteiro)
      eficazes  -> confirmadas uteis pela destilacao (so pra mostrar saude)
    Retorna (baldes_dict, aviso_maturidade|None)."""
    usos, primeiro_uso = _ler_ultimos_usos()
    no_indice = _slugs_no_indice()
    eficacia = _ler_eficacia()
    agora = _agora()

    # maturidade da instrumentacao de uso (so afeta poda por falta-de-uso)
    aviso_mat = None
    if primeiro_uso is None:
        dias_hist = 0
    else:
        dias_hist = (agora - primeiro_uso).days
    if dias_hist < DIAS_COLETA_MIN:
        falta = DIAS_COLETA_MIN - dias_hist
        aviso_mat = (f"instrumentacao de uso com {dias_hist}d de historico (< {DIAS_COLETA_MIN}). "
                     f"Poda por falta-de-uso suspensa por mais ~{falta}d; so status 'resolvido' "
                     "orfao do indice e proposto. Presenca no indice protege o resto.")

    baldes = {"mortas": [], "reescrever": [], "passivas": [], "eficazes": []}
    for path in sorted(MEMORY_DIR.glob("*.md")):
        nome = path.name
        if nome == "MEMORY.md" or nome.startswith("_"):
            continue
        status = _status_frontmatter(path)
        if status in ("ativo", "pausa"):
            continue  # em curso: intocavel
        try:
            mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        except Exception:
            continue
        idade = (agora - mtime).days
        if idade < DIAS_MIN_IDADE:
            continue  # nova/recem-mexida: intocavel

        vd = eficacia.get(nome)
        if vd == "eficaz":
            baldes["eficazes"].append(nome)
            continue
        if vd == "reforcar":
            baldes["reescrever"].append((nome, f"destilacao marcou 'reforcar'; idade {idade}d"))
            continue

        ult = usos.get(nome)
        dentro = nome in no_indice

        if dentro:
            # CAMADA 1: protegida por presenca. So vira INFO se nunca foi aberta de fato.
            if ult is None and dias_hist >= DIAS_COLETA_MIN:
                baldes["passivas"].append((nome, f"no indice mas sem leitura em {dias_hist}d — revisar ponteiro"))
            continue

        # ORFA do indice (ponteiro removido por /lint /audit, ou consolidada em bloco tematico):
        if status == "resolvido":
            baldes["mortas"].append((nome, f"status 'resolvido' + fora do indice; mexida ha {idade}d"))
            continue
        if dias_hist < DIAS_COLETA_MIN:
            continue  # sem historico de uso confiavel: nao propoe (conservador)
        if ult is None:
            baldes["mortas"].append((nome, f"fora do indice + nunca aberta em {dias_hist}d; mexida ha {idade}d"))
        else:
            sem_uso = (agora - ult).days
            if sem_uso >= DIAS_SEM_USO:
                baldes["mortas"].append((nome, f"fora do indice + sem uso ha {sem_uso}d; mexida ha {idade}d"))

    return baldes, aviso_mat


def _relatorio():
    baldes, aviso_mat = _classificar()
    if aviso_mat:
        print(f"[modo conservador] {aviso_mat}\n")

    mortas = baldes["mortas"]
    reescrever = baldes["reescrever"]
    passivas = baldes["passivas"]
    eficazes = baldes["eficazes"]

    if not any([mortas, reescrever, passivas]):
        msg = "Acervo saudavel: nenhuma regra morta, a reescrever, ou passiva sem leitura."
        if eficazes:
            msg += f" ({len(eficazes)} confirmada(s) eficaz(es) pela destilacao.)"
        print(msg)
        return

    if mortas:
        print(f"CANDIDATAS A PODA ({len(mortas)}) — GATE: revise uma a uma e arquive so as mortas com")
        print("  python -B poda_por_evidencia.py --mover <slug.md> [<slug.md> ...]")
        print("(move pra archives/, reversivel; nunca deleta).\n")
        for nome, motivo in mortas:
            print(f"  - {nome:48s}  {motivo}")
        print("")

    if reescrever:
        print(f"A REESCREVER ({len(reescrever)}) — regra marcada 'reforcar' pela destilacao. NAO podar:")
        print("  abra o arquivo e melhore a redacao (o problema e a regra falhar, nao existir).\n")
        for nome, motivo in reescrever:
            print(f"  ~ {nome:48s}  {motivo}")
        print("")

    if passivas:
        print(f"PASSIVAS ({len(passivas)}) — no indice mas sem leitura registrada. So INFO pro /audit:")
        print("  decida se o ponteiro ainda merece estar no indice fino (nao e poda automatica).\n")
        for nome, motivo in passivas:
            print(f"  . {nome:48s}  {motivo}")
        print("")

    if eficazes:
        print(f"EFICAZES ({len(eficazes)}): {', '.join(eficazes)}")


def _mover(slugs):
    os.makedirs(str(ARCHIVES), exist_ok=True)
    no_indice = _slugs_no_indice()
    usos, primeiro_uso = _ler_ultimos_usos()
    dias_hist = (_agora() - primeiro_uso).days if primeiro_uso else 0
    ts = _agora().strftime("%Y-%m-%d %H:%M")
    movidos = []
    for slug in slugs:
        origem = MEMORY_DIR / slug
        if not origem.exists():
            print(f"  ignorado (nao existe): {slug}")
            continue
        # TRAVA re-checada no mover (nao confia so em quem chamou):
        if _status_frontmatter(origem) in ("ativo", "pausa"):
            print(f"  RECUSADO (status em curso): {slug}")
            continue
        if slug in no_indice:
            print(f"  RECUSADO (ainda no indice MEMORY.md — remova o ponteiro antes): {slug}")
            continue
        if _status_frontmatter(origem) != "resolvido" and dias_hist < DIAS_COLETA_MIN:
            print(f"  RECUSADO (instrumentacao imatura {dias_hist}d < {DIAS_COLETA_MIN}d; so 'resolvido' passa): {slug}")
            continue
        destino = ARCHIVES / slug
        try:
            if destino.exists():
                destino = ARCHIVES / (slug + _agora().strftime(".%Y%m%d%H%M.bak"))
            origem.replace(destino)
            movidos.append(slug)
            print(f"  arquivado: {slug} -> archives/")
        except Exception as e:
            print(f"  ERRO ao mover {slug}: {e}")
    if movidos:
        try:
            with open(LOG_PODA, "a", encoding="utf-8") as f:
                for slug in movidos:
                    f.write(f"{ts}\tarquivado\t{slug}\n")
        except Exception:
            pass
        print(f"\n{len(movidos)} arquivado(s). LEMBRETE: confirme que nao sobrou ponteiro no MEMORY.md.")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--mover":
        slugs = [a for a in args[1:] if a.endswith(".md")]
        if not slugs:
            print("Uso: --mover <slug.md> [<slug.md> ...]")
            return
        _mover(slugs)
    else:
        _relatorio()


if __name__ == "__main__":
    main()
