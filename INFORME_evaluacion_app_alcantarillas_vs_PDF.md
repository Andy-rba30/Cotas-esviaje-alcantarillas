# ¿Produce la app un diseño de alcantarillas defendible en una tesis? Evaluación frente al PDF guía y a la norma

**Fecha:** 10 de noviembre de 2026
**Objeto evaluado:** app `Proyecto_alcantarillas` (repositorio `Andy-rba30/Proyecto_alcantarillas`, único commit `c2262a2` del 2026-09-22) y PDF "2.7. Estudio de Estructuras de Obras de Arte y Drenaje" (repositorio `Andy-rba30/VARIOS`).
**Contexto:** tesis de ingeniería civil, diseño de una vía de evitamiento en La Unión, Bajo Piura (según la propia documentación de la app). Las alcantarillas son obras complementarias que deben quedar sustentadas.
**Método:** lectura página a página de la memoria descriptiva del PDF (pp. 1–49), OCR de las 388 páginas para ubicar las memorias de cálculo de los anexos, auditoría del código de la app módulo por módulo (M0 a M11 y MD, 57 000 líneas) con cita archivo:línea, y cotejo con el Manual de Hidrología, Hidráulica y Drenaje del MTC, HDS-5, AASHTO LRFD, E.030, E.050 y E.060 (todos en `normas/` de la app, salvo donde se indica).

---

## 0. Veredicto en una página

**La app NO produce hoy un diseño de alcantarillas defendible como diseño completo. Produce una verificación hidráulica de alcantarillas circulares (y, bloqueada, de un marco), muy bien documentada, con la hidrología y todo el diseño de cabezales y aleros fuera del programa.** En su estado actual, además, **no dimensiona ningún punto**: la corrida de referencia dimensiona 0 de 4 obras porque varios criterios obligatorios están vacíos (`docs/indice_formulas.md:26-33`).

Lo que sí es defendible (y es mucho):

- El motor hidráulico (Manning, tirante crítico, control de entrada y salida de HDS-5, perfil de lámina por paso directo) está **bien transcrito**: coeficientes de las cartas, Ku = 1.811, Kf = 19.63, h_o = max(TW, (dc+D)/2). Verificado contra HDS-5 3.ª ed. Sin errores de unidades.
- El periodo de retorno por riesgo admisible (Tabla 02 del manual MTC) está bien calculado: 71 años para quebrada importante, 35 para quebrada menor y descarga de cunetas.
- Las verificaciones V1 (borde libre 25 %), V2 (V ≥ 0.25 m/s), V3 (V máx. por material), V4 (carga a la entrada vs subrasante), V4b (HW/D ≤ 1.5) y V7 (flotación LRFD) tienen fórmula, umbral y cita.
- La memoria de cálculo imprime fórmula, sustitución numérica, umbral y cita por paso. Eso es más de lo que trae el PDF guía.

Lo que falta, en orden de gravedad para un jurado:

1. **Hidrología:** la app no calcula el caudal. `Q_m3s` entra ya calculado en el CSV. La herramienta que lo calcularía (`legacy/Tc.py`) no corre. No hay IDF, Tc, coeficiente C ni método racional en el programa. Sin anexo hidrológico, el Q de cada obra no tiene sustento.
2. **Cabezales y aleros:** el módulo M9 (3 800 líneas) es una biblioteca de fórmulas de muro de contención, pero no dimensiona ningún cabezal, no ensambla la estabilidad, la capacidad portante y la flexión-corte están sin implementar (`NotImplementedError`), y **los aleros no existen en el código**. El PDF guía tampoco ayuda aquí: dice que los cabezales se diseñaron por LRFD, pero sus anexos no contienen ni un cálculo de cabezal (ver §1.3).
3. **Estructural del conducto:** la Fase 8 no verifica nada estructural del tubo: clase/calibre bloqueados, HL-93 nunca entra, sin relleno máximo.
4. **Familia C (cruce de canales):** no se dimensiona; cuatro criterios del marco vacíos y datos de ANA/Junta pendientes.
5. **Criterios vacíos que detienen todo**: `TW_receptor`, `acceso_mantenimiento_v2b`, `regimen_v2b`, `origen_cota_fondo_entrada` (ya tiene valor "cota_terreno"), `predimensionamiento_cabezal`, `angulo_aletas`, los cuatro ángulos de Coulomb, `gamma_EQ`, y otros (lista en §6).

Y un hallazgo sobre el propio pedido: el mensaje llegó con los corchetes de la plantilla sin rellenar (ubicación, ruta de la app, nombre del PDF). Se tomó la app `Proyecto_alcantarillas`, el PDF de VARIOS y la ubicación que la app declara. Si la tesis es de otro lugar, la parte sísmica de este informe cambia.

---

## 1. El PDF guía: qué es y qué metodología trae

**Qué es.** No es un manual ni una norma: es el capítulo 2.07 "Diseño de Estructuras de Obras de Arte y Drenaje" del *Estudio Definitivo para la Rehabilitación y Mejoramiento del Camino Vecinal Pacobamba – Huironay – Ccerabamba – Abra Cusqueña* (Apurímac, 28,83 km, Provías Descentralizado, Consorcio Vía Ingenieros, 2018). Son 388 páginas escaneadas sin capa de texto. Las páginas se citan por el número de página del archivo PDF (en la memoria descriptiva el sello del escaneo es ese número más uno; en los anexos el sello no coincide).

Es un **ejemplo de expediente técnico**, útil como referencia de "cómo se presenta" y de qué fórmulas usa un consultor, pero no como fuente normativa. En la tesis debe citarse como "el expediente X adopta…", y la norma aparte.

### 1.1 Estructura y contenido (con páginas)

