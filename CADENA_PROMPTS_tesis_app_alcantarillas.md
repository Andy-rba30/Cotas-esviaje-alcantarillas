# Cadena de prompts T — dejar `Proyecto_alcantarillas` lista para un diseño robusto y defendible de las tres familias

**Para:** una sesión orquestadora de Claude Code que ejecute los prompts, en paralelo donde el grafo lo permita y en secuencia donde no.
**Fuente:** `INFORME_evaluacion_app_alcantarillas_vs_PDF.md` (este repositorio), que a su vez resume cuatro auditorías del código con cita archivo:línea. Todo lo que estos prompts piden está anclado por símbolo (función, criterio, constante), no por número de línea.
**Fecha:** 10 de noviembre de 2026.

---

## 0. ¿Es posible con el contenido del repo `Normas`?

**Sí, para casi todo.** El repo `Andy-rba30/Normas` trae 18 PDF: manual MTC de Hidrología, Hidráulica y Drenaje; DG-2018; EG-2013; Manual de Puentes; Suelos y Pavimentos; E.030 (2026); E.050; E.060; AASHTO LRFD 9.ª; AASHTO M 36, M 170M, M 294 (traducción no oficial); ASTM A760, A796; HDS-5 (dos copias: `fhwa_culvert_hydraulics_hds5si.pdf` y `hif12026.pdf`, que **no es HEC-14** aunque su nombre lo sugiera); Seguridad Vial y Dispositivos de Control (no se usan).

Con eso se cubre: hidrología completa (MTC cap. III: Tabla 01–02 TR, §3.8.1 IDF, §3.9 Tabla 05 Tc, §3.12.2 Tabla 08 racional), hidráulica (HDS-5 Tablas A.1 y C.2, §3.3, §3.5, §5.4.3; MTC 4.1.1.3), geometría (DG-2018, EG-2013 508), estructural del conducto (AASHTO LRFD 3.6.1.2.6, 12.6, 12.7, 12.10, 12.11, 12.12; M 170M; A796; M 294), cabezales y aleros (AASHTO 3.11.5.3, 3.11.6.4, 11.6; Manual de Puentes 2.4; E.050 Art. 21 y 39.13; E.060 cap. 7, 11, 14, 22; E.030 Anexo 1), espaciamiento (MTC 4.1.2.1) y protección básica (MTC ec. 49 Laushey y Lámina 05).

**Las dos fuentes que faltaban ya están en `Normas`** (commit `eebfcca`): `hec14.pdf` (HEC-14, *Hydraulic Design of Energy Dissipators for Culverts and Channels*, FHWA-NHI-06-086, 287 pp.) y `HydraulicsManual.pdf` (WSDOT Hydraulics Manual M 23-03, 325 pp.). Con ellas T-8 calcula el apron y los disipadores con HEC-14 y T-4 verifica la Tabla 8-4 de velocidades de TMC y HDPE. Ambas son [C] (fuente técnica reconocida, no norma peruana) y deben darse de alta en `src/normativa/fuentes.py` con su edición y página (T-0 punto 5).

Lo que **no** es norma y la cadena **no** debe inventar, porque son entradas del proyecto: series SENAMHI, caudal y sección de drenes/canales (ANA/Junta), parámetros del EMS (φ, c, γ, q_adm, NF, SPT, Vs30), ensayos químicos de suelo y agua, IMDA, cotas y esviajes (este script de QGIS), ancho de derecho de vía. La cadena las deja como columnas del CSV, datos externos o `[S]` declarables, con validación de forma, nunca con valores por defecto.

---

## 1. Repositorios que debe abrir la sesión orquestadora

| Repo | Acceso | Para qué |
|---|---|---|
| `Andy-rba30/Proyecto_alcantarillas` | **escritura** (es el repo de trabajo; cada prompt termina en `origin/main`) | Todo el código y la documentación |
| `Andy-rba30/Normas` | lectura | PDF de normas. La app espera los PDF en `normas/` dentro de su propio repo; T-0 decide cómo se enlazan (ver T-0 punto 5) |
| `Andy-rba30/Cotas-esviaje-alcantarillas` | lectura | `INFORME_evaluacion_app_alcantarillas_vs_PDF.md` (especificación de esta cadena) y el script QGIS que produce el CSV |
| `Andy-rba30/VARIOS` | lectura, opcional | PDF "2.7 Estudio de Estructuras…": solo como modelo de presentación de la memoria de cabezal (pp. 110–122) |

Los prompts citan rutas relativas a la raíz de `Proyecto_alcantarillas`. El informe se cita como `INFORME` y sus secciones como `INFORME §3.2`, etc.

---

## 2. Reglas comunes (incluidas por referencia en todos los prompts)

1. **Lee `CLAUDE.md` entero antes de tocar nada.** Rigen sus cinco etiquetas [N]/[N→]/[S]/[C]/[A], sus tres archivos de valores (`constantes_normativas.py` solo [N]; `criterios_adoptados.py` para [N→], [C], [A] y [S] pendientes de ensayo; `datos_sitio.py` solo [S] de corredor), la taxonomía de excepciones (`DatoInvalidoError` / `DatoFaltanteError` / `CriterioPendienteError` / `LimiteNumericoError` / `MetodoNoEvaluableError`), «la memoria la emite el cálculo» y «ningún literal nuevo fuera de los tres archivos» (`tests/test_sin_literales.py`; `# literal-ok: <razón>` solo para fórmulas transcritas).
2. **Las entradas no se corrigen.** `Q_m3s`, `area_ha`, `S_cauce`, cotas, CBR, esviaje, `cota_fondo_receptor`, `Q_receptor_m3s`, `cota_TW`, NF, parámetros del EMS y datos de ANA/Junta son datos de diseño del proyecto. La cadena valida su forma y su dominio, declara de dónde salen y nunca les pone un valor por defecto. Cuando un prompt necesita un dato que hoy no existe, lo crea como columna opcional del CSV, dato externo (`--datos-externos`) o `[S]` declarable, con `DatoFaltanteError` claro si falta y se necesita.
3. **No se rompe nada.** Antes de cambiar una función con consumidores, se añade la nueva ruta al lado y se migra con test; nunca se cambia una API por valor sin actualizar a todos sus lectores (`grep` por símbolo). Cada número de la línea base (`docs/linea_base.md`, `tests/linea_base_familia_c/`) que se mueva se declara con la causa. Los cuatro puntos del fixture `tests/ejemplo_puntos.csv` deben seguir cargando.
4. **Tests primero, en rojo, como aceptación**: `pytest.mark.xfail(strict=True)` con la expectativa del invariante o de la fuente (un valor calculado a mano o un ejemplo publicado), nunca con la salida actual como oráculo. Al corregir, quitar el `xfail`.
5. **No inventes valores.** Si un criterio necesita una decisión de ingeniería que la norma no da, entrada `[A]` con `valor`, `sensibilidad` (ventana) y `justificacion` que cite la fuente más cercana; si ni siquiera hay fuente cercana, `valor=None` y `CriterioPendienteError` con `mensaje_gui` que diga qué dato o ensayo lo destraba. Un `[A]` de perfil sin `sensibilidad` viola el invariante de `CLAUDE.md`.
6. **Toda cita lleva numeral y página verificados contra el PDF de `normas/`** (`src/normativa/registro.py` y `fuentes.py`). Nunca se inventa un numeral. Si el PDF no está (HEC-14, WSDOT), se declara la ausencia en la ficha y en `docs/manifiesto_registro_normativo.md`.
7. **Un cluster por commit; un commit por prompt.** Serie: `tesis(T-n): <resumen> — <IDs del INFORME cerrados>`. IDs: `INF-5.1.k` para los errores de §5.1 del informe, `INF-3.x` para las carencias de §3, `INF-4.k` para los puntos de cabezal de §4.
8. **Ritual de cierre** (el de `CLAUDE.md`, resumido): (1) suite entera verde, `passed + skipped = collected`; (2) `python3 -m src.normativa.manifiesto --escribir --suite "<par>"` y `python3 -m src.indice_formulas --escribir --suite "<par>"` si tocaste citas, criterios, memoria o pasos; (3) fila en la hoja `Hallazgos` de `docs/auditorias/matriz_cruzada_auditorias.xlsx` por ID cerrado; (4) `docs/decisiones_diferidas.md` para lo que se difiera, con símbolo; (5) fusionar a `main`, empujar, medir el par sobre `origin/main`; (6) devolver: IDs cerrados (entero / en parte / no), tests nuevos, números movidos y por qué, diferidos. **Detenerse ahí; no ejecutar el prompt siguiente.**
9. **Entorno:** Python 3.11+, `numpy`, `scipy`, `pytest`, `openpyxl`. Si falta `scipy` en el sandbox, instalarlo antes de correr la suite; la cadena no debe "pasar" con tests saltados por dependencias ausentes.

