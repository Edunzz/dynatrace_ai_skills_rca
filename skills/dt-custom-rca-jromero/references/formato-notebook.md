# Formato obligatorio del Notebook RCA

Esta es la plantilla **mínima** obligatoria. Reemplaza `<...>` con datos reales. No cambies títulos, orden ni columnas de las tablas definidas. **Sí puedes agregar** subsecciones (`### N.x`), tablas, filas, evidencias DQL y diagramas draw.io adicionales en cualquier sección cuando aporten al análisis: la plantilla fija el piso, no el techo. Si un dato no existe, escribe `N/D` y explica en una línea por qué (y, si aplica, regístralo como brecha en la Sección 6).

## Audiencias del documento

| Parte | Lector | Cómo se escribe |
|---|---|---|
| Sección 1 (Resumen ejecutivo) y figuras D1, D2, D3 | **Cualquier persona**: gerencia, negocio, cliente, equipos no técnicos | Lenguaje simple, sin jerga ni código; se entiende sin leer el resto |
| Sección 0 (ficha) | Referencia rápida para todos | Datos clave; los términos técnicos se explican en 9.2 Glosario |
| Secciones 2 a 9 | Equipos técnicos (SRE, desarrollo, operaciones) | Técnico, con evidencia y referencias oficiales |

## Reglas generales de formato

| Regla | Detalle |
|---|---|
| Nombre del notebook | `RCA \| <Problem ID> \| <Servicio/Aplicación> \| <YYYY-MM-DD>` |
| Encabezado de sección | `## N. Título` (H2). Subsecciones `### N.x Título` (H3). Solo la portada usa H1. |
| Una sección markdown por bloque lógico | Cada sección numerada = 1 sección markdown principal + sus DQL de evidencia debajo. |
| Compacto | Sin líneas en blanco dobles, sin `&nbsp;`, sin HTML, sin `<br>`. Una línea en blanco solo antes/después de tablas e imágenes. |
| Tablas | Markdown estándar (`\| col \|` + `\|---\|`). Nunca tablas con caracteres de dibujo. |
| Viñetas | `-` con 2 espacios por nivel de anidación. Máx. 3 niveles. |
| Énfasis | `**negrita**` solo para valores clave (cifras de impacto, causa raíz). Sin cursivas decorativas. |
| Horas | `YYYY-MM-DD HH:MM UTC` y, en tablas de tiempo, una columna adicional `Hora local (UTC±hh:mm)`. |
| Hora local | Zona horaria de la **máquina donde se ejecuta el RCA** (configuración regional del sistema operativo): sirve en cualquier país sin preguntar. Convertir cada hora UTC con `python <skill>/scripts/hora_local.py <utc> ...`, que aplica el desfase vigente en esa fecha (incluye horario de verano). Se declara en la ficha. |
| Indicadores de estado | ✅ Confirmado/Completado · ❌ Descartado · ⚠️ Parcial/No concluyente · 🔴 Crítico · 🟠 Alto · 🟡 Medio · 🟢 Bajo |
| Imágenes | `![Alt descriptivo](data:image/png;base64,...)` + línea siguiente `*Figura N. <Qué muestra>: <lectura principal en una frase simple>.*` |
| Referencias a evidencia | Texto "(Evidencia N.x)" que coincide con el `title` de la sección DQL. |
| Referencias oficiales | `[Rn]` que remite a la tabla 9.3. Formato combinado: `(Evidencia 5.1; [R3])`. |
| Certeza | Afirmación sin sustento completo: prefijo `⚠️ Hipótesis no confirmada:` |
| Separadores | `---` solo al final de la portada. |

---

## Sección 0 — Portada y ficha del incidente (markdown)

