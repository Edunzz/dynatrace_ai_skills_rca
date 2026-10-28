<!-- Generado a partir de rca_spec.json: vista previa en Markdown del notebook. -->
> **Vista previa del notebook generado.** En Dynatrace cada bloque `[Evidencia N.x]` es una sección DQL que se ejecuta y muestra su gráfico o tabla; aquí se muestra la query. Datos anonimizados.

# RCA — Fallas en el servicio de autorización por presión de memoria (ejemplo)
**Cliente / Aplicación:** Empresa de ejemplo — servicio de autorización · **Entorno:** tenant de ejemplo · **Versión del documento:** 1.0 · **Estado del RCA:** Borrador (ejemplo generado con la skill dt-custom-rca-jromero 2.1.0)

| Campo | Valor |
|---|---|
| Problem ID | [P-2601001](/ui/apps/dynatrace.davis.problems/problem/1000000000000000001_1768536540000V2) (relacionado: [P-2601002](/ui/apps/dynatrace.davis.problems/problem/1000000000000000002_1768536720000V2)) |
| Ticket ITSM | N/D (no se registró ticket) |
| Severidad | 🟡 Media |
| Categoría Davis | ERROR (relacionado: RESOURCE_CONTENTION) |
| Inicio del impacto | 2026-01-16 04:08 UTC (23:08 hora local del 15-ene) |
| Fin del impacto | 2026-01-16 04:21 UTC (23:21 hora local del 15-ene) |
| Duración del impacto | 13 min |
| Zona horaria local | Hora est. Pacífico, Sudamérica (UTC-05:00) — la de la máquina donde se elaboró el RCA |
| MTTD / MTTR | 6 min / 13 min |
| Componente causa raíz | Proceso .NET AuthApi.dll en el pod auth-api-v1-5f7c9d8b6-pod-a |
| Certeza de la causa raíz | ⚠️ Probable |
| Anclaje de la investigación | Problem P-2601001 (caso de ejemplo) |
| Elaborado por | Autor de ejemplo — asistido por IA (skill dt-custom-rca-jromero 2.1.0) |
| Revisado por | Pendiente |
| Fecha de elaboración | 2026-01-16 |

---

## 1. Resumen ejecutivo
El 15 de enero entre las 23:08 y las 23:21 (hora local), el servicio que autoriza las solicitudes de las aplicaciones respondió con error a una parte de las consultas. Fallaron **9 de unas 4.900 consultas (0,2 %)**, algunas después de esperar más de un minuto; el resto se atendió con normalidad.
- **Por qué pasó (causa raíz, ⚠️ Probable):** una de las dos copias del servicio se quedó casi sin memoria disponible y pasó casi todo su tiempo intentando liberarla, por lo que dejó de responder a tiempo.
- **Qué lo desencadenó:** la memoria de esa copia venía creciendo de forma constante durante horas hasta llegar al 91 % de su límite.
- **Qué hicimos para recuperarlo:** la plataforma reinició automáticamente esa copia a las 23:14 y a las 23:21 el servicio ya funcionaba con normalidad.
- **Cómo nos enteramos:** Dynatrace lo detectó automáticamente 6 minutos después de la primera falla.
- **Cómo está hoy:** resuelto, pero el patrón se repite: en las últimas 48 horas las copias del servicio se reiniciaron 18 veces con el mismo crecimiento de memoria.
- **Qué haremos para que no se repita:** corregir el consumo de memoria del servicio (29-ene), alertar antes de llegar al límite (22-ene) y registrar los eventos de la plataforma (29-ene).

## 2. Alcance e impacto
### 2.1 Componentes afectados
| Componente | Tipo | Rol en el incidente | Impacto observado | Evidencia |
|---|---|---|---|---|
| auth-api-v*-* | Servicio | Afectado (síntoma) | Tasa de fallas 0 % → **9,43 %** en el minuto 04:13 UTC (Davis reportó 2,07 % en su ventana) | Evidencia 2.1 |
| Pod auth-api-v1-5f7c9d8b6-pod-a | Pod / proceso .NET | Origen | **9 de 2.298** solicitudes fallidas (0,39 %); GC 5 % → **99 %**; memoria al **91 %** del límite | Evidencia 2.2, 5.3 y 5.4 |
| Pod auth-api-v1-5f7c9d8b6-pod-b | Pod / proceso .NET | No afectado | 0 de 2.600 solicitudes fallidas; GC 0 % | Evidencia 2.2 |
### 2.2 Impacto en usuarios y negocio
| Dimensión | Valor | Fuente |
|---|---|---|
| Requests fallidas | **9 de 4.863 (0,19 %)** entre 03:45 y 04:45 UTC; todas con HTTP 500 | Evidencia 2.1 |
| Espera de las solicitudes fallidas | hasta **81 s** antes de responder con error | Evidencia 5.2 |
| Usuarios / sesiones afectadas | N/D — Davis no reporta usuarios afectados para este problema | Evidencia 3.2 |
| Transacciones de negocio perdidas | N/D — no hay eventos de negocio para este flujo | N/D |
| SLO afectado | N/D — no evaluado en este ejemplo | N/D |