---

## 3. Grafo de ejecución

```
T-0 (gobernanza, secuencial, primero)
 ├── T-1 hidrología            ─┐
 ├── T-2 hidráulica cierres     │  paralelo (módulos distintos)
 ├── T-3 familia C (marco)      │  → PERO T-2 y T-3 tocan M4/M5: T-3 va después de T-2
 ├── T-4 materiales y durabilidad
 └── T-6 geometría             ─┘
      T-5 estructural del conducto  (después de T-4)
      T-7a cabezal: geometría y aleros (después de T-2, por ke/cartas de aleros)
      T-7b cabezal: estabilidad       (después de T-7a)
      T-7c cabezal: armado            (después de T-7b)
      T-8 protección de salida        (después de T-2; paralelo a T-7)
      T-9 espaciamiento de alivios    (después de T-1; paralelo a T-7)
T-10 memoria M11                      (después de todos los anteriores; toca a todos)
T-11 validación integral de las 3 familias (después de T-10)
T-12 repositorio para sustentación    (último)
```

**Puntos calientes de conflicto** (si se paraleliza en ramas o worktrees, serializar los merges en este orden): `src/criterios_adoptados.py`, `src/constantes_normativas.py`, `src/modelos.py`, `src/servicio.py`, `src/modulos/M11_reporte.py`, `docs/hoja_de_ruta_alcantarillas_v8.md`, el tracker `.xlsx`. Regla: un prompt que añade criterios los añade al **final** de su sección en `criterios_adoptados.py`, nunca reordena; las constantes nuevas van en bloque propio con cabecera del prompt. Merge siempre con la suite verde en la rama destino.

---

## 4. Los prompts

### T-0 · Gobernanza, especificación y enlace a Normas (secuencial, sin código de cálculo)

```text
Ejecuta únicamente T-0 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Lee antes, enteros: CLAUDE.md, INFORME_evaluacion_app_alcantarillas_vs_PDF.md (repo Cotas-esviaje-alcantarillas) y docs/planes_mejora/07_CADENA_PROMPTS_EXT.md (es el modelo de estilo de esta cadena).

1. Tracker. Da de alta en la hoja Hallazgos del .xlsx todos los hallazgos del INFORME con prefijo INF- (INF-5.1.1 … INF-5.1.18 del §5.1; INF-5.2.* del §5.2; INF-3.1 … INF-3.4 por fila de "Qué falta"; INF-4.1 … INF-4.7 del §4), con severidad, cluster, prompt T-n que lo cierra y Estado «Abierto».

2. Hoja de ruta v8. Corrige el encabezado interno (dice v7) y enmienda con nota de corrección: Sec. 1.2 (encabezado del CSV: 19 columnas, las que M0_carga.COLUMNAS lista); Anexos A y B (claves MANNING["concreto_tubo_recto"] y ["metal_corrugado_dren_aguas_lluvias"], G = 9.81 en constantes_fisicas, G_LAUSHEY = 9.8 solo en M6 con su razón); §1.1 (el caudal lo calculará el módulo de hidrología de T-1, no legacy/Tc.py); §2.3 (familia B: declarar conjunto de verificaciones de aceptación, hoy None); Sec. 7.B (pendiente mínima/máxima del conducto y desnivel mínimo de entrega pasan a criterios, T-6); §9 (cabezal POR PUNTO y con aleros, T-7); fila V5 (método de remanso y ancho_derecho_via_m como dato externo).

3. Docstrings y comentarios falsos (INF-5.1.1, 5.1.2, 5.1.4, 5.1.9): corrige en el código, sin cambiar lógica, los textos de M1_clasificacion (umbral de área "sin valor"), M5_verificaciones (Sec. 1.3 "no implementada"), M4_control (HW/D < 0.75 "DIFERIDO"; DisenoNoFactibleError fija), constantes_normativas / MD / M11_reporte ("homogeneidad_serie_fen bloquea el Q"), y la cita HDS5_3ED.A.2 del paso "cuál control gobierna" (sustituir por la cita del procedimiento de diseño del Cap. III de HDS-5, página verificada). Añade formula_cita_id al tirante crítico y renombra el código de paso YC_RECT a uno neutro, manteniendo compatibilidad (alias) para los lectores de la traza.

4. Contrato de entrada que NO se toca: escribe en docs/contrato_entradas.md (nuevo) la lista de entradas de diseño (CSV, datos externos, [S]) con su origen (estudio hidrológico, ANA/Junta, EMS, topografía/QGIS, trazo), dejando claro que la cadena T no las rellena. Incluye la convención de esviaje (0° = perpendicular) y la fórmula de conversión desde expedientes que usan 90° = perpendicular.

5. Enlace a Normas. Decide y documenta en CLAUDE.md cómo se obtienen los PDF: (a) el repo Normas clonado y enlazado como normas/ (symlink o variable NORMAS_DIR leída por src/normativa/fuentes.py), o (b) git submodule. Implementa la opción elegida de modo que src/normativa/fuentes.py y verificar_sesion.py los encuentren, y da de alta en src/normativa/fuentes.py y en docs/manifiesto_registro_normativo.md las dos fuentes nuevas de Normas: hec14.pdf (HEC-14, FHWA-NHI-06-086) y HydraulicsManual.pdf (WSDOT M 23-03), con edición y paginación verificadas, para que T-4 y T-8 puedan citarlas. No borres todavía los PDF de normas/ del repo (eso es T-12).

6. Deja en docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md una copia de este documento.

No toques fórmulas ni umbrales. Ritual de cierre.
```

