---
name: dt-custom-rca-jromero
description: Lineamientos y estándar de entrega para que un agente realice un RCA (Root Cause Analysis) en Dynatrace con dtctl y las skills oficiales Dynatrace for AI, y entregue el resultado como Notebook de Dynatrace con estructura estandarizada, un resumen ejecutivo que entiende cualquier persona y diagramas draw.io con estilo Dynatrace incrustados. Incluye un validador de prerrequisitos (dtctl y su contexto, permisos, skills dt-*, skill drawio y draw.io Desktop) que se ejecuta antes de empezar. Usar cuando el usuario pida "RCA", "análisis de causa raíz", "post-mortem", "informe de incidente", "investiga el problema P-XXXX", "genera el notebook de RCA" o "valida los prerrequisitos del RCA". No reemplaza a las skills de Dynatrace ni restringe la investigación.
license: MIT
compatibility: Cualquier agente compatible con agentskills.io que ejecute comandos de shell (Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Kiro, Junie, OpenCode, etc.). Requiere dtctl con contexto autenticado a Dynatrace SaaS, Python 3.9+, skills Dynatrace for AI, una skill de draw.io y draw.io Desktop.
metadata:
  author: Edunzz (Jose Eduardo Romero Jimenez)
  version: "2.1.0"
  language: es
  repository: https://github.com/Edunzz/dynatrace_ai_skills_rca
---

# dt.custom.RCA.jromero — Lineamientos de RCA y estándar de entrega

## Qué es y qué no es esta skill

| Esta skill **SÍ** | Esta skill **NO** |
|---|---|
| Valida los requisitos para trabajar con un script (dtctl con contexto, permisos, skills Dynatrace, drawio) | Dice qué queries ejecutar ni en qué orden |
| Da **lineamientos** y buenas prácticas de investigación RCA | Limita fuentes de datos, número de queries, ventanas de tiempo ni profundidad |
| Define el **estándar de sustento** (evidencia + documentación oficial) | Reemplaza a `dt-dql-essentials`, `dt-obs-*` ni `dt-app-notebooks` |
| **Estandariza la respuesta**: Notebook con estructura, formato y diagramas con estilo Dynatrace | Restringe el razonamiento del agente o le impide seguir pistas |

**Principio rector — autonomía de investigación:** el objetivo es saber qué pasó. El agente investiga con total libertad: sigue cualquier pista, consulta cualquier fuente de datos de Grail, amplía o cambia ventanas, itera hipótesis las veces que haga falta y usa cualquier skill de Dynatrace que aplique. Los lineamientos son una **guía de calidad y cobertura**, no una secuencia obligatoria ni un límite. Lo único rígido es: (1) los requisitos de la Sección 1, (2) el sustento de las afirmaciones y (3) el formato de entrega.

**Jerarquía de autoridad** (si hay conflicto, gana la primera):
1. Documentación oficial de Dynatrace / del fabricante y la ayuda de la CLI (`dtctl <comando> --help`).
2. Skills oficiales Dynatrace for AI (cómo consultar, campos, DQL, notebooks).
3. Esta skill (lineamientos de RCA y formato de entrega).

## Flujo de punta a punta

```
1. Prerrequisitos ─► python <skill>/scripts/check_prereqs.py → si algo FALTA: detenerse
2. Ancla ──────────► Problem ID / evento / rango + entidad (hora local = zona de la máquina)
3. Investigación ──► libre, solo lectura; skills dt-obs-* según el mapa
4. Sustento ───────► hecho = Evidencia N.x (.dql reproducible); interpretación = + [Rn] oficial
5. Redacción ──────► secciones 0–9; resumen y figuras entendibles por cualquier persona
6. Diagramas ──────► D1, D2, D3 con draw.io y el kit de estilo Dynatrace
7. Ensamblado ─────► build_notebook.py (incrusta PNG y valida formato, sustento y lectura)
8. Publicación ────► dtctl apply --dry-run → dtctl apply → respuesta final
```

## Archivos

