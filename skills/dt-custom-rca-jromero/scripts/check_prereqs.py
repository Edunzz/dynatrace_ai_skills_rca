#!/usr/bin/env python3
"""
check_prereqs.py — Gate de prerrequisitos de la skill dt-custom-rca-jromero.

Valida (NO instala nada) y, si algo falta, indica cómo resolverlo según el sistema operativo:
  R1  dtctl instalado
  R2  contexto dtctl activo, autenticado y en Dynatrace SaaS (dtctl doctor)
  R3  scopes de lectura de Grail y de escritura de documentos (dtctl --check-scopes)
  R4  skills Dynatrace for AI (mínimas + de dominio disponibles)
  R5  skill drawio + draw.io Desktop (CLI que responde de verdad)
  R7  Python 3.9+
  R6  (punto de partida del incidente) lo valida el agente con el usuario.

Solo usa la librería estándar: funciona con cualquier agente (Claude Code, Codex, Copilot,
Cursor, etc.) en Windows, macOS y Linux.

Uso:
  python scripts/check_prereqs.py                  # reporte legible
  python scripts/check_prereqs.py --json           # salida estructurada para agentes
  python scripts/check_prereqs.py --context prod   # validar otro contexto dtctl
  python scripts/check_prereqs.py --offline        # sin llamadas al tenant (R2/R3 parciales)
  python scripts/check_prereqs.py --skills-dir D   # carpeta extra donde buscar skills (repetible)

Código de salida: 0 = listo para el RCA · 1 = falta algún requisito obligatorio.
"""
import argparse, json, os, platform, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

OK, FALTA, AVISO = "OK", "FALTA", "AVISO"
SYSTEM = platform.system()  # Windows | Darwin | Linux

DT_SKILLS_MIN = ["dt-dql-essentials", "dt-obs-problems", "dt-app-notebooks"]
DT_SKILLS_DOMAIN = ["dt-obs-services", "dt-obs-tracing", "dt-obs-logs", "dt-obs-hosts",
                    "dt-obs-kubernetes", "dt-obs-frontends", "dt-obs-aws", "dt-obs-azure",
                    "dt-obs-gcp", "dt-obs-analytics", "dt-obs-predictive-analytics",
                    "dt-alerting", "dt-migration"]
SCOPES_MIN = ["storage:buckets:read", "storage:events:read", "storage:logs:read",
              "storage:metrics:read", "storage:spans:read", "storage:entities:read",
              "storage:smartscape:read", "document:documents:read", "document:documents:write"]
SCOPES_REC = ["storage:bizevents:read", "storage:user.events:read",
              "storage:user.sessions:read", "storage:system:read"]
# Carpetas de skills de los agentes compatibles con agentskills.io (globales y del proyecto).
AGENT_DIRS = [".agents", ".claude", ".codex", ".github", ".cursor", ".kiro", ".junie",
              ".opencode", ".copilot", ".gemini", ".windsurf"]

DOC_DTCTL = "https://docs.dynatrace.com/docs/platform/dtctl"
FIX = {
    "dtctl": (["Descargar el .zip de Windows del último release: https://github.com/dynatrace-oss/dtctl/releases",
               "Extraer dtctl.exe en %LOCALAPPDATA%\\dtctl y agregar esa carpeta al PATH de usuario",
               f"Guía oficial: {DOC_DTCTL}"] if SYSTEM == "Windows" else
              ["brew install dynatrace-oss/tap/dtctl", f"Guía oficial: {DOC_DTCTL}"]),
    "contexto": ["Iniciar sesión: dtctl auth login --context <nombre> --environment https://<tenant>.apps.dynatrace.com",
                 "Cambiar al contexto del incidente: dtctl ctx <nombre>",
                 "Diagnóstico detallado: dtctl doctor"],
    "managed": ["Dynatrace Managed no es compatible con dtctl (la documentación oficial indica dtmgd).",
                "Este RCA requiere un tenant Dynatrace SaaS (https://<tenant>.apps.dynatrace.com)."],
    "scopes": ["Pedir al administrador del tenant los scopes faltantes para el token/cliente OAuth de dtctl",
               "Referencia de scopes: https://github.com/dynatrace-oss/dtctl (TOKEN_SCOPES.md)",
               "Si usas OAuth, vuelve a iniciar sesión tras el cambio: dtctl auth login"],
    "dt_skills": ["npx skills add dynatrace/dynatrace-for-ai",
                  "Claude Code (alternativa): claude plugin install dynatrace@claude-plugins-official"],
    "dtctl_skill": ["dtctl skills install            (detecta el agente)",
                    "dtctl skills install --cross-client --global   (todos los agentes compatibles)"],
    "drawio_skill": ["npx skills add jgraph/drawio-mcp --skill drawio",
                     "Claude Code (alternativa): /plugin marketplace add jgraph/drawio-mcp  y  /plugin install drawio@drawio"],
    "drawio_cli": (["winget install JGraph.Draw"] if SYSTEM == "Windows" else
                   ["brew install --cask drawio"] if SYSTEM == "Darwin" else
                   ["Instalar el .deb/.rpm/AppImage de https://github.com/jgraph/drawio-desktop/releases",
                    "Sin entorno gráfico: exportar con xvfb-run -a <ruta-drawio> ..."]),
    "python": ["Instalar Python 3.9 o superior: https://www.python.org/downloads/"],
}


