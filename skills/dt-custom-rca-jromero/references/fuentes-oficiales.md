# Sustento de afirmaciones: evidencia + documentación oficial

## 1. Regla
Cada afirmación del RCA pertenece a un tipo y requiere un sustento específico:

| Tipo de afirmación | Ejemplo | Sustento requerido |
|---|---|---|
| Hecho observado | "La tasa de error de checkout-service subió a 38 % a las 09:09" | Evidencia del tenant obtenida con dtctl (Evidencia N.x) |
| Interpretación del producto Dynatrace | "Davis agrupó los eventos en un único problema porque comparten causa raíz" | Evidencia + **documentación oficial de Dynatrace** |
| Interpretación de la tecnología afectada | "El error ORA-00018 indica que se excedió el máximo de sesiones" | Evidencia + **documentación oficial del fabricante** |
| Relación causal | "El deploy v2.4.1 causó el agotamiento del pool" | Evidencia temporal + evidencia del mecanismo + doc oficial del mecanismo + hipótesis alternativas descartadas |
| Dato externo | "El ticket se abrió a las 09:20" | Fuente externa declarada (proporcionada por el usuario) |

Si falta el sustento requerido → la afirmación se escribe con **⚠️ Hipótesis no confirmada** y se indica qué falta para confirmarla.

## 2. Fuentes oficiales aceptadas

| Prioridad | Fuente | Para qué |
|---|---|---|
| 1 | Documentación Dynatrace — https://docs.dynatrace.com | Comportamiento de Davis, problemas, eventos, métricas, OneAgent, Grail, DQL |
| 1 | Semantic Dictionary — https://docs.dynatrace.com/docs/semantic-dictionary | Significado y estabilidad de campos (stable/experimental/deprecated) |
| 1 | Root cause analysis concepts — https://docs.dynatrace.com/docs/dynatrace-intelligence/root-cause-analysis/concepts | Problemas, eventos Davis, impacto, ciclo de vida, duplicados |
| 1 | DQL best practices — https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/dql-best-practices | Cómo se construyeron las queries |
| 1 | dtctl — https://docs.dynatrace.com/docs/platform/dtctl y https://github.com/dynatrace-oss/dtctl/tree/main/docs | Comandos y flags usados |
| 1 | Documentación oficial del fabricante de la tecnología afectada (Oracle, Microsoft, Red Hat, Kubernetes, AWS, Azure, GCP, Spring, IBM, etc.) | Códigos de error, límites, comportamientos de la tecnología |
| 2 | Skills oficiales Dynatrace for AI (github.com/Dynatrace/dynatrace-for-ai) | Patrones DQL y campos; si se usa para una interpretación, confirmar en docs.dynatrace.com |
| 3 | Notas de versión / advisories oficiales del fabricante | Bugs conocidos, cambios de comportamiento por versión |

**No aceptadas como sustento único:** foros comunitarios, blogs, Stack Overflow, respuestas de IA, memoria del agente. Pueden orientar la búsqueda, pero la cita final debe ser oficial.

## 3. Cómo citar
- Cada fuente se registra en la Sección **9.3 Referencias oficiales** con ID `[R1]`, `[R2]`…: título, URL, fecha de consulta y qué afirmación sustenta.
- En el texto y tablas: `(Evidencia 5.1; [R3])`.
- Parafrasear, no copiar bloques de la documentación. Citas textuales solo si son imprescindibles y muy breves.
- Anotar la versión del producto cuando el comportamiento depende de ella (ej. versión de OneAgent, de la BD, del runtime).

## 4. Nivel de certeza de la causa raíz
Se declara en la Sección 5.1:

| Nivel | Criterio |
|---|---|
| ✅ Confirmada | Evidencia directa del mecanismo + relación temporal + doc oficial + alternativas descartadas |
| ⚠️ Probable | Evidencia fuerte pero falta un eslabón (p. ej. brecha de observabilidad impide verlo) |
| ❌ No determinada | Evidencia insuficiente; se documentan hipótesis y qué datos faltan |
