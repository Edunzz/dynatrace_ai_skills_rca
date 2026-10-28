## 6. Brechas de observabilidad detectadas
| # | Categoría | Brecha | Efecto en el incidente | Recomendación | Prioridad |
|---|---|---|---|---|---|
| B1 | Contexto | El tenant no recibe eventos de Kubernetes ni de despliegue (0 en 24 h, Evidencia 3.3) | No se pudo confirmar el motivo del reinicio ni descartar un cambio previo | Activar la ingesta de eventos de Kubernetes y enviar eventos de despliegue desde CI/CD | 🟠 Alta |
| B2 | Alertamiento | No hay alerta de memoria del contenedor cerca del límite ni de tiempo en GC | 18 reinicios en 48 h y problemas repetidos sin aviso preventivo (Evidencia 5.5 y 5.6) | Detector: memoria sobre el 85 % del límite por 10 min y GC sobre el 25 % | 🟠 Alta |
| B3 | Telemetría | Sin análisis de memoria del proceso .NET (qué objetos retienen memoria) | No se pudo confirmar por qué crece la memoria | Capturar un volcado de memoria cuando supere el 80 % del límite y analizarlo | 🟡 Media |
| B4 | Proceso | Sin registro del reconocimiento humano del problema | MTTA no medible | Vincular los problemas de Davis con la herramienta ITSM | 🟡 Media |