<details><summary><b>[Evidencia 2.1] Solicitudes, fallas y tasa de fallas por minuto del servicio</b> (sección DQL)</summary>

```dql
timeseries {
  solicitudes = sum(dt.service.request.count),
  fallas = sum(dt.service.request.failure_count)
}, filter: dt.smartscape.service == toSmartscapeId("SERVICE-0123456789ABCDEF"),
   from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z", interval: 1m
| fieldsAdd tasa_fallas_pct = fallas[] * 100.0 / solicitudes[]
```
</details>

<details><summary><b>[Evidencia 2.2] Solicitudes y fallas por pod</b> (sección DQL)</summary>

```dql
fetch spans, from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z"
| filter dt.smartscape.service == toSmartscapeId("SERVICE-0123456789ABCDEF") and request.is_root_span == true
| fieldsAdd m = coalesce(1 / ((power(2, 56) - coalesce(sampling.threshold, 0)) * power(2, -56)), 1) * coalesce(aggregation.count, 1)
| summarize {solicitudes = sum(m), fallidas = sum(if(request.is_failed == true, m, else: 0))}, by: {k8s.pod.name}
| fieldsAdd tasa_fallas_pct = fallidas * 100.0 / solicitudes
| sort fallidas desc
```
</details>

## 3. Línea de tiempo de los sucesos
![Línea de tiempo del incidente P-2601001 desde la primera falla hasta la normalización](diagrams/D2-linea-tiempo.png)
*Figura 1. Línea de tiempo del incidente (hora local, UTC-05:00): las fallas empezaron cuando la copia 1 dedicaba casi todo su tiempo a liberar memoria y terminaron tras su reinicio automático.*

| # | Hora UTC | Hora local (UTC-05:00) | Suceso | Tipo | Fuente |
|---|---|---|---|---|---|
| 1 | 2026-01-16 04:08 | 23:08 | Primera solicitud fallida (HTTP 500) en el pod …-a (copia 1); GC en 11,8 % | Impacto | Evidencia 2.1 y 5.2 |
| 2 | 2026-01-16 04:10 | 23:10 | El tiempo en GC del pod …-a (copia 1) sube a 39,5 % | Impacto | Evidencia 5.3 |
| 3 | 2026-01-16 04:12 | 23:12 | GC en 91 %: Davis registra el evento de GC larga; las solicitudes quedan detenidas hasta 81 s | Impacto | Evidencia 5.3, 3.1 y 5.2 |
| 4 | 2026-01-16 04:13 | 23:13 | Pico de fallas: 9,43 % de las solicitudes del minuto | Impacto | Evidencia 2.1 |
| 5 | 2026-01-16 04:14 | 23:14 | Davis abre P-2601001 (aumento de fallas) | Detección | Evidencia 3.2 |
| 6 | 2026-01-16 04:14 | 23:14 | Reinicio del contenedor dotnet-container del pod …-a (copia 1) (evento de reinicio de proceso a las 04:14:51) | Mitigación | Evidencia 3.1 y 5.5 |
| 7 | 2026-01-16 04:15 | 23:15 | Davis abre P-2601002 (GC larga); el tiempo en GC vuelve a 0 % | Detección | Evidencia 3.2 y 5.3 |
| 8 | 2026-01-16 04:21 | 23:21 | Se cierran los eventos de fallas; servicio normal | Resolución | Evidencia 3.1 y 2.1 |

| Indicador | Valor | Cálculo |
|---|---|---|
| MTTD | 6 min | Detección (04:14) − Inicio de impacto (04:08) |
| MTTA | N/D | No hay registro del reconocimiento por el equipo (ver B4) |
| MTTR | 13 min | Resolución (04:21) − Inicio de impacto (04:08) |

