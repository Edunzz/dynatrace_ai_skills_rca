# Instalación

La skill es una carpeta estándar de [agentskills.io](https://agentskills.io): `skills/dt-custom-rca-jromero/` con un `SKILL.md`, scripts y referencias. Instalarla es copiar esa carpeta donde tu agente busca skills. No requiere servidores ni plugins.

## 1. Instalar la skill

### Opción A — instalador de skills (recomendada)

```bash
npx skills add Edunzz/dynatrace_ai_skills_rca
```

El instalador detecta la skill dentro de `skills/` y pregunta para qué agente instalarla. Con `--agent <agente>` puedes indicarlo directamente. Requiere Node.js.

### Opción B — copia manual

```bash
git clone https://github.com/Edunzz/dynatrace_ai_skills_rca.git
```

Copia `dynatrace_ai_skills_rca/skills/dt-custom-rca-jromero/` en una de estas carpetas:

| Agente | Proyecto (solo ese repositorio) | Global (todos tus proyectos) |
|---|---|---|
| Cualquier agente compatible con agentskills.io | `.agents/skills/` | `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| OpenAI Codex | `.codex/skills/` | según la documentación de Codex |
| GitHub Copilot | `.github/skills/` | según la documentación de Copilot |
| Cursor | `.cursor/skills/` | — |
| Kiro | `.kiro/skills/` | — |
| Junie | `.junie/skills/` | según la documentación de Junie |
| OpenCode | `.opencode/skills/` | según la documentación de OpenCode |

En Windows, `~` es `%USERPROFILE%`. Por ejemplo, `C:\Users\<usuario>\.claude\skills\dt-custom-rca-jromero\SKILL.md`.

### Opción C — agentes sin soporte de skills

Los agentes que leen `AGENTS.md` toman las instrucciones del [`AGENTS.md`](../AGENTS.md) de este repositorio. En cualquier otro caso, pídele al agente al inicio de la conversación:

> Lee `skills/dt-custom-rca-jromero/SKILL.md` y sus referencias, y sigue ese estándar para hacer el RCA.

## 2. Instalar los prerrequisitos

| # | Requisito | Windows | macOS / Linux |
|---|---|---|---|
| R1 | `dtctl` | Descargar el `.zip` de https://github.com/dynatrace-oss/dtctl/releases, extraer `dtctl.exe` en `%LOCALAPPDATA%\dtctl` y agregar esa carpeta al PATH | `brew install dynatrace-oss/tap/dtctl` |
| R2 | Contexto autenticado (SaaS) | `dtctl auth login --context <ctx> --environment https://<tenant>.apps.dynatrace.com` | igual |
| R3 | Scopes | Lectura de Grail (`storage:*:read`, `storage:buckets:read`) y `document:documents:read/write`; los otorga el administrador del tenant | igual |
| R4 | Skills Dynatrace for AI | `npx skills add dynatrace/dynatrace-for-ai` | igual |
| R5 | Skill de draw.io | `npx skills add jgraph/drawio-mcp --skill drawio` (sirve cualquier skill que genere `.drawio`) | igual |
| R5 | draw.io Desktop | `winget install JGraph.Draw` | `brew install --cask drawio` · Linux: `.deb`, `.rpm` o AppImage de https://github.com/jgraph/drawio-desktop/releases |
| R7 | Python 3.9+ | https://www.python.org/downloads/ | normalmente ya instalado |
| — | Recomendado: skill de dtctl | `dtctl skills install` | igual |

**Dynatrace Managed no es compatible**: dtctl solo funciona con Dynatrace SaaS.

## 3. Verificar

```bash
python <carpeta-de-la-skill>/scripts/check_prereqs.py
```

| Opción | Para qué |
|---|---|
| `--context <ctx>` | Validar un contexto de dtctl distinto del activo, sin cambiarlo |
| `--offline` | No contactar el tenant: valida la instalación, pero no la autenticación ni los permisos |
| `--json` | Salida estructurada para agentes |
| `--skills-dir <dir>` | Agregar una carpeta de skills no estándar a la búsqueda |

Códigos de salida: `0` = listo, `1` = falta algún requisito obligatorio. El resultado `AVISO` no bloquea.

## 4. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `draw.io Desktop (CLI)` en AVISO: el `drawio` del PATH apunta a otro ejecutable | En Windows, winget puede dejar en el PATH un ejecutable que no responde | Usar la ruta exacta que reporta el script; el agente lo hace solo |
| R2 FALTA: contexto no encontrado | El contexto no existe o expiró la sesión OAuth | `dtctl ctx` para listar contextos; `dtctl auth login` para renovar |
| R3 FALTA `document:documents:write` | Sin permiso para publicar notebooks | Pedirlo al administrador del tenant |
| R2 FALTA con URL `/e/<id>` | Es Dynatrace Managed | No compatible con dtctl |
| R4 FALTA aunque las skills están instaladas | Están en una carpeta no estándar | `check_prereqs.py --skills-dir <carpeta>` |
| `build_notebook.py`: "Se cita Evidencia N.x pero no existe" | Falta la sección DQL `[Evidencia N.x]` en el spec | Agregarla o corregir la cita |
| `build_notebook.py`: el resumen ejecutivo no pasa | Tiene código, IDs o más de 10 líneas | Reescribirlo como lo contaría el negocio |
