# AGENTS.md

Instrucciones para agentes de IA que trabajan con este repositorio.

## Usar la skill

Este repositorio contiene la skill **dt-custom-rca-jromero** (estándar [agentskills.io](https://agentskills.io)) en `skills/dt-custom-rca-jromero/`.

Cuando el usuario pida un **RCA, análisis de causa raíz, post-mortem o informe de incidente sobre Dynatrace**, o que "investigues el problema P-XXXX":

1. Lee `skills/dt-custom-rca-jromero/SKILL.md` completo y síguelo. Carga cada archivo de `references/` en el momento en que el SKILL.md lo indica.
2. Antes de investigar, ejecuta `python skills/dt-custom-rca-jromero/scripts/check_prereqs.py`. Si el resultado es NO LISTO, detente e informa qué falta.
3. Confirma con el usuario el contexto de dtctl (tenant) antes de consultar.
4. Entrega el resultado solo en el formato definido: un notebook de Dynatrace validado con `scripts/build_notebook.py`.

## Modificar este repositorio

- Responde y documenta en español. El README tiene un resumen en inglés.
- **No subas datos de clientes.** Todo ejemplo debe estar anonimizado: nombres, tenant, IDs de entidad y de problema, hosts, pods y fechas. Las carpetas `rca/` y `rca-*/` de la raíz están en `.gitignore`.
- Si cambias la skill o el ejemplo, verifica que el ejemplo se ensamble sin errores ni advertencias:

  ```bash
  cd examples/rca-ejemplo-memoria-net
  python ../../skills/dt-custom-rca-jromero/scripts/build_notebook.py rca_spec.json -o /tmp/notebook.json --strict
  ```
- Mantén el frontmatter de `SKILL.md` válido para agentskills.io: `name` igual al nombre de la carpeta, `description` de 1024 caracteres como máximo y `compatibility` de 500 caracteres como máximo.
- Los scripts solo usan la biblioteca estándar de Python 3.9+ y deben funcionar en Windows, macOS y Linux.