| Sección del PDF | Páginas | Contenido |
|---|---|---|
| Índice y lista de tablas | 1–2 | Índice; nueve tablas. |
| 1. Aspectos generales | 3–5 | Objetivo, localización (Apurímac / Andahuaylas / Pacobamba), ruta AP-525, 28,83 km. |
| 2. Inventario y evaluación de campo | 5–17 | Tabla 1: 114 estructuras existentes (alcantarillas de concreto, TMC, PVC, piedra, madera; badenes; pontones; canales) con progresiva, longitud, diámetro y observación. Evaluación con fotos. |
| 3.1 Alcantarillas: geometría y materiales | 18–19 | Tipos de entrada (caja receptora, alero inclinado, alero recto), de salida (alero recto, alero inclinado, muro), protecciones (emboquillado, adecuación de salida). Todo cualitativo: **no hay fórmula hidráulica alguna**. |
| 3.1.2 Diseño estructural TMC | 19–22 | Método del *CSPI Handbook of Steel Drainage & Highway Construction Products* (pp. 213–218 del handbook): recubrimiento mínimo 0,30 m; compactación 90 % AASHTO T-99; Pv = (DL+LL) con K = 1 porque H < S; compresión de anillo C = Pv·S/2; fb según D/r (fb = fy = 230 MPa si D/r < 294; 279,6 − 574,3·10⁻⁶ (D/r)² si 294 ≤ D/r ≤ 500; 34·10⁶/(D/r)² si > 500); fc = fb/2; área requerida A = C/fc; rigidez FF = D²/(EI) ≤ 0,245 mm/N (corrugación 68×13). Tabla 6.2 del handbook. |
| "Diseño de cabezal de concreto" | 23–27 | Zona sísmica y aceleración 0,30 (mapa de isoaceleraciones UNI); estados límite AASHTO LRFD; tabla de combinaciones de carga; sobrecarga viva como altura equivalente heq (AASHTO 3.11.6.4: 1,7 m si H < 1,5 m; 1,2 m a 3 m; 0,76 m a 6 m; 0,61 m si > 9 m); LSx = Ka·heq·γs·H y LSy = heq·γs·b; Ka de Coulomb; EH = ½·Ka·H²·γs; pasivo despreciado salvo llave de corte; sismo por Mononobe-Okabe (K_AE, P_AE = ½·K_AE·γ·H²·(1−kv), θ = arctan(kh/(1−kv))); fuerza inercial de la pantalla; estabilidad: e < B/4 (servicio) y e < B/3 o 2B/5 en evento extremo (AASHTO 11.6.3.3, 11.6.5); deslizamiento μ = tan φf, φt = 0,80 / 1,00, Ft = μ·φt·Vt > Hu (AASHTO 10.6.3.3); presión en la base q = Vu/(B−2e). |
| 3.1.3 TMC 36" y 48" | 27–33 | Instalación (base, relleno en capas de 20 cm al 90 % T-99). Tabla 2: TMC de 0,60 a 1,80 m, cobertura mín. 0,30 m, máx. 17,8–14,8 m, pendiente longitudinal 2 %, Qmáx al 93,8 % del diámetro: 0,51 / 1,50 / 2,94 / 5,80 / 9,50 m³/s. Tabla 3: 130 TMC 36" (longitud, esviaje, sentido, entrada/salida, cotas). Tabla 4: 5 TMC 48". |
| 3.1.4 Marco de concreto | 33–34 | Criterio de uso (poca cobertura, canales de riego, caudal considerable); pendiente mínima 1 %; Tabla 5 con 8 marcos (0,60×0,60 a 3,50×2,50). |
| 3.1.5 Pases de agua | 34–35 | Tabla 6: 32 pases de riego Ø 0,30 m. (Página con anotaciones manuscritas de un revisor.) |
| 3.2 Muros de contención | 36–43 | Tablas 7–9 (ciclópeo, gaviones/Terramesh); repite íntegra la metodología LRFD de cabezales (pp. 37–42); predimensionamiento de muro de gravedad y en voladizo (p. 42). |
| 3.3 Drenaje longitudinal | 43 | Cunetas 0,75×0,30 m. Sin cálculo. |
| Conclusiones | 44 | TMC 36"/48" espesor 2,0 mm; **"todos los cabezales de concreto simple… método LRFD 2010"**; cajones por LRFD con SAP2000 y resortes de balasto, Fe = 1 + 0,20 (Hr/Bc); cajones sin sismo. |
| Anexo 1 panel fotográfico | 45–48 | Fotos. |
| Anexo 2 memoria TMC | 49–66 | TMC 36" (pp. 50–55), 48" (56–61), 60" (62–66): el mismo procedimiento CSPI con números: DL = γH = 15·0,30 = 4,5 kPa; LL = 86 kPa (H-20, Tabla 6.8, cobertura 0,30 m); Pv = 90,5 kPa; C = Pv·S/2 (40,7 kN/m para Ø 0,90; 54,3 para Ø 1,20); D/r = 207 / 276 < 294 ⇒ fb = 230 MPa, fc = 115 MPa; A = 0,354 / 0,472 mm²/mm ⇒ espesor 1,6 mm pasa, se adopta 2,0 mm; FF = 0,109 / 0,194 < 0,245 OK. |
| Anexo 3 memoria cajones | 67–109 | Cajones 0,60×0,60, 2,00×3,00 y 2,50×3,50 (por km): balasto Ko = 3 500 t/m³ con resortes por nudo, Ka = 0,271, presión hidrostática, Fe = 1 + 0,20 Hr/Bc, momentos y As por elemento. **Solo estructural; ningún cálculo hidráulico.** |
| Anexo 4 memoria muros de gravedad | 110–230 | Diez grupos de muros de contención por km (coinciden con la Tabla 7, p. 36): Coulomb con cuña activa y pasiva (Ka = 0,388, Kp = 2,578), Mononobe-Okabe (K_AE = 0,498, ΔP_AE), momento volcante sísmico M = P_A·H/3 + ΔP_AE·0,6H, sobrecarga heq (1,2 / 0,9 / 0,6 m según altura, Tabla 3.11.6.4-1), tablas DC y EV con brazos, fuerza inercial EQ = kh·W, verificaciones de excentricidad, deslizamiento y presiones. Es la **plantilla práctica** de lo que la tesis necesita para el cabezal (ver §4). |
| Anexo 5 gaviones / Terramesh | 231–388 | Salidas del programa MacStARS W (Maccaferri). No aplica a alcantarillas. |

### 1.2 Lo que el PDF NO contiene