<details><summary><b>[Evidencia 3.1] Eventos Davis de ambos problemas</b> (sección DQL)</summary>

```dql
fetch dt.davis.events, from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z"
| filter in(event.id, {"1000000000000000001_1768536540000", "1000000000000000003_1768536540000", "1000000000000000004_1768536891970", "1000000000000000002_1768536720000"})
| fields event.start, event.end, event.name, event.type, k8s.pod.name, host.name, event.description
| sort event.start asc
```
</details>

<details><summary><b>[Evidencia 3.2] Problemas Davis P-2601001 y P-2601002</b> (sección DQL)</summary>

```dql
fetch dt.davis.problems, from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z"
| filter in(display_id, {"P-2601001", "P-2601002"}) and not(dt.davis.is_duplicate)
| fields display_id, event.start, event.end, event.name, event.category, root_cause_entity_name, smartscape.affected_entity.ids
| sort event.start asc
```
</details>

<details><summary><b>[Evidencia 3.3] Eventos registrados en el tenant por tipo (24 h)</b> (sección DQL)</summary>

```dql
fetch events, from: "2026-01-15T04:45:00Z", to: "2026-01-16T04:45:00Z"
| summarize {eventos = count(), eventos_de_cambio = countIf(contains(toString(event.type), "DEPLOY") or contains(toString(event.type), "CONFIG") or contains(toString(event.kind), "K8S"))}, by: {event.kind}
| sort eventos desc
```
</details>

## 4. Diagrama de propagación de la afectación
![Propagación de la afectación desde la copia 1 del servicio hacia los consumidores](diagrams/D1-propagacion.png)
*Figura 2. Cómo se propagó la falla: una copia del servicio llegó casi al tope de memoria, dejó de responder y sus consultas fallaron; la otra copia siguió sana. Rojo: causa raíz y componentes con errores · Naranja: degradado · Verde: sano · Gris punteado: sin visibilidad.*

**Secuencia de propagación**
1. **23:12 — Copia 1 (pod …-a):** con la memoria del contenedor al 91 % del límite, el proceso .NET pasa 91–99 % del tiempo en GC y sus solicitudes quedan detenidas hasta 81 s (Evidencia 5.3, 5.4 y 5.2).
2. **23:13 — Servicio de autorización:** las solicitudes atendidas por esa copia terminan con HTTP 500; la tasa de fallas del servicio llega a 9,43 % en el minuto (Evidencia 2.1 y 5.1).
3. **23:13–23:14 — Consumidores:** reciben error en 9 autorizaciones (Evidencia 2.1).
4. **23:14 — Recuperación:** Kubernetes reinicia el contenedor, la GC vuelve a 0 % y el servicio se normaliza a las 23:21 (Evidencia 5.5 y 5.3).

**Componentes no afectados relevantes:** copia 2 (pod …-b) con 0 fallas, GC 0 % y memoria al 71 % del límite (Evidencia 2.2, 5.3 y 5.4); Davis no registró otras entidades afectadas (Evidencia 3.2).
**Puntos ciegos:** motivo exacto del reinicio (el tenant no recibe eventos de Kubernetes) y consumidores del servicio, no identificados en este ejemplo (ver B1).

## 5. Análisis de causa raíz
### 5.1 Causa raíz
> **El servicio de autorización acumula memoria de forma continua (75–90 MB por hora en cada copia) hasta acercarse al límite de 1 GiB del contenedor; al superar el 90 %, la recolección de basura de .NET ocupa casi todo el tiempo del proceso, la aplicación queda detenida y las solicitudes fallan hasta que el contenedor se reinicia.**

**Nivel de certeza:** ⚠️ Probable — el mecanismo está confirmado con evidencia (memoria al 91 % → GC 91–99 % → fallas solo en esa copia → reinicio → recuperación) y el patrón se repite en 48 h; falta identificar qué retiene la memoria (análisis de memoria, B3) y el motivo exacto del reinicio (sin eventos de Kubernetes, B1).