```markdown
# RCA — <Título corto del incidente, en lenguaje simple>
**Cliente / Aplicación:** <...> · **Entorno:** <PROD> · **Versión del documento:** 1.0 · **Estado del RCA:** <Borrador | En revisión | Aprobado>

| Campo | Valor |
|---|---|
| Problem ID | [<P-XXXXXXX>](/ui/apps/dynatrace.davis.problems/problem/<event.id>) |
| Ticket ITSM | <INC-XXXX o N/D> |
| Severidad | <🔴 Crítica / 🟠 Alta / 🟡 Media / 🟢 Baja> |
| Categoría Davis | <AVAILABILITY / ERROR / SLOWDOWN / RESOURCE / CUSTOM> |
| Inicio del impacto | <YYYY-MM-DD HH:MM UTC> (<HH:MM> hora local) |
| Fin del impacto | <YYYY-MM-DD HH:MM UTC> (<HH:MM> hora local) |
| Duración del impacto | <N h M min> |
| Zona horaria local | <zona del sistema (UTC±hh:mm)> — la de la máquina donde se elaboró el RCA |
| MTTD / MTTR | <N min> / <N min> |
| Componente causa raíz | <Entidad> |
| Certeza de la causa raíz | <✅ Confirmada / ⚠️ Probable / ❌ No determinada> |
| Anclaje de la investigación | <Problem ID / Evento <id> / Rango + entidad> |
| Elaborado por | <Nombre — rol> |
| Revisado por | <Nombre — rol> |
| Fecha de elaboración | <YYYY-MM-DD> |

---
```

## Sección 1 — Resumen ejecutivo (markdown)

**Debe entenderlo cualquier persona.** Es lo primero que se lee y, muchas veces, lo único. Prueba antes de entregar: si alguien de negocio que no conoce Dynatrace ni la arquitectura lo leyera solo, ¿entendería qué pasó, a quién afectó, por qué, cómo se resolvió y qué se hará? Si no, reescribir.

| Regla | Detalle |
|---|---|
| Sin tecnicismos | Sin código, DQL, IDs de entidad, nombres de métricas ni siglas técnicas. "MTTR" → "tiempo hasta recuperar el servicio". |
| Componentes por su función | "el servicio de pagos", "la base de datos de clientes". El nombre técnico, solo si ayuda, entre paréntesis y una vez: "el servicio de pagos (checkout-service)". |
| Impacto en unidades de negocio | Personas, operaciones, montos, minutos. Un porcentaje siempre con su base: "38 % de los pagos". |
| Estilo | Frases cortas, voz activa, sin culpar personas. Máximo **10 líneas**. El detalle técnico va en las Secciones 2 a 9. |
| Validación | `build_notebook.py` bloquea código, DQL, IDs de entidad y más de 10 líneas; advierte la jerga técnica. |

```markdown
## 1. Resumen ejecutivo
El <fecha> entre las <HH:MM> y las <HH:MM> (hora local), <qué dejó de funcionar, contado como lo vivió el cliente o el negocio>. Afectó a **<cifra principal en términos de negocio: personas, operaciones o monto>** durante **<duración>**.
- **Por qué pasó (causa raíz, <✅ Confirmada / ⚠️ Probable / ❌ No determinada>):** <una frase sin jerga>.
- **Qué lo desencadenó:** <una frase>.
- **Qué hicimos para recuperarlo:** <qué se hizo y a qué hora>.
- **Cómo nos enteramos:** <Dynatrace lo detectó automáticamente a los N minutos / por reporte de un cliente>.
- **Cómo está hoy:** <Resuelto / Mitigado con una solución temporal / En observación>.
- **Qué haremos para que no se repita:** <2–3 acciones principales, con fecha>.
```

## Sección 2 — Alcance e impacto (markdown + DQL)

```markdown
## 2. Alcance e impacto
### 2.1 Componentes afectados
| Componente | Tipo | Rol en el incidente | Impacto observado | Evidencia |
|---|---|---|---|---|
| <checkout-service> | Servicio | Origen | Error rate 0,2 % → **38 %** | Evidencia 2.1 |
| <frontend-web> | Aplicación | Afectado aguas arriba | Sesiones con error +x % | Evidencia 2.2 |
### 2.2 Impacto en usuarios y negocio
| Dimensión | Valor | Fuente |
|---|---|---|
| Requests fallidas | <N (x %)> | Evidencia 2.1 |
| Usuarios / sesiones afectadas | <N> | Evidencia 2.2 |
| Transacciones de negocio perdidas | <N / monto o N/D> | <bizevents o N/D> |
| SLO afectado | <nombre — presupuesto consumido x %> | <SLO> |
```
DQL de esta sección: `[Evidencia 2.1] Errores y tiempo de respuesta del servicio raíz` (timeseries), `[Evidencia 2.2] Impacto por servicio afectado` (tabla).

