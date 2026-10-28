# dt-custom-rca-jromero — RCA en Dynatrace con entrega estandarizada

Skill portable (estándar abierto [agentskills.io](https://agentskills.io)) para que un agente de IA haga un **análisis de causa raíz (RCA)** sobre un tenant Dynatrace SaaS usando `dtctl` y las skills oficiales *Dynatrace for AI*. El resultado es un **Notebook de Dynatrace** con:

- Un resumen ejecutivo que entiende cualquier persona.
- Evidencia DQL re-ejecutable y referencias oficiales.
- Tres diagramas draw.io con estilo Dynatrace: propagación, línea de tiempo y 5 porqués.

Funciona con cualquier agente compatible con skills (Claude Code, Codex, GitHub Copilot, Cursor, etc.).

**Autor:** Edunzz (Jose Eduardo Romero Jimenez) · **Versión:** 2.1.0 · **Idioma:** español

## 1. Instalación

Copia la carpeta `dt-custom-rca-jromero/` en la carpeta de skills de tu agente:

| Agente | Carpeta global |
|---|---|
| Cualquier agente compatible (compartida) | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| Otros | La carpeta de skills que indique tu agente (también sirve a nivel de proyecto: `.<agente>/skills/`) |

Desde el repositorio público (instala para el agente que elijas): `npx skills add Edunzz/dynatrace_ai_skills_rca`. Guía completa por agente: https://github.com/Edunzz/dynatrace_ai_skills_rca/blob/main/docs/instalacion.md

## 2. Prerrequisitos

| # | Qué | Cómo se instala |
|---|---|---|
| R1 | `dtctl` | macOS/Linux: `brew install dynatrace-oss/tap/dtctl` · Windows: release de https://github.com/dynatrace-oss/dtctl/releases |
| R2 | Contexto dtctl autenticado contra el tenant **SaaS** del incidente | `dtctl auth login --context <ctx> --environment https://<tenant>.apps.dynatrace.com` |
| R3 | Scopes de lectura de Grail y de lectura/escritura de documentos | Los otorga el administrador del tenant |
| R4 | Skills Dynatrace for AI (`dt-dql-essentials`, `dt-obs-problems`, `dt-app-notebooks`, `dt-obs-*`) | `npx skills add dynatrace/dynatrace-for-ai` |
| R5 | Cualquier skill de draw.io + draw.io Desktop | `npx skills add jgraph/drawio-mcp --skill drawio` · Windows `winget install JGraph.Draw` · macOS `brew install --cask drawio` |
| R7 | Python 3.9+ | https://www.python.org/downloads/ |
| — | Recomendado: skill de dtctl | `dtctl skills install` |

**Valídalos en un paso** (no instala nada; dice qué falta y cómo resolverlo):

```bash
python <carpeta-de-la-skill>/scripts/check_prereqs.py
```

```
[OK]    R1  dtctl                       0.37.0 (...\dtctl.exe)
[OK]    R2  Contexto dtctl              prod -> https://abc12345.apps.dynatrace.com - CONFIRMAR con el usuario...
[OK]    R3  Permisos (scopes)           9/9 obligatorios · 4/4 recomendados
[OK]    R4  Skills Dynatrace for AI     dt-dql-essentials, dt-obs-problems, dt-app-notebooks · dominio: 13/13
[OK]    R5  Skill drawio                drawio
[OK]    R5  draw.io Desktop (CLI)       31.1.8 -> "C:\Program Files\draw.io\draw.io.exe"
[OK]    R7  Python                      3.12.4
RESULTADO: LISTO para iniciar el RCA (confirma el contexto con el usuario).
```

Opciones: `--context <ctx>` valida otro contexto · `--offline` no contacta el tenant · `--json` da salida para agentes · `--skills-dir <dir>` agrega una carpeta de skills.

## 3. Uso

Pídeselo al agente en lenguaje natural:

- "Haz el RCA del problema P-2609301"
- "Investiga qué pasó con checkout-service ayer entre las 9:00 y las 10:00 y genera el notebook de RCA"

Las horas se muestran en UTC y en la **hora local de tu máquina**, sea cual sea tu país. El horario de verano se aplica solo.
- "Valida los prerrequisitos del RCA"

El agente:
1. Valida los prerrequisitos y te pide confirmar el tenant.
2. Te pide el punto de partida y la zona horaria, si faltan.
3. Investiga con las skills de Dynatrace.
4. Dibuja los diagramas.
5. Ensambla y valida el notebook, y lo publica.

Al final te entrega el enlace al notebook, la causa raíz en 3 líneas con su nivel de certeza y los archivos `.drawio` fuente.

## 4. Qué entrega

**Notebook** `RCA | <Problem ID> | <Servicio> | <YYYY-MM-DD>`:

| # | Sección | Para quién |
|---|---|---|
| 0 | Portada y ficha del incidente | Todos |
| 1 | Resumen ejecutivo | **Cualquier persona** (sin jerga, máx. 10 líneas) |
| 2 | Alcance e impacto | Técnico |
| 3 | Línea de tiempo + figura D2 | Figura: todos |
| 4 | Propagación de la afectación + figura D1 | Figura: todos |
| 5 | Causa raíz, 5 porqués + figura D3, hipótesis, validación de Davis | Figura: todos |
| 6 | Brechas de observabilidad | Técnico |
| 7 | Plan de acción (responsable, fecha, criterio de cierre) | Técnico y responsables |
| 8 | Lecciones aprendidas | Todos |
| 9 | Anexos: ventanas y evidencia, glosario, referencias oficiales, versiones | Técnico |

**Carpeta de trabajo** (queda en tu directorio para auditar o regenerar):

```
rca/
├── rca_spec.json        orden de secciones
├── sections/            00-portada.md … 09-anexos.md
├── queries/             E<N.x>-*.dql   (las mismas queries ejecutadas con dtctl)
├── evidence/            resultados + INDEX.md
├── diagrams/            D1/D2/D3 .drawio (editables) + .png
└── notebook.json        regenerable con build_notebook.py (algunas versiones de dtctl lo borran al publicar)
```

## 5. Estilo de los diagramas

Paleta de los design tokens **Strato** de Dynatrace (tema claro). La marca va en una banda azul → violeta en la parte superior. Dentro del diagrama el color indica estado:

| Color | Significa |
|---|---|
| Rojo intenso, borde grueso, etiqueta CAUSA RAÍZ | Causa raíz |
| Rojo claro | Con errores / falla |
| Naranja | Degradado (lento o parcial) |
| Verde | Sano |
| Azul | Cambio / deploy |
| Gris punteado | Sin visibilidad (sin monitoreo) |

Kit para copiar: `assets/drawio/rca-kit-dynatrace.drawio` · vista previa: `assets/drawio/rca-kit-dynatrace.png`.

## 6. Contenido de la skill

```
dt-custom-rca-jromero/
├── SKILL.md                         instrucciones para el agente
├── README.md                        esta guía
├── scripts/
│   ├── check_prereqs.py             gate de prerrequisitos (R1–R7)
│   ├── build_notebook.py            ensambla y valida el notebook
│   └── hora_local.py                UTC -> hora local de la máquina
├── references/
│   ├── formato-notebook.md          plantilla obligatoria por sección
│   ├── drawio-diagramas.md          D1/D2/D3 + estilos exactos Dynatrace
│   ├── lineamientos-investigacion.md
│   ├── dtctl-lineamientos.md
│   ├── senales-y-skills.md          pregunta del RCA → skill a cargar
│   └── fuentes-oficiales.md         estándar de sustento y citación
└── assets/
    ├── rca_spec.example.json
    └── drawio/rca-kit-dynatrace.drawio + .png
```

## 7. Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `draw.io Desktop (CLI)` en AVISO: el `drawio` del PATH apunta a otro ejecutable | Usar la ruta exacta que reporta el script (el agente lo hace solo) |
| R3 FALTA `document:documents:write` | Sin ese scope no se puede publicar el notebook; pedirlo al administrador |
| R2 FALTA con URL `/e/<id>` | Es Dynatrace Managed: dtctl no aplica |
| `build_notebook.py` falla con "Se cita Evidencia N.x pero no existe" | Falta la sección DQL `[Evidencia N.x]` en el spec, o el número está mal citado |
| El resumen ejecutivo no pasa la validación | Quitar código, IDs y siglas; contarlo como lo vivió el negocio |

## 8. Cambios

- **2.1.0**:
  - Validador de prerrequisitos portable (`check_prereqs.py`).
  - Resumen ejecutivo para cualquier persona, validado automáticamente.
  - Diagramas con paleta Dynatrace (Strato), con kit y leyenda estándar.
  - Hora local = zona horaria de la máquina, sirve en cualquier país (antes fija en Lima).
  - R5 acepta cualquier skill de draw.io.
  - `build_notebook.py` valida además subsecciones, figuras por sección, evidencias y referencias cruzadas, y placeholders; repara PNG truncados.
  - Mapa de skills corregido y ampliado.
- **2.0.0**: versión base (lineamientos, sustento, plantilla del notebook, D1/D2/D3).