- **Ninguna hidrología**: ni área de cuenca, ni tiempo de concentración, ni IDF, ni periodo de retorno, ni caudal de diseño. Remite al capítulo de Hidrología y Drenaje del mismo expediente, que no está en VARIOS.
- **Ninguna hidráulica de alcantarillas**: no hay Manning, control de entrada/salida, HW/D ni velocidades. Lo único es la columna "Qmáx al 93,8 % del diámetro" de la Tabla 2, un dato de fabricante que no sustituye el cálculo.
- **Ningún cálculo de cabezal ni de aleros.** Las pp. 23–27 exponen el método (cargas y criterios de estabilidad) pero no lo aplican a ningún cabezal; los anexos 2 a 4 son tubería, cajones y muros de contención. La conclusión 3 de la p. 44 ("todos los cabezales… LRFD 2010") no tiene respaldo en el documento. Por OCR, la palabra "cabezal" aparece únicamente en los encabezados de la memoria TMC ("Para cabezales de concreto se utiliza el LRFD") y en el inventario.
- **Ninguna geometría de aleros** (ángulo, longitud, altura) ni criterio de altura del muro de cabecera frente a HW.

### 1.3 Errores y cosas fuera de lugar en el propio PDF (para no copiarlos)

- Dice "Nuestro proyecto se ubica en el departamento de Cusco – Pocobamba" (pp. 23 y 37) cuando la localización oficial (p. 4) es **Apurímac**, Andahuaylas, Pacobamba. Habla de "Factor sísmico de Zona A" y 0,30 g de un mapa de isoaceleraciones de la UNI, que no es la zonificación de la E.030: en el Anexo 1 de la E.030 vigente, Pacobamba está en **Zona 2, Z = 0,25**. Para la tesis esto importa porque el Bajo Piura (provincias de Piura y Sechura) está en **Zona 4, Z = 0,45**, y la app declara además PGA = 0,50 g por licuefacción: la componente sísmica de los cabezales pesa mucho más que en el ejemplo.
- El bloque de metodología de cabezales (pp. 23–27) está **copiado y pegado** como metodología de muros (pp. 37–42), letra por letra, con la numeración de incisos saltando de a)–d) a e)–h).
- La memoria TMC (pp. 50–66) tiene el pie de página de **otro proyecto** ("Mejoramiento y rehabilitación de camino vecinal Huanca Huanca – Ccarapa – Santa Rosa de Patahuasi"): es una hoja reutilizada.
- Mezcla de unidades: CSPI en MPa/mm/kN; sobrecargas en "kg/m² o ton/m²"; muros en kg y ton.
- El índice marca "¡Error! Marcador no definido" en 1.4 (p. 1) y la numeración de la lista de tablas es inconsistente (p. 2).
- Tabla 4 clasifica dos alcantarillas de 0,90 m como "TMC 48"" (ítems 4 y 5, p. 33).
- La carga viva de la memoria TMC es **H-20 / HS-20** (Tabla 6.8 del CSPI), no HL-93 de AASHTO LRFD que es la que la app y el Manual de Puentes exigen.
- Los **esviajes** de las tablas 3 a 6 se miden como ángulo entre conducto y eje de la vía (90° = cruce perpendicular), al revés de la convención de HDS-5, del manual MTC y de la app (0° = perpendicular). Si se copian valores del PDF a la app: esviaje_app = 90° − esviaje_PDF.

---

## 2. La app: qué calcula, con qué fórmulas, qué pide y qué supuestos tiene

### 2.1 Alcance declarado y flujo

Calculador de alcantarillas de cruce de carretera con memoria auditable, para la vía de evitamiento de La Unión (Piura), **a nivel de perfil**; el expediente queda "preparado, no escrito" (`docs/hoja_de_ruta_correcciones_v12.md` §15). Flujo: M0 carga del CSV → M1 clasificación y TR → M2 material y catálogo de diámetros → M3 Manning → M4 control de entrada/salida (HDS-5) y perfil de lámina → M5 verificaciones V1–V9 (+VC1) → M6 protección de salida → M7 geometría → M8 estructural → M9 cabezal → M10 espaciamiento → M11 memoria. MD orquesta por punto, iterando material y diámetro.

El propio código declara que **no hace hidrología** (`src/modulos/M5_verificaciones.py:2309-2311`), **no dimensiona cabezales** (`docs/ruta_familia_c.md` §13: "el programa no dimensiona cabezales de ninguna familia") y no diseña flexión ni corte (`src/modulos/M9_cabezal.py:3526`, `NotImplementedError`).

### 2.2 Entradas (CSV de 19 columnas, `src/modulos/M0_carga.py:65-80`)

| Columna | Unidad | Obligatoria | Quién la fija según la app |
|---|---|---|---|
| id, progresiva_km (`0+380` o km), familia (A/B/C) | – | sí | proyectista / trazo |
| Q_m3s | m³/s | A y B; vacío en C | "el estudio hidrológico (Fase 1-bis)"; en C, ANA/Junta |
| area_ha | ha | A y B; vacío en C | delimitación de cuenca; "solo clasificador" |
| S_cauce | m/m | A y B; vacío en C | perfil del cauce |
| cota_terreno, cota_rasante, cota_subrasante | msnm | sí | topografía / perfil |
| cbr_subrasante | % | sí | calicatas |
| esviaje_grados | ° | sí | QGIS (este script) |
| ancho_plataforma | m | sí | sección típica |
| cota_fondo_receptor | msnm | sí | nivelación del dren |
| Q_receptor_m3s, cota_TW | – | vacío admitido | ANA / Junta (Tablero 3.1) |
| sucs_fundacion | texto | sí, **nadie la lee** | calicata |
| NF_profundidad_m, cota_fondo_entrada, cota_coronacion_canal | m / msnm | vacío admitido | geotecnia / levantamiento |

Datos que no van en el CSV pero son obligatorios: `luz_m` (decide alcantarilla o puente, umbral 6,0 m) y `categoria_tr` por punto (`src/modulos/M1_clasificacion.py:25-32, 259-285`).

### 2.3 Fórmulas y criterios implementados (resumen; detalle en §3)