def run(cmd, timeout=60):
    """Ejecuta un comando y devuelve (código, salida). Nunca lanza excepción."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""
    except OSError as e:
        return 126, str(e)


def fmt_offset(td):
    mins = int(td.total_seconds() // 60)
    sign, mins = ("+" if mins >= 0 else "-"), abs(mins)
    return f"UTC{sign}{mins // 60:02d}:{mins % 60:02d}"


def check(cid, nombre, estado, detalle, solucion=None):
    return {"id": cid, "nombre": nombre, "estado": estado, "detalle": detalle,
            "solucion": solucion or []}


# ---------------------------------------------------------------- R1 / R2 / R3 (dtctl)

def find_dtctl():
    w = shutil.which("dtctl")
    if w:
        return Path(w), True
    extra = []
    if SYSTEM == "Windows" and os.environ.get("LOCALAPPDATA"):
        extra.append(Path(os.environ["LOCALAPPDATA"]) / "dtctl" / "dtctl.exe")
    extra += [Path.home() / ".local" / "bin" / "dtctl", Path("/usr/local/bin/dtctl"),
              Path("/opt/homebrew/bin/dtctl")]
    for p in extra:
        if p.is_file():
            return p, False
    return None, False


def check_dtctl(ctx_args):
    """Devuelve (lista de checks, contexto dict, ruta dtctl)."""
    out, contexto = [], {}
    path, in_path = find_dtctl()
    if not path:
        return [check("R1", "dtctl", FALTA, "no encontrado", FIX["dtctl"])], contexto, None
    rc, txt = run([str(path), "version"], timeout=30)
    m = re.search(r"version\s+v?(\d+\.\d+\.\d+)", txt)
    if rc != 0 or not m:
        return [check("R1", "dtctl", FALTA, f"no responde ({path})", FIX["dtctl"])], contexto, None
    detalle = f"{m.group(1)} ({path})"
    if in_path:
        out.append(check("R1", "dtctl", OK, detalle))
    else:
        out.append(check("R1", "dtctl", AVISO, detalle + " - no está en el PATH",
                         [f"Agregar {path.parent} al PATH, o invocar dtctl con la ruta completa"]))
    return out, contexto, path


def check_context(dtctl, ctx_args, offline):
    contexto = {}
    if offline:
        rc, txt = run([str(dtctl), "ctx", "current", "--no-agent", "--plain"] + ctx_args, timeout=30)
        name = txt.strip().splitlines()[-1].strip() if rc == 0 and txt.strip() else ""
        contexto = {"nombre": name or None, "entorno": None}
        if not name:
            return check("R2", "Contexto dtctl", FALTA, "sin contexto activo", FIX["contexto"]), contexto
        return check("R2", "Contexto dtctl", AVISO,
                     f"{name} - autenticación no verificada (--offline); CONFIRMAR con el usuario"), contexto

    rc, txt = run([str(dtctl), "doctor", "--no-agent"] + ctx_args, timeout=90)
    lines = [re.match(r"^\[(\w+)\]\s+(.+?)\s{2,}(.*)$", l.strip()) for l in txt.splitlines()]
    lines = [m for m in lines if m]
    if not lines:
        return check("R2", "Contexto dtctl", FALTA, "dtctl doctor no devolvió diagnóstico",
                     FIX["contexto"]), contexto
    fallas, avisos = [], []
    for m in lines:
        tag, name, det = m.group(1).upper(), m.group(2).strip(), m.group(3).strip()
        if name.lower() == "token":
            det = "(presente; no se muestra)"
        if name.lower() == "current context":
            cm = re.match(r"^(\S+)\s+\(environment:\s*([^,\s)]+)", det)
            if cm:
                contexto = {"nombre": cm.group(1), "entorno": cm.group(2)}
        if tag in ("FAIL", "FAILED", "ERROR", "ERR", "X"):
            fallas.append(f"{name}: {det}")
        elif tag != "OK":
            avisos.append(f"{name}: {det}")
    env = contexto.get("entorno") or ""
    if re.search(r"/e/[0-9a-f-]{8,}", env):
        return check("R2", "Contexto dtctl", FALTA, f"{env} parece Dynatrace Managed",
                     FIX["managed"]), contexto
    if fallas:
        return check("R2", "Contexto dtctl", FALTA, "; ".join(fallas), FIX["contexto"]), contexto
    det = f"{contexto.get('nombre', '?')} -> {env or '?'} - CONFIRMAR con el usuario que es el tenant del incidente"
    if avisos:
        return check("R2", "Contexto dtctl", AVISO, det + " | " + "; ".join(avisos)), contexto
    return check("R2", "Contexto dtctl", OK, det), contexto


def check_scopes(dtctl, ctx_args):
    rc, txt = run([str(dtctl), "get", "notebooks", "--check-scopes", "-o", "json", "--no-agent"]
                  + ctx_args, timeout=60)
    granted = None
    try:
        data = json.loads(txt[txt.index("{"):]) if "{" in txt else {}
        res = data.get("result", data)
        granted = res.get("granted_scopes")
    except (ValueError, AttributeError):
        pass
    if granted is None:
        return check("R3", "Permisos (scopes)", AVISO,
                     "no se pudieron leer los scopes concedidos; se validarán al primer error insufficient_scope")
    falt_min = [s for s in SCOPES_MIN if s not in granted]
    falt_rec = [s for s in SCOPES_REC if s not in granted]
    if falt_min:
        return check("R3", "Permisos (scopes)", FALTA, "faltan: " + ", ".join(falt_min), FIX["scopes"])
    det = f"{len(SCOPES_MIN)}/{len(SCOPES_MIN)} obligatorios"
    if falt_rec:
        return check("R3", "Permisos (scopes)", AVISO,
                     det + " - recomendados faltantes (limitan el análisis de impacto): " + ", ".join(falt_rec))
    return check("R3", "Permisos (scopes)", OK, det + f" · {len(SCOPES_REC)}/{len(SCOPES_REC)} recomendados")


# ---------------------------------------------------------------- R4 / R5 (skills)

def skill_roots(extra_dirs):
    here = Path(__file__).resolve().parents[1]          # carpeta de esta skill
    roots = [here.parent]                               # skills hermanas (misma instalación)
    for base in (Path.home(), Path.cwd()):
        roots += [base / d / "skills" for d in AGENT_DIRS]
    roots += [Path.home() / ".config" / "opencode" / "skills", Path(".") / "skills"]
    roots += [Path(d) for d in extra_dirs]
    seen, res = set(), []
    for r in roots:
        try:
            rr = r.resolve()
        except OSError:
            continue
        if rr.is_dir() and rr not in seen:
            seen.add(rr)
            res.append(rr)
    return res, here


def skill_name(skill_md):
    try:
        head = skill_md.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return None
    m = re.search(r"^name:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", head, re.M)
    return m.group(1).strip() if m else None


def frontmatter(skill_md):
    try:
        txt = skill_md.read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return ""
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    return m.group(1) if m else ""


def index_skills(extra_dirs):
    """({nombre: [rutas]}, {nombres de skills de draw.io}) de todas las skills encontradas
    (incluye la caché de plugins de Claude Code)."""
    roots, here = skill_roots(extra_dirs)
    found, drawio = {}, set()

    def add(md):
        d = md.parent
        if d.resolve() == here:
            return
        # Cualquier skill que genere diagramas draw.io cumple R5 (jgraph "drawio", "drawio-skill", etc.)
        if re.search(r"draw\.?io", frontmatter(md), re.I):
            drawio.add(skill_name(md) or d.name)
        for n in {skill_name(md), d.name}:
            if n:
                found.setdefault(n, [])
                if str(d) not in found[n]:
                    found[n].append(str(d))

    for r in roots:
        for child in r.iterdir():
            md = child / "SKILL.md"
            if md.is_file():
                add(md)
    plugins = Path.home() / ".claude" / "plugins" / "cache"
    if plugins.is_dir():
        base = len(plugins.parts)
        for dirpath, dirnames, filenames in os.walk(plugins):
            if len(Path(dirpath).parts) - base > 7:
                dirnames[:] = []
                continue
            if "SKILL.md" in filenames:
                add(Path(dirpath) / "SKILL.md")
    return found, drawio, roots


def check_skills(found, drawio):
    out = []
    falt = [s for s in DT_SKILLS_MIN if s not in found]
    dom = [s for s in DT_SKILLS_DOMAIN if s in found]
    if falt:
        out.append(check("R4", "Skills Dynatrace for AI", FALTA, "faltan: " + ", ".join(falt), FIX["dt_skills"]))
    else:
        det = ", ".join(DT_SKILLS_MIN) + f" · dominio: {len(dom)}/{len(DT_SKILLS_DOMAIN)}"
        if not dom:
            out.append(check("R4", "Skills Dynatrace for AI", AVISO,
                             det + " - sin skills dt-obs-* de dominio", FIX["dt_skills"]))
        else:
            out.append(check("R4", "Skills Dynatrace for AI", OK, det + " (" + ", ".join(dom) + ")"))

    draw = sorted(drawio)
    if draw:
        out.append(check("R5", "Skill drawio", OK, ", ".join(draw) + f" ({found[draw[0]][0]})"))
    else:
        out.append(check("R5", "Skill drawio", FALTA, "no encontrada", FIX["drawio_skill"]))

    if "dtctl" in found:
        out.append(check("--", "Skill dtctl (recomendada)", OK, found["dtctl"][0]))
    else:
        out.append(check("--", "Skill dtctl (recomendada)", AVISO, "no instalada", FIX["dtctl_skill"]))
    return out


def drawio_candidates():
    c = []
    if SYSTEM == "Windows":
        for env in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
            if os.environ.get(env):
                c.append(Path(os.environ[env]) / "draw.io" / "draw.io.exe")
        if os.environ.get("LOCALAPPDATA"):
            c.append(Path(os.environ["LOCALAPPDATA"]) / "Programs" / "draw.io" / "draw.io.exe")
    elif SYSTEM == "Darwin":
        c += [Path("/Applications/draw.io.app/Contents/MacOS/draw.io"),
              Path.home() / "Applications" / "draw.io.app" / "Contents" / "MacOS" / "draw.io"]
    else:
        c += [Path("/opt/drawio/drawio"), Path("/usr/bin/drawio"), Path("/usr/local/bin/drawio"),
              Path("/snap/bin/drawio")]
    for n in ("drawio", "draw.io"):
        w = shutil.which(n)
        if w:
            c.append(Path(w))
    seen, res = set(), []
    for p in c:
        k = str(p).lower()
        if k not in seen and p.is_file():
            seen.add(k)
            res.append(p)
    return res


def check_drawio_cli():
    """Prueba candidatos en orden y se queda con el primero que devuelve una versión."""
    for p in drawio_candidates():
        rc, txt = run([str(p), "--version"], timeout=30)
        m = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", txt)
        if rc == 0 and m:
            det = f"{m.group(0)} -> \"{p}\" (usar EXACTAMENTE esta ruta al exportar)"
            sol = []
            on_path = shutil.which("drawio")
            if on_path and Path(on_path).resolve() != p.resolve():
                sol.append(f"El comando 'drawio' del PATH apunta a otro ejecutable ({on_path}); no usarlo")
            if int(m.group(1)) < 30:
                sol.append("Versión < 30: sin conversión Mermaid ni --layout (no bloquea)")
            if SYSTEM == "Linux" and not os.environ.get("DISPLAY"):
                sol.append("Sin DISPLAY: exportar con xvfb-run -a")
            return check("R5", "draw.io Desktop (CLI)", AVISO if sol else OK, det, sol), str(p)
    return check("R5", "draw.io Desktop (CLI)", FALTA, "no encontrado o no responde a --version",
                 FIX["drawio_cli"]), None


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Valida los prerrequisitos del RCA (no instala nada).")
    ap.add_argument("--context", help="contexto dtctl a validar (por defecto, el activo)")
    ap.add_argument("--offline", action="store_true", help="no contactar el tenant (R2/R3 parciales)")
    ap.add_argument("--skills-dir", action="append", default=[], help="carpeta extra de skills")
    ap.add_argument("--json", action="store_true", help="salida JSON para agentes")
    a = ap.parse_args()
    ctx_args = ["--context", a.context] if a.context else []

    checks, contexto, drawio_bin = [], {}, None
    r1, _, dtctl = check_dtctl(ctx_args)
    checks += r1
    if dtctl:
        r2, contexto = check_context(dtctl, ctx_args, a.offline)
        checks.append(r2)
        if a.offline:
            checks.append(check("R3", "Permisos (scopes)", AVISO, "no verificado (--offline)"))
        elif r2["estado"] != FALTA:
            checks.append(check_scopes(dtctl, ctx_args))
        else:
            checks.append(check("R3", "Permisos (scopes)", FALTA, "no verificable sin contexto válido",
                                FIX["contexto"]))
    else:
        checks.append(check("R2", "Contexto dtctl", FALTA, "requiere dtctl", FIX["contexto"]))
        checks.append(check("R3", "Permisos (scopes)", FALTA, "requiere dtctl", FIX["scopes"]))

    found, drawio, roots = index_skills(a.skills_dir)
    checks += check_skills(found, drawio)
    cli, drawio_bin = check_drawio_cli()
    checks.append(cli)
    py = ".".join(map(str, sys.version_info[:3]))
    checks.append(check("R7", "Python", OK if sys.version_info >= (3, 9) else FALTA,
                        f"{py} ({sys.executable})", None if sys.version_info >= (3, 9) else FIX["python"]))
    now = datetime.now().astimezone()
    zona = f"{now.tzname()} ({fmt_offset(now.utcoffset())})"
    checks.append(check("--", "Zona horaria (máquina)", OK,
                        zona + " - hora local del RCA; convertir con scripts/hora_local.py"))

    faltan = sorted({c["id"] for c in checks if c["estado"] == FALTA})
    listo = not faltan
    if a.json:
        print(json.dumps({"listo": listo, "faltan": faltan, "sistema": SYSTEM, "contexto": contexto,
                          "zona_horaria": zona, "drawio_cli": drawio_bin,
                          "skills_roots": [str(r) for r in roots],
                          "checks": checks}, ensure_ascii=True, indent=2))
        sys.exit(0 if listo else 1)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    print(f"Prerrequisitos RCA - dt-custom-rca-jromero  ({SYSTEM}, Python {py})\n")
    for c in checks:
        print(f"[{c['estado']}]".ljust(8) + f"{c['id']:<4}{c['nombre']:<28}{c['detalle']}")
        if c["solucion"]:
            print("        Cómo resolverlo:")
            for s in c["solucion"]:
                print(f"          - {s}")
    print("\nR6 (punto de partida) se valida con el usuario: Problem ID, ID de evento o rango + entidad.")
    if listo:
        print("RESULTADO: LISTO para iniciar el RCA (confirma el contexto con el usuario).")
    else:
        print("RESULTADO: NO LISTO - faltan: " + ", ".join(faltan)
              + ". Detener el RCA y pedir al usuario que lo resuelva.")
    sys.exit(0 if listo else 1)


if __name__ == "__main__":
    main()
