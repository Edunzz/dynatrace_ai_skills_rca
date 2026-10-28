# Mapa: preguntas del RCA → skills de Dynatrace

> Esta skill **no define queries**. Para cada pregunta, cargar la skill oficial indicada y construir las consultas según ella y el Semantic Dictionary (https://docs.dynatrace.com/docs/semantic-dictionary). El mapa es orientativo: el agente puede usar cualquier otra fuente o skill que aporte. `scripts/check_prereqs.py` lista qué skills de dominio están instaladas.

| Pregunta del RCA | Fuentes típicas en Grail | Skill(s) a cargar |
|---|---|---|
| ¿Qué datos existen en este tenant? (antes de buscar) | catálogo de datos, buckets, entidades | `dtctl inventory` + `dt-dql-essentials` |
| ¿Qué detectó Davis y cuándo? ¿Es recurrente? | problemas y eventos Davis | `dt-obs-problems` |
| ¿Por qué se agruparon esos eventos? ¿Por qué alertó tarde, o no alertó? ¿A quién se notificó? | eventos de alerta, detectores, workflows | `dt-alerting` |
| ¿Hubo cambios (deploy, configuración, reinicios)? | eventos | `dt-obs-problems` (+ `dt-obs-kubernetes` para eventos K8s) |
| ¿Cuánto se degradaron los servicios? | métricas de servicio, spans | `dt-obs-services`, `dt-obs-tracing` |
| ¿Dónde falló dentro de la transacción? | spans / traces | `dt-obs-tracing` |
| ¿Qué registraron los logs? | logs | `dt-obs-logs` |
| ¿Hosts, procesos, contenedores? | métricas y eventos de infraestructura | `dt-obs-hosts` |
| ¿Kubernetes (pods, nodos, workloads)? | métricas y eventos K8s | `dt-obs-kubernetes` |
| ¿Servicios de nube (AWS / Azure / GCP)? | recursos y métricas cloud | `dt-obs-aws`, `dt-obs-azure`, `dt-obs-gcp` |
| ¿Usuarios / frontend afectados? | eventos y sesiones de usuario | `dt-obs-frontends` |
| ¿Impacto de negocio (transacciones, montos)? | bizevents | `dt-dql-essentials` (`fetch bizevents`) |
| ¿Es una anomalía frente al baseline? ¿Qué métricas se correlacionan? | timeseries de la evidencia | `dt-obs-analytics` (analizadores Davis sobre las evidencias o el notebook) |
| ¿Hubo una tendencia o saturación previa (capacidad)? | timeseries históricas | `dt-obs-predictive-analytics` |
| ¿Fue un incidente de seguridad? | security.events | `dt-sec-insights`, `dt-sec-contextualization` |
| ¿Topología / dependencias? | Smartscape | `dt-dql-essentials` + skill del dominio |
| Queries heredadas con entidades clásicas (`fetch dt.entity.*`, `entityName`) | — | `dt-migration` |
| Sintaxis y buenas prácticas DQL | — | `dt-dql-essentials` |
| Comandos y flags de dtctl | — | skill `dtctl` (`dtctl skills install`) |
| Crear/actualizar el notebook | — | `dt-app-notebooks` |

Si el incidente involucra un dominio sin skill instalada (p. ej. una base de datos o una extensión específica), verificar en el catálogo de `dynatrace/dynatrace-for-ai` si existe y pedir su instalación; si no existe, apoyarse en `dt-dql-essentials` y en la documentación oficial.
