## 1. Resumen ejecutivo
El 15 de enero entre las 23:08 y las 23:21 (hora local), el servicio que autoriza las solicitudes de las aplicaciones respondió con error a una parte de las consultas. Fallaron **9 de unas 4.900 consultas (0,2 %)**, algunas después de esperar más de un minuto; el resto se atendió con normalidad.
- **Por qué pasó (causa raíz, ⚠️ Probable):** una de las dos copias del servicio se quedó casi sin memoria disponible y pasó casi todo su tiempo intentando liberarla, por lo que dejó de responder a tiempo.
- **Qué lo desencadenó:** la memoria de esa copia venía creciendo de forma constante durante horas hasta llegar al 91 % de su límite.
- **Qué hicimos para recuperarlo:** la plataforma reinició automáticamente esa copia a las 23:14 y a las 23:21 el servicio ya funcionaba con normalidad.
- **Cómo nos enteramos:** Dynatrace lo detectó automáticamente 6 minutos después de la primera falla.
- **Cómo está hoy:** resuelto, pero el patrón se repite: en las últimas 48 horas las copias del servicio se reiniciaron 18 veces con el mismo crecimiento de memoria.
- **Qué haremos para que no se repita:** corregir el consumo de memoria del servicio (29-ene), alertar antes de llegar al límite (22-ene) y registrar los eventos de la plataforma (29-ene).