### T-1 · Hidrología: módulo nuevo, Q por cuenca (paralelo con T-2, T-4, T-6)

```text
Ejecuta únicamente T-1 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.1 (hidrología) e INF-5.2 "legacy/Tc.py". Fuentes: manual MTC de Hidrología, Hidráulica y Drenaje, cap. III: §3.6 y Tablas 01–02 (TR; ya en M1), §3.7 (distribuciones y bondad de ajuste), §3.8.1 (IDF, método Dick y Peschke y Tabla 04 de coeficientes regionales si aplica), §3.9 y Tabla 05 (Tc: Kirpich, Témez, California, y sus observaciones de validez), §3.12.2 ecuación (28) Q = 0.278·C·I·A con A en km² y Tabla 08 (C), §3.13 (avenida de diseño). Verifica cada página contra el PDF.

Objetivo: que el caudal de diseño de las familias A y B pueda calcularse dentro de la app a partir de datos de cuenca y de lluvia, dejando una memoria auditable, SIN quitar la vía actual (Q_m3s como columna sigue siendo válida y gana si viene llena).

1. Crea src/modulos/MH_hidrologia.py (nuevo módulo, importado solo por servicio.py) con: (a) tc por los métodos de la Tabla 05, cada uno con su rango de validez transcrito y MetodoNoEvaluableError fuera de rango (Kirpich fuera de 3–10 % de pendiente, como ya advierte legacy/Tc.py); (b) intensidad I(tc, TR) desde una serie de precipitación máxima en 24 h por estación (entrada: CSV de la estación con año y P24, más el método de ajuste elegido entre los de §3.7 con prueba de bondad) y desde la relación IDF de §3.8.1; (c) C desde la Tabla 08 por cobertura, suelo y pendiente (clave de fila, nunca número suelto); (d) Q = 0.278·C·I·A con guardia A ≤ 10 km² (fuera, MetodoNoEvaluableError que remita a §3.12.3 hidrograma unitario); (e) caudal específico Q/A como indicador de plausibilidad con aviso, sin umbral duro.

2. Entradas: nuevo CSV opcional de cuencas (id de la obra, area_km2, L_cauce_m, S_cauce_cuenca, cobertura, suelo, estacion) y CSV de la estación; entran por --cuencas y --estacion (servicio.py), nunca por valores por defecto. Si Q_m3s viene lleno en puntos.csv, se usa y la memoria imprime "Q declarado por el estudio hidrológico"; si viene vacío y hay cuencas+estación, se calcula y se imprime la memoria hidrológica del punto; si no hay ninguna de las dos, DatoFaltanteError('Q_m3s') como hoy.

3. Fase 1-bis: da consumidor real al criterio homogeneidad_serie_fen: la serie de la estación debe declarar qué años FEN (1983, 1998, 2017 u otros) incluye y cómo se tratan (serie completa / serie sin FEN / dos poblaciones), y la memoria lo imprime. Sin esa declaración el cálculo hidrológico se detiene con CriterioPendienteError; con Q declarado por columna, imprime aviso (no bloquea: el Q externo es responsabilidad del estudio hidrológico, INF-5.1.1).

4. Familia B: el Q de la cuneta se calcula con el mismo módulo (área tributaria de plataforma y talud, C de pavimento/talud de la Tabla 08, tc de la cuneta) o entra declarado; deja el enlace listo para T-9.

5. Tests: casos a mano con el ejemplo de §3.12.2 del manual si lo trae, un caso Kirpich/Témez con valores de la Tabla 05 y un caso de IDF con serie sintética; test de que Q_m3s lleno gana; test de que legacy/Tc.py deja de ser la fuente declarada (origen_del_caudal de PERFILES[A] en M1 pasa a nombrar MH_hidrologia). Marca legacy/Tc.py como superseded en su cabecera; no lo borres.

6. Pasos de memoria (PasoDeMemoria) con fórmula sustituida para tc, I, C, Q y Q/A, con cita.

Ritual de cierre.
```

### T-2 · Hidráulica: cierres de método (paralelo con T-1, T-4, T-6; antes de T-3, T-7a, T-8)

```text
Ejecuta únicamente T-2 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.2 (filas pendiente, borde libre, tailwater, control, velocidades), INF-5.1.6, INF-5.1.7. Fuentes: HDS-5 3.ª ed. (Tabla A.1 completa, Tabla C.2 completa, §3.1.6, §3.3.3, §3.5, §5.3.3, ejemplos de diseño del Cap. III), manual MTC 4.1.1.3.3, 4.1.1.3.6, 4.1.1.3.7 b).

1. Pendiente del barril: admite S = 0 en M3.resolver_manning (sin tirante normal: régimen gobernado por control de salida) y en M4 (Ks·S = 0), con guardia MAT-D13 solo contra S < 0. Crea criterios [A] de perfil pendiente_minima_conducto (ventana 0.0–0.005, justificación MTC 4.1.1.3.3 y HDS-5 §5.3.3) y pendiente_maxima_conducto (ventana 0.02–0.10, por V3) con valor y sensibilidad, y la verificación V10 que los aplica (M5), sin cambiar V2b.

2. Borde libre bajo ahogamiento por TW (INFORME §3.2): separa en V1 el caso "lleno por el caudal de diseño" (NO cumple, MTC p. 79) del caso "lleno por nivel del receptor" y crea criterio [A] borde_libre_bajo_tw_ahogante ∈ {no_cumple, aviso} con sensibilidad y justificación; la memoria imprime cuál aplicó. Valor adoptado: aviso, por defecto NO; elige el que la ficha justifique y deja el otro como alternativa barrible.

3. Tailwater: la vía 4 (receptor lleno con seccion_receptor adoptada) pasa a imprimir en la memoria "sección adoptada [A] por falta de levantamiento" y a disparar aviso; añade como entrada opcional del CSV o datos externos la sección medida del receptor (ancho de fondo, talud z, profundidad, n, pendiente), que este script QGIS puede exportar, y que gana sobre el criterio cuando viene.

4. Cartas HDS-5 para aleros: transcribe a constantes_normativas las filas de la Tabla A.1 de cajón y tubo con aleros (wingwall 30°–75°, 90° y 15°, y socket/bevel donde existan para concreto; TMC headwall/mitered ya están) y las filas correspondientes de ke de la Tabla C.2, con página verificada, de modo que embocadura_cajon, hds5_embocadura_* y ke_entrada puedan nombrar una fila de aleros. No cambies la embocadura adoptada hoy (square edge w/ headwall): solo deja las filas disponibles para T-7a.

5. Validación externa: reproduce en tests/fixtures/casos_patron.py al menos un ejemplo publicado de HDS-5 (Cap. III, ejemplo de diseño con control de entrada y salida) como dorado, con página, y un test que lo compare con tolerancia declarada. Si alguna diferencia supera la tolerancia, no ajustes el test: documenta la causa en decisiones_diferidas.md.

6. Criterios vacíos que detienen la Fase 5 y tienen respaldo documental: regimen_v2b (HDS-5 §5.3.3 presenta la pendiente como indicador: adopta "indicador_con_aviso" [C] con cita), acceso_mantenimiento_v2b (manual MTC 4.1.1.3.7 d): adopta la exigencia de mantenimiento como texto [N] y deja el dato de acceso como entrada booleana por punto, opcional), hw_entrada_fuera_de_rango (adopta "energia_critica" [C] con cita HDS-5 Tabla A.1 nota de Ks·S). TW_receptor sigue siendo entrada (no se adopta): la vía 4 lo cubre.

7. Q_receptor_m3s = 0 admitido (receptor seco), coherente con variables_entrada.

Ritual de cierre. Reporta por ID.
```

