# Diagramas draw.io para el RCA — estilo Dynatrace

## 0. Dependencia obligatoria
- Toda imagen del RCA se crea con **cualquier skill de draw.io** que genere `.drawio` (la oficial de jgraph `drawio`, `drawio-skill` u otra) y se exporta con **draw.io Desktop**. `scripts/check_prereqs.py` valida ambas (gate R5).
- Usar **exactamente la ruta del ejecutable que reporta `check_prereqs.py`** en los comandos de exportación; el `drawio` del PATH puede apuntar a otro ejecutable que no responde.
- Leer el `SKILL.md` de la skill drawio antes de dibujar: ahí están las reglas de XML, layout y validación.
- No sustituir por Mermaid renderizado, matplotlib, Graphviz, imágenes por URL ni capturas.
- D1, D2 y D3 son el mínimo. Se pueden agregar diagramas (arquitectura detallada, antes/después) con el mismo estándar.

## 1. Para quién se dibuja
Las figuras las mira **cualquier persona**, no solo el equipo técnico. Un diagrama está bien si alguien de negocio entiende en 10 segundos qué falló, dónde empezó y cómo llegó al cliente.

| Regla | Detalle |
|---|---|
| Título simple | Arriba: `<Qué muestra> — <Problem ID>` en lenguaje simple ("Cómo se propagó la falla de pagos — P-2609301"). |
| Cómo leerlo | Debajo del título, una línea gris: "Cómo leer este diagrama: …" (dirección de lectura y qué significa el rojo). |
| Nombres | Nombre de negocio primero ("Pagos"), nombre técnico debajo y más pequeño ("checkout-service"). Nunca IDs de entidad. |
| Cifras | Una métrica clave por nodo en palabras ("errores 38 %", "respuesta +2,1 s"). |
| Color con respaldo | El color nunca es la única señal: la causa raíz además lleva borde grueso y la etiqueta **CAUSA RAÍZ**; sin visibilidad, borde punteado; descartada, texto tachado. |
| Densidad | Máx. ~15 nodos. Si hay más, agrupar en una capa con contador ("Servicios backend (6)"). |
| Horas | Hora local de la máquina (la misma de la ficha), calculada con `scripts/hora_local.py`. |
| Leyenda | Obligatoria, esquina inferior derecha (copiarla del kit). |

## 2. Estilo visual Dynatrace (tokens Strato, tema claro)

Kit listo para copiar: `assets/drawio/rca-kit-dynatrace.drawio` (vista previa en `rca-kit-dynatrace.png`). Contiene todos los nodos, flechas, marcadores de la línea de tiempo, la banda de marca y la leyenda. **Partir de ese archivo** (copiar celdas) en lugar de inventar estilos.

Principio: **la marca Dynatrace va en el marco y el color semántico en el contenido.** La banda superior azul → violeta identifica el documento como Dynatrace. Dentro del diagrama, el rojo se reserva para errores y fallas, como en la interfaz de Dynatrace.

| Elemento | Especificación |
|---|---|
| Lienzo | Horizontal, ancho 1400–1800 px a escala 1, fondo `#ffffff` |
| Banda de marca | Rectángulo de 8 px de alto, ancho completo, arriba: `fillColor=#1966ff;gradientColor=#7d6afa;gradientDirection=east;strokeColor=none` |
| Fuente | `fontFamily=Helvetica` (se ve igual en Windows, macOS y Linux). Título 20 bold, nodos 12, notas 11 |
| Texto | Principal `#31323a`, secundario `#5c5d66` |
| Flechas | Unidireccionales, del origen al afectado. Etiqueta con fondo blanco: orden ①②③ + hora local + mecanismo |

Base de todo nodo: `rounded=1;arcSize=10;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=12;spacing=6;` + el estilo del rol:

| Rol | Significado | Estilo (agregar a la base) |
|---|---|---|
| Causa raíz | Origen del incidente | `fillColor=#e01032;strokeColor=#c80026;strokeWidth=3;fontColor=#ffffff;` + etiqueta "CAUSA RAÍZ" |
| Con errores / falla | Falla visible | `fillColor=#faeae9;strokeColor=#c80026;strokeWidth=2;fontColor=#31323a;` |
| Degradado | Lento o parcial, sin caerse | `fillColor=#fdf3dd;strokeColor=#d56b1a;strokeWidth=2;fontColor=#31323a;` |
| Sano | No afectado | `fillColor=#eaf4ee;strokeColor=#007242;strokeWidth=1;fontColor=#31323a;` |
| Cambio / deploy | Cambio relevante | `fillColor=#e7eefb;strokeColor=#0b56e5;strokeWidth=2;fontColor=#31323a;` |
| Sin visibilidad | Sin telemetría (conecta con Sección 6) | `fillColor=#f4f4f6;strokeColor=#5c5d66;strokeWidth=1;dashed=1;dashPattern=6 4;fontColor=#5c5d66;` |
| Neutro | Pasos intermedios del árbol D3 | `fillColor=#ffffff;strokeColor=#5c5d66;strokeWidth=1;fontColor=#31323a;` |
| Hipótesis descartada | Rama ❌ en D3 | `fillColor=#f4f4f6;strokeColor=#5c5d66;strokeWidth=1;dashed=1;fontColor=#5c5d66;fontStyle=8;` |

| Otros elementos | Estilo |
|---|---|
| Capa / contenedor | `rounded=1;arcSize=3;whiteSpace=wrap;html=1;fontFamily=Helvetica;fillColor=#fafafb;strokeColor=#e4e4e7;verticalAlign=top;align=left;spacingLeft=12;spacingTop=4;fontSize=11;fontStyle=1;fontColor=#5c5d66;` (etiqueta en MAYÚSCULAS) |
| Flecha de propagación | `endArrow=block;endFill=1;html=1;fontFamily=Helvetica;strokeColor=#c80026;strokeWidth=2;fontColor=#c80026;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;` |
| Flecha normal / del árbol | `endArrow=block;endFill=1;html=1;fontFamily=Helvetica;strokeColor=#5c5d66;strokeWidth=1;fontColor=#5c5d66;fontSize=11;labelBackgroundColor=#ffffff;` |
| Banda de impacto (D2) | `rounded=0;html=1;fillColor=#e01032;opacity=10;strokeColor=none;` + texto "Impacto en clientes" en `#c80026` |
| Medida MTTD/MTTA/MTTR (D2) | `endArrow=baseDash;startArrow=baseDash;endFill=0;startFill=0;html=1;fontFamily=Helvetica;strokeColor=#31323a;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;` |

Marcadores de la línea de tiempo (D2), por **Tipo** de suceso (trazo / relleno):

| Tipo | Trazo | Relleno |
|---|---|---|
| Cambio | `#0b56e5` | `#e7eefb` |
| Impacto | `#c80026` | `#faeae9` |
| Detección | `#d56b1a` | `#fdf3dd` |
| Respuesta / Diagnóstico | `#8261cf` | `#f1edfb` |
| Mitigación | `#815d00` | `#fdf7e8` |
| Resolución | `#007242` | `#eaf4ee` |
| Comunicación | `#5c5d66` | `#f4f4f6` |