| Archivo | Para qué |
|---|---|
| `scripts/check_prereqs.py` | **Gate**: valida R1–R5 y R7 e indica cómo resolver lo que falte (no instala nada) |
| `scripts/build_notebook.py` | Ensambla el notebook, incrusta imágenes y valida formato, sustento y legibilidad |
| `scripts/hora_local.py` | Zona horaria de la máquina y conversión de horas UTC → hora local (respeta horario de verano) |
| `references/lineamientos-investigacion.md` | Principios, buenas prácticas y checklist de cobertura de un RCA |
| `references/dtctl-lineamientos.md` | Uso seguro y trazable de dtctl (no limita qué se consulta) |
| `references/senales-y-skills.md` | Mapa de preguntas del RCA → skill de Dynatrace a cargar |
| `references/fuentes-oficiales.md` | Estándar de sustento y citación |
| `references/formato-notebook.md` | **Plantilla obligatoria** del notebook y reglas por audiencia |
| `references/drawio-diagramas.md` | Estándar de los diagramas y estilo Dynatrace (tokens Strato) |
| `assets/drawio/rca-kit-dynatrace.drawio` | Kit visual para copiar: nodos, flechas, línea de tiempo, banda de marca y leyenda (vista previa `.png`) |
| `assets/rca_spec.example.json` | Ejemplo de entrada de `build_notebook.py` |

---

## 1. Prerrequisitos (gate — sin esto NO se inicia)

Ejecutar al inicio, desde cualquier carpeta:

```bash
python <ruta-de-esta-skill>/scripts/check_prereqs.py           # reporte legible
python <ruta-de-esta-skill>/scripts/check_prereqs.py --json    # salida estructurada
python <ruta-de-esta-skill>/scripts/check_prereqs.py --context <ctx>   # validar otro contexto
```

| # | Requisito | Qué valida el script | Si falta |
|---|---|---|---|
| R1 | `dtctl` instalado | `dtctl version` (y si está en el PATH) | El script muestra el comando de instalación según el sistema operativo |
| R2 | **Contexto dtctl activo, autenticado, SaaS** | `dtctl doctor`: contexto, URL, token, conectividad, autenticación; detecta Managed | `dtctl auth login --context <ctx> --environment https://<tenant>.apps.dynatrace.com` |
| R3 | Lectura de Grail y documentos + escritura de documentos | `--check-scopes`: 9 scopes obligatorios y 4 recomendados | Pedir los scopes faltantes al administrador del tenant |
| R4 | **Skills Dynatrace for AI**: `dt-dql-essentials`, `dt-obs-problems`, `dt-app-notebooks` + las `dt-obs-*` del dominio | Busca en las carpetas de skills de todos los agentes compatibles | `npx skills add dynatrace/dynatrace-for-ai` |
| R5 | **Cualquier skill de draw.io** (jgraph `drawio`, `drawio-skill` u otra que genere `.drawio`) + **draw.io Desktop** | Skill instalada y CLI que responde a `--version`; reporta la **ruta exacta** a usar | `npx skills add jgraph/drawio-mcp --skill drawio`; instalar draw.io Desktop |
| R6 | Punto de partida del incidente | Lo valida el agente (Sección 2) | Pedirlo al usuario |
| R7 | Python 3.9+ | Versión del intérprete | Instalar Python |

Reglas del gate:
- Resultado **NO LISTO** (algún `FALTA`): detenerse, mostrar al usuario exactamente lo que falta con los comandos del script y esperar. No buscar sustitutos ni avanzar parcialmente. Si el usuario pide instalarlo, ejecutar los comandos sugeridos con su aprobación.
- `AVISO` no bloquea, pero se informa (p. ej. skill `dtctl` recomendada, scopes recomendados faltantes, `drawio` del PATH que apunta a otro ejecutable).
- **Confirmar siempre con el usuario** que el contexto reportado es el tenant del incidente. Si no lo es, usar `--context <ctx>` en cada comando en vez de cambiar el contexto global.
- Dynatrace Managed: dtctl no aplica (la documentación oficial indica `dtmgd`); informar y detenerse.
- Si el script no puede ejecutarse (sin Python), validar a mano con `dtctl version`, `dtctl doctor` y la lista de skills, con los mismos criterios.

Mensaje estándar cuando falta algo (adaptar la lista):

> Para ejecutar el RCA necesito que estén disponibles: <lista de faltantes con el comando de instalación/configuración>. Avísame cuando esté listo y continúo. No usaré herramientas alternativas.

---

## 2. Punto de partida (no es un límite)

Para no escanear el tenant a ciegas, el agente necesita **al menos uno**: Problem ID de Davis, ID de evento de referencia, o rango de fecha/hora de la afectación + servicio/aplicación/entidad afectada. Si no lo tiene, lo pide una sola vez.