- **TR** = 1/(1−(1−R)^(1/n)) con R y n de la Tabla 02 del manual MTC (`M1_clasificacion.py:292-359`): 71 años (R 0,30, n 25) y 35 años (R 0,35, n 15).
- **Manning** Q = (1/n)·A·R^(2/3)·S^(1/2), resuelto por Brent (`M3_hidraulica.py:352-385`), con doble n: n máx para capacidad, n mín para velocidad de erosión.
- **Tirante crítico** A³/T = Q²/g (`M4_control.py:645-684`).
- **Control de entrada** HDS-5 Formas 1 y 2 con Ku = 1,811, límites q* 3,5 / 4,0, interpolación lineal en la transición, Ks = −0,5 / +0,7 (`M4_control.py:691-897`). Cartas: concreto *square edge w/ headwall* (K 0,0098, M 2,0, c 0,0398, Y 0,67), TMC *headwall* y *mitered*, cajón cartas 8 a 13. Verificado contra la Tabla A.1 de HDS-5.
- **Control de salida** HW = H + h_o − S·L, H = (1 + ke + 19,63·n²·L/R^(4/3))·V²/2g con sección llena, h_o = max(TW, (dc+D)/2), ke = 0,5 (`M4_control.py:1166-1326`).
- **Perfil de lámina** por paso directo, 2 000 pasos, clasifica M1/M2/S1 y entrega HW por remanso (`M4_control.py:1692-1936`).
- **TW**: cuatro vías en precedencia: declarado; `cota_TW`; Manning en el receptor con `Q_receptor_m3s`; y, sin dato, el mayor de salida libre y receptor lleno (`M3_hidraulica.py:577-727`).
- **Verificaciones** (`M5_verificaciones.py`): V1 y/D ≤ 0,75; V2 V ≥ 0,25 m/s; V2b S_conducto ≥ S_cauce; V3 V ≤ 6,0 (concreto) / 4,572 m/s (TMC, HDPE, de WSDOT); V4 cota_entrada + HW ≤ subrasante − resguardo(CBR) (0,60 a 1,20 m, Manual de Suelos 4.5.4 por analogía); V4b HW/D ≤ 1,5; V5 remanso (siempre pendiente); V6 N = 1; V7 flotación LRFD; V8 evento extremo (siempre pendiente); V9 D ≤ tope de catálogo; VC1 corona del canal − 0,50 m.
- **Geometría** (`M7_geometria.py`): L = (ancho_plataforma + 2·talud·H_terraplén)/cos θ, talud 2H:1V; cota_salida = cota_entrada − S·L; rasante mínima por recubrimiento (AASHTO 12.6.6.3 y EG-2013 508.07) y por HW + resguardo.
- **Protección** (`M6_proteccion.py:119-121`): d50 = V²/(3,1·g) (Laushey, manual MTC ec. 49), espesor 1,75·d50, longitud 5,0 m (adoptados).
- **Espaciamiento** (`M10_espaciamiento.py:78-107`): min(200 m, L_hidráulico externo).
- **Cabezal** (`M9_cabezal.py`): cadena sísmica (PGA 0,50 → kh 0,50, kv 0), Ka Rankine, Coulomb, Mononobe-Okabe, heq, empujes, subpresión, peso, excentricidad, presión de contacto, FS de E.050, recubrimientos y cuantías mínimas E.060. **Nada ensamblado, nada por punto, aleros inexistentes.**

### 2.4 Supuestos fijos y vacíos (los que deciden la obra)

Con valor adoptado: umbral 100 ha para quebrada importante; máximos de riesgo admisible de la Tabla 02 ("el extremo menos conservador", `M1_clasificacion.py:494-547`); n HDPE por analogía con concreto; V máx TMC/HDPE 4,572 m/s de un manual de WSDOT que **no está en `normas/`**; diámetros 0,90 + 0,15 m hasta 2,70 / 2,10 / 1,50 m según material (topes sin respaldo documental); ke = 0,5; sección llena para H; talud 2H:1V; pavimento flexible; cota de fondo de entrada = cota de terreno; γ relleno 17 kN/m³; γ concreto 23,56; sección del receptor adoptada b 2,0 m, z 1,5, S 0,0008, n 0,030, h 1,80 m; PGA 0,50 g; F_pga 1,0; kh sin reducción.

Vacíos que detienen (`None` ⇒ `CriterioPendienteError`): `TW_receptor`, `acceso_mantenimiento_v2b`, `regimen_v2b`, `hw_entrada_fuera_de_rango`, `TR_evento_extremo`, `remanso_derecho_via`, `n_manning_cajon`, `embocadura_cajon`, `ke_entrada_cajon`, `n_celdas_cajon`, `secciones_cajon_normalizadas`, `cobertura_minima_cajon`, `espesor_pared_conducto` (solo concreto), `clases_producto_por_relleno`, `predimensionamiento_cabezal`, `angulo_aletas`, `phi_relleno_trasdos`, `pendiente_relleno_trasdos_i`, `inclinacion_muro_beta`, `friccion_muro_suelo_delta`, `punto_aplicacion_incremento_sismico`, `gamma_EQ`, `N_cq_N_gammaq_meyerhof`, `metodo_estabilidad_global`, `categoria_refuerzo_aashto`, `exposicion_quimica_ems`, `c_phi_fundacion`, `capacidad_portante_adm`, `homogeneidad_serie_fen`.

---

## 3. Comparación por etapa: PDF, app y norma

### 3.1 Hidrología

