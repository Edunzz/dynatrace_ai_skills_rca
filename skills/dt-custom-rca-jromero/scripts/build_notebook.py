#!/usr/bin/env python3
"""
build_notebook.py — Ensambla y valida el Notebook RCA de Dynatrace (skill dt-custom-rca-jromero).

- Lee una especificación JSON (ver assets/rca_spec.example.json).
- Idioma: campo "language" del spec, "es" (por defecto) o "en". Define los títulos obligatorios,
  la palabra de las evidencias ("Evidencia" / "Evidence") y el idioma de los mensajes.
- Inserta las secciones markdown (desde archivo o texto inline) y DQL en orden.
- Convierte cada imagen local ![Alt](img:ruta.png) a data URI base64 para que quede DENTRO
  del notebook. La ruta se resuelve primero junto al .md de la sección y luego junto al spec.
- Repara el PNG si draw.io lo exportó con el bloque IEND truncado (versiones antiguas con -e).
- Las queries DQL se cargan desde los mismos .dql ejecutados con dtctl (query_file).

Validaciones (errores = no se genera el notebook):
  formato      nombre, portada, títulos y subsecciones obligatorias del idioma, sin HTML, solo PNG
               incrustado, D2/D1/D3 dentro de las secciones 3/4/5, timeframe absoluto, nivel de certeza
  sustento     toda "Evidencia N.x" / "Evidence N.x" citada existe como sección DQL "[Evidencia N.x]" /
               "[Evidence N.x]"; toda referencia [Rn] existe en la tabla 9.3
  lectura      el resumen ejecutivo (Sección 1) tiene máx. 10 líneas y no contiene código,
               DQL ni IDs de entidad (debe entenderlo cualquier persona)
Advertencias: jerga técnica en el resumen, placeholders sin reemplazar, evidencias o
referencias definidas pero no citadas, tamaño de imágenes. Con --strict, también bloquean.

Uso:
  python scripts/build_notebook.py rca/rca_spec.json -o rca/notebook.json [--strict]
"""
import argparse, base64, json, re, sys
from pathlib import Path