| Clasificación | Descripción | Evidencia | Referencia oficial |
|---|---|---|---|
| Disparador | La copia 1 llegó a 936 MB (91 % del límite de 1 GiB) y su tiempo en GC pasó de 15 % a 99 % entre 04:09 y 04:14 UTC | Evidencia 5.4 y 5.3 | [R2] |
| Causa raíz | Crecimiento continuo de memoria del proceso .NET (75–90 MB/h) en todas las copias, que solo se libera al reiniciar | Evidencia 5.7 y 5.5 | [R2] |
| Factor contribuyente | Durante la GC se suspenden los hilos de la aplicación, por lo que las solicitudes en curso esperaron hasta 81 s | Evidencia 5.2 | [R3] |
| Factor contribuyente | Sin alerta preventiva de memoria frente al límite: 18 reinicios en 48 h y problemas repetidos en 7 días | Evidencia 5.5 y 5.6 | — |
| Factor mitigante | La copia 2 atendió 2.600 solicitudes sin fallas y la copia afectada se reinició sola | Evidencia 2.2 y 5.5 | — |

### 5.2 Análisis de los 5 porqués
![Árbol de causa raíz (5 porqués) del incidente P-2601001](diagrams/D3-causa-raiz.png)
*Figura 3. Árbol de los 5 porqués: las autorizaciones fallaron porque una copia del servicio, casi sin memoria libre, pasó la mayor parte del tiempo liberándola; la memoria del servicio crece de forma constante en todas sus copias.*

| # | Pregunta | Respuesta | Evidencia | Referencia oficial |
|---|---|---|---|---|
| 1 | ¿Por qué fallaron 9 autorizaciones? | La copia 1 dejó las solicitudes en espera hasta 81 s y respondió HTTP 500; la otra copia no falló | Evidencia 2.1, 2.2 y 5.2 | — |
| 2 | ¿Por qué se detuvieron las solicitudes? | El proceso .NET pasó 91–99 % del tiempo en GC, que suspende los hilos de la aplicación | Evidencia 5.3 | [R3] |
| 3 | ¿Por qué tanta GC? | El contenedor estaba al 91 % de su límite de 1 GiB; .NET toma ese límite como memoria física y sobre el 90 % hace recolecciones completas más agresivas | Evidencia 5.4 | [R2] |
| 4 | ¿Por qué estaba tan cerca del límite? | La memoria crece 75–90 MB por hora en todas las copias y solo baja al reiniciar (18 reinicios en 48 h) | Evidencia 5.7 y 5.5 | — |
| 5 | ¿Por qué crece la memoria? | ⚠️ Hipótesis no confirmada: retención de objetos en el código (fuga o caché sin límite); requiere análisis de memoria del proceso | N/D (B3) | — |
"—" solo es válido para hechos observados; toda interpretación requiere una referencia oficial.

### 5.3 Hipótesis evaluadas
| # | Hipótesis | A favor (Evidencia) | En contra (Evidencia) | Referencia oficial | Estado |
|---|---|---|---|---|---|
| H1 | Presión de memoria en la copia 1 → GC excesiva → fallas | Fallas solo en la copia 1 (Ev. 2.2); GC 91–99 % (Ev. 5.3); memoria 91 % (Ev. 5.4) | — | [R2], [R3] | ✅ Confirmada |
| H2 | Falla general del servicio o de sus dependencias | — | La copia 2 sin fallas y con GC 0 % (Ev. 2.2, 5.1) | — | ❌ Descartada |
| H3 | Contenedor terminado por memoria agotada (OOM) | Reinicio a las 04:14 (Ev. 5.5) | Uso máximo 91 %, nunca alcanzó el límite (Ev. 5.4) | — | ❌ Descartada |
| H4 | Despliegue o cambio de configuración previo | — | Sin eventos de cambio en 24 h, pero el tenant no los recibe (Ev. 3.3) | — | ⚠️ No concluyente |
| H5 | El reinicio lo provocó la sonda de vida de Kubernetes mientras el proceso estaba suspendido | El reinicio coincide con la GC al 99 % (Ev. 5.3, 5.5) | No hay evento de Kubernetes con el motivo | [R4] | ⚠️ Hipótesis no confirmada |

### 5.4 Validación de Davis
- **Entidad raíz propuesta por Davis:** el servicio auth-api-v*-* (P-2601001) y, en un problema separado, el grupo de procesos AuthApi.dll (P-2601002) (Evidencia 3.2).
- **Coincide con la causa raíz confirmada:** Parcialmente — Davis señaló el servicio (síntoma) y, por separado, la GC del proceso (mecanismo); los mantuvo como dos problemas, mientras que el análisis muestra una sola cadena causal en la copia 1.
- **Cómo determina Davis la causa raíz:** correlaciona en un único problema los eventos que comparten la misma causa raíz y prioriza la anomalía más probable como origen [R1].