| Aspecto | PDF guía | App | Norma (manual MTC) | Qué falta |
|---|---|---|---|---|
| Área de cuenca | No aparece | Columna `area_ha`, usada solo para clasificar ≥ 100 ha | §3.5 | Delimitación por cuenca con plano; el umbral de 100 ha es adopción propia con fuente "PENDIENTE" y calibrado sobre el fixture de tests (`criterios_adoptados.py:1925-1932`). |
| Tiempo de concentración | No | No (solo en `legacy/Tc.py`, que no corre) | §3.9, Tabla 05 (Kirpich, Témez…) | Calcular por cuenca; Kirpich está fuera de su rango de pendiente (3–10 %) en llanura, como advierte el propio Tc.py. |
| Curvas IDF | No | No | §3.8.1 (Dick-Peschke, Tabla 04) | IDF de la estación SENAMHI representativa, con serie, años faltantes y ajuste de distribución (§3.7). |
| Periodo de retorno | No | T = 1/(1−(1−R)^(1/n)); 71 / 35 años | §3.6, Tabla 02 | Correcto. Declarar quién fija R y n (el Propietario) o justificar los máximos recomendados. Decidir el tratamiento de la población mixta por FEN (1983, 1998, 2017): `homogeneidad_serie_fen` está vacío y nadie lo lee. |
| Método | No | No | §3.12.2 racional Q = 0,278·C·I·A (A < 10 km²), Tabla 08 de C | Memoria hidrológica completa como anexo o integrada. |
| Caudal de diseño | No (solo Qmáx de fabricante) | Entra por CSV; se verifica solo Q > 0 y finito | §3.13 | Verificación de plausibilidad (caudal específico Q/A, cuencas vecinas). Hoy A-01 850 ha → 1,167 m³/s y B-01 18 ha → 0,095 m³/s pasan sin aviso. |

**Conclusión:** el eslabón más débil. Ni el PDF ni la app resuelven la hidrología; en la tesis tiene que estar como capítulo propio, con los TR que la app ya calcula.

### 3.2 Hidráulica

| Aspecto | PDF guía | App | Norma | Qué falta |
|---|---|---|---|---|
| Manning | No | Sí, doble n (Tabla 09) | MTC 4.1.1.3.6 ec. 47 | n del cajón vacío (`n_manning_cajon`); n HDPE por analogía, confirmar con ficha del fabricante. |
| Control de entrada y salida | No | HDS-5 completo, cartas verificadas | MTC remite a FHWA (nota al pie p. 74) | Validar contra un ejemplo publicado de HDS-5 o una corrida HY-8 por punto (nunca hecho, `auditoria_y_ruta_despliegue_v9.md` Etapa E). Transcribir filas de la Tabla A.1 y C.2 para aleros 30°–75° si se adoptan aleros (hoy solo "square edge w/ headwall"). |
| Tirante | No | Normal (Brent) y crítico | – | Correcto. |
| Velocidades | No | 0,25 ≤ V; V ≤ 6,0 concreto, 4,572 TMC/HDPE | MTC Tabla 10 y párrafo tras ella | El 4,572 viene de WSDOT (no está en `normas/`). Para TMC la ficha reconoce que la fuente no fija techo. |
| HW/D | No | HW/D ≤ 1,5 (adoptado, sensibilidad 1,2–1,5); además V4 con resguardo por CBR | HDS-5 2.2.5 | V4 (resguardo de napa aplicado a avenida) es una analogía [N→] que puede gobernar el diseño en terraplenes bajos; justificarla o acotarla. |
| Borde libre | No | y/D ≤ 0,75 | MTC 4.1.1.3.7 b) p. 79 | Correcto, pero con TW alto el régimen es LLENO y V1 falla siempre, lo que fuerza D ≥ 1,95 m: la lectura "sección llena por ahogamiento del receptor = no cumple" decide la obra y no está explicitada. |
| Pendiente | 2 % TMC, 1 % marco (Tabla 2 y 3.1.4) | **No existe** verificación de pendiente mínima ni máxima; S = 0 se rechaza como dato inválido | MTC 4.1.1.3.3 | Declarar criterio de pendiente mín/máx; admitir S = 0 si se defiende barril plano en llanura. |
| Tailwater | No | Cuatro vías; sin dato, receptor lleno con sección adoptada | HDS-5 3.3.3 | Levantamiento del dren receptor y su caudal (ANA/Junta): hoy el TW adoptado decide el diámetro. |
| Sedimentación | No | V2b S_conducto ≥ S_cauce | HDS-5 5.3.3 | Segundo indicador (n del cauce) no evaluado. |

**Conclusión:** la mejor etapa de la app, superior al PDF. Le falta validación externa y cerrar los criterios vacíos que la detienen.

### 3.3 Estructural y geométrica del conducto

| Aspecto | PDF guía | App | Norma | Qué falta |
|---|---|---|---|---|
| Tipo y material | TMC 36"/48"/60" (CSPI), marcos de concreto, pases Ø 0,30 | Concreto, TMC, HDPE para A y B; marco solo en C; elige el primero que cumple | MTC 4.1.1.3.4 b): no hay regla general | Matriz de durabilidad (sulfatos, cloruros, pH, resistividad; E.060 Tabla 4.4) prevista en la hoja de ruta pero **no implementada**: en el Bajo Piura, con suelos salinos y NF a 1,4 m, es decisiva. Topes de diámetro 2,70 / 2,10 / 1,50 sin respaldo. |
| Diámetro mínimo | 36" (0,90) | 0,90 m | MTC 4.1.1.3.4 a) p. 72 | Correcto. |
| Longitud | Tablas 3–6 (dato) | L = (ancho + 2·talud·H)/cos θ | DG-2018 | Usa altura al eje para ambos taludes; sin pasos de memoria con fórmula sustituida para L, caída y cota de salida. |
| Recubrimiento mínimo | 0,30 m (proveedor) | max(EG-2013 508.07, AASHTO 12.6.6.3) | EG-2013 / AASHTO | Correcto para concreto; TMC y HDPE quedan descartados antes por `espesor_pared_conducto` solo definido para concreto (`criterios_adoptados.py:5226-5229`). |
| Carga viva | H-20 / HS-20 (CSPI Tabla 6.8) | Rótulo "HL-93", **nunca entra al conducto** | AASHTO 3.6.1.2.6, 12.10/12.12 | Carga de tierra + HL-93 a través del relleno; clase D-load (M 170M) o procedimiento A796 para TMC; relleno máximo. Hoy la Fase 8 solo imprime cama de apoyo y tres "diferido al expediente". |
| Flotación | No | V7 LRFD con γ relleno 17 kN/m³ | AASHTO 12 | Correcto; DC = 0 conservador. |
| Protección de salida | Emboquillado (cualitativo) | d50 Laushey, espesor 1,75·d50, 5 m | MTC ec. 49, Lámina 05 | Falta apron HEC-14 (L en función de D, Q, TW), filtro, Froude, protección de entrada. |
| Espaciamiento de alivios | No | min(200 m, L_hidráulico externo) | MTC 4.1.2.1 d) | L_hidráulico no se calcula; la verificación no puede fallar por construcción. |