IMG_LOCAL = re.compile(r'!\[([^\]]*)\]\(img:([^)\s]+)\)')
IMG_ANY = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
HTML_TAG = re.compile(r'<\s*/?\s*(br|div|span|p|img|table|font|b|i|u)(\s[^<>]*)?/?>', re.I)
LANGS = {
    "es": {
        "titles": [
            "## 1. Resumen ejecutivo",
            "## 2. Alcance e impacto",
            "### 2.1 Componentes afectados",
            "### 2.2 Impacto en usuarios y negocio",
            "## 3. Línea de tiempo de los sucesos",
            "## 4. Diagrama de propagación de la afectación",
            "## 5. Análisis de causa raíz",
            "### 5.1 Causa raíz",
            "### 5.2 Análisis de los 5 porqués",
            "### 5.3 Hipótesis evaluadas",
            "### 5.4 Validación de Davis",
            "## 6. Brechas de observabilidad detectadas",
            "## 7. Plan de acción",
            "## 8. Lecciones aprendidas",
            "## 9. Anexos",
            "### 9.1 Anclaje, ventanas y evidencia",
            "### 9.2 Glosario",
            "### 9.3 Referencias oficiales",
            "### 9.4 Control de versiones",
        ],
        "diagrams": {"3": "D2 (línea de tiempo)", "4": "D1 (propagación)", "5": "D3 (árbol de causa raíz)"},
        "evidence": "Evidencia",
        "ev_ref": re.compile(r"\b(?:Evidencias?|Ev\.)\s*(\d+\.\d+(?:\s*(?:,\s*y|,|y)\s*\d+\.\d+)*)"),
        "certainty": "Nivel de certeza",
        "name": "RCA | <Problem ID> | <Servicio> | <YYYY-MM-DD>",
    },
    "en": {
        "titles": [
            "## 1. Executive summary",
            "## 2. Scope and impact",
            "### 2.1 Affected components",
            "### 2.2 Impact on users and business",
            "## 3. Timeline of events",
            "## 4. Failure propagation diagram",
            "## 5. Root cause analysis",
            "### 5.1 Root cause",
            "### 5.2 5 whys analysis",
            "### 5.3 Hypotheses evaluated",
            "### 5.4 Davis validation",
            "## 6. Observability gaps found",
            "## 7. Action plan",
            "## 8. Lessons learned",
            "## 9. Appendices",
            "### 9.1 Anchor, time windows and evidence",
            "### 9.2 Glossary",
            "### 9.3 Official references",
            "### 9.4 Version history",
        ],
        "diagrams": {"3": "D2 (timeline)", "4": "D1 (propagation)", "5": "D3 (root cause tree)"},
        "evidence": "Evidence",
        "ev_ref": re.compile(r"\b(?:Evidence|Ev\.)\s*(\d+\.\d+(?:\s*(?:,\s*and|,|and)\s*\d+\.\d+)*)"),
        "certainty": "Certainty level",
        "name": "RCA | <Problem ID> | <Service> | <YYYY-MM-DD>",
    },
}
NAME_RE = re.compile(r"^RCA \| .+ \| .+ \| \d{4}-\d{2}-\d{2}$")
R_REF = re.compile(r"\[R(\d+)(?::[^\]]*)?\]")
R_DEF = re.compile(r"^\|\s*R(\d+)\s*\|", re.M)
# Resumen ejecutivo: lo que lo vuelve ilegible para alguien no técnico
SUMMARY_BLOCK = [
    (re.compile(r"`"), ("contiene código o nombres entre backticks", "contains code or names in backticks")),
    (re.compile(r"\b[A-Z_]{3,}-[0-9A-F]{16}\b"), ("contiene IDs de entidad de Dynatrace", "contains Dynatrace entity IDs")),
    (re.compile(r"\b(fetch|timeseries|makeTimeseries|summarize)\b|\|\s*filter\b"), ("contiene DQL", "contains DQL")),
]
SUMMARY_JARGON = re.compile(r"\b(DQL|Grail|Smartscape|spans?|traces?|OneAgent|MTT[DAR]|p9[059]|"
                            r"SLO|RUM|OOM\w*|pods?|namespaces?|bizevents?|endpoints?)\b", re.I)
PLACEHOLDER = re.compile(r"<[^<>\n]{1,60}>|YYYY-MM-DD|P-XXXX|\bHH:MM\b")
MAX_IMG_KB = 400
MAX_TOTAL_KB = 1536
PNG_SIG = b"\x89PNG\r\n\x1a\n"
IEND_TAIL = b"IEND\xaeB`\x82"
LANG = "es"


def t(es, en):
    """Mensaje en el idioma del notebook."""
    return en if LANG == "en" else es


def read_png(p, errors, warnings):
    data = p.read_bytes()
    if not data.startswith(PNG_SIG):
        errors.append(t(f"No es un PNG válido: {p.name} (exportar con draw.io: -x -f png)",
                        f"Not a valid PNG: {p.name} (export with draw.io: -x -f png)"))
        return None
    if not data.endswith(IEND_TAIL):
        data = data + IEND_TAIL if data.endswith(b"\x00\x00\x00\x00") else data + b"\x00\x00\x00\x00" + IEND_TAIL
        warnings.append(t(f"{p.name}: bloque IEND truncado (draw.io -e); reparado al incrustar.",
                          f"{p.name}: truncated IEND chunk (draw.io -e); repaired when embedding."))
    return data


