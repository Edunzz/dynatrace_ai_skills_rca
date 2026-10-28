## 7. Plan de acción
| ID | Acción | Tipo | Origen | Responsable | Fecha compromiso | Prioridad | Estado | Criterio de cierre |
|---|---|---|---|---|---|---|---|---|
| A1 | Reinicio automático del contenedor afectado | Contención | Disparador | @Kubernetes (automático) | 2026-01-15 | 🔴 Crítica | ✅ Completado | Servicio en baseline desde las 23:21 |
| A2 | Analizar un volcado de memoria y corregir la retención en el código | Correctiva | Causa raíz | @Por asignar | 2026-01-29 | 🔴 Crítica | Pendiente | Crecimiento de memoria menor a 10 MB/h durante 48 h |
| A3 | Mitigación temporal: reciclado programado de pods antes del 80 % de memoria o ajuste del límite | Preventiva | Factor contribuyente | @Por asignar | 2026-01-22 | 🟠 Alta | Pendiente | 0 problemas de GC o fallas en 7 días |
| A4 | Crear detector de memoria frente al límite y de tiempo en GC | Detección | B2 | @Por asignar | 2026-01-22 | 🟠 Alta | Pendiente | Alerta probada antes del siguiente ciclo de memoria |
| A5 | Ingerir eventos de Kubernetes y de despliegue | Detección | B1 | @Por asignar | 2026-01-29 | 🟠 Alta | Pendiente | Eventos de Kubernetes visibles en Grail para el clúster |
- Responsables `@Por asignar`: definir con el equipo dueño del servicio.
