# -*- coding: utf-8 -*-
"""Cotas de cada alcantarilla sobre el MDT del dron, para la app Proyecto_alcantarillas.

Uso: QGIS > Complementos > Consola de Python > Mostrar editor > abrir este
archivo > Ejecutar (triángulo verde). Revisa antes la sección CONFIGURACIÓN.

Antes de ejecutar, carga en el proyecto:
- el MDT del dron (terreno desnudo, no la superficie con cultivos),
- el eje (eje_via.gpkg),
- opcional: los cauces (cauces_E2.gpkg de Exutorios Viales, o los que digitalices
  sobre la ortofoto) y los canales y drenes como líneas.
Todo en el mismo sistema de coordenadas (EPSG:32717).

Para cada obra de puntos_via_evitamiento.csv el script:
1. ubica el cruce en el eje por su progresiva;
2. toma la dirección del cauce (o del canal) que cruza ahí; si no hay, la
   perpendicular al eje;
3. lee el MDT cada 2 m a lo largo de esa línea, 75 m aguas arriba y 75 m aguas
   abajo, y ajusta una recta: su pendiente es S_cauce y su lado bajo es aguas abajo;
4. lee la cota del terreno en el eje, la del receptor a 13 m del eje aguas abajo
   y, en los canales, la corona más baja de sus dos bordos;
5. calcula el esviaje: ángulo entre esa línea y la perpendicular al eje.

Salidas, en la carpeta de resultados:
- cotas_alcantarillas_dron.csv: todo lo medido, con alertas por obra.
- puntos_via_evitamiento_con_cotas.csv: el CSV de la app con las columnas
  topográficas llenas (rasante y subrasante solo si das el perfil).
- control_cotas_dron.gpkg: los puntos y líneas usados, para revisarlos sobre
  la ortofoto.
"""
import csv
import math
import os

import numpy as np

# ------------------------------------------------------------------ CONFIGURACIÓN
CARPETA = "D:/Modelado via/COTAS_DRON"                 # carpeta de resultados
PUNTOS_CSV = "D:/Modelado via/APP/puntos_via_evitamiento.csv"
PERFIL_CSV = ""      # opcional: perfil del diseño exportado de Civil 3D
#                      (columnas: progresiva, cota_rasante, cota_subrasante)

# Texto que aparece en el nombre o en la ruta de cada capa cargada
MDT_FUENTE = ("MDT", "DTM", "dron")
EJE_FUENTE = ("eje_via", "EJE VIA DE EVITAMIENTO")
CAUCES_FUENTE = ("cauces_E2", "cauces")      # opcional; () si no hay
CANALES_FUENTE = ("canales", "drenes")       # opcional; () si no hay

L_CAUCE = 75.0          # m aguas arriba y aguas abajo para la pendiente del cauce
PASO = 2.0              # m entre lecturas del MDT a lo largo del cauce
DIST_SALIDA = 13.0      # m del eje al punto de entrega (media plataforma + talud + disipador)
RADIO_FONDO = 2.0       # m: radio donde se busca el punto más bajo (fondo del cauce)
RADIO_SALIDA = 3.0      # m: radio donde se busca el fondo del receptor
BUSCAR_CAUCE = 30.0     # m: distancia máxima del cruce a un cauce o canal para usarlo
ANCHO_CANAL = 8.0       # m a cada lado del eje del canal para leer sus bordos
S_MINIMA = 0.0005       # pendiente bajo la cual se avisa (0.05 %)
# ---------------------------------------------------------------------------------

COLUMNAS_TOPO = ("cota_terreno", "cota_rasante", "cota_subrasante", "cota_fondo_receptor",
                 "S_cauce", "esviaje_grados", "cota_coronacion_canal")


