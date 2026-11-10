# Cotas y esviaje de alcantarillas (QGIS + MDT de dron)

Script para la consola de Python de QGIS que mide, para cada alcantarilla de `puntos_via_evitamiento.csv`, los datos topograficos que necesita [Proyecto_alcantarillas](https://github.com/Andy-rba30/Proyecto_alcantarillas):

- `esviaje_grados`: angulo entre la direccion del cauce/canal y la perpendicular al eje de la via.
- `S_cauce`: pendiente del cauce (recta ajustada sobre el MDT, 75 m aguas arriba y abajo).
- `cota_terreno`, `cota_fondo_receptor` (a 13 m del eje aguas abajo) y `cota_coronacion_canal`.

## Uso
1. En QGIS cargue el MDT del dron (terreno desnudo), el eje (`eje_via.gpkg`) y, opcional, los cauces (`cauces_E2.gpkg` de [Exutorios](https://github.com/Andy-rba30/Exutorios)) y canales. Todo en EPSG:32717.
2. Abra `cotas_esviaje_alcantarillas.py` en el editor de la consola de Python, revise la seccion CONFIGURACION y ejecute.
   - `progresiva_km` se lee como en la app: `0+380` o kilometros decimales (`0.380`). Si el eje no empieza en 0+000 o esta digitalizado al reves, ajuste `PROG_INICIO_EJE` y `EJE_INVERTIDO`.
   - El perfil de Civil 3D trae progresivas en metros (`PERFIL_PROGRESIVA_EN = "m"`); cambie a `"km"` si las exporta en kilometros.
   - Las capas de cauces y canales deben estar en el mismo CRS que el eje; si no, el script se detiene y lo dice.

## Salidas
- `cotas_alcantarillas_dron.csv`: todo lo medido, con alertas por obra.
- `puntos_via_evitamiento_con_cotas.csv`: el CSV de la app con las columnas topograficas llenas.
- `control_cotas_dron.gpkg`: puntos y lineas usados, para revisar sobre la ortofoto.

`puntos_via_evitamiento_con_cotas.csv` conserva el separador y las columnas del CSV original: la app rechaza columnas nuevas, asi que un valor sin columna (p. ej. `cota_coronacion_canal`) queda solo en `cotas_alcantarillas_dron.csv`, y el script lo avisa.

Requiere `numpy` (incluido en QGIS). Probado con QGIS 3.x; las enumeraciones y tipos de campo tienen alternativa para QGIS 4.

## Estado (nov. 2026)
Funcional y verificado sin QGIS con un MDT sintetico (`procesar`, `medir_obra`, `leer_perfil`, cache del MDT): cauce, perpendicular, canal, canal desplazado, CSV con `;` y coma decimal, progresivas en km, fuera del eje. El CSV de salida lo acepta el modulo M0 de la app.

Pendiente de comprobar en QGIS real (no se pudo en esta sesion): apertura del MDT con GDAL, escritura de `control_cotas_dron.gpkg` y la compatibilidad de enumeraciones en QGIS 4.