### T-3 · Familia C: el marco de concreto se dimensiona (después de T-2)

```text
Ejecuta únicamente T-3 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.x "Familia C no se dimensiona" y los criterios del cajón. Fuentes: manual MTC Tabla 09 (n concreto), 4.1.1.3.4 (secciones y alcantarillas múltiples, separación de tubos), HDS-5 Tabla A.1 cartas 8–13 y Tabla C.2 (box), §5.4.3 (reparto multicelda); AASHTO LRFD 12.11 (box culverts: cobertura, cargas), 12.6.6.3; EG-2013 Sec. 500 (marcos); E.060 (espesores mínimos). docs/ruta_familia_c.md entera.

1. Da valor, con cita y sensibilidad, a: n_manning_cajon (par mín/máx de la fila de concreto de la Tabla 09, misma lectura corregida que concreto_tubo_recto); embocadura_cajon (fila de la Tabla A.1 para cajón con aleros o cabezal recto; coherente con lo que T-7a adopte, por ahora "square edge headwall 90°"); ke_entrada_cajon (fila de la Tabla C.2); secciones_cajon_normalizadas (progresión declarada: anchos 1.00–4.00 m paso 0.50, alturas 1.00–3.00 paso 0.25, [A] de catálogo constructivo, sin cambiar los pasos que siguen el dato de la Junta cuando viene); n_celdas_cajon (1 por defecto, entero, con V6 ampliada para N > 1 usando el reparto Q/N ya implementado y la separación entre celdas del manual MTC 4.1.1.3.4); cobertura_minima_cajon (AASHTO 12.11 o losa a nivel de rasante: cita verificada); espesor de pared del marco (E.060 / práctica EG-2013, [A] con ventana).

2. VC1 (corona del canal − borde libre): mantén; añade VC2 (cota de salida vs fondo del canal aguas abajo) que docs/ruta_familia_c.md §16.17 deja "evaluada, no implementada", y la longitud del remanso aguas arriba del canal como aviso (no umbral), con la sección medida del canal (T-2 punto 3) cuando venga.

3. La geometría del marco entra a M7 (cota de clave = cota_fondo_entrada + H + espesor de losa) y a M8 (T-5 la completará); comprueba que 7.A y G1/G2 corren para C-01 del fixture con datos de canal declarados por --datos-externos.

4. Regenera la línea base de Familia C (tests/linea_base_familia_c/regenerar.sh) y declara qué se movió.

Ritual de cierre.
```

### T-4 · Materiales, espesores, topes y durabilidad (paralelo con T-1, T-2, T-6; antes de T-5)

```text
Ejecuta únicamente T-4 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-5.1.13 (TMC y HDPE descartados por espesor_pared_conducto), INF-3.3 "material / durabilidad / topes". Fuentes: AASHTO M 36 y ASTM A760 (tablas de espesores y propiedades de TMC: corrugación 68×13, espesores 1.6–4.2 mm, área, I, r); AASHTO M 170M (Wall A/B/C, diámetros); AASHTO M 294 (traducción no oficial: diámetros 300–1500 mm, rigidez); EG-2013 (secciones 505–508: materiales de tubería y relleno); E.060 Tabla 4.4 (sulfatos) y 4.4.x (cloruros); manual MTC 4.1.1.3.7 e) y f) (abrasión y corrosión) y 4.1.1.3.4 b).

1. espesor_pared_conducto para TMC y HDPE: TMC por tabla de M 36/A760 (clave de fila = corrugación y espesor nominal; valor por defecto de perfil = 2.0 mm 68×13 como adopción [A] barrible, justificada con la práctica del mercado peruano que documenta el PDF de VARIOS p. 57); HDPE por tabla de M 294 (diámetro exterior vs interior). Comprueba que con esto TMC y HDPE llegan a 7.A y V7 para A-01 y B-01 del fixture, y que H_RELLENO_MIN de HDPE (0.30 m, EG-2013 508.07) se aplica de verdad.

2. D_max_catalogo: sustituye los topes 2.70 / 2.10 / 1.50 [A] sin respaldo por los que dan las normas de producto (M 170M diámetros nominales; M 36 diámetros de fabricación; M 294 300–1500 mm), citados, y deja la disponibilidad local como [A] opcional que solo puede bajar el tope.

3. Velocidad máxima TMC y HDPE: la fuente ya está en Normas (HydraulicsManual.pdf, WSDOT M 23-03.12, abril 2026). OJO: su Tabla 8-4 (pág. 8-27, §8-6 Abrasión) NO es una tabla de velocidades máximas sino de NIVELES DE ABRASIÓN: no abrasivo < 3 ft/s, poco abrasivo < 6 ft/s, moderadamente abrasivo 6–15 ft/s, severamente abrasivo > 15 ft/s; para el nivel severo el manual prohíbe el termoplástico (§8-3.3: "shall not be used for severely abrasive conditions") y para el metal exige más calibre o protección, no lo prohíbe. Por tanto: v_max_hdpe = 4.572 m/s puede quedar [C] citando §8-3.3 y Tabla 8-4 con página; v_max_tmc pasa a [A] con ventana (3.0–4.6 m/s) y justificación (abrasión, manual MTC 4.1.1.3.7 e); Tabla 8-4 como referencia de nivel), o se sustituye por la regla de la propia tabla (nivel de abrasión del sitio como entrada [S] y aumento de calibre como consecuencia, enlazado con T-5). Elige una de las dos y documenta; corrige la ficha que hoy etiqueta ambos como [C].

4. Matriz de durabilidad (hoja de ruta Sec. 3.4) como filtro real de M2.materiales_candidatos: entradas [S] por sitio o por punto, todas opcionales y sin valor por defecto: sulfatos_ppm, cloruros_ppm, pH, resistividad_ohm_cm, abrasion (categoría). Reglas: sulfatos → tipo de cemento y concreto admisible (E.060 Tabla 4.4); cloruros → recubrimiento/concreto; pH y resistividad → TMC inadmisible o con recubrimiento (cita AASHTO/ASTM A760 o EG-2013 donde lo diga; si la fuente peruana no da umbral, [C] con cita FHWA/AASHTO y ventana); "suelo de fundación deficiente → marco" (hoja Sec. 3.1) como aviso, no filtro. Sin datos, el filtro no actúa y la memoria imprime "durabilidad: sin ensayos, matriz no aplicada".

5. n_manning_hdpe: deja de ser analogía con concreto: cita M 294 o ficha técnica si trae n; si no, mantén la analogía pero etiquetada [A] con ventana (0.009–0.013).

Ritual de cierre.
```