# ============================== geometría ======================================
class Polilinea:
    def __init__(self, coords):
        self.xy = np.asarray(coords, dtype=float)[:, :2]
        d = np.hypot(*np.diff(self.xy, axis=0).T)
        self.acum = np.concatenate([[0.0], np.cumsum(d)])
        self.largo = float(self.acum[-1])

    def punto(self, s):
        s = min(max(s, 0.0), self.largo)
        i = int(np.searchsorted(self.acum, s, side="right")) - 1
        i = min(max(i, 0), len(self.xy) - 2)
        seg = self.acum[i + 1] - self.acum[i]
        t = 0.0 if seg == 0 else (s - self.acum[i]) / seg
        p = self.xy[i] + t * (self.xy[i + 1] - self.xy[i])
        v = self.xy[i + 1] - self.xy[i]
        v = v / (np.hypot(*v) or 1.0)
        return p, v

    def proyectar(self, p):
        """Distancia a lo largo de la línea del punto más cercano a p, y su separación."""
        mejor = (None, math.inf)
        for i in range(len(self.xy) - 1):
            a, b = self.xy[i], self.xy[i + 1]
            ab = b - a
            l2 = float(ab @ ab)
            t = 0.0 if l2 == 0 else min(max(float((p - a) @ ab) / l2, 0.0), 1.0)
            q = a + t * ab
            sep = float(np.hypot(*(p - q)))
            if sep < mejor[1]:
                mejor = (self.acum[i] + t * math.sqrt(l2), sep)
        return mejor


def leer_progresiva(texto):
    texto = str(texto).strip()
    if "+" in texto:
        km, m = texto.split("+")
        return float(km) * 1000 + float(m)
    return float(texto)


# ============================== MDT por ventanas ================================
class MDT:
    """Lee el MDT por ventanas, para no cargar en memoria un ráster de dron entero.

    `leer(xmin, ymin, xmax, ymax)` devuelve (matriz, x0, y0, dx, dy, nodata), con
    x0, y0 la esquina superior izquierda de la ventana.
    """

    def __init__(self, leer):
        self._leer = leer
        self._cache = None

    def ventana(self, x, y, radio):
        c = self._cache
        if c is not None:
            arr, x0, y0, dx, dy, nd = c
            if (x - radio >= x0 and x + radio <= x0 + arr.shape[1] * dx
                    and y + radio <= y0 and y - radio >= y0 - arr.shape[0] * dy):
                return c
        return None

    def cargar(self, xmin, ymin, xmax, ymax):
        self._cache = self._leer(xmin, ymin, xmax, ymax)

    def _celdas(self, x, y, radio):
        c = self.ventana(x, y, radio + 1.0)
        if c is None:
            self.cargar(x - radio - 50, y - radio - 50, x + radio + 50, y + radio + 50)
            c = self._cache
        arr, x0, y0, dx, dy, nd = c
        col = (x - x0) / dx
        fil = (y0 - y) / dy
        rc = max(int(math.ceil(radio / dx)), 0)
        rf = max(int(math.ceil(radio / dy)), 0)
        c0, c1 = int(math.floor(col)) - rc, int(math.floor(col)) + rc + 1
        f0, f1 = int(math.floor(fil)) - rf, int(math.floor(fil)) + rf + 1
        c0, f0 = max(c0, 0), max(f0, 0)
        c1, f1 = min(c1, arr.shape[1]), min(f1, arr.shape[0])
        if c0 >= c1 or f0 >= f1:
            return np.array([])
        bloque = arr[f0:f1, c0:c1].astype(float)
        cx = x0 + (np.arange(c0, c1) + 0.5) * dx
        cy = y0 - (np.arange(f0, f1) + 0.5) * dy
        gx, gy = np.meshgrid(cx, cy)
        dentro = np.hypot(gx - x, gy - y) <= max(radio, 0.71 * max(dx, dy))
        vals = bloque[dentro]
        if nd is not None:
            vals = vals[vals != nd]
        return vals[np.isfinite(vals)]

    def valor(self, x, y):
        v = self._celdas(x, y, 0.0)
        return float(v[0]) if v.size else None

    def minimo(self, x, y, radio):
        v = self._celdas(x, y, radio)
        return float(v.min()) if v.size else None

    def maximo(self, x, y, radio):
        v = self._celdas(x, y, radio)
        return float(v.max()) if v.size else None