## Sección 3 — Línea de tiempo de los sucesos (markdown con imagen D2 + DQL)

```markdown
## 3. Línea de tiempo de los sucesos
![Línea de tiempo del incidente <P-XXXX> desde el cambio previo hasta el cierre](data:image/png;base64,...)
*Figura 1. Línea de tiempo del incidente (hora local, UTC±hh:mm): <lectura principal, p. ej. "el problema empezó 7 minutos después del despliegue y se resolvió con la vuelta atrás">.*

| # | Hora UTC | Hora local (UTC±hh:mm) | Suceso | Tipo | Fuente |
|---|---|---|---|---|---|
| 1 | <2026-09-30 14:02> | <09:02> | Despliegue v2.4.1 de checkout-service | Cambio | Evidencia 3.1 |
| 2 | <14:09> | <09:09> | Inicio de impacto: error rate > 5 % | Impacto | Evidencia 2.1 |
| 3 | <14:12> | <09:12> | Davis abre Problem P-XXXX | Detección | Evidencia 3.2 |
| 4 | <14:20> | <09:20> | Equipo reconoce alerta | Respuesta | ITSM |
| 5 | <14:41> | <09:41> | Rollback a v2.4.0 | Mitigación | Evidencia 3.1 |
| 6 | <14:47> | <09:47> | Métricas en baseline; Problem cerrado | Resolución | Evidencia 3.2 |

| Indicador | Valor | Cálculo |
|---|---|---|
| MTTD | <3 min> | Detección − Inicio de impacto |
| MTTA | <8 min> | Reconocimiento − Detección |
| MTTR | <38 min> | Resolución − Inicio de impacto |
```
Tipos permitidos en la columna **Tipo**: Cambio · Impacto · Detección · Respuesta · Diagnóstico · Mitigación · Resolución · Comunicación.
DQL: `[Evidencia 3.1] Despliegues y cambios en la ventana`, `[Evidencia 3.2] Eventos Davis del problema`.

## Sección 4 — Diagrama de propagación de la afectación (markdown con imagen D1)

```markdown
## 4. Diagrama de propagación de la afectación
![Propagación de la afectación desde <componente origen> hacia <usuarios>](data:image/png;base64,...)
*Figura 2. Cómo se propagó la falla: <lectura principal en una frase>. Rojo: causa raíz y componentes con errores · Naranja: degradado · Verde: sano · Gris punteado: sin visibilidad.*

**Secuencia de propagación**
1. **<HH:MM> — <Componente origen>:** <qué le pasó>.
2. **<HH:MM> — <Componente 2>:** <cómo le llegó (timeouts, colas, reintentos)>.
3. **<HH:MM> — <Usuarios / canal>:** <síntoma visible>.

**Componentes no afectados relevantes:** <lista breve — ayuda a acotar>.
**Puntos ciegos:** <componentes sin telemetría — se detallan en Sección 6>.
```

## Sección 5 — Análisis de causa raíz (markdown con imagen D3 + DQL)

