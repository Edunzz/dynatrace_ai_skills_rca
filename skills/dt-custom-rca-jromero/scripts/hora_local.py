#!/usr/bin/env python3
"""
hora_local.py — Hora local del RCA = zona horaria de la máquina donde se ejecuta el agente.

Funciona en cualquier país: usa la configuración regional del sistema operativo y calcula el
desfase vigente EN CADA INSTANTE (respeta horario de verano), no el desfase de hoy.

Uso:
  python scripts/hora_local.py                                  # zona de la máquina
  python scripts/hora_local.py 2026-09-30T14:02:00Z 2026-09-30T14:09Z   # convierte UTC -> hora local
  python scripts/hora_local.py --json 2026-09-30T14:02:00Z      # salida para agentes
"""
import argparse, json, os, sys
from datetime import datetime, timezone
from pathlib import Path


def iana_name():
    """Nombre IANA si el sistema lo expone (Linux/macOS/TZ); en Windows no está disponible."""
    if os.name == "nt":
        return None
    tz = os.environ.get("TZ", "").lstrip(":")
    if "/" in tz:
        return tz
    tzfile = Path("/etc/timezone")
    if tzfile.is_file():
        name = tzfile.read_text(encoding="utf-8", errors="replace").strip()
        if name:
            return name
    lt = Path("/etc/localtime")
    if lt.is_symlink():
        target = str(lt.resolve())
        if "zoneinfo/" in target:
            return target.split("zoneinfo/", 1)[1]
    return None


def fmt_offset(td):
    mins = int(td.total_seconds() // 60)
    sign = "+" if mins >= 0 else "-"
    mins = abs(mins)
    return f"UTC{sign}{mins // 60:02d}:{mins % 60:02d}"


def parse_utc(s):
    s = s.strip().replace(" ", "T")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def main():
    ap = argparse.ArgumentParser(description="Zona horaria de la máquina y conversión UTC -> hora local.")
    ap.add_argument("utc", nargs="*", help="instantes en UTC (ISO-8601)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    now = datetime.now().astimezone()
    zona = {"nombre_sistema": now.tzname(), "iana": iana_name(), "desfase_actual": fmt_offset(now.utcoffset())}
    zona["etiqueta"] = f"{zona['iana'] or zona['nombre_sistema']} ({zona['desfase_actual']})"
    conv = []
    for s in a.utc:
        try:
            u = parse_utc(s)
        except ValueError:
            print(f"Fecha no válida: {s}", file=sys.stderr)
            sys.exit(1)
        loc = u.astimezone()  # reglas del sistema operativo para ESE instante
        conv.append({"utc": u.strftime("%Y-%m-%d %H:%M"), "local": loc.strftime("%Y-%m-%d %H:%M"),
                     "hora_local": loc.strftime("%H:%M"), "desfase": fmt_offset(loc.utcoffset())})

    if a.json:
        print(json.dumps({"zona": zona, "conversiones": conv}, ensure_ascii=True, indent=2))
        return
    print(f"Zona horaria de la máquina: {zona['etiqueta']}")
    desfases = sorted({c["desfase"] for c in conv})
    for c in conv:
        print(f"  {c['utc']} UTC  ->  {c['local']}  ({c['desfase']})")
    if len(desfases) > 1:
        print("  Atención: el desfase cambia dentro de la ventana (horario de verano); indicarlo por fila.")


if __name__ == "__main__":
    main()