### T-5 · Estructural del conducto: Fase 8 real (después de T-4)

```text
Ejecuta únicamente T-5 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.3 "carga viva / clase / relleno máximo" e INF-5.1.5 "Fase 8 no verifica nada". Fuentes: AASHTO LRFD 9.ª: 3.6.1.2.6 (distribución de la carga viva a través del relleno), 3.6.2.2 (impacto en estructuras enterradas), 12.6 (general, cobertura mínima 12.6.6.3), 12.7 (metal corrugado: empuje de anillo, área de pared, pandeo, costuras, factor de flexibilidad, 12.7.2.x), 12.10 (tubería de concreto: método indirecto por D-load con factor de cama, 12.10.4.3), 12.11 (box), 12.12 (termoplástico: empuje, pandeo, deformación); AASHTO M 170M Tablas 1–5 (clases I–V por D-load); ASTM A796 §7–§11 (procedimiento de diseño de TMC: el mismo que el PDF de VARIOS aplica en pp. 50–66 con el CSPI, útil como caso de comprobación numérica: D 0.90 m, H 0.30 m, DL 4.5 kPa, LL 86 kPa H-20, C 40.7 kN/m, A 0.354 mm²/mm); AASHTO M 294; EG-2013 505–508 (camas, rellenos, compactación 95 %). Manual de Puentes 2.4.3 (HL-93).

1. Carga de tierra sobre el conducto (AASHTO 12.10.2 / 12.7.2 según material, con factor de interacción suelo-estructura Fe = 1 + 0.20·H/Bc donde AASHTO lo prescribe) y carga viva HL-93 distribuida a través del relleno (3.6.1.2.6 con impacto 3.6.2.2), ambas como PasoDeMemoria con fórmula sustituida. Altura de relleno real por punto = cota_subrasante − cota de clave (ya existe M5.altura_relleno_sobre_clave) más el paquete estructural donde corresponda.

2. Concreto: clase por D-load (M 170M Tablas 1–5 transcritas a constantes_normativas con página; clases_producto_por_relleno deja de ser None) con factor de cama por tipo de instalación (AASHTO 12.10.4.3, Tabla de factores de cama; tipo de instalación como [A] con ventana, por defecto el más desfavorable que EG-2013 admita). Resultado: clase mínima requerida y relleno máximo admisible por clase.

3. TMC: procedimiento de A796 / AASHTO 12.7.2: empuje de anillo, área de pared requerida vs tabla de M 36 (T-4), pandeo, resistencia de costura, factor de flexibilidad, relleno mínimo y máximo. Caso de comprobación: el ejemplo del PDF de VARIOS (valores arriba) debe reproducirse dentro de tolerancia declarada, con la salvedad de que el PDF usa H-20 y la app HL-93 (documentar la diferencia).

4. HDPE: AASHTO 12.12 (empuje, pandeo, deflexión 5 %) con M 294.

5. Marco: AASHTO 12.11 (cargas sobre losa y paredes); el diseño de la sección del marco (momentos, As) sigue fuera del alcance (hoja de ruta): deja la demanda calculada y un PasoDeMemoria "diseño del pórtico: diferido al expediente, demanda en kN·m/m".

6. Elimina los AssertionError("inalcanzable") de M8 sustituyéndolos por las rutas reales; verificacion_diferida_estructural pasa a imprimir solo lo que de verdad siga diferido.

Tests: un dorado por material calculado a mano con página; test de que la Fase 8 produce al menos una Verificacion con cumple ∈ {True, False} por material candidato (hoy produce cero).

Ritual de cierre.
```

### T-6 · Geometría: fondo de entrada medido, longitud, pendiente y entrega (paralelo con T-1, T-2, T-4)

```text
Ejecuta únicamente T-6 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-5.1.14 (cota de fondo de entrada = terreno), INF-3.3 "longitud / pasos de memoria", y la parte de M7 de INF-5.1.4. Fuentes: DG-2018 (sección transversal tipo, taludes, Tabla 304.11), EG-2013, manual MTC 4.1.1.3.2 y 4.1.1.3.3, Láminas 01–03.

1. cota_fondo_entrada: ya es columna opcional del CSV. Cuando viene (este script QGIS puede medirla en el cauce), gana; cuando falta, el criterio origen_cota_fondo_entrada = "cota_terreno" sigue, pero la memoria imprime aviso "fondo de entrada adoptado igual al terreno de plataforma: medir en el cauce" y 7.A marca el delta de rasante como provisional. Ninguna otra regla nueva.

2. Longitud del conducto: calcula con la altura hasta la clave (o invert, según el talud) EN CADA EXTREMO (entrada y salida, la salida S·L más baja) y con el bombeo/peralte si la sección típica lo da (dato externo opcional); conserva la fórmula actual como caso particular (terraplén simétrico) y haz que la memoria imprima cuál se usó. PasoDeMemoria con fórmula sustituida para L, factor de esviaje, caída S·L, cota de salida y G2 (hoy van como frase).

3. G2 con desnivel mínimo de entrega: criterio [A] desnivel_minimo_entrega_m (ventana 0.0–0.30 m, justificación: evitar remanso del receptor y sedimentación, MTC 4.1.1.3.3) que la verificación aplica; cota_salida ≥ cota_fondo_receptor + desnivel.

4. Esviaje: tope esviaje_max_grados pasa a tener valor [A] (ventana 45°–60°) con la justificación de MTC 4.1.1.3.2 (seguir la corriente) y de la longitud resultante; la verificación es aviso, no bloqueo, porque el esviaje es entrada.

5. Pendientes del conducto (T-2 crea los criterios): aquí M7 deja la pendiente adoptada S_conducto como dato con tres orígenes (S_cauce por defecto, declarada, o la mínima/máxima si gobierna), y la memoria lo imprime.

Ritual de cierre.
```