<details><summary><b>[Evidencia 5.1] Solicitudes y fallas por pod y minuto</b> (sección DQL)</summary>

```dql
fetch spans, from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z"
| filter dt.smartscape.service == toSmartscapeId("SERVICE-0123456789ABCDEF") and request.is_root_span == true
| makeTimeseries {solicitudes = count(), fallidas = countIf(request.is_failed == true)}, by: {k8s.pod.name}, interval: 1m
```
</details>

<details><summary><b>[Evidencia 5.2] Detalle de las solicitudes fallidas</b> (sección DQL)</summary>

```dql
fetch spans, from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z"
| filter dt.smartscape.service == toSmartscapeId("SERVICE-0123456789ABCDEF") and request.is_root_span == true and request.is_failed == true
| fields start_time, k8s.pod.name, endpoint.name, http.response.status_code, duration, dt.failure_detection.results, trace.id
| sort start_time asc
```
</details>

<details><summary><b>[Evidencia 5.3] Tiempo en recolección de basura (.NET) por proceso</b> (sección DQL)</summary>

```dql
timeseries gc_tiempo_pct = avg(dt.runtime.clr.gc.time_percentage),
   by: {dt.smartscape.process, k8s.pod.name},
   from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z", interval: 1m
| filter in(dt.smartscape.process, {toSmartscapeId("PROCESS-0123456789ABC00A"), toSmartscapeId("PROCESS-0123456789ABC00B")})
| fieldsAdd gc_max_pct = arrayMax(gc_tiempo_pct)
```
</details>

<details><summary><b>[Evidencia 5.4] Memoria del contenedor frente al límite por pod</b> (sección DQL)</summary>

```dql
timeseries {
  memoria_ws = avg(dt.kubernetes.container.memory_working_set),
  limite_memoria = avg(dt.kubernetes.container.limits_memory)
}, by: {k8s.pod.name, k8s.container.name},
   from: "2026-01-16T03:45:00Z", to: "2026-01-16T04:45:00Z", interval: 1m
| filter contains(k8s.pod.name, "auth-api") and k8s.container.name == "dotnet-container"
| fieldsAdd ws_max_mb = arrayMax(memoria_ws) / 1048576, limite_mb = arrayMax(limite_memoria) / 1048576
| fieldsAdd uso_max_pct = ws_max_mb * 100.0 / limite_mb
```
</details>

<details><summary><b>[Evidencia 5.5] Reinicios de contenedor por pod (48 h)</b> (sección DQL)</summary>

```dql
timeseries reinicios = sum(dt.kubernetes.container.restarts),
   by: {k8s.pod.name, k8s.container.name},
   from: "2026-01-14T04:45:00Z", to: "2026-01-16T04:45:00Z", interval: 1h
| filter contains(k8s.pod.name, "auth-api")
| fieldsAdd total_reinicios_48h = arraySum(reinicios)
| sort total_reinicios_48h desc
```
</details>

<details><summary><b>[Evidencia 5.6] Recurrencia de problemas del servicio (7 días)</b> (sección DQL)</summary>

```dql
fetch dt.davis.problems, from: "2026-01-09T04:45:00Z", to: "2026-01-16T04:45:00Z"
| filter not(dt.davis.is_duplicate)
| filter in(root_cause_entity_id, {"SERVICE-0123456789ABCDEF", "PROCESS_GROUP-0123456789ABCDEF"})
| summarize {problemas = count(), primero = min(event.start), ultimo = max(event.start)}, by: {event.name, root_cause_entity_name}
| sort problemas desc
```
</details>

<details><summary><b>[Evidencia 5.7] Tendencia de memoria del contenedor por pod (48 h)</b> (sección DQL)</summary>

```dql
timeseries memoria_ws = avg(dt.kubernetes.container.memory_working_set),
   by: {k8s.pod.name, k8s.container.name},
   from: "2026-01-14T04:45:00Z", to: "2026-01-16T04:45:00Z", interval: 1h
| filter contains(k8s.pod.name, "auth-api") and k8s.container.name == "dotnet-container"
| fieldsAdd ws_max_mb = arrayMax(memoria_ws) / 1048576, ws_min_mb = arrayMin(memoria_ws) / 1048576
```
</details>