### 3.4 Cabezales (muros de cabecera y aleros)

| Aspecto | PDF guía | App (M9) | Norma | Qué falta |
|---|---|---|---|---|
| Geometría del muro de cabecera | Solo predimensionamiento genérico de muro (p. 42) | `predimensionamiento_cabezal` **vacío**; la estructura `GeometriaCabezal` no tiene longitud | Plano tipo MTC (Láminas 02–03), HDS-5 | Ver §4. |
| Aleros / aletas | Tipos de entrada y salida (p. 18) sin dimensiones | **No existen** (ni función, ni campo); solo el criterio `angulo_aletas` vacío | HDS-5 Tabla C.2, plano tipo | Ver §4. |
| Cargas | Coulomb, heq, M-O, inercia (pp. 23–27, aplicado a muros en pp. 110–230) | Las mismas fórmulas, implementadas y testeadas, **sin consumidor en producción** | AASHTO 3.11, 11.6; Manual de Puentes 2.4 | Dar valor a φ, δ, i, β y γ_EQ con el EMS; ensamblar. |
| Estabilidad | e < B/4, deslizamiento μ·φt, q = Vu/(B−2e) | E1–E3 reciben momentos ya calculados por "el llamador", que no existe; capacidad portante (Meyerhof) y estabilidad global `AssertionError` | E.050 Art. 21 y 39.13.6 (FS 3,0/2,5; 1,5/1,25) o AASHTO 11.6 | Ensamble y un solo marco (ASD E.050 o LRFD AASHTO; hoy M9 mezcla γ LRFD con FS de E.050). |
| Armado | "concreto simple" | Cuantías mínimas 0,0020/0,0015, recubrimientos E.060 7.7.1; flexión y corte `NotImplementedError` | E.060 14.3, 11.10 | Diseño de pantalla y zapata, o justificar ciclópeo (f'c ≥ 14 MPa, piedra ≤ 30 %). |
| Sismo | 0,30 g "zona A" (incorrecto) | PGA 0,50 g, kh 0,50 sin reducción | E.030 Zona 4 Z 0,45; Manual de Puentes | Justificar kh (reducción 0,5·kh0 si se admite desplazamiento) y la componente vertical. |
| Memoria | Solo muros de contención | **La Fase 9 no aparece en la memoria HTML**; solo en CLI/JSON | – | Sección de cabezal por punto con fórmulas sustituidas. |

---

## 4. Diseño de cabezales: lo que un jurado esperará y cómo cerrarlo

Este es el bloque que la app "todavía no tiene". Lo que hay en M9 sirve como caja de herramientas; lo que falta es un procedimiento por punto que lo use. Propuesta concreta, alineada con la app, el PDF y la norma:

**4.1 Datos por punto (todos salen de lo que ya existe).** D o B×H adoptados, HW de diseño (de M4), cota de fondo de entrada y salida (M7), altura de terraplén y talud (M7), esviaje (CSV), γ, φ, c, capacidad portante y NF del EMS, PGA y clase de sitio (datos de sitio), γ_EQ.

**4.2 Geometría del muro de cabecera (hoy `predimensionamiento_cabezal` vacío).**
- Altura H_c ≥ cota de clave exterior + recubrimiento mínimo + bordillo, y coronación ≥ cota de fondo + HW de diseño (el agua no desborda el muro).
- Longitud ≥ D + 2·espesor + empotramiento de aleros; espesor de pantalla 0,20–0,30 m (voladizo) o H/8–H/6 (gravedad, p. 42 del PDF); zapata B = 0,4–0,7·H, peralte H/12–H/10; profundidad de desplante ≥ 0,80 m y por debajo de la socavación local a la salida; dentellón.
- Alternativa para cabezales pequeños (D ≤ 1,20 m): plano tipo MTC (Láminas 02–03 del manual) con verificación simplificada.

**4.3 Aleros (hoy inexistentes).** Ángulo 30°–45°–60° con el eje del conducto, elegido con el esviaje y con la embocadura adoptada en HDS-5 (si se adoptan aleros, cambia ke y las cartas de control de entrada: hoy la app usa *square edge w/ headwall*, ke = 0,5). Longitud proyectada hasta el pie del talud: L_a = H_terraplén·talud/sen α (o la del plano tipo); altura variable desde H_c hasta 0,30–0,50 m; espesor y zapata propios; losa o zampeado de entrada y salida con dentellón.

**4.4 Cargas (ya en M9).** Empuje activo Coulomb P_A = ½·Ka·γ·H² (con δ, i, β del EMS; descomponer la componente vertical, cosa que hoy M9 no hace); sobrecarga viva por heq (AASHTO 3.11.6.4: 1,2 / 0,9 / 0,6 m para H de 1,5 / 3 / ≥ 6 m, como en la p. 115 del PDF); hidrostática y subpresión con NF a 1,4 m (corregir la doble cuenta del agua, hallazgo EXT-7 de la propia app); sismo Mononobe-Okabe con kh = 0,5·kh0 si se admite desplazamiento (AASHTO 11.6.5.2.2) o kh0 si no, y fuerza inercial kh·W; empuje del agua del cauce sobre la cara frontal cuando HW > 0.

**4.5 Estabilidad (ensamblar lo que M9 ya calcula).** Volteo FS ≥ 1,5 estático / 1,25 sísmico (E.050 39.13.6) o e ≤ B/3 (AASHTO 11.6.3.3); deslizamiento F_r = N·tan δ_base + c·B ≥ FS·H_u (1,5 / 1,25); capacidad portante q_máx = N/(B−2e) ≤ q_adm (FS 3,0 / 2,5, E.050 Art. 21) con q_ult de Meyerhof con factores de talud (N_q = 0 en borde); un solo marco en toda la verificación.

**4.6 Estructural.** Flexión y corte de pantalla y zapata (E.060 o AASHTO Sec. 5), cuantía mínima 0,0020 horizontal / 0,0015 vertical, recubrimientos 70 / 50 / 40 mm, espaciamiento ≤ min(3h, 400 mm), dos capas si h > 200 mm; o ciclópeo f'c ≥ 14 MPa.

**4.7 Memoria.** Sección "Fase 9 – Cabezal" por punto en la memoria HTML (hoy no existe) con tabla estática/sísmica, fórmulas sustituidas, FS obtenidos vs admisibles, geometría y referencia al plano. El formato de las pp. 110–122 del PDF (tablas DC, EV, brazos, momentos) es un buen modelo.

---

## 5. Errores y cosas fuera de lugar

### 5.1 En la app (código)

1. **Afirmación falsa repetida**: "`homogeneidad_serie_fen` bloquea el Q de toda la Familia A" (`constantes_normativas.py:1130-1131`, `MD.py:875-877`, `M11_reporte.py:3139`). Ningún módulo lee ese criterio; un Q vacío en A es `DatoFaltanteError`, no `CriterioPendienteError`; el fixture corre con Q lleno.
2. **Docstrings de M1 contradictorios** sobre el umbral de área (declarado en 100 ha en `M1_clasificacion.py:39-44`; "sin valor y bloqueando" en `:53-55, 73-76, 648-649, 698-700` y `criterios_adoptados.py:1907-1909`).
3. **Umbral de 100 ha justificado con los puntos del fixture de tests** (`criterios_adoptados.py:1925-1932`), que M1 califica de "no puntos del expediente". Adopción circular.
4. **Docstring de M5 desactualizado** (`M5_verificaciones.py:108-120`): afirma que el procedimiento del TW (Sec. 1.3) "no está implementado"; `M3_hidraulica.py:577-727` lo implementa. Lo mismo en `M4_control.py:271-281` sobre HW/D < 0,75.
5. **Mezcla de marcos** en Fase 9: γ de carga LRFD (`M9_cabezal.py:2032-2108`) con FS globales de E.050 (ASD); M9 no dice si E1–E3 reciben cargas factoradas o de servicio. Choca con la "Vía 1: AASHTO LRFD de extremo a extremo" de la hoja de ruta.
6. **Pendiente nula rechazada** (`M3_hidraulica.py:188`, `M4_control.py:1029, 1256`): HDS-5 admite S = 0; en una llanura es un caso plausible.
7. **`Q_receptor_m3s`**: la ayuda dice "≥ 0" (`variables_entrada.py:684`) y M0 exige "> 0" (`M0_carga.py:582-584`): un receptor seco se rechaza.
8. **`area_ha` obligatoria en Familia B sin consumidor** (`M0_carga.py:119` vs `servicio.py:276-281`), contra la regla del propio M0 de no pedir datos que no se usan.
9. **`sucs_fundacion` obligatoria y nunca leída** (`modelos.py:674-682`).
10. **Cita de fórmula fuera de lugar**: el paso "cuál control gobierna" cita `HDS5_3ED.A.2` (ecuaciones de entrada) (`M4_control.py:2861`); el tirante crítico no lleva cita y su código de paso es "YC_RECT" aunque se emite también para circular.
11. **Hoja de ruta vs código**: claves de Manning `concreto_recto` / `metal_corrugado` (hoja, Anexos A y B) no existen; G = 9,8 en la hoja y 9,81 en `constantes_fisicas.py:133`; la hoja lista 16 columnas y el código 19; el archivo `hoja_de_ruta_alcantarillas_v8.md` se titula "v7" por dentro.
12. **M10** devuelve CUMPLE siempre (`M10_espaciamiento.py:146-150`): min(L_normativo, L_hidráulico) ≤ L_normativo por construcción.
13. **M6** se titula "Protección de entrada y salida" y no tiene protección de entrada.
14. **Dos gravedades**: 9,81 en M4 y 9,8 en Laushey (M6), declaradas pero sin unificar la explicación.
15. **Fase 9 "del proyecto" pero NF "del punto"**: una sola geometría de cabezal para las tres familias (incluido el marco de 2,75 m).
16. **`DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO`** existe y nadie lo consume; inocuo pero confunde.
17. Con `espesor_pared_conducto` solo para concreto, **TMC y HDPE nunca llegan a 7.A ni V7**: la matriz de materiales degenera a concreto, y el relleno mínimo de 0,30 m para HDPE nunca se aplica.
18. Cota de fondo de entrada = cota de terreno natural por defecto (`criterios_adoptados.py:3313`): en un cruce de cauce (familia A) el fondo suele estar bajo el terreno de la plataforma; 7.A puede exigir rasante alta sin necesidad. Este script de QGIS ya mide `cota_fondo_receptor` y `cota_terreno` con el MDT; conviene medir también el fondo de entrada.

### 5.2 En el repositorio de la app (para la sustentación)

- **Historial git de un solo commit** (`c2262a2`): todos los SHAs que citan los documentos y el tracker (19bcf5a, 5196dd2, 71b134fb…) no existen en el clon; la trazabilidad por commit es inverificable.
- **Material de desarrollo con IA versionado**: `.claude/agents/`, 13 prompts literales en `docs/planes_mejora/` ("pega desde aquí como primer mensaje de la sesión"), `CLAUDE.md` de 105 KB con bitácora de incidentes de entorno y tuteo rioplatense, un dictamen sobre un informe "producido por otra IA", verificación normativa delegada a NotebookLM. Un jurado puede cuestionarlo; conviene segregarlo del entregable.
- **`normas/` con 18 PDF (~308 MB) con copyright** (AASHTO LRFD completo, M 36, M 170M, A760, A796; una "traducción no oficial" de M 294 sin autor) y dos manuales que ningún cálculo usa. Redistribuirlos en un repo público es un problema legal, no técnico.
- **Fixtures que parecen datos de proyecto**: `tests/fixtures/datos_referenciales_prueba.md` titulado "Datos referenciales – Vía de Evitamiento La Unión" con φ, c, capacidad portante, TR 100 años, aletas 45° "para destrabe"; memorias HTML en `tests/linea_base_familia_c/` sin advertencia de fixture. Quien las abra creerá que son resultados.
- **`legacy/Tc.py`**: único origen declarado del caudal, no ejecutable, con 185 literales exentos del barrido.
- Fuentes citadas y ausentes: WSDOT Tabla 8-4, HEC-14, Ley 29338, M 294 original, series SENAMHI/ANA, EMS. Citas fechadas "abril 2026" y "RM 183-2026" que un jurado querrá confirmar.
- Sin `LICENSE` ni `pyproject.toml`; `scipy` requerido no está en el sandbox usado para auditar, así que las fases 6–8 se analizaron por código y tests, no por corrida.

### 5.3 En el PDF guía

Ver §1.3: ubicación equivocada (Cusco por Apurímac), sismo fuera de la E.030, metodología de cabezales copiada a muros, memoria TMC con pie de página de otro proyecto, carga H-20 en vez de HL-93, conclusión sobre cabezales sin cálculo que la respalde, esviaje con convención invertida.

### 5.4 En el pedido

- Plantilla con placeholders sin rellenar ([ubicación, región], [ruta/carpeta], [nombre del PDF]).
- El PDF guía es de una carretera de sierra (Apurímac, 2 700–3 500 msnm, TMC con 2 % de pendiente); la tesis es de llanura costera con napa alta, suelos salinos y Zona sísmica 4. Varios criterios del PDF (pendiente 2 %, cobertura 0,30 m, 0,30 g) no se trasladan.
- El pedido dice que la app "todavía no tiene" cabezales; en rigor tiene 3 800 líneas de fórmulas de cabezal (M9) sin ensamblar. Conviene decirlo así en la tesis: "verificaciones implementadas, procedimiento de diseño pendiente".

---

## 6. Plan de cierre priorizado

| # | Acción | Dónde | Efecto en la tesis |
|---|---|---|---|
| 1 | Capítulo de hidrología: cuencas, Tc, IDF (SENAMHI), tratamiento FEN, C, Q por TR 71/35; tabla de Q por obra con caudal específico | Anexo de tesis (o reactivar `legacy/Tc.py`) | Sustenta `Q_m3s`; sin esto nada aguas abajo se defiende |
| 2 | Cerrar los criterios vacíos que detienen la Fase 5: `TW_receptor` (o dato real del dren), `acceso_mantenimiento_v2b`, `regimen_v2b`, `hw_entrada_fuera_de_rango`; declarar `remanso_derecho_via` y `TR_evento_extremo` o diferir V5/V8 con nota | `criterios_adoptados.py` | La app pasa de 0 a N puntos dimensionados |
| 3 | Datos de terceros: caudal y sección de drenes/canales (ANA/Junta), sulfatos/cloruros/pH/resistividad, SPT ≥ 15 m | Tableros 3.1–3.6 | Habilita familia C, matriz de materiales y cabezal |
| 4 | Validar el motor hidráulico contra un ejemplo de HDS-5 o HY-8 por punto | `tests/` | Credibilidad del cálculo frente al jurado |
| 5 | Cabezal por punto según §4: geometría, aleros, ensamble de estabilidad, portante, armado, sección en la memoria | M9 + M11 | Cierra la carencia que el pedido destaca |
| 6 | Fase 8 real: carga de tierra + HL-93, clase D-load o A796, relleno máximo; `espesor_pared_conducto` para TMC y HDPE | M8, M2 | Hoy la "verificación estructural" no verifica nada |
| 7 | Declarar pendiente mín/máx del barril y admitir S = 0; medir cota de fondo de entrada (este script QGIS puede hacerlo) | M7, CSV | Evita rasantes artificialmente altas |
| 8 | Sincronizar docstrings y documentación con el código (hallazgos 5.1.1–5.1.4, 5.1.11) | docs, M1, M4, M5 | Un auditor que lea el código no debe encontrar afirmaciones falsas |
| 9 | Segregar del entregable: prompts, agentes, dictámenes de IA, PDFs con copyright, fixtures sin advertencia; añadir LICENSE y pyproject | repo | Presentación ante jurado |
| 10 | Regenerar `docs/indice_formulas.md` con una corrida que dimensione; cubrir V7, VC1, Laushey y el control gobernante con cita correcta | M11 | Memoria completa |

---

## Anexo A. Fuentes consultadas

- PDF "2.7. Estudio de Estructuras de Obras de Arte y Drenaje" (VARIOS), 388 pp.: memoria descriptiva leída página a página (pp. 1–49, 49–62, 113–116); resto por OCR (Tesseract, español) con índice de títulos por página.
- Manual de Hidrología, Hidráulica y Drenaje del MTC (`normas/`): §3.6 Tablas 01–02, §3.9, §3.12.2 Tabla 08, §4.1.1.3 (pp. 70–80 del manual), ec. 47 y 49.
- Norma E.030 (`normas/`, edición 2026): Tabla 1 (Z) y Anexo 1 (Pacobamba Zona 2; Piura y Sechura Zona 4).
- Código y documentación de `Proyecto_alcantarillas`: auditoría de M0–M11, MD, `criterios_adoptados.py`, `constantes_normativas.py`, `modelos.py`, `servicio.py`, `cli.py`, hoja de ruta v8/v12, auditoría v9, decisiones diferidas, planes de mejora, dictamen 2026-09-19, tracker `matriz_cruzada_auditorias.xlsx`.

## Anexo B. Cómo encaja este script de QGIS

El CSV que produce `cotas_esviaje_alcantarillas.py` alimenta exactamente las columnas topográficas que la app exige (`cota_terreno`, `cota_fondo_receptor`, `S_cauce`, `esviaje_grados`, `cota_coronacion_canal`, y rasante/subrasante si se da el perfil). Dos mejoras que ayudarían a cerrar hallazgos de este informe: medir también `cota_fondo_entrada` en el cauce (hallazgo 5.1.18) y exportar la sección del receptor a 13 m aguas abajo (ancho de fondo, taludes, profundidad) para sustituir la `seccion_receptor` adoptada de la app (hallazgo de §3.2, tailwater).