def embed_images(md, dirs, stats, errors, warnings):
    def repl(m):
        alt, rel = m.group(1), m.group(2)
        cands = [(d / rel).resolve() for d in dirs]
        p = next((c for c in cands if c.exists()), None)
        if p is None:
            where = ", ".join(str(d) for d in dirs)
            errors.append(t(f"Imagen no encontrada: {rel} (buscada en: {where})",
                            f"Image not found: {rel} (searched in: {where})"))
            return m.group(0)
        if p.suffix.lower() != ".png":
            errors.append(t(f"Formato no permitido: {p.name}. Solo PNG exportado de draw.io.",
                            f"Format not allowed: {p.name}. Only PNG exported from draw.io."))
            return m.group(0)
        data = read_png(p, errors, warnings)
        if data is None:
            return m.group(0)
        kb = len(data) / 1024
        stats.append((p.name, kb))
        if kb > MAX_IMG_KB:
            warnings.append(t(f"{p.name} pesa {kb:.0f} KB (> {MAX_IMG_KB} KB). Re-exportar con -s 1 o simplificar.",
                              f"{p.name} is {kb:.0f} KB (> {MAX_IMG_KB} KB). Re-export with -s 1 or simplify."))
        return f"![{alt}](data:image/png;base64,{base64.b64encode(data).decode()})"
    return IMG_LOCAL.sub(repl, md)


def compact(md):
    md = md.replace("&nbsp;", " ").replace("\r\n", "\n")
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def h2_blocks(md):
    """{'1': texto, '2': texto, ...} según los encabezados '## N.' del markdown completo."""
    blocks, cur = {}, None
    for line in md.splitlines():
        m = re.match(r"^## (\d+)\.", line)
        if m:
            cur = m.group(1)
        if cur:
            blocks.setdefault(cur, []).append(line)
    return {k: "\n".join(v) for k, v in blocks.items()}


def lint_summary(block, errors, warnings):
    lines = [l for l in block.splitlines()[1:] if l.strip()]
    if len(lines) > 10:
        errors.append(t(f"Resumen ejecutivo: {len(lines)} líneas (máx. 10). Debe leerse en un minuto.",
                        f"Executive summary: {len(lines)} lines (max. 10). It must be readable in a minute."))
    for rx, (why_es, why_en) in SUMMARY_BLOCK:
        if rx.search(block):
            errors.append(t(f"Resumen ejecutivo {why_es}; debe entenderlo alguien sin conocimiento técnico.",
                            f"Executive summary {why_en}; a non-technical reader must understand it."))
    jerga = ", ".join(sorted({m.group(0) for m in SUMMARY_JARGON.finditer(block)}, key=str.lower))
    if jerga:
        warnings.append(t(f"Resumen ejecutivo con términos técnicos ({jerga}): reemplazar por lenguaje de negocio o explicarlos.",
                          f"Executive summary uses technical terms ({jerga}): use business language or explain them."))


def load_text(base, rel, what, errors):
    p = (base / rel)
    try:
        return p.read_text(encoding="utf-8"), p.resolve().parent
    except OSError:
        errors.append(t(f"No se encontró el archivo de {what[0]}: {p}", f"File not found for {what[1]}: {p}"))
        return None, None