# ============================== cálculo por obra ================================
def linea_mas_cercana(p, lineas, maximo):
    """La línea (cauce o canal) más cercana a p dentro de `maximo` metros."""
    mejor = None
    for nombre, pl in lineas:
        s, sep = pl.proyectar(p)
        if sep <= maximo and (mejor is None or sep < mejor[2]):
            mejor = (nombre, pl, sep, s)
    return mejor


def perfil_a_lo_largo(mdt, puntos_y_dist):
    xs, zs = [], []
    for d, (x, y) in puntos_y_dist:
        z = mdt.minimo(x, y, RADIO_FONDO)
        if z is not None:
            xs.append(d)
            zs.append(z)
    return np.array(xs), np.array(zs)


def medir_obra(obra, eje, mdt, cauces, canales, perfil):
    prog = leer_progresiva(obra["progresiva_km"])
    familia = obra["familia"].strip().upper()
    P, t = eje.punto(prog)
    n = np.array([-t[1], t[0]])                     # perpendicular al eje
    r = {"id": obra["id"], "progresiva": obra["progresiva_km"], "familia": familia,
         "x": round(float(P[0]), 3), "y": round(float(P[1]), 3), "alertas": []}
    alertas = r["alertas"]
    lineas_control = []

    # 1. dirección del cauce o del canal en el cruce
    fuente = canales if familia == "C" else cauces
    cerca = linea_mas_cercana(P, fuente, BUSCAR_CAUCE) if fuente else None
    if cerca is not None:
        nombre, pl, sep, s0 = cerca
        pasos = np.arange(-L_CAUCE, L_CAUCE + PASO / 2, PASO)
        pts = [(d, tuple(pl.punto(s0 + d)[0])) for d in pasos if 0 <= s0 + d <= pl.largo]
        r["direccion"] = ("canal" if familia == "C" else "cauce") + " '%s' a %.1f m del cruce" % (nombre, sep)
        a, b = pl.punto(max(s0 - 10, 0))[0], pl.punto(min(s0 + 10, pl.largo))[0]
        u = (b - a) / (np.hypot(*(b - a)) or 1.0)
        if sep > 10:
            alertas.append("el %s pasa a %.0f m de la progresiva: revisar la ubicación de la obra"
                           % ("canal" if familia == "C" else "cauce", sep))
    else:
        u = n.copy()
        pasos = np.arange(-L_CAUCE, L_CAUCE + PASO / 2, PASO)
        pts = [(d, tuple(P + d * u)) for d in pasos]
        r["direccion"] = "perpendicular al eje (sin %s a menos de %.0f m)" % (
            "canal" if familia == "C" else "cauce", BUSCAR_CAUCE)
        if familia == "C":
            alertas.append("falta la capa de canales: esviaje y corona no se pueden medir")
    lineas_control.append([p for _, p in pts])

    # 2. pendiente por ajuste lineal; el lado bajo es aguas abajo
    xs, zs = perfil_a_lo_largo(mdt, pts)
    if len(xs) >= 5:
        pend = float(np.polyfit(xs, zs, 1)[0])      # dz/dd en el sentido de u
        if pend > 0:                                  # sube en el sentido de u: aguas abajo es -u
            u, pend = -u, -pend
        S = -pend
        r["S_cauce"] = round(S, 5)
        if S < S_MINIMA:
            alertas.append("pendiente casi nula (%.3f %%): el agua no tiene hacia dónde correr" % (100 * S))
    else:
        r["S_cauce"] = None
        alertas.append("el MDT no cubre la línea del cauce")

    # 3. esviaje: ángulo entre la línea del conducto y la perpendicular al eje
    cosang = abs(float(u @ n))
    r["esviaje_grados"] = round(math.degrees(math.acos(min(cosang, 1.0))), 1)
    if r["esviaje_grados"] > 45:
        alertas.append("esviaje de %.0f°: revisar en planta" % r["esviaje_grados"])

    # 4. cotas en el eje y en la entrega
    r["cota_terreno"] = mdt.minimo(P[0], P[1], RADIO_FONDO)
    r["terreno_puntual"] = mdt.valor(P[0], P[1])
    Q = P + DIST_SALIDA * u
    r["x_salida"], r["y_salida"] = round(float(Q[0]), 3), round(float(Q[1]), 3)
    r["cota_fondo_receptor"] = mdt.minimo(Q[0], Q[1], RADIO_SALIDA)
    up = P - DIST_SALIDA * u
    r["cota_aguas_arriba"] = mdt.minimo(up[0], up[1], RADIO_SALIDA)
    if r["cota_terreno"] is None or r["cota_fondo_receptor"] is None:
        alertas.append("el cruce o la entrega quedan fuera del MDT")
    elif r["cota_fondo_receptor"] >= r["cota_terreno"] - 0.01:
        alertas.append("EMPOZA: el terreno a %.0f m aguas abajo (%.2f) no está más bajo que en el eje (%.2f)"
                       % (DIST_SALIDA, r["cota_fondo_receptor"], r["cota_terreno"]))

    # 5. canales: corona más baja de los dos bordos y fondo
    if familia == "C" and cerca is not None:
        m = np.array([-u[1], u[0]])                  # perpendicular al canal
        izq = [mdt.maximo(*(P + d * m), 0.0) for d in np.arange(0.5, ANCHO_CANAL, 0.25)]
        der = [mdt.maximo(*(P - d * m), 0.0) for d in np.arange(0.5, ANCHO_CANAL, 0.25)]
        izq, der = [v for v in izq if v is not None], [v for v in der if v is not None]
        if izq and der:
            r["corona_izquierda"], r["corona_derecha"] = round(max(izq), 3), round(max(der), 3)
            r["cota_coronacion_canal"] = min(r["corona_izquierda"], r["corona_derecha"])
            alertas.append("fondo del canal: el dron no ve bajo el agua; confirmar con nivel o estación total")
        lineas_control.append([tuple(P + ANCHO_CANAL * m), tuple(P - ANCHO_CANAL * m)])
    if familia == "C":
        r["S_canal_mdt"] = r.pop("S_cauce", None)    # en C la pendiente es la de la junta
        alertas.append("S del canal: usar la de la Junta de Usuarios (la del MDT es solo referencia)")

    # 6. rasante y subrasante del perfil de diseño
    if perfil:
        for col in ("cota_rasante", "cota_subrasante"):
            xs_p = [p for p, f in perfil if f.get(col) is not None]
            ys_p = [f[col] for p, f in perfil if f.get(col) is not None]
            if xs_p and xs_p[0] <= prog <= xs_p[-1]:
                r[col] = round(float(np.interp(prog, xs_p, ys_p)), 3)

    for k in ("cota_terreno", "terreno_puntual", "cota_fondo_receptor", "cota_aguas_arriba"):
        if r.get(k) is not None:
            r[k] = round(r[k], 3)
    if r.get("cota_terreno") is not None and r.get("cota_subrasante") is not None:
        alto = r["cota_subrasante"] - r["cota_terreno"]
        r["altura_subrasante_m"] = round(alto, 2)
        if alto < 0.9:
            alertas.append("solo %.2f m entre terreno y subrasante: no cabe ni el tubo mínimo de 0.90 m" % alto)
    return r, [tuple(P), tuple(Q)], lineas_control