```markdown
## 5. Análisis de causa raíz
### 5.1 Causa raíz
> **<Enunciado de la causa raíz en una o dos frases, accionable y verificable.>**

**Nivel de certeza:** <✅ Confirmada / ⚠️ Probable / ❌ No determinada> — <criterio cumplido o eslabón faltante>.

| Clasificación | Descripción | Evidencia | Referencia oficial |
|---|---|---|---|
| Disparador | <evento que inició el incidente> | Evidencia 3.1 | [R1] |
| Causa raíz | <condición subyacente> | Evidencia 5.1 | [R2] |
| Factor contribuyente | <lo que amplificó / retrasó> | Evidencia 5.2 | [R3] |
| Factor mitigante | <lo que limitó el impacto> | <...> | <...> |

### 5.2 Análisis de los 5 porqués
![Árbol de causa raíz (5 porqués) del incidente <P-XXXX>](data:image/png;base64,...)
*Figura 3. Árbol de los 5 porqués: <lectura principal, p. ej. "los pagos fallaron porque la base de datos se quedó sin conexiones disponibles tras el cambio de configuración">.*

| # | Pregunta | Respuesta | Evidencia | Referencia oficial |
|---|---|---|---|---|
| 1 | ¿Por qué <síntoma de negocio>? | <...> | Evidencia 2.1 | — |
| 2 | ¿Por qué <respuesta 1>? | <...> | Evidencia 5.1 | [R2] |
| 3 | ¿Por qué <respuesta 2>? | <...> | Evidencia 5.2 | [R3] |
| 4 | ¿Por qué <respuesta 3>? | <...> | <...> | <...> |
| 5 | ¿Por qué <respuesta 4>? | <causa raíz> | <...> | <...> |
"—" solo es válido para hechos observados; toda interpretación requiere `[Rn]`.

### 5.3 Hipótesis evaluadas
| # | Hipótesis | A favor (Evidencia) | En contra (Evidencia) | Referencia oficial | Estado |
|---|---|---|---|---|---|
| H1 | <...> | <... (Ev. 5.1)> | <...> | [R2] | ✅ Confirmada |
| H2 | <...> | <...> | <... (Ev. 5.3)> | [R4] | ❌ Descartada |

### 5.4 Validación de Davis
- **Entidad raíz propuesta por Davis:** <entidad>.
- **Coincide con la causa raíz confirmada:** <Sí / Parcialmente / No — explicar en una línea>.
- **Cómo determina Davis la causa raíz:** <paráfrasis breve> [Rn: Root cause analysis concepts].
```
DQL: `[Evidencia 5.1] ...`, `[Evidencia 5.2] ...` (traces, logs, infraestructura que prueban la causa).

## Sección 6 — Brechas de observabilidad detectadas (markdown)

```markdown
## 6. Brechas de observabilidad detectadas
| # | Categoría | Brecha | Efecto en el incidente | Recomendación | Prioridad |
|---|---|---|---|---|---|
| B1 | Cobertura | <BD Oracle sin extensión de monitoreo> | <No se pudo confirmar bloqueo de sesiones> | <Activar extensión SQL Oracle> | 🔴 Crítica |
| B2 | Alertamiento | <...> | <Detección tardía +N min> | <...> | 🟠 Alta |
| B3 | Contexto | <Sin eventos de despliegue enviados desde el pipeline> | <Correlación manual del cambio> | <Enviar CUSTOM_DEPLOYMENT desde CI/CD> | 🟠 Alta |
```
Categorías permitidas: Cobertura · Telemetría · Alertamiento · Contexto · Proceso.
Si no hubo brechas, escribir una línea: "No se identificaron brechas; la telemetría disponible fue suficiente para confirmar la causa raíz." (raro — revisar antes).

## Sección 7 — Plan de acción (markdown)

```markdown
## 7. Plan de acción
| ID | Acción | Tipo | Origen | Responsable | Fecha compromiso | Prioridad | Estado | Criterio de cierre |
|---|---|---|---|---|---|---|---|---|
| A1 | <Agregar validación de config en pipeline> | Correctiva | Causa raíz | @<Nombre> | <YYYY-MM-DD> | 🔴 Crítica | ⚠️ En curso | <Pipeline falla si falta la clave X> |
| A2 | <Alerta de pool de conexiones > 80 %> | Preventiva | B2 | @<Nombre> | <YYYY-MM-DD> | 🟠 Alta | Pendiente | <Alerta activa y probada> |
| A3 | <Rollback ejecutado> | Contención | Disparador | @<Nombre> | <YYYY-MM-DD> | 🔴 Crítica | ✅ Completado | <Servicio en baseline> |
```
- **Tipo:** Contención (inmediata, ya hecha) · Correctiva (elimina la causa raíz) · Preventiva (evita recurrencia/similar) · Detección (mejora observabilidad).
- **Origen:** Causa raíz · Disparador · Factor contribuyente · B# (brecha).
- Regla: debe existir **al menos una acción Correctiva vinculada a la causa raíz** y **una acción por cada brecha 🔴/🟠**.
- Responsables con `@Nombre`; si no se conocen, `@Por asignar` y señalarlo al usuario.

