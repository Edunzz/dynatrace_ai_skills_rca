# Dynatrace AI Skills — RCA

Skill abierta para que **cualquier agente de IA** haga un **análisis de causa raíz (RCA)** sobre Dynatrace con `dtctl` y entregue un **Notebook de Dynatrace estandarizado**. El notebook incluye:

- Un resumen ejecutivo que entiende cualquier persona.
- Evidencia DQL reproducible y referencias oficiales.
- Tres diagramas draw.io con estilo Dynatrace.

Sigue el estándar abierto [agentskills.io](https://agentskills.io), así que funciona con Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Kiro, Junie, OpenCode y otros agentes que puedan ejecutar comandos.

![Ejemplo de diagrama de propagación generado por la skill](examples/rca-ejemplo-memoria-net/diagrams/D1-propagacion.png)
*Diagrama de propagación (D1) de un RCA real, con datos anonimizados.*

---

## Contenido

- [Qué obtienes](#qué-obtienes)
- [Instalación rápida](#instalación-rápida)
- [Prerrequisitos](#prerrequisitos)
- [Uso](#uso)
- [Cómo funciona](#cómo-funciona)
- [Ejemplo completo](#ejemplo-completo)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Privacidad](#privacidad)
- [Contribuir](#contribuir)
- [English summary](#english-summary)

## Qué obtienes

Un notebook `RCA | <Problem ID> | <Servicio> | <fecha>` con 10 secciones fijas, escrito para dos audiencias:

| # | Sección | Para quién |
|---|---|---|
| 0 | Portada y ficha del incidente | Todos |
| 1 | Resumen ejecutivo | **Cualquier persona**: sin jerga, máximo 10 líneas, validado automáticamente |
| 2 | Alcance e impacto | Técnico |
| 3 | Línea de tiempo + diagrama D2 | Figura: todos · tabla: técnico |
| 4 | Propagación de la afectación + diagrama D1 | Figura: todos · secuencia: técnico |
| 5 | Causa raíz, 5 porqués + diagrama D3, hipótesis y validación de Davis | Figura: todos · análisis: técnico |
| 6 | Brechas de observabilidad | Técnico |
| 7 | Plan de acción con responsable, fecha y criterio de cierre | Técnico y responsables |
| 8 | Lecciones aprendidas | Todos |
| 9 | Anexos: ventanas, evidencia, glosario, referencias oficiales y versiones | Técnico |

Cada afirmación lleva una sección DQL `[Evidencia N.x]` que se puede volver a ejecutar en el notebook. Cada interpretación cita además documentación oficial `[Rn]`.

**Diagramas con la paleta de Dynatrace (tokens Strato).** El color comunica estado: rojo = error o falla, naranja = degradado, verde = sano, azul = cambio y gris punteado = sin visibilidad.

| Línea de tiempo (D2) | Árbol de 5 porqués (D3) |
|---|---|
| ![D2](examples/rca-ejemplo-memoria-net/diagrams/D2-linea-tiempo.png) | ![D3](examples/rca-ejemplo-memoria-net/diagrams/D3-causa-raiz.png) |

Vista previa del notebook completo de ejemplo: [`examples/rca-ejemplo-memoria-net/NOTEBOOK.md`](examples/rca-ejemplo-memoria-net/NOTEBOOK.md).
Kit visual para los diagramas: [`rca-kit-dynatrace.png`](skills/dt-custom-rca-jromero/assets/drawio/rca-kit-dynatrace.png).

## Instalación rápida

```bash
# Con el instalador de skills (pregunta para qué agente instalar)
npx skills add Edunzz/dynatrace_ai_skills_rca

# O copiando la carpeta en la carpeta de skills de tu agente
git clone https://github.com/Edunzz/dynatrace_ai_skills_rca.git
cp -r dynatrace_ai_skills_rca/skills/dt-custom-rca-jromero ~/.agents/skills/   # compartida por agentes compatibles
```

| Agente | Carpeta de skills del proyecto | Global |
|---|---|---|
| Compartida (agentskills.io) | `.agents/skills/` | `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| OpenAI Codex | `.codex/skills/` | ver documentación del agente |
| GitHub Copilot | `.github/skills/` | ver documentación del agente |
| Cursor | `.cursor/skills/` | — |
| Kiro / Junie / OpenCode | `.kiro/skills/` · `.junie/skills/` · `.opencode/skills/` | ver documentación del agente |

Si tu agente no soporta skills, apúntalo al archivo [`AGENTS.md`](AGENTS.md) o pídele que lea [`skills/dt-custom-rca-jromero/SKILL.md`](skills/dt-custom-rca-jromero/SKILL.md) antes de empezar.
Guía detallada por agente y por sistema operativo: [`docs/instalacion.md`](docs/instalacion.md).

## Prerrequisitos

| # | Qué | Cómo se instala |
|---|---|---|
| R1 | [`dtctl`](https://docs.dynatrace.com/docs/platform/dtctl) | macOS/Linux: `brew install dynatrace-oss/tap/dtctl` · Windows: [releases](https://github.com/dynatrace-oss/dtctl/releases) |
| R2 | Contexto dtctl autenticado contra el tenant **SaaS** del incidente | `dtctl auth login --context <ctx> --environment https://<tenant>.apps.dynatrace.com` |
| R3 | Scopes de lectura de Grail y de lectura/escritura de documentos | Los otorga el administrador del tenant |
| R4 | Skills [Dynatrace for AI](https://github.com/Dynatrace/dynatrace-for-ai) | `npx skills add dynatrace/dynatrace-for-ai` |
| R5 | Una skill de draw.io + draw.io Desktop | `npx skills add jgraph/drawio-mcp --skill drawio` · Windows `winget install JGraph.Draw` · macOS `brew install --cask drawio` |
| R7 | Python 3.9+ | https://www.python.org/downloads/ |

La skill trae un validador que **no instala nada**: revisa todo y, si falta algo, muestra el comando para tu sistema operativo.

```bash
python skills/dt-custom-rca-jromero/scripts/check_prereqs.py            # reporte legible
python skills/dt-custom-rca-jromero/scripts/check_prereqs.py --json     # para agentes
```

```
[OK]    R1  dtctl                       0.37.0 (...\dtctl.exe)
[OK]    R2  Contexto dtctl              mi-tenant -> https://abc12345.apps.dynatrace.com - CONFIRMAR con el usuario...
[OK]    R3  Permisos (scopes)           9/9 obligatorios · 4/4 recomendados
[OK]    R4  Skills Dynatrace for AI     dt-dql-essentials, dt-obs-problems, dt-app-notebooks · dominio: 13/13
[OK]    R5  Skill drawio                drawio
[OK]    R5  draw.io Desktop (CLI)       31.1.8 -> "C:\Program Files\draw.io\draw.io.exe"
[OK]    R7  Python                      3.12.4
[OK]    --  Zona horaria (máquina)      Hora est. Pacífico, Sudamérica (UTC-05:00) - hora local del RCA
RESULTADO: LISTO para iniciar el RCA (confirma el contexto con el usuario).
```

## Uso

Pídeselo al agente en lenguaje natural:

- "Haz el RCA del problema P-1234567"
- "Investiga qué pasó con checkout-service ayer entre las 9:00 y las 10:00 y genera el notebook de RCA"
- "Valida los prerrequisitos del RCA"

El agente:

1. Valida los prerrequisitos y te pide confirmar el tenant.
2. Toma el punto de partida que le diste.
3. Investiga con las skills de Dynatrace.
4. Dibuja los diagramas.
5. Ensambla y valida el notebook.
6. Lo publica.

Al final te entrega el enlace al notebook, la causa raíz en tres líneas con su nivel de certeza y los archivos `.drawio` editables.

Las horas se muestran en UTC y en la **hora local de la máquina** donde corre el agente, sea cual sea tu país; el horario de verano se aplica solo.

## Cómo funciona

![Flujo de la skill](docs/images/flujo-skill.png)

- **La investigación es libre.** El agente decide qué consultar, en qué orden y con qué profundidad. Usa las skills oficiales de Dynatrace y no tiene un guion fijo.
- **Tres cosas son obligatorias:**
  - Los prerrequisitos.
  - El sustento: hechos con evidencia reproducible, interpretaciones con documentación oficial y nivel de certeza declarado.
  - El formato de entrega.
- **Hay validación automática.** `build_notebook.py` bloquea la publicación en estos casos:
  - Falta una sección.
  - Se cita una evidencia o referencia que no existe.
  - El resumen ejecutivo tiene código, DQL o IDs.
  - Falta un diagrama.

Detalle completo: [`docs/como-funciona.md`](docs/como-funciona.md).

## Ejemplo completo

[`examples/rca-ejemplo-memoria-net/`](examples/rca-ejemplo-memoria-net/) es un RCA real con todos los datos anonimizados. Un servicio .NET en Kubernetes fallaba porque su memoria crecía de forma continua hasta acercarse al límite del contenedor. A ese nivel, la recolección de basura detenía la aplicación hasta que el contenedor se reiniciaba.

Incluye las 10 secciones, las 12 queries de evidencia, los 3 diagramas editables y el spec. Se puede volver a ensamblar con un solo comando.

## Estructura del repositorio

```
dynatrace_ai_skills_rca/
├── skills/
│   └── dt-custom-rca-jromero/        la skill (lo que se instala)
│       ├── SKILL.md                  instrucciones para el agente
│       ├── README.md                 guía rápida de la skill
│       ├── scripts/                  check_prereqs.py · build_notebook.py · hora_local.py
│       ├── references/               formato del notebook, diagramas, dtctl, sustento, investigación
│       └── assets/                   spec de ejemplo y kit visual draw.io
├── examples/
│   └── rca-ejemplo-memoria-net/      RCA de ejemplo anonimizado (secciones, queries, diagramas, vista previa)
├── docs/
│   ├── instalacion.md                instalación por agente y sistema operativo
│   ├── como-funciona.md              funcionamiento detallado
│   └── images/                       diagramas de la documentación
├── AGENTS.md                         instrucciones para agentes sin soporte de skills
└── LICENSE
```

## Privacidad

- El ejemplo publicado está **anonimizado**: los nombres de cliente, tenant, servicios, pods, hosts, IDs de entidad y de problema, y las fechas fueron reemplazados. Solo se conservan cifras operativas que no identifican a nadie.
- Las carpetas de trabajo de un RCA real (`rca/`, `rca-*/`) contienen datos del tenant. El `.gitignore` las excluye en la raíz; **no las subas a repositorios públicos**.

## Contribuir

Los issues y pull requests son bienvenidos. Antes de enviar cambios:

```bash
cd examples/rca-ejemplo-memoria-net
python ../../skills/dt-custom-rca-jromero/scripts/build_notebook.py rca_spec.json -o /tmp/notebook.json --strict
```

El ejemplo debe ensamblarse sin errores ni advertencias, y cualquier dato nuevo de ejemplo debe estar anonimizado.

## Licencia

[MIT](LICENSE) © Jose Romero.

## English summary

An open, portable [agentskills.io](https://agentskills.io) skill that lets any AI agent perform a **root cause analysis on Dynatrace** using `dtctl` and the official *Dynatrace for AI* skills. It delivers a standardized **Dynatrace Notebook** with:

- A plain-language executive summary.
- Reproducible DQL evidence for every claim and official documentation references.
- Three draw.io diagrams in Dynatrace style: propagation, timeline and 5-whys.

It includes a cross-platform prerequisite checker, a notebook builder that validates format, evidence and readability, and a fully anonymized real-world example. The documentation is in Spanish.

Install with `npx skills add Edunzz/dynatrace_ai_skills_rca`.
