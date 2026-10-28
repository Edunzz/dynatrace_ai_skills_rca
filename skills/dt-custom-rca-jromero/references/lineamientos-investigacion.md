# Lineamientos y buenas prácticas de investigación RCA

> Esto es una **guía de calidad**, no un procedimiento. El agente decide el orden, las fuentes y la profundidad. Puede seguir cualquier pista adicional que la evidencia sugiera. El "cómo consultar" lo definen las skills de Dynatrace (`dt-dql-essentials`, `dt-obs-*`).

## 1. Principios

| Principio | En la práctica |
|---|---|
| El objetivo es saber qué pasó | No detener la investigación por cantidad de queries, ventana o tiempo invertido si aún hay preguntas abiertas que cambian la conclusión. |
| Partir de un ancla, no quedarse en ella | Problem / evento / rango es el inicio; ampliar a donde lleve la evidencia y registrarlo. |
| Davis orienta, no concluye | La entidad raíz de Davis indica dónde mirar; validar con evidencia propia. |
| Evidencia antes que opinión | Cada hecho con evidencia reproducible del tenant (dtctl). |
| Sustento oficial para interpretar | Comportamiento de Dynatrace o de la tecnología → documentación oficial. |
| Correlación ≠ causalidad | Una relación causal necesita secuencia temporal + mecanismo + alternativas descartadas. |
| Comparar contra baseline | Un valor es "anómalo" solo frente a un período comparable. |
| Datos completos | Nada truncado, con límite alcanzado o muestreado sostiene una conclusión. |
| Blameless | Sistemas y procesos, no personas. |
| Escribir para quien lee | El resumen y los diagramas los entiende cualquier persona; el detalle técnico va en las Secciones 2 a 9. |
| Brechas en el momento | Cada vez que falta un dato que debería existir, registrarlo como brecha. |

## 2. Preguntas que un RCA completo responde (checklist de cobertura)

Revisar antes de entregar; no es un orden de ejecución.

**Qué pasó**
- [ ] ¿Cuál fue el síntoma visible para usuarios/negocio?
- [ ] ¿Qué detectó Davis, cuándo, en qué entidad, qué eventos agrupó? ¿Es recurrente?

**Impacto**
- [ ] ¿Qué servicios, aplicaciones, usuarios y transacciones se afectaron, en qué magnitud y por cuánto tiempo?
- [ ] ¿Se afectaron SLOs o procesos de negocio medibles?

**Dónde y cómo se propagó**
- [ ] ¿Cuál fue el primer componente anómalo (en el tiempo)?
- [ ] ¿Por qué camino de dependencias llegó a los usuarios? ¿Qué componentes no se afectaron?
- [ ] ¿Qué componentes no tienen visibilidad?

**Por qué**
- [ ] ¿Hubo cambios previos (deploy, configuración, infraestructura, escalado, certificados, cuotas, tráfico)?
- [ ] ¿Qué dicen métricas, traces, logs y eventos de la entidad candidata frente a su baseline?
- [ ] ¿Qué hipótesis se evaluaron, con qué evidencia a favor/en contra, y cuál quedó?
- [ ] ¿Cuál es el disparador, la causa raíz, los factores contribuyentes y mitigantes?
- [ ] ¿La causa raíz es accionable (5 porqués) y no se queda en "error humano" o "fallo puntual"?
- [ ] ¿Coincide con lo propuesto por Davis? Si no, ¿por qué?

**Tiempos y respuesta**
- [ ] Inicio de impacto, detección, reconocimiento, mitigación, resolución (MTTD/MTTA/MTTR) con fuente.

**Qué no vimos y qué haremos**
- [ ] Brechas de cobertura, telemetría, alertamiento, contexto y proceso.
- [ ] Acciones de contención, correctivas, preventivas y de detección, cada una vinculada a su origen.

## 3. Técnicas recomendadas (usar las que apliquen)
- **5 Porqués** para profundizar hasta una causa accionable; ramificar si hay más de una causa.
- **Tabla de hipótesis** (a favor / en contra / estado) para mantener la investigación honesta.
- **Comparación de traces** normales vs. fallidos para ubicar dónde se concentra el tiempo o el error.
- **Agrupación de logs por patrón** en lugar de lectura línea a línea.
- **Comparación temporal** (mismo período día/semana anterior) para distinguir anomalía de patrón normal.
- **Análisis de recurrencia** de la misma entidad/categoría en el histórico.
- **Inventario del tenant** (`dtctl inventory`) al inicio, para saber qué datos existen y detectar brechas de cobertura con evidencia.
- **Analizadores Davis** (`dt-obs-analytics`) sobre las timeseries de evidencia, para confirmar anomalías frente al baseline y correlaciones.

## 4. Brechas de observabilidad — categorías
Cobertura (sin OneAgent/instrumentación, componentes opacos) · Telemetría (logs sin contexto de entidad/trace, falta de métricas de negocio, retención) · Alertamiento (detección tardía, umbrales, ruido) · Contexto (sin eventos de deploy/config, sin ownership/tags, sin versión) · Proceso (sin runbook, notificación errónea).

## 5. Antipatrones
- Investigar sin ancla (escaneos amplios sin filtro de entidad).
- Detenerse en lo que dijo Davis.
- Concluir con datos parciales o muestreados.
- Afirmar significado de campos/errores sin documentación oficial.
- Acciones genéricas sin responsable, fecha ni criterio de cierre.
- Capturas de pantalla como evidencia en lugar de queries reproducibles.
- Zonas horarias mezcladas sin indicarlo.
- Resumen ejecutivo escrito en jerga técnica (DQL, IDs, siglas) que solo entiende el equipo que investigó.