## Sección 8 — Lecciones aprendidas (markdown)

```markdown
## 8. Lecciones aprendidas
- **Qué funcionó bien:** <...>
- **Qué se puede mejorar:** <...>
- **Dónde tuvimos suerte:** <...>
```
Máximo 3 viñetas por categoría.

## Sección 9 — Anexos (markdown + DQL)

```markdown
## 9. Anexos
### 9.1 Anclaje, ventanas y evidencia
**Anclaje:** <Problem ID / evento / rango + entidad, entregado por el usuario el YYYY-MM-DD>.
| Ventana | Desde (UTC) | Hasta (UTC) | Motivo |
|---|---|---|---|
| Inicial | <...> | <...> | Derivada del anclaje |
| Ampliación 1 | <...> | <...> | <p. ej. buscar cambio previo en la entidad raíz> |

| Evidencia | Archivo .dql | Registros | Advertencias / límites ajustados | Sustenta |
|---|---|---|---|---|
| 2.1 | E2.1-errores-servicio.dql | <N> | <Ninguna / --max-result-records 100000> | <conclusión> |
Toda la evidencia se obtuvo con dtctl <versión> sobre el contexto <ctx>; las secciones `[Evidencia N.x]` son re-ejecutables.
### 9.2 Glosario
| Término | Definición |
|---|---|
| MTTD | Tiempo medio de detección |
| MTTR | Tiempo medio de resolución |
### 9.3 Referencias oficiales
| ID | Fuente oficial | URL | Consultada | Sustenta |
|---|---|---|---|---|
| R1 | Dynatrace Docs — Root cause analysis concepts | https://docs.dynatrace.com/docs/dynatrace-intelligence/root-cause-analysis/concepts | <YYYY-MM-DD> | Agrupación de eventos y causa raíz Davis |
| R2 | <Fabricante — documento> | <URL oficial> | <YYYY-MM-DD> | <afirmación> |
| R3 | <...> | <...> | <YYYY-MM-DD> | <...> |
| R4 | <...> | <...> | <YYYY-MM-DD> | <...> |
**Otras referencias:** Problem [<P-XXXX>](/ui/apps/dynatrace.davis.problems/problem/<event.id>) · Ticket <...> (fuente externa declarada) · Fuentes draw.io: D1-propagacion.drawio, D2-linea-tiempo.drawio, D3-causa-raiz.drawio (el PNG incrustado contiene el XML editable).
### 9.4 Control de versiones
| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0 | <YYYY-MM-DD> | <...> | Versión inicial (dtctl <versión>) |
```

---

## Mapeo a JSON del notebook

- Secciones markdown: `{ "id": "<n>", "type": "markdown", "markdown": "<texto>" }`
- Secciones DQL: `{ "id": "<n>", "type": "dql", "title": "[Evidencia N.x] ...", "showTitle": true, "showInput": false, "state": { "input": { "value": "<query>" }, "visualizationSettings": { "autoSelectVisualization": true } } }`
- `showInput: false` en evidencias para lectura ejecutiva; el lector puede expandir la query.
- IDs como enteros en string ("1", "2", …) en orden.
- `content.defaultTimeframe` = ventana de análisis en ISO-8601 UTC fijo (el script rechaza `now()` para que el RCA sea reproducible).
- Imágenes en los `.md` como `![Alt](img:../diagrams/D1-propagacion.png)`: la ruta se resuelve junto al `.md` y, si no existe, junto al spec. El script las incrusta en base64.
- Generar el JSON con `scripts/build_notebook.py`, no a mano. Las queries se cargan desde los mismos `.dql` ejecutados con dtctl (`query_file`).
