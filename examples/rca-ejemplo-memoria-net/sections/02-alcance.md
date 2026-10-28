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
