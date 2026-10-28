## 8. Lecciones aprendidas
- **Qué funcionó bien:** Dynatrace detectó el aumento de fallas y la GC larga en pocos minutos; Kubernetes reinició la copia afectada y la otra copia absorbió la carga.
- **Qué se puede mejorar:** alertar sobre la tendencia de memoria antes de que afecte a los clientes; ingerir eventos de Kubernetes para conocer el motivo de cada reinicio.
- **Dónde tuvimos suerte:** la otra copia estaba al 71 % y subiendo; si ambas hubieran llegado al tope a la vez, la falla habría sido total.
