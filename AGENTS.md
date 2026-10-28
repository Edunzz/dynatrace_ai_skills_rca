# AGENTS.md

Instrucciones para agentes de IA que trabajan con este repositorio.

## Usar la skill

Este repositorio contiene la skill **dt-custom-rca-jromero** (estándar [agentskills.io](https://agentskills.io)) en `skills/dt-custom-rca-jromero/`.

Cuando el usuario pida un **RCA, análisis de causa raíz, post-mortem o informe de incidente sobre Dynatrace**, o que "investigues el problema P-XXXX":

1. Lee `skills/dt-custom-rca-jromero/SKILL.md` completo y síguelo. Carga cada archivo de `references/` en el momento en que el SKILL.md lo indica.
2. Antes de investigar, ejecuta `python skills/dt-custom-rca-jromero/scripts/check_prereqs.py`. Si el resultado es NO LISTO, detente e informa qué falta.
3. Confirma con el usuario el contexto de dtctl (tenant) antes de consultar.
4. Entrega el resultado solo en el formato definido: un notebook de Dynatrace validado con `scripts/build_notebook.py`.
5. Escribe el notebook en el idioma del pedido (español o inglés), salvo que el usuario indique otro, y decláralo en el spec con `"language"`.

## Modificar este repositorio

- El `README.md` está en inglés. La skill y la carpeta `docs/` están en español. Los notebooks se generan en español o en inglés.
- El ejemplo existe en los dos idiomas (`examples/rca-ejemplo-memoria-net` y `examples/rca-example-memory-net`). Si cambias uno, refleja el cambio en el otro.
- Los diagramas del README se editan en `docs/images/*.drawio`. Exporta el PNG con el XML embebido: `drawio -x -f png -e -s 2 -b 10`.
- **No subas datos de clientes.** Todo ejemplo debe estar anonimizado: nombres, tenant, IDs de entidad y de problema, hosts, pods y fechas. Las carpetas `rca/` y `rca-*/` de la raíz están en `.gitignore`.
- Si cambias la skill o los ejemplos, verifica que los dos ejemplos se ensamblen sin errores ni advertencias:

  ```bash
  cd examples/rca-ejemplo-memoria-net
  python ../../skills/dt-custom-rca-jromero/scripts/build_notebook.py rca_spec.json -o /tmp/notebook-es.json --strict
  cd ../rca-example-memory-net
  python ../../skills/dt-custom-rca-jromero/scripts/build_notebook.py rca_spec.json -o /tmp/notebook-en.json --strict
  ```
- Mantén el frontmatter de `SKILL.md` válido para agentskills.io: `name` igual al nombre de la carpeta, `description` de 1024 caracteres como máximo y `compatibility` de 500 caracteres como máximo.
- Los scripts solo usan la biblioteca estándar de Python 3.9+ y deben funcionar en Windows, macOS y Linux.
