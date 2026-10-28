## 3. Línea de tiempo de los sucesos
![Línea de tiempo del incidente P-2601001 desde la primera falla hasta la normalización](img:../diagrams/D2-linea-tiempo.png)
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