def leer_perfil(ruta):
    if not ruta:
        return []
    with open(ruta, encoding="utf-8-sig") as f:
        muestra = f.read(2048)
        f.seek(0)
        sep = ";" if muestra.count(";") > muestra.count(",") else ","
        filas = list(csv.DictReader(f, delimiter=sep))
    cols = {c.lower().strip(): c for c in filas[0]}
    c_prog = next(c for k, c in cols.items() if "prog" in k)
    c_ras = next((c for k, c in cols.items() if "rasante" in k and "sub" not in k), None)
    c_sub = next((c for k, c in cols.items() if "subrasante" in k), None)
    perfil = []
    for f in filas:
        def num(c):
            v = (f.get(c) or "").strip().replace(",", ".") if c else ""
            return float(v) if v else None
        perfil.append((leer_progresiva(f[c_prog]), {"cota_rasante": num(c_ras), "cota_subrasante": num(c_sub)}))
    return sorted(perfil, key=lambda x: x[0])


def procesar(puntos_csv, eje, mdt, cauces, canales, perfil, carpeta):
    with open(puntos_csv, encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        campos = lector.fieldnames
        obras = list(lector)
    resultados, puntos, lineas = [], [], []
    for obra in obras:
        r, pts, lin = medir_obra(obra, eje, mdt, cauces, canales, perfil)
        resultados.append(r)
        puntos.append((obra["id"], pts))
        lineas.append((obra["id"], lin))
        for col in COLUMNAS_TOPO:
            if r.get(col) is not None:
                obra[col] = r[col]

    os.makedirs(carpeta, exist_ok=True)
    det = ["id", "progresiva", "familia", "direccion", "cota_terreno", "terreno_puntual",
           "cota_aguas_arriba", "cota_fondo_receptor", "S_cauce", "S_canal_mdt", "esviaje_grados",
           "cota_coronacion_canal", "corona_izquierda", "corona_derecha", "cota_rasante",
           "cota_subrasante", "altura_subrasante_m", "x", "y", "x_salida", "y_salida", "alertas"]
    with open(os.path.join(carpeta, "cotas_alcantarillas_dron.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(det)
        for r in resultados:
            w.writerow([" | ".join(r[c]) if c == "alertas" else ("" if r.get(c) is None else r[c]) for c in det])
    with open(os.path.join(carpeta, "puntos_via_evitamiento_con_cotas.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(obras)
    return resultados, puntos, lineas


# ============================== QGIS ===========================================
def _en_qgis():
    try:
        from qgis.utils import iface  # noqa: F401
        return iface is not None
    except Exception:
        return False


def main():
    from osgeo import gdal
    from qgis.core import (QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsProject,
                           QgsRasterLayer, QgsVectorFileWriter, QgsVectorLayer, QgsWkbTypes)
    from qgis.PyQt.QtCore import QVariant
    proyecto = QgsProject.instance()

    def capa(textos, tipo, geometria=None, obligatoria=True):
        for texto in textos:
            for c in proyecto.mapLayers().values():
                if texto.lower() not in c.source().lower() and texto.lower() not in c.name().lower():
                    continue
                if geometria == "raster" and (not isinstance(c, QgsRasterLayer) or c.bandCount() != 1):
                    continue                          # descarta la ortofoto (3 bandas)
                if geometria in (0, 1):
                    if not isinstance(c, QgsVectorLayer) or c.geometryType() != geometria or c.featureCount() == 0:
                        continue
                return c
        if obligatoria:
            raise Exception("No encontré la capa de %s ('%s'). Cárgala y vuelve a ejecutar." % (tipo, " o ".join(textos)))
        return None

    def polilineas(c):
        out = []
        for f in c.getFeatures():
            g = f.geometry()
            partes = g.asMultiPolyline() if g.isMultipart() else [g.asPolyline()]
            nombre = next((str(f[k]) for k in ("nombre", "name", "id", "fid") if k in f.fields().names()), str(f.id()))
            for parte in partes:
                if len(parte) >= 2:
                    out.append((nombre, Polilinea([(p.x(), p.y()) for p in parte])))
        return out

    mdt_capa = capa(MDT_FUENTE, "MDT del dron", "raster")
    eje_capa = capa(EJE_FUENTE, "eje (líneas)", 1)
    if mdt_capa.crs().authid() != eje_capa.crs().authid():
        raise Exception("El MDT (%s) y el eje (%s) están en sistemas distintos. Reproyecta uno de los dos."
                        % (mdt_capa.crs().authid(), eje_capa.crs().authid()))
    cauces_capa = capa(CAUCES_FUENTE, "cauces", 1, obligatoria=False) if CAUCES_FUENTE else None
    canales_capa = capa(CANALES_FUENTE, "canales", 1, obligatoria=False) if CANALES_FUENTE else None

    tramos = polilineas(eje_capa)
    if len(tramos) != 1:
        g = QgsGeometry.unaryUnion([f.geometry() for f in eje_capa.getFeatures()]).mergeLines()
        if g.isMultipart():
            raise Exception("El eje tiene tramos separados; únelos antes de seguir.")
        tramos = [("eje", Polilinea([(p.x(), p.y()) for p in g.asPolyline()]))]
    eje = tramos[0][1]
    print("Eje: %.2f m" % eje.largo)

    ds = gdal.Open(mdt_capa.source().split("|")[0])
    banda = ds.GetRasterBand(1)
    gt = ds.GetGeoTransform()
    nd = banda.GetNoDataValue()
    print("MDT: %s (celda %.3f m)" % (mdt_capa.source(), gt[1]))

    def leer(xmin, ymin, xmax, ymax):
        c0 = max(int((xmin - gt[0]) / gt[1]), 0)
        c1 = min(int((xmax - gt[0]) / gt[1]) + 1, ds.RasterXSize)
        f0 = max(int((gt[3] - ymax) / -gt[5]), 0)
        f1 = min(int((gt[3] - ymin) / -gt[5]) + 1, ds.RasterYSize)
        if c1 <= c0 or f1 <= f0:
            return (np.full((1, 1), np.nan), xmin, ymax, gt[1], -gt[5], nd)
        arr = banda.ReadAsArray(c0, f0, c1 - c0, f1 - f0)
        return (arr, gt[0] + c0 * gt[1], gt[3] + f0 * gt[5], gt[1], -gt[5], nd)

    cauces = polilineas(cauces_capa) if cauces_capa else []
    canales = polilineas(canales_capa) if canales_capa else []
    print("Cauces: %d líneas · Canales: %d líneas" % (len(cauces), len(canales)))
    perfil = leer_perfil(PERFIL_CSV)
    if perfil:
        print("Perfil: %d progresivas" % len(perfil))

    resultados, puntos, lineas = procesar(PUNTOS_CSV, eje, MDT(leer), cauces, canales, perfil, CARPETA)

    # capas de control
    crs = eje_capa.crs().authid()
    cp = QgsVectorLayer("Point?crs=%s" % crs, "control_puntos", "memory")
    cl = QgsVectorLayer("LineString?crs=%s" % crs, "control_lineas", "memory")
    for c in (cp, cl):
        c.dataProvider().addAttributes([QgsField("id", QVariant.String), QgsField("tipo", QVariant.String)])
        c.updateFields()
    for oid, (p_eje, p_sal) in puntos:
        for tipo, p in (("eje", p_eje), ("entrega", p_sal)):
            f = QgsFeature(cp.fields())
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(*p)))
            f.setAttributes([oid, tipo])
            cp.dataProvider().addFeature(f)
    for oid, lins in lineas:
        for i, lin in enumerate(lins):
            f = QgsFeature(cl.fields())
            f.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(*p) for p in lin]))
            f.setAttributes([oid, "cauce" if i == 0 else "seccion canal"])
            cl.dataProvider().addFeature(f)
    ruta = os.path.join(CARPETA, "control_cotas_dron.gpkg")
    for i, c in enumerate((cp, cl)):
        op = QgsVectorFileWriter.SaveVectorOptions()
        op.driverName = "GPKG"
        op.layerName = c.name()
        op.actionOnExistingFile = (QgsVectorFileWriter.CreateOrOverwriteFile if i == 0
                                   else QgsVectorFileWriter.CreateOrOverwriteLayer)
        QgsVectorFileWriter.writeAsVectorFormatV3(c, ruta, proyecto.transformContext(), op)
        proyecto.addMapLayer(QgsVectorLayer(ruta + "|layername=" + c.name(), c.name(), "ogr"))

    print("\n%-8s %-6s %9s %9s %8s %6s  alertas" % ("obra", "prog", "terreno", "receptor", "S %", "esv°"))
    for r in resultados:
        S = r.get("S_cauce") if r.get("S_cauce") is not None else r.get("S_canal_mdt")
        print("%-8s %-6s %9s %9s %8s %6s  %s" % (
            r["id"], r["progresiva"], r.get("cota_terreno"), r.get("cota_fondo_receptor"),
            "" if S is None else "%.2f" % (100 * S), r.get("esviaje_grados"), " | ".join(r["alertas"])))
    print("\nListo. Resultados en", CARPETA)


if _en_qgis():
    main()
