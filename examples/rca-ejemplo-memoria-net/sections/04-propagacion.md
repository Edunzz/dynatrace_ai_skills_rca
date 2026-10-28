## 4. Diagrama de propagación de la afectación
![Propagación de la afectación desde la copia 1 del servicio hacia los consumidores](img:../diagrams/D1-propagacion.png)
*Figura 2. Cómo se propagó la falla: una copia del servicio llegó casi al tope de memoria, dejó de responder y sus consultas fallaron; la otra copia siguió sana. Rojo: causa raíz y componentes con errores · Naranja: degradado · Verde: sano · Gris punteado: sin visibilidad.*

**Secuencia de propagación**
1. **23:12 — Copia 1 (pod …-a):** con la memoria del contenedor al 91 % del límite, el proceso .NET pasa 91–99 % del tiempo en GC y sus solicitudes quedan detenidas hasta 81 s (Evidencia 5.3, 5.4 y 5.2).
2. **23:13 — Servicio de autorización:** las solicitudes atendidas por esa copia terminan con HTTP 500; la tasa de fallas del servicio llega a 9,43 % en el minuto (Evidencia 2.1 y 5.1).
3. **23:13–23:14 — Consumidores:** reciben error en 9 autorizaciones (Evidencia 2.1).
4. **23:14 — Recuperación:** Kubernetes reinicia el contenedor, la GC vuelve a 0 % y el servicio se normaliza a las 23:21 (Evidencia 5.5 y 5.3).

**Componentes no afectados relevantes:** copia 2 (pod …-b) con 0 fallas, GC 0 % y memoria al 71 % del límite (Evidencia 2.2, 5.3 y 5.4); Davis no registró otras entidades afectadas (Evidencia 3.2).
**Puntos ciegos:** motivo exacto del reinicio (el tenant no recibe eventos de Kubernetes) y consumidores del servicio, no identificados en este ejemplo (ver B1).
