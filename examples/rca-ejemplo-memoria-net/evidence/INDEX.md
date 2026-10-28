# Índice de evidencia — RCA P-2601001 (ejemplo)

> En un RCA real esta carpeta guarda además los resultados `E<N.x>.json` de cada query. En este ejemplo se omiten porque contienen datos del tenant.

Contexto dtctl: `mi-tenant` (https://abc12345.apps.dynatrace.com) · dtctl 0.37.0 · Ejecutado: 2026-01-16.
Todas las queries llevan la ventana absoluta dentro del `.dql`; se validaron con `dtctl verify query` y se ejecutaron con `dtctl query -f <archivo> -o json`.

| ID | Archivo | Ventana (UTC) | Registros | Advertencias | Sustenta |
|---|---|---|---|---|---|
| E2.1 | queries/E2.1-errores-servicio.dql | 2026-01-16 03:45 → 04:45 | 1 serie | Ninguna | 9 fallas de 4.863 solicitudes; pico 9,43 % a las 04:13 |
| E2.2 | queries/E2.2-impacto-por-pod.dql | 2026-01-16 03:45 → 04:45 | 2 | Conteos extrapolados (muestreo de trazas) | pod-a 9 de 2.298 fallidas; pod-b 0 de 2.600 |
| E3.1 | queries/E3.1-eventos-davis.dql | 2026-01-16 03:45 → 04:45 | 4 | Ninguna | Fallas 04:09–04:21; GC larga 04:12–04:18; reinicio 04:14:51 |
| E3.2 | queries/E3.2-problemas-davis.dql | 2026-01-16 03:45 → 04:45 | 2 | Ninguna | P-2601001 04:14–04:21; P-2601002 04:15–04:18 |
| E3.3 | queries/E3.3-eventos-de-cambio-24h.dql | 2026-01-15 04:45 → 2026-01-16 04:45 | 4 | Ninguna | 0 eventos de cambio o de Kubernetes en 24 h |
| E5.1 | queries/E5.1-fallas-por-pod-minuto.dql | 2026-01-16 03:45 → 04:45 | 2 series | Ninguna | Fallas solo en la copia 1 (04:08 y 04:12–04:14) |
| E5.2 | queries/E5.2-detalle-fallas.dql | 2026-01-16 03:45 → 04:45 | 6 | 6 trazas muestreadas representan 9 fallas | HTTP 500; duraciones 2,6 s a 81 s |
| E5.3 | queries/E5.3-gc-proceso-net.dql | 2026-01-16 03:45 → 04:45 | 2 series | Ninguna | GC pod-a 5 % → 99 % (04:14), 0 % tras reinicio; pod-b 0 % |
| E5.4 | queries/E5.4-memoria-contenedor.dql | 2026-01-16 03:45 → 04:45 | 2 series | Ninguna | pod-a 936 MB (91,4 % de 1 GiB); pod-b 728 MB (71,1 %) |
| E5.5 | queries/E5.5-reinicios-contenedor.dql | 2026-01-14 04:45 → 2026-01-16 04:45 | 5 series | Ninguna | 18 reinicios en 48 h (pod-c 8, pod-b 5, pod-d 2, pod-a 2, pod-e 1) |
| E5.6 | queries/E5.6-recurrencia-7d.dql | 2026-01-09 04:45 → 2026-01-16 04:45 | 2 | Ninguna | 2 problemas de fallas y 2 de GC en 7 días |
| E5.7 | queries/E5.7-tendencia-memoria-48h.dql | 2026-01-14 04:45 → 2026-01-16 04:45 | 5 series | Ninguna | Patrón en sierra: +75–90 MB/h hasta 850–930 MB en todas las copias |

Descartado durante la exploración: la suma de `dt.runtime.clr.memory.consumption` por generación devolvía valores mayores al límite del contenedor (no es aditiva), por lo que no se usó para concluir; se reemplazó por el working set del contenedor (E5.4, E5.7).