Origen de los colores: design tokens de Strato (https://developer.dynatrace.com/design/design-tokens/Colors/, tema claro): Critical `#c80026`/`#e01032`/`#faeae9`, Success `#007242`/`#eaf4ee`, Primary `#0b56e5`/`#1966ff`/`#e7eefb`, Warning `#815d00`/`#fdf7e8`, Neutral `#31323a`/`#5c5d66`/`#f4f4f6`/`#e4e4e7`/`#fafafb`. El naranja de degradado `#d56b1a` es el token de gráficos `loglevel-severe`, el mismo que usan los dashboards. El violeta `#7d6afa`/`#8261cf` viene de la paleta de íconos de apps de Dynatrace.

## 3. D1 — Diagrama de propagación de la afectación
- Tipo: grafo dirigido por capas (contenedores), de izquierda a derecha: **Usuarios/Canales → Frontend → Servicios → Dependencias (BD, colas, APIs externas) → Infraestructura (procesos, pods, hosts, nodos)**. Se puede invertir para que el origen quede a la izquierda si mejora la lectura.
- Cada nodo: nombre de negocio + nombre técnico + métrica clave del impacto, con el estilo de su rol.
- Flechas de propagación en rojo, numeradas en orden temporal ①②③ con la hora local.
- Componente causa raíz con el estilo "Causa raíz" (relleno rojo, borde grueso, etiqueta CAUSA RAÍZ).
- Componentes sin telemetría con el estilo "Sin visibilidad" (conectan con la Sección 6).
- Fuente de datos: topología Smartscape + Evidencias 2.x y 3.x.
- Para más de ~10 nodos, usar el layout automático de la skill drawio en vez de posicionar a mano.

## 4. D2 — Línea de tiempo de los sucesos
- Tipo: eje horizontal en hora local, con flecha al final.
- Un marcador (círculo) por cada suceso de la tabla de la Sección 3, con su tarjeta "HH:MM · Tipo + descripción corta", alternando arriba/abajo para evitar solapamiento.
- Color de marcador y tarjeta según la tabla de tipos.
- Banda de impacto translúcida entre el inicio y el fin del impacto.
- Debajo del eje, medidas MTTD, MTTA y MTTR con su valor. Primera mención en lenguaje simple: "MTTR 38 min · tiempo hasta volver a la normalidad".
- Mermaid `timeline` puede servir de punto de partida si la skill drawio lo soporta, pero el resultado final debe cumplir estas reglas.

## 5. D3 — Árbol de causa raíz (5 porqués)
- Tipo: árbol vertical de arriba a abajo. Raíz arriba = síntoma de negocio (estilo "Con errores"); hojas abajo = causa(s) raíz (estilo "Causa raíz").
- Cada nodo intermedio (estilo "Neutro"): "¿Por qué? → respuesta" (máx. 2 líneas) + etiqueta pequeña "Ev. N.x".
- Ramas descartadas con el estilo "Hipótesis descartada" (tachado + punteado).
- Factores contribuyentes con el estilo "Degradado", colgando lateralmente de la rama que amplificaron.

## 6. Exportación, revisión e incrustación

```bash
# DRAWIO = ruta exacta reportada por scripts/check_prereqs.py (p. ej. "C:\Program Files\draw.io\draw.io.exe")
# 1) Borrador para revisión visual: SIN -e y con ancho acotado (las imágenes con XML embebido o muy grandes
#    pueden fallar al leerlas con visión)
"$DRAWIO" -x -f png --width 2000 -b 10 -o rca/diagrams/D1-propagacion.preview.png rca/diagrams/D1-propagacion.drawio
# 2) Final: PNG con XML embebido (editable en draw.io), escala 2, borde 10 px
"$DRAWIO" -x -f png -e -s 2 -b 10 -o rca/diagrams/D1-propagacion.png rca/diagrams/D1-propagacion.drawio
"$DRAWIO" -x -f png -e -s 2 -b 10 -o rca/diagrams/D2-linea-tiempo.png rca/diagrams/D2-linea-tiempo.drawio
"$DRAWIO" -x -f png -e -s 2 -b 10 -o rca/diagrams/D3-causa-raiz.png rca/diagrams/D3-causa-raiz.drawio
```
- **Revisar visualmente cada borrador** contra la checklist de abajo y corregir antes del export final. Si el modelo no puede ver imágenes, validar la estructura con la herramienta de la skill drawio (solapes, aristas sueltas) y pedir al usuario que revise los PNG antes de publicar.
- Si el PNG final pesa más de 400 KB: re-exportar con `-s 1` o reducir nodos.
- En Linux sin entorno gráfico: anteponer `xvfb-run -a`.
- `build_notebook.py` incrusta las referencias `img:` como `data:image/png;base64` y repara el bloque IEND si una versión antigua de draw.io lo truncó con `-e`.
- PNG es el formato obligatorio; no usar SVG ni JPG incrustados.

## 7. Checklist visual (antes de incrustar)
- [ ] Banda de marca arriba, título simple y línea "Cómo leer este diagrama".
- [ ] Rojo solo en errores/fallas; causa raíz con borde grueso y etiqueta CAUSA RAÍZ.
- [ ] Nombres de negocio legibles; sin IDs; una métrica por nodo.
- [ ] Flechas del origen al afectado, numeradas con hora local; etiquetas sin solaparse.
- [ ] Leyenda abajo a la derecha; ≤ ~15 nodos; nada cortado en los bordes.
- [ ] Alguien no técnico entiende el mensaje principal en 10 segundos.