## 6. Brechas de observabilidad detectadas
| # | Categoría | Brecha | Efecto en el incidente | Recomendación | Prioridad |
|---|---|---|---|---|---|
| B1 | Contexto | El tenant no recibe eventos de Kubernetes ni de despliegue (0 en 24 h, Evidencia 3.3) | No se pudo confirmar el motivo del reinicio ni descartar un cambio previo | Activar la ingesta de eventos de Kubernetes y enviar eventos de despliegue desde CI/CD | 🟠 Alta |
| B2 | Alertamiento | No hay alerta de memoria del contenedor cerca del límite ni de tiempo en GC | 18 reinicios en 48 h y problemas repetidos sin aviso preventivo (Evidencia 5.5 y 5.6) | Detector: memoria sobre el 85 % del límite por 10 min y GC sobre el 25 % | 🟠 Alta |
| B3 | Telemetría | Sin análisis de memoria del proceso .NET (qué objetos retienen memoria) | No se pudo confirmar por qué crece la memoria | Capturar un volcado de memoria cuando supere el 80 % del límite y analizarlo | 🟡 Media |
| B4 | Proceso | Sin registro del reconocimiento humano del problema | MTTA no medible | Vincular los problemas de Davis con la herramienta ITSM | 🟡 Media |

## 7. Plan de acción
| ID | Acción | Tipo | Origen | Responsable | Fecha compromiso | Prioridad | Estado | Criterio de cierre |
|---|---|---|---|---|---|---|---|---|
| A1 | Reinicio automático del contenedor afectado | Contención | Disparador | @Kubernetes (automático) | 2026-01-15 | 🔴 Crítica | ✅ Completado | Servicio en baseline desde las 23:21 |
| A2 | Analizar un volcado de memoria y corregir la retención en el código | Correctiva | Causa raíz | @Por asignar | 2026-01-29 | 🔴 Crítica | Pendiente | Crecimiento de memoria menor a 10 MB/h durante 48 h |
| A3 | Mitigación temporal: reciclado programado de pods antes del 80 % de memoria o ajuste del límite | Preventiva | Factor contribuyente | @Por asignar | 2026-01-22 | 🟠 Alta | Pendiente | 0 problemas de GC o fallas en 7 días |
| A4 | Crear detector de memoria frente al límite y de tiempo en GC | Detección | B2 | @Por asignar | 2026-01-22 | 🟠 Alta | Pendiente | Alerta probada antes del siguiente ciclo de memoria |
| A5 | Ingerir eventos de Kubernetes y de despliegue | Detección | B1 | @Por asignar | 2026-01-29 | 🟠 Alta | Pendiente | Eventos de Kubernetes visibles en Grail para el clúster |
- Responsables `@Por asignar`: definir con el equipo dueño del servicio.

## 8. Lecciones aprendidas
- **Qué funcionó bien:** Dynatrace detectó el aumento de fallas y la GC larga en pocos minutos; Kubernetes reinició la copia afectada y la otra copia absorbió la carga.
- **Qué se puede mejorar:** alertar sobre la tendencia de memoria antes de que afecte a los clientes; ingerir eventos de Kubernetes para conocer el motivo de cada reinicio.
- **Dónde tuvimos suerte:** la otra copia estaba al 71 % y subiendo; si ambas hubieran llegado al tope a la vez, la falla habría sido total.

## 9. Anexos
### 9.1 Anclaje, ventanas y evidencia
**Anclaje:** Problem P-2601001, elegido el 2026-01-16 como ejemplo sencillo y reciente del tenant de ejemplo para probar la skill.
| Ventana | Desde (UTC) | Hasta (UTC) | Motivo |
|---|---|---|---|
| Inicial | 2026-01-16 03:45 | 2026-01-16 04:45 | Derivada del anclaje (problema 04:14–04:21 con margen previo) |
| Ampliación 1 | 2026-01-15 04:45 | 2026-01-16 04:45 | Buscar cambios previos (eventos de 24 h) |
| Ampliación 2 | 2026-01-14 04:45 | 2026-01-16 04:45 | Tendencia de memoria y reinicios de todas las copias (48 h) |
| Ampliación 3 | 2026-01-09 04:45 | 2026-01-16 04:45 | Recurrencia del problema (7 días) |

