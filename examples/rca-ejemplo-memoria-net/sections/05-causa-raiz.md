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
![Árbol de causa raíz (5 porqués) del incidente P-2601001](img:../diagrams/D3-causa-raiz.png)
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
