# Lineamientos de uso de dtctl en el RCA

> Estos lineamientos cuidan **seguridad y trazabilidad**. No limitan qué se consulta, cuántas veces ni sobre qué ventanas. Fuente de verdad de comandos y flags: https://docs.dynatrace.com/docs/platform/dtctl, el repo https://github.com/dynatrace-oss/dtctl (`docs/`), `dtctl <comando> --help` y `dtctl commands` (catálogo para agentes). Si un flag mencionado aquí no existe en la versión instalada, manda la ayuda de la CLI. Verificado con dtctl 0.37.

## 1. Sesión
- Validar con `python <skill>/scripts/check_prereqs.py`. El script ejecuta `dtctl version`, `dtctl doctor` y `--check-scopes`, y reporta el contexto activo y su URL.
- **Confirmar con el usuario** que ese contexto es el tenant del incidente (gate R2). Si es otro, no cambiar el contexto global del usuario: pasar `--context <ctx>` en **cada** comando (no se persiste). Para validar otro contexto: `check_prereqs.py --context <ctx>`.
- Antes de un comando dudoso, `--check-scopes` dice si el token tiene los scopes necesarios sin ejecutarlo.
- Modo agente: dtctl lo detecta solo (envelope JSON con códigos de error estables); `-A` lo fuerza y `--no-agent` lo desactiva.
- Manejo de errores según `docs/AGENT_MODE.md`: `insufficient_scope` / `permission_denied` → no reintentar, informar el permiso faltante; `rate_limited` / `server_error` / `timeout` → reintentar con espera; `bad_request` → corregir la query.
- `dtctl inventory` (solo lectura) dice qué datos y capacidades existen en el tenant. Evita buscar en fuentes vacías, y cada capacidad ausente, con su evidencia, es candidata a brecha de la Sección 6.

## 2. Seguridad
- Sobre el tenant, **solo lectura** durante la investigación (`query`, `verify`, `inspect`, `inventory`, `get`, `describe`, `doctor`, `ctx`…). El agente puede usar cualquier comando de lectura que necesite.
- La única escritura es publicar/actualizar el notebook del RCA (`dtctl apply`).
- Nunca imprimir tokens ni secretos en evidencia o notebook (`check_prereqs.py` ya oculta el token de `dtctl doctor`).

## 3. Trazabilidad de la evidencia
Cualquier query puede ejecutarse libremente durante la exploración. Las que **sustentan una afirmación** del RCA deben:
1. Guardarse como archivo en `rca/queries/E<N.x>-<descripcion>.dql`.
2. Validarse (`dtctl verify query -f <archivo>`) y ejecutarse desde el archivo con ventana **absoluta** para que sea reproducible:
   `dtctl query -f rca/queries/E2.1-errores-servicio.dql --default-timeframe-start 2026-09-30T12:00:00Z --default-timeframe-end 2026-09-30T16:00:00Z --timezone UTC -o json > rca/evidence/E2.1.json`
3. Guardar el resultado en `rca/evidence/` y anotarlo en `rca/evidence/INDEX.md` (ID, ventana, registros, advertencias, qué sustenta).
4. Incluirse en el notebook como sección `[Evidencia N.x]` usando el mismo `.dql` (`query_file` en el spec). `build_notebook.py` rechaza citas a evidencias que no existan.

## 4. Datos completos (no truncar conclusiones)
- Revisar en cada resultado advertencias de truncamiento, límite de escaneo o sampling.
- Si hay truncamiento: refinar la query (filtros, agregación) siguiendo DQL best practices, y/o elevar los límites de esa ejecución: `--max-result-records`, `--max-result-bytes`, `--default-scan-limit-gbytes`.
- Para cifras que sostienen conclusiones, ejecutar sin sampling (no usar `--default-sampling-ratio`).
- Resultados grandes: `--spill-to rca/evidence/E<N.x>.jsonl` los guarda en disco y `dtctl inspect` los revisa sin volver a consultar Grail.
- Si se elevaron límites, replicarlos en `querySettings` de esa evidencia en el spec del notebook.
- Una `timeseries` con varias métricas devuelve solo las series que existen en todas ellas: si una métrica no existe para alguna entidad (p. ej. reinicios), esa entidad desaparece del resultado. Separar en evidencias distintas las métricas con distinta cobertura.
- Antes de sumar una métrica entre dimensiones, comprobar que sea aditiva: si la suma da un valor imposible (p. ej. memoria mayor que el límite del contenedor), no usarla para concluir y buscar otra métrica.

## 5. Cuando dtctl no alcanza
- Datos fuera de Dynatrace (ITSM, chat de guerra, cambios no registrados): pedirlos al usuario y citarlos como **fuente externa declarada**.
- Si el dato debería estar en Dynatrace y no está → brecha de observabilidad (Sección 6).