### T-7a · Cabezal: geometría por punto y aleros (después de T-2)

```text
Ejecuta únicamente T-7a de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-4.1, INF-4.2, INF-4.3 e INF-5.1.12 (cabezal "del proyecto"). Fuentes: HDS-5 Tabla A.1 y C.2 (filas de aleros, ya transcritas en T-2), §3.1.6; manual MTC Láminas 02–03 (secciones típicas TMC y marco con protecciones) y 4.1.1.3.4; EG-2013 Sec. 500 (cabezales: concreto estructural f'c, ciclópeo); E.050 (profundidad de desplante mínima, Art. sobre cimentaciones superficiales); E.060 (espesores mínimos de muros, cap. 14); AASHTO 11.6 (geometría de muros); el PDF de VARIOS p. 42 (predimensionamiento de muro de gravedad y en voladizo) y p. 18 (tipos de entrada/salida) solo como referencia de práctica.

1. El cabezal pasa a ser POR PUNTO: GeometriaCabezal (modelos.py) gana longitud del muro, geometría de aleros y referencia al punto; servicio.correr_cabezal recorre los puntos dimensionados y usa el NF, la cota de fondo, el D o B×H, el HW y la altura de terraplén de cada uno. La Fase 9 "del proyecto" se conserva como suma (reporte) pero deja de ser el único nivel.

2. predimensionamiento_cabezal deja de ser None: implementa M9.predimensionar_cabezal(punto, resultado) que devuelve una GeometriaCabezal propuesta con reglas declaradas [A] y sus ventanas: altura H_c = max(cota de clave exterior + recubrimiento + bordillo, cota_fondo + HW de diseño + resguardo) − cota de desplante; longitud L_c ≥ D (o B) + 2·espesor + empotramiento de aleros; espesor de pantalla (voladizo: 0.20–0.30 m; gravedad: H/8–H/6); zapata B = 0.4–0.7·H_c, peralte H/12–H/10, punta y talón; profundidad de desplante D_f ≥ 0.80 m y ≥ socavación estimada a la salida (de T-8 cuando exista, si no, dato externo); dentellón. Tipo (voladizo armado / gravedad ciclópeo) como [A] con regla por altura (ciclópeo hasta 2.0 m, con ventana). El proyectista puede pisar cualquier dimensión por --datos-externos; la memoria imprime "propuesta por regla" o "declarada".

3. Aleros: nueva dataclass Aleros (ángulo α, longitud L_a, altura inicial H_c y final H_f, espesor, zapata) y M9.predimensionar_aleros: α ∈ {30°, 45°, 60°} elegido por esviaje y por la embocadura adoptada (criterio angulo_aletas deja de ser None: regla [A] "45° por defecto; 30° si esviaje > 30°; 60° en caja receptora", ventana completa); L_a = (H_terraplén − H_f)·talud/sen α o la del plano tipo MTC (Lámina 02) si aplica; H_f [A] 0.30–0.50 m. Coherencia obligatoria: si la embocadura adoptada en HDS-5 es con aleros, ke y la carta de control de entrada cambian a las filas de aleros (T-2) y M4 debe recalcular; un test lo exige (cambiar α no puede dejar ke intacto).

4. Compatibilidad cabezal–tubo: convierte la verificacion_pendiente del criterio en una Verificacion real: L_c ≥ D + 2t, H_c ≥ clave exterior + recubrimiento, coronación ≥ cota_fondo + HW.

5. Losa/zampeado de entrada y salida y dentellón: geometría declarada [A] (longitud 1.0–1.5·D, espesor 0.20–0.30 m) como parte de la GeometriaCabezal; su verificación hidráulica queda para T-8.

6. Memoria: el objeto geométrico completo se imprime (tabla) en la memoria de cada punto; el plano no es alcance.

Ritual de cierre.
```

### T-7b · Cabezal: ensamble de estabilidad en un solo marco (después de T-7a)

```text
Ejecuta únicamente T-7b de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-4.4, INF-4.5, INF-5.1.5 (mezcla de marcos) y los EXT-7-01..04 que decisiones_diferidas.md deja abiertos (componente vertical de Coulomb, doble cuenta del agua, E6, γ_EQ). Fuentes: AASHTO LRFD 3.11.5.3 (Coulomb), 3.11.6.4 (heq), 3.11.3 (agua), 11.6.3.3 (excentricidad), 11.6.3.5–11.6.3.6 (deslizamiento, capacidad), 11.6.5 (sismo, Mononobe-Okabe, kh = 0.5·kh0 si se admite desplazamiento), 10.6.3 (capacidad portante, Nγq/Ncq en talud); Manual de Puentes 2.4.2.2, 2.4.4.1.5.3, 2.4.5 (combinaciones); E.050 Art. 21 (FS portante 3.0/2.5) y 39.13.6 (FS volteo y deslizamiento 1.5/1.25), 39.13.8 (drenaje del trasdós); E.030 Anexo 1 (zona); PDF de VARIOS pp. 110–122 como ejemplo de ensamble numérico (tablas DC/EV con brazos, ΔP_AE, EQ muro).

1. Decide el marco y escríbelo en la hoja de ruta §9: (a) ASD con FS de E.050 sobre cargas de servicio, o (b) LRFD AASHTO 11.6 con φ y e ≤ B/3 sobre cargas factoradas. Recomendación: (b) para ser coherente con la "Vía 1" de la hoja y con el PDF guía, dejando (a) como verificación paralela impresa (ambos marcos se calculan; el que rige se declara [A] con justificación). Ningún número de FS ni γ se inventa: todos de la fuente con página.

2. Ensamble por punto, consumiendo lo que M9 ya tiene (empujes_trasdos, fuerza_inercia_muro, presion_contacto_base, demanda_sismica_cabezal, verificar_capacidad_portante/volteo/deslizamiento): N = ΣW_muro + W_suelo talón + E_v (componente vertical de Coulomb, hoy omitida) − U; H = E_h + LS_h + E_w + ΔP_AE + P_IR; M_e y M_v con brazos; e, q_máx/q_mín, FS o φ·R ≥ ΣγQ por condición (estática, sísmica). Corrige la doble cuenta del agua bajo el NF (γ sumergido + hidrostática, AASHTO 3.11.3) y declara el drenaje del trasdós (lloraderos) como [A] que reduce la hidrostática solo si se declara.

3. Capacidad portante: implementa q_ult (Meyerhof/Terzaghi con factores de forma, profundidad e inclinación y los factores de talud de AASHTO 10.6.3.1.2 Figura/Tabla con N_cq y N_γq transcritos de la fuente, no de un ábaco ilegible: si el PDF de AASHTO no permite leerlos, [A] con ventana y fuente alternativa citada). Entradas [S] por punto o corredor: c, φ, γ, NF, q_adm si el EMS la da directamente (gana sobre el cálculo). Sin EMS → CriterioPendienteError que nombre el ensayo.

4. Sismo: PGA, F_pga y kh desde los datos de sitio (ya existe la cadena); kh reducido 0.5·kh0 solo si se declara desplazamiento admisible (AASHTO 11.6.5.2.2) como [A]; γ_EQ con valor [A] en su ventana (0–1, AASHTO 3.4.1); punto de aplicación de ΔP_AE 0.6H [C] con cita.

5. Los cuatro ángulos de Coulomb (φ, δ, i, β) son entradas: φ del EMS ([S]), δ = 2/3·φ [C] con cita (AASHTO 3.11.5.3 / Tabla C3.11.5.3-1), i de la geometría del terraplén (M7), β de la geometría del cabezal (T-7a). Quitar el bloqueo que hoy detiene incluso el caso estático.

6. Estabilidad global (E4) y talud (E5): si no hay método implementado, quedan como "diferido al expediente con el EMS" impresos, sin AssertionError.

Tests: ejemplo numérico del PDF de VARIOS (pp. 112–122: B 1.50 m, h 0.38, Ka 0.388, Kp 2.578, K_AE 0.498, heq 0.90, P_A 2793 kg, ΔP_AE 791 kg, M sísmico 4217.9 kg·m, DC 7.47 t, EV 3.07 t, EQ 1.58 t) reproducido con tolerancia declarada y con las diferencias documentadas (unidades, φt, δ); test de que ningún punto dimensionado sale de Fase 9 sin las tres verificaciones E1–E3 evaluadas.

Ritual de cierre.
```