def main():
    global LANG
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--output", default="notebook.json")
    ap.add_argument("--strict", action="store_true", help="las advertencias también bloquean / warnings also block")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    spec_path = Path(a.spec).resolve()
    base = spec_path.parent
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"ERROR: no se pudo leer el spec / could not read the spec {spec_path}: {e}", file=sys.stderr)
        sys.exit(1)
    LANG = str(spec.get("language", "es")).lower()
    if LANG not in LANGS:
        print(f"ERROR: \"language\" debe ser \"es\" o \"en\" / must be \"es\" or \"en\" (spec: {LANG!r}).",
              file=sys.stderr)
        sys.exit(1)
    L = LANGS[LANG]
    ev_word = L["evidence"]
    ev_def_re = re.compile(rf"^\[{ev_word} (\d+\.\d+)\]")

    sections, errors, warnings, stats, all_md, ev_defs = [], [], [], [], [], []
    for i, s in enumerate(spec.get("sections", []), start=1):
        kind = s.get("type")
        if kind == "markdown":
            if "file" in s:
                md, md_dir = load_text(base, s["file"], (f"la sección {i}", f"section {i}"), errors)
                if md is None:
                    continue
            else:
                md, md_dir = s.get("markdown", ""), base
            if HTML_TAG.search(md):
                errors.append(t(f"Sección {i}: contiene HTML; usar solo Markdown.",
                                f"Section {i}: contains HTML; use Markdown only."))
            dirs = [md_dir] if md_dir == base else [md_dir, base]
            md = compact(embed_images(md, dirs, stats, errors, warnings))
            for url in IMG_ANY.findall(md):
                if not url.startswith("data:image/png;base64,"):
                    errors.append(t(f"Sección {i}: imagen externa/no incrustada -> {url[:80]}",
                                    f"Section {i}: external/not embedded image -> {url[:80]}"))
            all_md.append(md)
            sections.append({"id": str(i), "type": "markdown", "markdown": md})
        elif kind == "dql":
            title = s.get("title", "")
            m = ev_def_re.match(title)
            if not m:
                errors.append(t(f"Sección {i}: el título DQL debe iniciar con '[{ev_word} N.x]'.",
                                f"Section {i}: the DQL title must start with '[{ev_word} N.x]'."))
            elif m.group(1) in ev_defs:
                errors.append(t(f"Sección {i}: evidencia duplicada [{ev_word} {m.group(1)}].",
                                f"Section {i}: duplicated evidence [{ev_word} {m.group(1)}]."))
            else:
                ev_defs.append(m.group(1))
            if "query_file" in s:
                query, _ = load_text(base, s["query_file"], (f"la query de la sección {i}", f"the query of section {i}"), errors)
                if query is None:
                    continue
                query = query.strip()
            else:
                query = s.get("query", "")
            qs = {"maxResultRecords": 1000, "defaultScanLimitGbytes": 500,
                  "maxResultMegaBytes": 1, "defaultSamplingRatio": 10, "enableSampling": False}
            qs.update(s.get("querySettings", {}))  # igualar a los límites usados en dtctl si se elevaron
            state = {
                "input": {"value": query},
                "visualizationSettings": {"autoSelectVisualization": s.get("visualization") is None,
                                          "chartSettings": {}},
                "querySettings": qs,
            }
            if s.get("visualization"):
                state["visualization"] = s["visualization"]
            if s.get("timeframe"):
                state["input"]["timeframe"] = s["timeframe"]
            sections.append({"id": str(i), "type": "dql", "title": title, "showTitle": True,
                             "showInput": s.get("showInput", False), "state": state})
        else:
            errors.append(t(f"Sección {i}: tipo no soportado '{kind}'.", f"Section {i}: unsupported type '{kind}'."))

    joined = "\n".join(all_md)
    # Formato
    missing = [req for req in L["titles"] if req not in joined]
    for req in missing:
        errors.append(t(f"Falta la sección obligatoria: '{req}'", f"Missing required section: '{req}'"))
    other = "en" if LANG == "es" else "es"
    if missing and LANGS[other]["titles"][0] in joined:  # primero, porque explica el resto de errores
        errors.insert(0, t('Las secciones están en inglés: agrega "language": "en" al spec.',
                           'The sections are in Spanish: set "language": "es" in the spec (or remove "language").'))
    if not re.search(r"^# RCA", joined, re.M):
        errors.append(t("Falta la portada '# RCA — ...' (Sección 0).", "Missing the cover '# RCA — ...' (Section 0)."))
    if L["certainty"] not in joined:
        errors.append(t(f"La sección 5.1 debe declarar '{L['certainty']}'.",
                        f"Section 5.1 must state the '{L['certainty']}'."))
    blocks = h2_blocks(joined)
    for num, diag in L["diagrams"].items():
        if num in blocks and "data:image/png;base64," not in blocks[num]:
            errors.append(t(f"Sección {num}: falta la imagen {diag} incrustada.",
                            f"Section {num}: the embedded {diag} image is missing."))
    if "1" in blocks:
        lint_summary(blocks["1"], errors, warnings)
    total = sum(kb for _, kb in stats)
    if total > MAX_TOTAL_KB:
        warnings.append(t(f"Las imágenes suman {total:.0f} KB (> {MAX_TOTAL_KB} KB).",
                          f"Images add up to {total:.0f} KB (> {MAX_TOTAL_KB} KB)."))

    # Sustento: evidencias y referencias oficiales cruzadas
    ev_refs = {n for grp in L["ev_ref"].findall(joined) for n in re.findall(r"\d+\.\d+", grp)}
    for ev in sorted(ev_refs - set(ev_defs)):
        errors.append(t(f"Se cita '{ev_word} {ev}' pero no existe la sección DQL '[{ev_word} {ev}]'.",
                        f"'{ev_word} {ev}' is cited but there is no DQL section '[{ev_word} {ev}]'."))
    for ev in sorted(set(ev_defs) - ev_refs):
        warnings.append(t(f"La sección DQL '[{ev_word} {ev}]' no se cita en ninguna parte del texto.",
                          f"The DQL section '[{ev_word} {ev}]' is not cited anywhere in the text."))
    r_refs, r_defs = set(R_REF.findall(joined)), set(R_DEF.findall(blocks.get("9", "")))
    for r in sorted(r_refs - r_defs, key=int):
        errors.append(t(f"Se cita [R{r}] pero no existe en la tabla 9.3 Referencias oficiales.",
                        f"[R{r}] is cited but it is not in table 9.3 Official references."))
    for r in sorted(r_defs - r_refs, key=int):
        warnings.append(t(f"La referencia R{r} de la tabla 9.3 no se cita en el texto.",
                          f"Reference R{r} in table 9.3 is not cited in the text."))
    ph = sorted({m.group(0) for m in PLACEHOLDER.finditer(re.sub(r"data:image/png;base64,[^)]+", "", joined))})
    if ph:
        warnings.append(t("Posibles placeholders sin reemplazar: ", "Possible placeholders left in the text: ")
                        + ", ".join(ph[:8]) + (" ..." if len(ph) > 8 else ""))

    tf = spec.get("defaultTimeframe", {})
    if not tf.get("from") or not tf.get("to"):
        errors.append(t("defaultTimeframe debe tener 'from' y 'to'.", "defaultTimeframe must have 'from' and 'to'."))
    elif "now()" in str(tf.get("from")) or "now()" in str(tf.get("to")):
        errors.append(t("defaultTimeframe debe ser absoluto (ISO-8601) para que el RCA sea reproducible.",
                        "defaultTimeframe must be absolute (ISO-8601) so the RCA can be reproduced."))
    name = spec.get("name", "")
    if not NAME_RE.match(name):
        errors.append(t(f"El nombre debe seguir '{L['name']}'.", f"The name must follow '{L['name']}'."))

    if warnings:
        print(t("ADVERTENCIAS:", "WARNINGS:"), file=sys.stderr)
        for w in warnings:
            print(f" - {w}", file=sys.stderr)
    if errors or (a.strict and warnings):
        print(t("ERRORES DE VALIDACIÓN:", "VALIDATION ERRORS:") if errors else
              t("BLOQUEADO POR --strict.", "BLOCKED BY --strict."), file=sys.stderr)
        for e in errors:
            print(f" - {e}", file=sys.stderr)
        sys.exit(1)

    nb = {"name": name, "type": "notebook",
          "content": {"version": "7", "defaultTimeframe": tf, "sections": sections}}
    Path(a.output).write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
    print(t(f"OK: {a.output} | secciones: {len(sections)} | evidencias: {len(ev_defs)} | "
            f"imágenes: {len(stats)} ({total:.0f} KB)",
            f"OK: {a.output} | sections: {len(sections)} | evidence: {len(ev_defs)} | "
            f"images: {len(stats)} ({total:.0f} KB)"))
    for n, kb in stats:
        print(f"   - {n}: {kb:.0f} KB")


if __name__ == "__main__":
    main()