| Evidencia | Archivo .dql | Registros | Advertencias / límites ajustados | Sustenta |
|---|---|---|---|---|
| 2.1 | E2.1-errores-servicio.dql | 1 serie | Ninguna | Impacto: 9 fallas de 4.863, pico 9,43 % |
| 2.2 | E2.2-impacto-por-pod.dql | 2 | Conteos extrapolados por muestreo de trazas | Fallas solo en el pod …-a (copia 1) |
| 3.1 | E3.1-eventos-davis.dql | 4 | Ninguna | Horas de fallas, GC larga y reinicio |
| 3.2 | E3.2-problemas-davis.dql | 2 | Ninguna | Apertura y cierre de ambos problemas |
| 3.3 | E3.3-eventos-de-cambio-24h.dql | 4 | Ninguna | Sin eventos de cambio ni de Kubernetes (B1) |
| 5.1 | E5.1-fallas-por-pod-minuto.dql | 2 series | Ninguna | Distribución de fallas por pod y minuto |
| 5.2 | E5.2-detalle-fallas.dql | 6 | Trazas muestreadas: 6 registros representan 9 fallas | HTTP 500 y esperas de hasta 81 s |
| 5.3 | E5.3-gc-proceso-net.dql | 2 series | Ninguna | GC 99 % en la copia 1 y 0 % en la copia 2 |
| 5.4 | E5.4-memoria-contenedor.dql | 2 series | Ninguna | Memoria al 91 % (copia 1) y 71 % (copia 2) del límite |
| 5.5 | E5.5-reinicios-contenedor.dql | 5 series | Ninguna | 18 reinicios en 48 h |
| 5.6 | E5.6-recurrencia-7d.dql | 2 | Ninguna | 2 problemas de fallas y 2 de GC en 7 días |
| 5.7 | E5.7-tendencia-memoria-48h.dql | 5 series | Ninguna | Crecimiento de 75–90 MB/h en todas las copias |
Toda la evidencia se obtuvo con dtctl 0.37.0 sobre el contexto mi-tenant; las secciones de evidencia son re-ejecutables y llevan la ventana fija dentro de la query.
### 9.2 Glosario
| Término | Definición |
|---|---|
| GC (recolección de basura) | Proceso de .NET que libera memoria que ya no se usa; mientras trabaja, detiene a la aplicación |
| Pod / contenedor | Copia del servicio que se ejecuta en Kubernetes con un límite de memoria propio |
| Working set | Memoria que el contenedor está usando realmente |
| Davis | Motor de IA de Dynatrace que detecta anomalías y abre problemas |
| MTTD | Tiempo medio de detección |
| MTTA | Tiempo medio de reconocimiento |
| MTTR | Tiempo medio de resolución |
### 9.3 Referencias oficiales
| ID | Fuente oficial | URL | Consultada | Sustenta |
|---|---|---|---|---|
| R1 | Dynatrace Docs — Root cause analysis concepts | https://docs.dynatrace.com/docs/dynatrace-intelligence/root-cause-analysis/concepts | 2026-01-16 | Davis agrupa eventos con la misma causa raíz en un problema |
| R2 | Microsoft Learn — Garbage collector config settings (.NET) | https://learn.microsoft.com/en-us/dotnet/core/runtime-config/garbage-collector | 2026-01-16 | En contenedores el límite se trata como memoria física; sobre el 90 % la GC hace recolecciones completas más agresivas; límite del heap 75 % |
| R3 | Microsoft Learn — Fundamentals of garbage collection | https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/fundamentals | 2026-01-16 | Durante una recolección se suspenden los hilos administrados |
| R4 | Kubernetes Docs — Configure Liveness, Readiness and Startup Probes | https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ | 2026-01-16 | Si falla la sonda de vida, kubelet mata y reinicia el contenedor |
**Otras referencias:** Problem [P-2601001](/ui/apps/dynatrace.davis.problems/problem/1000000000000000001_1768536540000V2) · Problem [P-2601002](/ui/apps/dynatrace.davis.problems/problem/1000000000000000002_1768536720000V2) · Fuentes draw.io: D1-propagacion.drawio, D2-linea-tiempo.drawio, D3-causa-raiz.drawio (el PNG incrustado contiene el XML editable).
### 9.4 Control de versiones
| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0 | 2026-01-16 | Autor de ejemplo (asistido por IA) | Versión inicial — ejemplo de la skill dt-custom-rca-jromero 2.1.0 (dtctl 0.37.0) |
