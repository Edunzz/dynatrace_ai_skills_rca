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