### T-7c · Cabezal: armado o concreto ciclópeo (después de T-7b)

```text
Ejecuta únicamente T-7c de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-4.6 y el NotImplementedError de M9.diseno_flexion_corte. Fuentes: E.060 cap. 9 y 10 (flexión), 11 (cortante; 11.10 muros), 14 (muros: cuantías 0.0020/0.0015, espaciamiento), 7.7.1 (recubrimientos), cap. 22 (concreto simple/ciclópeo); AASHTO LRFD Sec. 5 (5.6 flexión, 5.7 cortante método simplificado β = 2, θ = 45°, 5.10.1 recubrimientos); EG-2013 Sec. 500 (ciclópeo f'c, piedra ≤ 30 %).

1. Pantalla y zapata como vigas de 1 m: momentos y cortantes de las cargas factoradas de T-7b (Resistencia I y Evento Extremo I); As por flexión (E.060 o AASHTO 5.6: elige UNO, coherente con el marco de T-7b, y cita), cortante con el método simplificado (nada de MCFT general: el procedimiento MCFT transcrito en ksi-pulgadas se retira o se deja como referencia no ejecutable con nota), cuantías mínimas y máximas, espaciamiento, recubrimientos por exposición (categoria_refuerzo_aashto y exposicion_quimica_ems pasan a entradas [S] con valor por defecto NO; sin dato, recubrimiento de E.060 7.7.1 "en contacto con el suelo" 70 mm [N]).

2. Cortante alto en muros (E.060 11.10.10): implementa la regla completa (ec. 11-32 y topes); los tres criterios vacíos de cortante alto pasan a tener valor [N] con numeral.

3. Alternativa ciclópea para cabezales de gravedad (tipo elegido en T-7a): verificación de tracciones nulas en la base y en la sección media (e ≤ B/6), f'c ≥ el de EG-2013, piedra ≤ 30 %.

4. Memoria: tabla de armado por elemento (As requerido, As mínimo, barra y espaciamiento propuestos como [A] de catálogo) y, para ciclópeo, la verificación de tracciones.

Tests: un dorado de flexión y uno de cortante calculados a mano con E.060; test de que diseno_flexion_corte ya no lanza NotImplementedError para un punto dimensionado.

Ritual de cierre.
```

### T-8 · Protección de entrada y salida (después de T-2; paralelo con T-7)

```text
Ejecuta únicamente T-8 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.3 "protección" e INF-5.1.11 (M6 sin protección de entrada). Fuentes: manual MTC 4.1.1.3.7 c) ec. (49) Laushey y Láminas 04–05; HDS-5 §3.1.6 (velocidad de salida) y §5.x (scour, referencia a HEC-14); HEC-14 (hec14.pdf, ya en Normas): cap. 10 (riprap aprons y riprap basins), cap. 4–5 (velocidad de salida y disipadores internos), cap. 3 (socavación a la salida); cada fórmula transcrita con página verificada.

1. Salida: conserva Laushey (d50) y añade: Froude a la salida; longitud y d50 del apron por HEC-14 cap. 10 (Froude a la salida, TW/D), con la Lámina 05 del MTC como contraste; espesor 1.5–2.0·d50 [C/A]; filtro (geotextil o granular) como requisito declarado [N] de EG-2013 si lo trae, o [A]; velocidad admisible del cauce receptor (manual MTC Tabla 11 por tipo de terreno, entrada [S] tipo_terreno_receptor) con aviso cuando V_salida la supera y cálculo del d50 solo entonces.

2. Entrada: protección de taludes del terraplén y zampeado/caja según tipo de embocadura (T-7a); emboquillado de piedra como [A] de catálogo con cita a las Láminas.

3. Socavación local a la salida (HEC-14 cap. 3, método de la hoya de socavación) como estimación para la profundidad de desplante del cabezal (T-7a punto 2); el dato externo "profundidad de socavación estimada" gana si viene.

4. M6 pasa a llamarse de verdad "protección de entrada y salida"; todas las magnitudes con PasoDeMemoria y fórmula sustituida.

Ritual de cierre.
```

### T-9 · Espaciamiento de alivios con L hidráulico calculado (después de T-1; paralelo con T-7)