**Hora local** = zona horaria de la máquina donde se ejecuta el agente (la reporta `check_prereqs.py`). Así el RCA sirve en cualquier país sin preguntar. Las horas se convierten con `python <skill>/scripts/hora_local.py <utc> ...`, que aplica el desfase vigente en cada fecha.

Ese dato es el **ancla de inicio**, no el perímetro: el agente puede ampliar ventanas, incorporar otras entidades, revisar recurrencia histórica o cualquier otra línea que la evidencia sugiera. Solo debe **registrar en el Anexo 9.1 qué ventanas/alcances usó y por qué**, para que el RCA sea reproducible.

---

## 3. Lineamientos de investigación (guía, no guion)

Detalle en `references/lineamientos-investigacion.md`. En síntesis, un buen RCA:

- Parte del Problem/evento/rango, pero **valida** lo que propone Davis en vez de asumirlo.
- Cuantifica el **impacto** y reconstruye la **propagación** por la topología.
- Busca **cambios** (deploys, configuración, infraestructura, tráfico) y compara contra **baseline**.
- Correlaciona métricas, traces, logs y eventos; formula **hipótesis** y las confirma o descarta con evidencia.
- Distingue **disparador, causa raíz, factores contribuyentes y mitigantes**; llega a una causa accionable (5 porqués), sin culpar personas.
- Mide **MTTD / MTTA / MTTR** y registra las **brechas de observabilidad** que encuentre (`dtctl inventory` ayuda a evidenciarlas).

El agente decide cómo, en qué orden y con qué profundidad. La checklist de cobertura sirve para no dejar huecos antes de entregar, no para restringir.

Cómo consultar: **lo definen las skills de Dynatrace** (`dt-dql-essentials` y `dt-obs-*`, ver `references/senales-y-skills.md`) y la ayuda de dtctl. Esta skill no impone queries.

---

## 4. Estándar de sustento (obligatorio)

Detalle en `references/fuentes-oficiales.md`.
- **Hechos** → evidencia reproducible del tenant obtenida con dtctl (incluida en el notebook como sección DQL `[Evidencia N.x]`).
- **Interpretaciones** (cómo funciona Davis, qué significa un campo/métrica, qué provoca un error de la tecnología) → además, **documentación oficial** de Dynatrace o del fabricante, citada como `[Rn]`.
- Sin sustento completo → `⚠️ Hipótesis no confirmada:` + qué faltaría para confirmarla.
- No se concluye sobre resultados truncados, con límite de escaneo alcanzado o muestreados: se re-consulta hasta tener el dato completo (ver `references/dtctl-lineamientos.md`).

---

## 5. Estándar de entrega (obligatorio)

### 5.1 Estructura mínima del notebook
Las secciones y su orden son fijos; **el contenido dentro de cada sección no tiene límite** (se agregan subsecciones, tablas y evidencias que hagan falta).

| # | Sección | Imagen draw.io | Lector |
|---|---|---|---|
| 0 | Portada y ficha del incidente | — | Todos (referencia rápida) |
| 1 | Resumen ejecutivo | — | **Cualquier persona** |
| 2 | Alcance e impacto | — | Técnico |
| 3 | Línea de tiempo de los sucesos | D2 | Figura: cualquier persona · tabla: técnico |
| 4 | Diagrama de propagación de la afectación | D1 | Figura: cualquier persona · secuencia: técnico |
| 5 | Análisis de causa raíz | D3 | Figura: cualquier persona · análisis: técnico |
| 6 | Brechas de observabilidad detectadas | — | Técnico |
| 7 | Plan de acción | — | Técnico y responsables |
| 8 | Lecciones aprendidas | — | Todos |
| 9 | Anexos (anclaje y ventanas, evidencia, glosario, referencias oficiales, versiones) | — | Técnico |

Plantilla exacta (títulos, tablas, columnas, indicadores, horas UTC + hora local): `references/formato-notebook.md`.

