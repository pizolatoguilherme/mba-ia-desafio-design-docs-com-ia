#!/usr/bin/env python3
"""Validador dos critérios de aceite do desafio "Design Docs com IA".

Checa estrutura, rastreabilidade e consistência de docs/, docs/adrs/ e README.md
contra TRANSCRICAO.md e o código do repositório. Só usa a stdlib.

Uso (na raiz do repo):
  python3 .claude/skills/tracker-builder/scripts/validate_docs.py [--only GRUPO] [--list-ids]
  GRUPO: prd | rfc | fdd | adrs | tracker | readme | paths
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs"
ADRS = DOCS / "adrs"

ID_CORE = (
    r"(?:PRD-(?:MET|FR|NFR|OUT|DEP|RISK|AC)-\d{2}|RFC-(?:ALT|Q|RISK)-\d{2}|"
    r"FDD-(?:OBJ|FLUXO|CONTRATO|ERR|RES|OBS|INT|AC|RISK)-\d{2})"
)
ID_RE = re.compile(r"\b" + ID_CORE + r"\b")
TS_RE = re.compile(r"\[(\d{2}:\d{2})\]\s+([A-ZÀ-Ú][a-zà-ú]+)")
PATH_RE = re.compile(r"(?<![\w/.-])((?:src|prisma|tests)/[\w./\-\[\]{},*]+)")

# Arquivos futuros aceitos (decididos na reunião) — devem vir com "(novo, a criar)".
FUTURE_WHITELIST = {
    "src/worker.ts",
    "src/modules/webhooks",
    "src/modules/webhooks/",
    "src/modules/webhooks/webhook.controller.ts",
    "src/modules/webhooks/webhook.service.ts",
    "src/modules/webhooks/webhook.repository.ts",
    "src/modules/webhooks/webhook.routes.ts",
    "src/modules/webhooks/webhook.schemas.ts",
    "src/modules/webhooks/webhook.worker.ts",
    "src/modules/webhooks/webhook.processor.ts",
}

BLACKLIST_TERMS = {
    "email": r"\be-?mail\b",
    "rate limiting": r"rate[\s-]?limit",
    "dashboard/painel": r"\bdashboard\b|\bpainel\b",
    "arquivamento": r"arquiv",
    "exactly-once": r"exactly[\s-]?once",
}

REQUIRED = {
    "prd": [
        "Resumo e contexto", "Problema e motivação", "Público-alvo e cenários de uso",
        "Objetivos e métricas de sucesso", "Escopo", "Fora de escopo", "Requisitos funcionais",
        "Requisitos não funcionais", "Decisões e trade-offs principais", "Dependências",
        "Riscos e mitigação", "Critérios de aceitação", "Estratégia de testes e validação",
    ],
    "rfc": [
        "Metadados", "Resumo executivo (TL;DR)", "Contexto e problema", "Proposta técnica",
        "Alternativas consideradas", "Questões em aberto", "Impacto e riscos",
        "Decisões relacionadas",
    ],
    "fdd": [
        "Contexto e motivação técnica", "Objetivos técnicos", "Escopo e exclusões",
        "Fluxos detalhados", "Contratos públicos", "Matriz de erros",
        "Estratégias de resiliência", "Observabilidade", "Métricas", "Logs", "Tracing",
        "Dependências e compatibilidade", "Critérios de aceite técnicos", "Riscos e mitigação",
        "Integração com o sistema existente",
    ],
    "adr": ["Status", "Contexto", "Decisão", "Alternativas Consideradas", "Consequências"],
    "readme": [
        "Sobre o desafio", "Ferramentas de IA utilizadas", "Workflow adotado",
        "Prompts customizados", "Iterações e ajustes", "Como navegar a entrega",
    ],
}

PLACEHOLDERS = re.compile(r"\[NEEDS INPUT|ADR-XXX|\bTODO\b|\{\{|<!-- documento a ser elaborado")


class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []
        self.oks: list[str] = []

    def ok(self, msg: str) -> None:
        self.oks.append(msg)

    def fail(self, msg: str) -> None:
        self.fails.append(msg)

    def warn(self, msg: str) -> None:
        self.warns.append(msg)

    def check(self, cond: bool, msg: str, warn_only: bool = False) -> bool:
        if cond:
            self.ok(msg)
        elif warn_only:
            self.warn(msg)
        else:
            self.fail(msg)
        return cond


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def headings(text: str) -> list[str]:
    return [norm(m.group(2)) for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.M)]


def has_heading(text: str, name: str) -> bool:
    n = norm(name)
    return any(n in h for h in headings(text))


def section(text: str, name: str) -> str:
    """Retorna o corpo da seção cujo heading contém `name` (até o próximo heading de nível <=)."""
    lines = text.splitlines()
    n = norm(name)
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m and n in norm(m.group(2)):
            level = len(m.group(1))
            body = []
            for nxt in lines[i + 1:]:
                mm = re.match(r"^(#{1,6})\s+", nxt)
                if mm and len(mm.group(1)) <= level:
                    break
                body.append(nxt)
            return "\n".join(body)
    return ""


def strip_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def transcript_index() -> set[tuple[str, str]]:
    idx = set()
    for line in read(ROOT / "TRANSCRICAO.md").splitlines():
        m = re.match(r"^\[(\d{2}:\d{2})\]\s+([^:*]+):", line)
        if m:
            idx.add((m.group(1), m.group(2).strip()))
    return idx


def doc_files() -> dict[str, Path]:
    files = {"prd": DOCS / "PRD.md", "rfc": DOCS / "RFC.md", "fdd": DOCS / "FDD.md",
             "tracker": DOCS / "TRACKER.md", "readme": ROOT / "README.md"}
    for p in sorted(ADRS.glob("ADR-*.md")):
        files[p.stem] = p
    return files


def collect_ids() -> dict[str, tuple[str, int]]:
    """IDs definidos nos documentos (primeira ocorrência em negrito ou heading)."""
    ids: dict[str, tuple[str, int]] = {}
    for key, p in doc_files().items():
        if key in ("tracker", "readme"):
            continue
        rel = str(p.relative_to(ROOT))
        if key.startswith("ADR-"):
            ids[key[:7]] = (rel, 1)
            continue
        for ln, line in enumerate(read(p).splitlines(), 1):
            for m in re.finditer(r"\*\*(" + ID_CORE + r")\*\*|^\|\s*\**(" + ID_CORE + r")\**\s*\|", line):
                i = m.group(1) or m.group(2)
                if i:
                    ids.setdefault(i, (rel, ln))
    return ids


# ----------------------------------------------------------------------------- checks

def check_timestamps(r: Report, name: str, text: str, idx: set[tuple[str, str]]) -> None:
    bad = sorted({f"[{t}] {n}" for t, n in TS_RE.findall(text) if (t, n) not in idx})
    r.check(not bad, f"{name}: todos os [hh:mm] Nome existem na transcrição"
            + (f" — inválidos: {', '.join(bad[:15])}" if bad else ""))


def check_paths(r: Report) -> None:
    for key, p in doc_files().items():
        text = read(p)
        missing = set()
        unlabeled = set()
        for m in PATH_RE.finditer(text):
            raw = m.group(1).rstrip(".,);:`'\"")
            if any(ch in raw for ch in "*{[") :
                base = re.split(r"[*{\[]", raw)[0].rstrip("/")
                if not (ROOT / base).exists() and base not in FUTURE_WHITELIST and base + "/" not in FUTURE_WHITELIST:
                    missing.add(raw)
                continue
            if (ROOT / raw).exists():
                continue
            if raw in FUTURE_WHITELIST or raw.rstrip("/") in FUTURE_WHITELIST:
                ctx = text[max(0, m.start() - 200): m.end() + 200]
                if "novo" not in norm(ctx):
                    unlabeled.add(raw)
                continue
            missing.add(raw)
        r.check(not missing, f"{p.relative_to(ROOT)}: caminhos de código citados existem"
                + (f" — inexistentes: {', '.join(sorted(missing))}" if missing else ""))
        if unlabeled:
            r.warn(f"{p.relative_to(ROOT)}: arquivo futuro sem rótulo '(novo, a criar)' por perto: {', '.join(sorted(unlabeled))}")


def check_common(r: Report, name: str, text: str, idx) -> None:
    r.check(bool(text.strip()), f"{name}: arquivo existe e não está vazio")
    r.check(not PLACEHOLDERS.search(text), f"{name}: sem placeholders ([NEEDS INPUT], ADR-XXX, TODO, {{{{}}}})")
    r.check("—" not in text, f"{name}: sem travessões (—)", warn_only=True)
    check_timestamps(r, name, text, idx)


def check_required(r: Report, name: str, text: str, kind: str) -> None:
    missing = [h for h in REQUIRED[kind] if not has_heading(text, h)]
    r.check(not missing, f"{name}: seções obrigatórias presentes"
            + (f" — faltando: {missing}" if missing else ""))


def check_blacklist_in(r: Report, name: str, body: str, where: str) -> None:
    hits = [k for k, pat in BLACKLIST_TERMS.items() if re.search(pat, norm(strip_code(body)))]
    r.check(not hits, f"{name}: nenhum item fora de escopo dentro de '{where}'"
            + (f" — encontrados: {hits}" if hits else ""), warn_only=True)


def check_prd(r: Report, idx) -> None:
    t = read(DOCS / "PRD.md")
    check_common(r, "PRD", t, idx)
    check_required(r, "PRD", t, "prd")
    fr = set(re.findall(r"PRD-FR-\d{2}", t))
    r.check(len(fr) >= 8, f"PRD: ≥8 requisitos funcionais (encontrados {len(fr)})")
    met = section(t, "Objetivos e métricas de sucesso")
    r.check(bool(re.search(r"\d", met)) and "PRD-MET-" in met, "PRD: ≥1 métrica com meta quantitativa (PRD-MET + número)")
    out = section(t, "Fora de escopo")
    r.check(len(set(re.findall(r"PRD-OUT-\d{2}", out))) >= 2 and len(TS_RE.findall(out)) >= 2,
            "PRD: Fora de escopo com ≥2 itens rastreados à reunião")
    risks = section(t, "Riscos e mitigação")
    n_risk = len(set(re.findall(r"PRD-RISK-\d{2}", risks)))
    has_pim = all(k in norm(risks) for k in ("probabilidade", "impacto", "mitigacao"))
    r.check(n_risk >= 2 and has_pim, f"PRD: ≥2 riscos com probabilidade, impacto e mitigação (riscos: {n_risk})")
    check_blacklist_in(r, "PRD", section(t, "Requisitos funcionais"), "Requisitos funcionais")
    check_blacklist_in(r, "PRD", section(t, "Requisitos não funcionais"), "Requisitos não funcionais")
    r.check(not re.search(r"```json", t), "PRD: sem payload JSON (fronteira com o FDD)", warn_only=True)


def check_rfc(r: Report, idx) -> None:
    t = read(DOCS / "RFC.md")
    check_common(r, "RFC", t, idx)
    check_required(r, "RFC", t, "rfc")
    meta = norm(section(t, "Metadados"))
    r.check(all(k in meta for k in ("autor", "status", "data", "revisor")), "RFC: metadados com autor, status, data e revisores")
    r.check(all(n in section(t, "Metadados") for n in ("Larissa", "Marcos", "Bruno", "Diego", "Sofia")),
            "RFC: participantes da reunião nos metadados")
    alts = section(t, "Alternativas consideradas")
    n_alt = len(set(re.findall(r"RFC-ALT-\d{2}", alts)))
    r.check(n_alt >= 2 and len(TS_RE.findall(alts)) >= 2, f"RFC: ≥2 alternativas descartadas com fonte (encontradas {n_alt})")
    qs = section(t, "Questões em aberto")
    n_q = len(set(re.findall(r"RFC-Q-\d{2}", qs)))
    r.check(n_q >= 2 and len(TS_RE.findall(qs)) >= 2, f"RFC: ≥2 questões em aberto com fonte (encontradas {n_q})")
    links = re.findall(r"\]\((?:\./)?(adrs/ADR-\d{3}-[\w-]+\.md)\)", t)
    broken = [l for l in links if not (DOCS / l).exists()]
    r.check(len(set(links)) >= 2 and not broken, f"RFC: ≥2 links para ADRs válidos ({len(set(links))} links, quebrados: {broken})")
    words = len(re.findall(r"\w+", strip_code(t)))
    r.check(900 <= words <= 2400, f"RFC: tamanho de 2 a 4 páginas (~{words} palavras; alvo 1000-2200)", warn_only=True)
    r.check("```json" not in t, "RFC: sem payload JSON (detalhe é do FDD)", warn_only=True)


def check_fdd(r: Report, idx) -> None:
    t = read(DOCS / "FDD.md")
    check_common(r, "FDD", t, idx)
    check_required(r, "FDD", t, "fdd")
    flows = norm(section(t, "Fluxos detalhados"))
    r.check(all(k in flows for k in ("outbox", "worker", "retry", "dlq")), "FDD: fluxos cobrem outbox, worker, retry e DLQ")
    contracts = section(t, "Contratos públicos")
    endpoints = set(re.findall(r"\b(GET|POST|PATCH|PUT|DELETE)\s+(/[\w/:\-{}]+)", contracts))
    r.check(len(endpoints) >= 4, f"FDD: ≥4 endpoints HTTP nos contratos (encontrados {len(endpoints)})")
    blocks = re.findall(r"```json", contracts)
    r.check(len(blocks) >= 8, f"FDD: exemplos de payload request/response (blocos json: {len(blocks)}, mínimo 8)")
    r.check(len(re.findall(r"\b[1-5]\d{2}\b", contracts)) >= 8, "FDD: status codes documentados nos contratos")
    errs = section(t, "Matriz de erros")
    codes = set(re.findall(r"WEBHOOK_[A-Z_]+", errs))
    r.check(len(codes) >= 3, f"FDD: matriz de erros com códigos WEBHOOK_ ({len(codes)} códigos)")
    obs = norm(section(t, "Observabilidade"))
    r.check(all(k in obs for k in ("metrica", "log", "tracing")), "FDD: observabilidade cita métricas, logs e tracing")
    integ = section(t, "Integração com o sistema existente")
    real = {p.rstrip(".,);:`") for p in PATH_RE.findall(integ) if (ROOT / p.rstrip(".,);:`")).is_file()}
    r.check(len(real) >= 4, f"FDD: integração referencia ≥4 arquivos reais ({len(real)}: {sorted(real)[:8]})")


def check_adrs(r: Report, idx) -> None:
    files = sorted(ADRS.glob("ADR-*.md"))
    r.check(5 <= len(files) <= 8, f"ADRs: entre 5 e 8 arquivos (encontrados {len(files)})")
    for p in files:
        r.check(bool(re.fullmatch(r"ADR-\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*\.md", p.name)), f"{p.name}: nome no formato ADR-NNN-kebab-case.md")
        t = read(p)
        check_common(r, p.name, t, idx)
        check_required(r, p.name, t, "adr")
        alts = section(t, "Alternativas Consideradas")
        r.check(bool(re.search(r"^#{3,4}\s|^\s*[-*]\s|^\|", alts, re.M)), f"{p.name}: ≥1 alternativa listada")
        cons = norm(section(t, "Consequências"))
        r.check(all(k in cons for k in ("positiva", "negativa", "trade-off")), f"{p.name}: consequências positivas, negativas e trade-off")
    code_refs = [p.name for p in files if any((ROOT / m.rstrip(".,);:`")).exists() for m in PATH_RE.findall(read(p)))]
    r.check(len(code_refs) >= 1, f"ADRs: ≥1 referencia arquivo real do código ({code_refs})")
    joined = norm(" ".join(read(p) for p in files))
    topics = {
        "outbox": "outbox" in joined,
        "retry/backoff/DLQ": all(k in joined for k in ("backoff", "dead")),
        "HMAC-SHA256": "hmac" in joined,
        "at-least-once/X-Event-Id": "at-least-once" in joined and "x-event-id" in joined,
        "worker/polling": "polling" in joined,
        "reuso de padrões": "apperror" in joined and "pino" in joined,
    }
    covered = [k for k, v in topics.items() if v]
    r.check(len(covered) >= 5, f"ADRs: cobrem ≥5 das 6 decisões principais ({len(covered)}: {covered})")


def check_tracker(r: Report, idx) -> None:
    t = read(DOCS / "TRACKER.md")
    check_common(r, "TRACKER", t, idx)
    header = re.search(r"^\|\s*ID\s*\|\s*Documento\s*\|\s*Tipo\s*\|\s*Conteúdo \(resumo\)\s*\|\s*Fonte\s*\|\s*Localização\s*\|\s*$", t, re.M)
    r.check(bool(header), "TRACKER: cabeçalho exato ID | Documento | Tipo | Conteúdo (resumo) | Fonte | Localização")
    rows = []
    if header:
        for line in t[header.end():].splitlines()[2:]:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 6:
                rows.append(cells)
    r.check(len(rows) > 0, f"TRACKER: tabela com linhas ({len(rows)})")
    if not rows:
        return
    bad_src = [c[0] for c in rows if c[4] not in ("TRANSCRICAO", "CODIGO")]
    r.check(not bad_src, f"TRACKER: Fonte só TRANSCRICAO/CODIGO" + (f" — inválidas: {bad_src[:10]}" if bad_src else ""))
    tr_valid, tr_bad, code_ok, code_bad, doc_bad = 0, [], 0, [], []
    for c in rows:
        if not (ROOT / c[1].strip("`")).exists():
            doc_bad.append(c[0])
        if c[4] == "TRANSCRICAO":
            locs = TS_RE.findall(c[5])
            if locs and all((ts, n) in idx for ts, n in locs) and re.match(r"^\[\d{2}:\d{2}\] \S+", c[5]):
                tr_valid += 1
            else:
                tr_bad.append(f"{c[0]}={c[5]}")
        elif c[4] == "CODIGO":
            path = re.split(r"[\s(;]", c[5].strip("`"))[0].strip("`")
            if path and (ROOT / path).exists():
                code_ok += 1
            else:
                code_bad.append(f"{c[0]}={c[5]}")
    pct = 100 * tr_valid / len(rows)
    r.check(not tr_bad, "TRACKER: toda localização TRANSCRICAO é [hh:mm] Nome válido" + (f" — inválidas: {tr_bad[:10]}" if tr_bad else ""))
    r.check(pct >= 70, f"TRACKER: ≥70% das linhas TRANSCRICAO válidas ({pct:.1f}%)")
    r.check(pct >= 75, f"TRACKER: margem de segurança ≥75% TRANSCRICAO ({pct:.1f}%)", warn_only=True)
    r.check(code_ok >= 5 and not code_bad, f"TRACKER: ≥5 linhas CODIGO com caminho real ({code_ok})" + (f" — inválidas: {code_bad}" if code_bad else ""))
    r.check(not doc_bad, "TRACKER: coluna Documento aponta para arquivos existentes" + (f" — {doc_bad[:10]}" if doc_bad else ""))
    ids = collect_ids()
    tracked = {c[0] for c in rows}
    cov = 100 * len(set(ids) & tracked) / max(1, len(ids))
    missing = sorted(set(ids) - tracked)
    r.check(cov >= 80, f"TRACKER: cobertura ≥80% dos IDs dos documentos ({cov:.1f}% de {len(ids)})")
    r.check(not missing, f"TRACKER: cobertura 100% (faltando: {missing[:20]})", warn_only=True)
    orphan = sorted(tracked - set(ids))
    r.check(not orphan, f"TRACKER: sem linhas órfãs (IDs inexistentes nos docs: {orphan[:20]})", warn_only=True)
    dup = sorted({i for i in tracked if [c[0] for c in rows].count(i) > 1})
    r.check(not dup, f"TRACKER: sem IDs duplicados ({dup[:10]})", warn_only=True)


def check_readme(r: Report, idx) -> None:
    t = read(ROOT / "README.md")
    r.check(bool(t.strip()), "README: existe")
    check_required(r, "README", t, "readme")
    prompts = section(t, "Prompts customizados")
    r.check(len(re.findall(r"^```", prompts, re.M)) >= 4, "README: ≥2 prompts em blocos de código")
    tools = section(t, "Ferramentas de IA utilizadas")
    r.check(bool(re.search(r"claude|chatgpt|cursor|copilot|gemini", norm(tools))), "README: ≥1 ferramenta de IA listada")
    its = section(t, "Iterações e ajustes")
    r.check(len(re.findall(r"^\s*(?:\d+\.|[-*]|\|)", its, re.M)) >= 2, "README: ≥2 iterações descritas")
    r.check(bool(re.search(r"\d+\s+(?:iterac|ciclo)", norm(its))), "README: informa o número de iterações principais", warn_only=True)
    r.check("Neste desafio você vai transformar a transcrição" not in t and "## Critérios de Aceite" not in t, "README: enunciado original substituído")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["prd", "rfc", "fdd", "adrs", "tracker", "readme", "paths"])
    ap.add_argument("--list-ids", action="store_true")
    a = ap.parse_args()

    if a.list_ids:
        for i, (doc, ln) in sorted(collect_ids().items()):
            print(f"{i}\t{doc}:{ln}")
        return 0

    idx = transcript_index()
    r = Report()
    groups = {
        "adrs": lambda: check_adrs(r, idx), "rfc": lambda: check_rfc(r, idx),
        "fdd": lambda: check_fdd(r, idx), "prd": lambda: check_prd(r, idx),
        "tracker": lambda: check_tracker(r, idx), "readme": lambda: check_readme(r, idx),
        "paths": lambda: check_paths(r),
    }
    for name, fn in groups.items():
        if a.only in (None, name):
            fn()
    if a.only is None:
        protected = ["src", "prisma", "tests", "package.json", "package-lock.json", "tsconfig.json",
                     "tsconfig.build.json", "docker-compose.yml", ".env.example", ".eslintrc.json",
                     ".prettierrc", ".prettierignore", ".gitignore", "vitest.config.ts", "TRANSCRICAO.md"]
        try:
            out = subprocess.run(["git", "diff", "--name-only", "upstream/main", "--", *protected],
                                 cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
            out += subprocess.run(["git", "status", "--porcelain", "--", *protected],
                                  cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
            changed = sorted({x.strip() for x in out if x.strip()})
            r.check(not changed, "Código/configs/transcrição intocados vs upstream/main"
                    + (f" — alterados: {changed}" if changed else ""))
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            r.warn(f"Não foi possível checar git diff vs upstream/main: {e}")

    for m in r.oks:
        print(f"  OK    {m}")
    for m in r.warns:
        print(f"  WARN  {m}")
    for m in r.fails:
        print(f"  FAIL  {m}")
    print(f"\nRESULTADO: {'OK' if not r.fails else 'FALHOU'} ({len(r.oks)} ok, {len(r.warns)} avisos, {len(r.fails)} falhas)")
    return 0 if not r.fails else 1


if __name__ == "__main__":
    sys.exit(main())