```text
Ejecuta únicamente T-9 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-5.1.11 (M10 no puede fallar) e INF-3.3 "espaciamiento". Fuentes: manual MTC 4.1.2.1 (cunetas: sección típica, Tabla de dimensiones mínimas, longitud máxima 250/200 m d), velocidad admisible por revestimiento Tabla 10/11, ec. 47 Manning), §3.12.2 (racional para el área tributaria de plataforma y talud), DG-2018 (sección típica: anchos de calzada, berma, talud de corte).

1. L_hidraulico deja de ser dato externo obligatorio: M10 lo calcula como la longitud de cuneta a partir de la cual el caudal acumulado (racional con C de la Tabla 08, I de T-1 para TR 35 años y tc de la cuneta, área = L·(ancho tributario)) supera la capacidad de la cuneta (Manning con la sección de la cuneta y pendiente longitudinal de la rasante) o la velocidad admisible. Entradas: sección de cuneta (dimensiones y revestimiento, [A] de sección típica con ventana), ancho tributario (dato externo de la sección típica), pendiente longitudinal (del perfil; si no, dato externo). Si falta algo, DatoFaltanteError con nombre; el dato externo L_hidraulico_m sigue aceptándose y gana si viene.

2. Verificación: espaciamiento adoptado entre alivios (dato: progresivas de las obras B del CSV) ≤ min(L_normativo, L_hidráulico); ahora sí puede fallar y lo dice por tramo.

3. Memoria: pasos con fórmula sustituida para Q de cuneta, capacidad y L.

Ritual de cierre.
```

### T-10 · Memoria M11 completa (después de T-1 … T-9)

```text
Ejecuta únicamente T-10 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.4 "memoria", INF-4.7 e INF-5.1.9. M11 no calcula (test AST): solo imprime lo que los módulos emiten.

1. Secciones nuevas en src/plantillas/memoria_alcantarillas.html y M11: hidrología por punto (T-1), Fase 8 estructural por material (T-5), Fase 9 cabezal por punto (geometría, aleros, tabla estática/sísmica con cargas, brazos, momentos, e, q, FS o φR vs ΣγQ, armado), protección (T-8), espaciamiento (T-9). Todo con PasoDeMemoria y fórmula sustituida; nada como frase suelta (L, caída, cota de salida, G2, V4b, V6, V9 ganan paso).

2. Unifica lo que CLI/JSON imprimen y el HTML no (cadena sísmica).

3. Regenera docs/indice_formulas.md con una corrida que SÍ dimensione los cuatro puntos del fixture (con datos externos del fixture claramente marcados como tales) para que V7, VC1, Laushey, control gobernante y las fórmulas nuevas aparezcan con cita correcta.

4. Anexo de la memoria "criterios adoptados [A] y su sensibilidad" por punto (ya existe el barrido PF-3): asegúrate de que todo [A] nuevo de T-1 … T-9 tiene ventana y aparece.

5. Longitud de la memoria: mantén el objetivo de EXT-8 (< 15 KB / 10 páginas por punto) o documenta por qué no.

Ritual de cierre.
```

### T-11 · Validación integral de las tres familias (después de T-10)

```text
Ejecuta únicamente T-11 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes.

1. Corrida de punta a punta, --alcance expediente, de tests/ejemplo_puntos.csv con un conjunto de datos externos de prueba NUEVO en tests/fixtures/ (claramente titulado "DATOS DE PRUEBA, NO DEL PROYECTO", con todos los [S] y entradas opcionales llenos con valores plausibles). Las tres familias deben llegar a Fase 11 con diseño (A y B circular; C marco) o con un bloqueo cuya causa sea una ENTRADA faltante, nunca un criterio vacío ni un NotImplementedError/AssertionError. Lista exacta de lo que sigue requiriendo entrada del proyecto.

2. Validación externa: tabla de comparación HDS-5 (ejemplos publicados, T-2) y, si HY-8 está disponible en el entorno, una corrida por punto; si no, deja el procedimiento escrito en docs/validacion_hy8.md para que el autor lo corra.

3. Sensibilidad: barrido (PF-3) de los [A] que gobiernan el diámetro (HW_D_max, borde_libre_bajo_tw_ahogante, seccion_receptor, v_max_*) y el cabezal (kh reducción, γ_EQ, δ) sobre el fixture; anexo de resultados en docs/.

4. Censo final: ningún criterio de perfil con valor None salvo los que dependen de entradas del proyecto (lista con nombre y entrada que los destraba); ninguna función en M9.FUNCIONES_SIN_CONSUMIDOR que T-7 debía consumir; ningún AssertionError("inalcanzable") en M8/M9.

5. Actualiza docs/linea_base.md y CLAUDE.md (tabla de entornos y conteo de tests).

Ritual de cierre.
```

### T-12 · Repositorio listo para sustentación (último)

```text
Ejecuta únicamente T-12 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-5.2. Sin cambios de cálculo.

1. Normas: retira los PDF de normas/ del repo de la app y deja el enlace al repo Normas que T-0 definió (submodule o NORMAS_DIR); recomienda en README que Normas sea privado por el copyright de AASHTO/ASTM. verificar_sesion.py y src/normativa/fuentes.py deben seguir encontrando los PDF.

2. Segrega el material de proceso con IA a una carpeta ignorada por el entregable (p. ej. proceso/) o a una rama: .claude/agents/, docs/planes_mejora/*.md (incluida esta cadena), docs/auditorias/, la bitácora de incidentes de entorno de CLAUDE.md (deja en CLAUDE.md solo las reglas técnicas), verificar_sesion.py si solo sirve al proceso. Nada se borra del historial; se mueve.

3. Fixtures: cabecera de advertencia en tests/fixtures/datos_referenciales_prueba*.md, entradas_ampliadas.json y en las memorias HTML de tests/linea_base_familia_c/ ("FIXTURE DE PRUEBA, NO ES UN RESULTADO DEL PROYECTO", visible al abrirlas).

4. LICENSE (elige con el autor; por defecto MIT sobre el código, con nota de que los PDF de normas no se licencian), pyproject.toml con dependencias fijadas, README de usuario (instalación, entradas, corrida, salidas) separado del README de proceso.

5. docs/manifiesto_registro_normativo.md: estado final de las 20 fuentes presentes en Normas (incluidas HEC-14 y WSDOT) y de las que sigan citadas sin PDF.

Ritual de cierre.
```

---

## 5. Lo que seguirá dependiendo del proyecto (no de la app) al terminar la cadena

- Series de lluvia SENAMHI y su tratamiento FEN (T-1 las consume; no las trae).
- Caudal y sección de drenes y canales receptores (ANA / Junta de Usuarios): tailwater real y Familia C.
- EMS: φ, c, γ, q_adm, NF, SPT, Vs30, ensayos químicos de suelo y agua (durabilidad, cabezal).
- Topografía: cotas, esviaje, fondo de entrada, sección del receptor (este script QGIS cubre la mayor parte).
- Sección típica de la vía y perfil de rasante (DG-2018), ancho de derecho de vía (V5).
- Decisiones del Propietario: riesgo admisible, desplazamiento sísmico admisible del cabezal, tipo de cabezal.

Con la cadena completa la app deja de bloquearse por criterios vacíos y pasa a bloquearse solo por entradas que faltan, que es lo que un jurado acepta: "este dato lo da el estudio X".