### 5.2 Resumen ejecutivo y figuras: para cualquier persona
El documento es técnico, pero **empieza por un resumen que entiende cualquiera**: gerencia, negocio, el cliente. Regla de oro: si alguien que no conoce Dynatrace ni la arquitectura leyera solo la Sección 1, debe entender qué pasó, a quién afectó, por qué, cómo se resolvió y qué se hará.
- Sin código, DQL, IDs de entidad, nombres de métricas ni siglas técnicas.
- Componentes por su función de negocio ("el servicio de pagos"); el nombre técnico, si hace falta, entre paréntesis una vez.
- Impacto en personas, operaciones, montos y minutos. Máximo 10 líneas, frases cortas, sin culpar personas.
- Cada figura lleva título simple, una línea "cómo leer este diagrama" y un pie `*Figura N. …*` con la lectura principal en una frase.
- `build_notebook.py` bloquea código, DQL, IDs y más de 10 líneas en el resumen, y advierte la jerga técnica.

### 5.3 Imágenes con estilo Dynatrace
- Todas con la skill **drawio** (D1, D2, D3 mínimo; se pueden agregar más). Si no está instalada → gate R5.
- **Estilo Dynatrace con color semántico**: paleta de los design tokens Strato. La marca (banda azul → violeta) va en el marco; dentro del diagrama, **rojo = error o falla** (la causa raíz además con borde grueso y la etiqueta CAUSA RAÍZ), naranja = degradado, verde = sano, azul = cambio, gris punteado = sin visibilidad.
- Partir del kit `assets/drawio/rca-kit-dynatrace.drawio` (copiar celdas y estilos). Estilos exactos y reglas de D1/D2/D3 en `references/drawio-diagramas.md`.
- Exportar PNG con XML embebido usando la ruta de draw.io que reporta `check_prereqs.py`, revisar cada imagen visualmente e **incrustarla dentro del notebook** como `data:image/png;base64`. Nunca URL externa ni ruta local.

### 5.4 Estructura de trabajo, ensamblado y publicación

```
rca/                          (o rca-<Problem ID>/ si hay varios RCA en la misma carpeta)
├── rca_spec.json             orden de secciones (partir de assets/rca_spec.example.json)
├── sections/                 00-portada.md … 09-anexos.md
├── queries/                  E<N.x>-<descripcion>.dql   (las mismas ejecutadas con dtctl)
├── evidence/                 E<N.x>.json + INDEX.md     (ventana, registros, advertencias, qué sustenta)
├── diagrams/                 D1-propagacion · D2-linea-tiempo · D3-causa-raiz  (.drawio + .png)
└── notebook.json             salida de build_notebook.py (regenerable; según la versión, dtctl apply lo borra al publicar)
```

1. Imágenes en los `.md` como `![Alt](img:../diagrams/D1-propagacion.png)` (relativas al `.md` o al spec).
2. `python <skill>/scripts/build_notebook.py rca/rca_spec.json -o rca/notebook.json` → corregir **todos** los errores. Las advertencias también se revisan; con `--strict` bloquean.
3. Publicar siguiendo `dt-app-notebooks`: `dtctl apply -f rca/notebook.json --dry-run` (valida todas las queries contra el tenant sin publicar) y luego `dtctl apply -f rca/notebook.json` (añadir `--context <ctx>` si aplica).
4. Para actualizar un RCA ya publicado: descargar primero (`dtctl get notebook <id> -o json --plain`), aplicar los cambios sobre ese archivo (conserva el `id`) y `dtctl apply`. Reflejar también los cambios en `rca/sections/` para no perderlos en una próxima regeneración.

### 5.5 Checklist de entrega
- [ ] Gate R1–R7 cumplido (`check_prereqs.py` → LISTO) y contexto confirmado con el usuario.
- [ ] Ancla, zona horaria y ventanas usadas registradas (ficha y 9.1).
- [ ] Cada afirmación de las Secciones 1, 4 y 5 tiene Evidencia N.x y, si interpreta comportamiento, `[Rn]`.
- [ ] Nivel de certeza de la causa raíz declarado.
- [ ] Resumen ejecutivo entendible por cualquier persona (prueba de la regla de oro).
- [ ] Estructura mínima completa; D1, D2, D3 con estilo Dynatrace, revisadas e incrustadas en base64.
- [ ] Plan de acción con responsable, fecha, origen y criterio de cierre.
- [ ] Sin secretos/PII; lenguaje blameless; horas UTC + hora local.
- [ ] `build_notebook.py` sin errores y `dtctl apply --dry-run` sin errores.

Respuesta final al usuario: nombre, ID y enlace del notebook (`/ui/apps/dynatrace.notebooks/notebook/<id>`), causa raíz en 3 líneas con nivel de certeza, y archivos `.drawio` fuente.
