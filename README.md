# Cotas y esviaje de alcantarillas (QGIS + MDT de dron)

Script para la consola de Python de QGIS que mide, para cada alcantarilla de `puntos_via_evitamiento.csv`, los datos topograficos que necesita [Proyecto_alcantarillas](https://github.com/Andy-rba30/Proyecto_alcantarillas):

- `esviaje_grados`: angulo entre la direccion del cauce/canal y la perpendicular al eje de la via.
- `S_cauce`: pendiente del cauce (recta ajustada sobre el MDT, 75 m aguas arriba y abajo).
- `cota_terreno`, `cota_fondo_receptor` (a 13 m del eje aguas abajo) y `cota_coronacion_canal`.

## Uso
1. En QGIS cargue el MDT del dron (terreno desnudo), el eje (`eje_via.gpkg`) y, opcional, los cauces (`cauces_E2.gpkg` de [Exutorios](https://github.com/Andy-rba30/Exutorios)) y canales. Todo en EPSG:32717.
2. Abra `cotas_esviaje_alcantarillas.py` en el editor de la consola de Python, revise la seccion CONFIGURACION y ejecute.

## Salidas
- `cotas_alcantarillas_dron.csv`: todo lo medido, con alertas por obra.
- `puntos_via_evitamiento_con_cotas.csv`: el CSV de la app con las columnas topograficas llenas.
- `control_cotas_dron.gpkg`: puntos y lineas usados, para revisar sobre la ortofoto.

Requiere `numpy` (incluido en QGIS).
