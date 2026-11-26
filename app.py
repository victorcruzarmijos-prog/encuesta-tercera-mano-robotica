import json
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN GENERAL DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Brazo Robótico Asistente de Soldadura | Diseño de Máquinas EPN",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CONEXIÓN CON GOOGLE SHEETS Y APPS SCRIPT
# ==============================================================================
# PEGA AQUÍ TU ENLACE DE APPS SCRIPT QUE TERMINA EN /exec (ENTRE COMILLAS):
URL_APPS_SCRIPT = "PEGA_AQUI_TU_URL_QUE_TERMINA_EN_EXEC"
ID_HOJA = "1vn_id57bRE3l3dTh_ScTknJpTW3HDjmUnIA7tc4BX6M"
NOMBRE_HOJA = "Datos_Limpios"
URL_CSV_HOJA = (
    f"https://docs.google.com/spreadsheets/d/{ID_HOJA}"
    f"/gviz/tq?tqx=out:csv&sheet={NOMBRE_HOJA}"
)

# ==============================================================================
# 3. DATOS OFICIALES DEL PROYECTO Y EQUIPO (GR1S4 · EPN)
# ==============================================================================
EQUIPO = [
    {
        "nombre": "Stalin Alexander Boada Guacollante",
        "carrera": "Ingeniería Mecatrónica · EPN (GR1S4)",
        "rol": "Planteamiento, Ciclo de Vida Comercial y Modelo OpenLCA",
        "capitulo": "Capítulo 1 · Secciones 1.1 a 1.7",
        "icono": "🌱",
    },
    {
        "nombre": "Victor Cruz",
        "carrera": "Ingeniería Mecatrónica · EPN (GR1S4)",
        "rol": "Encuesta Python/Streamlit, Analítica Real e IA de Bocetos",
        "capitulo": "Cap. 2 (2.1–2.5) y Cap. 3 (3.7–3.8)",
        "icono": "💻",
    },
    {
        "nombre": "Maverick Cadena",
        "carrera": "Ingeniería Mecatrónica · EPN (GR1S4)",
        "rol": "Tres Casas de Calidad (QFD), Competidores y Trazabilidad",
        "capitulo": "Capítulo 2 · Secciones 2.6 a 2.9",
        "icono": "📐",
    },
    {
        "nombre": "Alan Villamarín",
        "carrera": "Ingeniería Mecatrónica · EPN (GR1S4)",
        "rol": "Análisis Funcional, Módulos, Matriz Morfológica y Selección",
        "capitulo": "Capítulo 3 · Secciones 3.1 a 3.6 y 3.9",
        "icono": "⚙️",
    },
]

PALETA = [
    "#1d4ed8", "#0284c7", "#0d9488", "#2563eb",
    "#7c3aed", "#d97706", "#059669", "#dc2626",
]

# Datos oficiales del Cap. 1 (Ciclo de vida y OpenLCA)
CICLO_VIDA_DF = pd.DataFrame(
    [
        ("T1", 1, "Desarrollo", 0, "Diseño conceptual del producto"),
        ("T2", 1, "Desarrollo", 0, "Diseño CAD, cálculos y selección de componentes"),
        ("T3", 1, "Introducción", 15, "Fabricación del prototipo, programación e integración"),
        ("T4", 1, "Introducción", 32, "Pruebas finales, lanzamiento y primeras ventas"),
        ("T5", 2, "Crecimiento", 55, "Captación de clientes y aumento de ventas"),
        ("T6", 2, "Crecimiento", 76, "Mejoras técnicas y expansión comercial"),
        ("T7", 2, "Crecimiento", 92, "Incremento de producción y recuperación"),
        ("T8", 2, "Madurez", 98, "Consolidación del producto en el mercado"),
        ("T9", 3, "Madurez", 100, "Ventas elevadas y relativamente estables"),
        ("T10", 3, "Madurez", 94, "Optimización de costos y mantenimiento"),
        ("T11", 3, "Declinación", 68, "Reducción gradual de la demanda"),
        ("T12", 3, "Declinación", 40, "Evaluación de actualización o reemplazo"),
    ],
    columns=["Trimestre", "Año", "Etapa", "Nivel relativo de ventas", "Actividad principal"],
)

OPENLCA_INV_DF = pd.DataFrame(
    [
        ("PET / PETG (estructura 3D)", "Polímeros", 0.440),
        ("Acero laminado en caliente", "Metales y conductores", 0.200),
        ("Polipropileno (PP)", "Polímeros", 0.100),
        ("Alambre de cobre", "Metales y conductores", 0.065),
        ("ABS", "Polímeros", 0.045),
        ("Plomo (aprox. aporte)", "Metales y conductores", 0.045),
        ("Poliamida PA 6", "Polímeros", 0.025),
        ("Lámina de aluminio", "Metales y conductores", 0.015),
        ("Resina PVC", "Polímeros", 0.015),
        ("Fibra de vidrio continua", "Compuestos / otros", 0.008),
    ],
    columns=["Material", "Categoría", "Masa (kg)"],
)

# Datos oficiales del Cap. 2 (Tres Casas QFD y Análisis Competitivo)
NECESIDADES_QFD_DF = pd.DataFrame(
    [
        (1, "Tiempo de soldadura", 25, 5, 5, 4, 3),
        (2, "Precisión del punto de soldadura", 20, 4, 5, 4, 3),
        (3, "Estabilidad de la PCB", 15, 5, 4, 5, 2),
        (4, "Cantidad adecuada de inyección", 12, 4, 5, 3, 2),
        (5, "Seguridad operativa", 10, 3, 3, 3, 4),
        (6, "Evitar daños a los componentes", 7, 4, 4, 5, 2),
        (7, "Disminución de costos", 6, 3, 4, 4, 3),
        (8, "Ergonomía", 3, 4, 5, 5, 3),
        (9, "Calidad de las uniones soldadas", 1, 5, 5, 5, 2),
        (10, "Funcionamiento confiable y repetible", 1, 5, 3, 2, 5),
    ],
    columns=["N°", "Necesidad", "Importancia (%)", "Diseño Propio", "Apollo Seko", "Japan Unix", "Quick Soldering"],
)

CASA1_DF = pd.DataFrame(
    [
        ("Resolución de avance de estaño", 297, 13.2, "0,01 mm"),
        ("Tiempo promedio de soldadura por punto", 238, 10.6, "≤ 10 s/punto"),
        ("Temperatura de la punta", 225, 10.0, "380 °C"),
        ("Desplazamiento de la PCB", 198, 8.8, "≤ 0,5°"),
        ("Tasa de procesamiento visual", 189, 8.4, "≥ 30 fps"),
        ("Diámetro de la punta", 189, 8.4, "0,9 mm"),
        ("Espesor de la punta", 189, 8.4, "1,5 mm"),
        ("Velocidad de retracción", 183, 8.1, "25 mm/s"),
        ("Sistema de enfriamiento", 153, 6.8, "3 CFM"),
        ("Distancia operador–máquina", 117, 5.2, "≥ 0,4 m"),
        ("Tipo de corriente", 111, 4.9, "12 V DC"),
        ("Intervenciones manuales por unión", 94, 4.2, "≤ 1 interv./unión"),
        ("Costos de fabricación", 54, 2.4, "USD 100"),
        ("Tipo de control automático", 12, 0.5, "PID visual"),
    ],
    columns=["Característica técnica", "Peso abs.", "Peso rel. (%)", "Valor objetivo"],
)

CASA2_DF = pd.DataFrame(
    [
        ("Tipo de punta (referencia externa)", 262.9, 14.9, "1,5 mm"),
        ("Tipo de motor de paso", 245.4, 13.9, "30"),
        ("Tipo de controlador", 197.3, 11.2, "240"),
        ("Calidad de impresión", 169.3, 9.6, "0,16 mm"),
        ("Tipos de ventiladores", 158.5, 9.0, "3 CFM"),
        ("Corriente continua", 141.7, 8.0, "12 V DC"),
        ("Tipo de cámara", 121.7, 6.9, "640×480"),
        ("Programación con IA", 118.1, 6.7, "60"),
        ("Calidad de los soportes", 113.4, 6.4, "0,6"),
        ("Velocidad del brazo", 96.8, 5.5, "90"),
        ("Tamaño de brazo", 68.4, 3.9, "300"),
        ("Tipo de servomotores", 53.4, 3.0, "AC/DC"),
        ("Tipos de filamento", 21.6, 1.2, "PETG"),
    ],
    columns=["Componente / subsistema", "Peso abs.", "Peso rel. (%)", "Objetivo"],
)

CASA3_DF = pd.DataFrame(
    [
        ("Error de localización de la punta", 221.9, 15.6),
        ("Capacidad de procesamiento del controlador", 193.8, 13.6),
        ("Longitud de las piezas", 148.1, 10.4),
        ("Motor paso a paso PM", 124.9, 8.8),
        ("Caudal de extracción de humos", 104.7, 7.3),
        ("Resistencia mecánica de los soportes", 101.7, 7.1),
        ("Servomotor DC (contingencia)", 99.3, 7.0),
        ("Filamento PETG", 97.1, 6.8),
        ("Torque de los servomotores", 96.5, 6.8),
        ("Espesor de los soportes", 89.4, 6.3),
        ("Altura de capa (impresión 3D)", 86.2, 6.0),
        ("Cámara Web USB de alta velocidad", 61.9, 4.3),
    ],
    columns=["Parámetro de diseño", "Peso abs.", "Peso rel. (%)"],
)

# Datos oficiales del Cap. 3 (Módulos, Interfaces y Alternativas)
MODULOS_LIST = [
    ("M1", "Visión artificial", "F1", "Cámara web USB de alta velocidad, soporte elevado e iluminación", "≥ 30 fps · 640×480"),
    ("M2", "Procesamiento y control", "F2, F3, F8", "Computador/Raspberry Pi + microcontrolador, control PID visual y límites virtuales", "≤ 10 s/punto · PID"),
    ("M3", "Posicionamiento robótico", "F4, F9", "Brazo con motores a paso PM, estructura y soporte de PCB en PETG impreso", "PCB ≤ 0,5° · capa 0,16 mm"),
    ("M4", "Extrusión de estaño", "F5", "Motor a paso con rodillos moleteados, guía PTFE y boquilla cónica", "Avance 0,01 mm · 25 mm/s"),
    ("M5", "Alimentación eléctrica", "F7, F10", "Fuente 12 V DC, convertidores, protecciones y ventilador extractor", "12 V DC · 3 CFM"),
    ("M6", "Seguridad e interfaz", "F6", "Gesto de palma abierta, paro físico de emergencia y paro por pérdida visual", "≥ 0,4 m · ≤ 1 interv."),
]

INTERFACES_DF = pd.DataFrame(
    [
        ("I1", "M1 ↔ M2", "Información", "Imagen y coordenadas detectadas (USB, 640×480)", "Latencia, ≥ 30 fps y error de localización"),
        ("I2", "M2 → M3", "Control", "Órdenes de posición y trayectoria del brazo", "Error de posicionamiento y repetibilidad"),
        ("I3", "M2 → M4", "Control", "Activación y velocidad de extrusión de estaño", "Sincronización y resolución de 0,01 mm"),
        ("I4", "M3 ↔ M4", "Mecánica", "Unión física, posición y orientación del extrusor", "Rigidez, alineación y cero interferencias"),
        ("I5", "M5 → M1–M4, M6", "Energía", "Bus de potencia 12 V DC y protecciones", "Separación potencia/señal y verificación eléctrica"),
        ("I6", "M6 ↔ M2", "Seguridad", "Inicio, habilitación y parada de emergencia", "Ensayo de respuesta ante paro y fallos"),
    ],
    columns=["ID", "Módulos", "Tipo", "Intercambio", "Criterio de verificación"],
)

ALTERNATIVAS_DF = pd.DataFrame(
    [
        ("Accionamiento", "Motor paso a paso PM", "Servomotor DC con encoder", "Actuador lineal neumático"),
        ("Visión", "Cámara web USB de alta velocidad", "Sistema de visión industrial", "Visión industrial"),
        ("Alimentación de estaño", "Motor paso a paso con rodillos", "Motorreductor DC con rodillos", "No definida"),
        ("Salida de estaño", "Guía PTFE y boquilla cónica", "Guía metálica y boquilla biselada", "Guía metálica"),
        ("Estructura / límites", "PETG impreso 3D y límites por software", "Perfiles de aluminio y finales de carrera", "Estructura impresa"),
        ("Seguridad", "Palma abierta + paro + pérdida visual", "Paro de emergencia + pérdida visual", "No definida"),
        ("Estado", "SELECCIONADA (4,75 / 5)", "Alternativa robusta (3,45 / 5)", "DESCARTADA (filtro compatibilidad)"),
    ],
    columns=["Subfunción", "Alternativa A · QFD (Elegida)", "Alternativa B · Industrial", "Alternativa C · Neumática"],
)

# ==============================================================================
# 4. ESTILOS WEB (ADAPTABLES A MODO CLARO Y MODO OSCURO)
# ==============================================================================
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background: transparent;}

    .block-container {
        max-width: 1240px;
        padding-top: 2.6rem;
        padding-bottom: 3rem;
    }

    /* Portada principal */
    .hero-box {
        background: linear-gradient(135deg, #0b1f3a 0%, #163a70 54%, #0284c7 100%);
        color: #ffffff;
        padding: 2.2rem 2.4rem;
        border-radius: 18px;
        margin-bottom: 1.4rem;
        box-shadow: 0 12px 28px rgba(11, 31, 58, 0.24);
        border: 1px solid rgba(255, 255, 255, 0.14);
    }
    .hero-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.28);
        color: #e0f2fe;
        padding: 0.28rem 0.9rem;
        border-radius: 999px;
        font-size: 0.79rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 0.75rem;
    }
    .hero-box h1 {
        color: #ffffff !important;
        font-size: 2.08rem;
        font-weight: 800;
        margin: 0 0 0.55rem 0;
        line-height: 1.2;
    }
    .hero-box p {
        color: #e2e8f0 !important;
        font-size: 1.0rem;
        margin: 0 0 1.15rem 0;
        max-width: 900px;
        line-height: 1.55;
    }
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
    }
    .badge-item {
        background: rgba(15, 23, 42, 0.42);
        border: 1px solid rgba(255, 255, 255, 0.16);
        color: #f8fafc;
        padding: 0.36rem 0.85rem;
        border-radius: 10px;
        font-size: 0.84rem;
        font-weight: 500;
    }

    /* Tarjetas de indicadores KPI */
    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-left: 4px solid #0284c7;
        padding: 0.95rem 1.1rem;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.06);
    }

    /* Tarjetas informativas */
    .info-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 14px;
        padding: 1.25rem 1.35rem;
        height: 100%;
        margin-bottom: 0.9rem;
    }
    .info-card h4 {
        margin: 0 0 0.45rem 0;
        color: #38bdf8;
        font-size: 1.04rem;
        font-weight: 700;
    }
    .info-card p {
        margin: 0;
        font-size: 0.91rem;
        line-height: 1.5;
        opacity: 0.92;
    }

    /* Tarjetas del equipo */
    .team-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-top: 4px solid #1d4ed8;
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        height: 100%;
        margin-bottom: 0.8rem;
    }
    .team-icon {font-size: 1.6rem; margin-bottom: 0.3rem;}
    .team-name {font-size: 1.0rem; font-weight: 700; margin-bottom: 0.15rem;}
    .team-major {font-size: 0.79rem; color: #38bdf8; font-weight: 600; margin-bottom: 0.35rem;}
    .team-role {font-size: 0.86rem; opacity: 0.88; margin-bottom: 0.5rem; line-height: 1.4;}
    .team-cap {
        display: inline-block;
        background: rgba(2, 132, 199, 0.16);
        color: #38bdf8;
        padding: 0.2rem 0.6rem;
        border-radius: 8px;
        font-size: 0.76rem;
        font-weight: 600;
    }

    /* Tarjetas de módulos M1-M6 */
    .mod-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-left: 4px solid #0d9488;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        height: 100%;
        margin-bottom: 0.8rem;
    }
    .mod-head {font-size: 0.98rem; font-weight: 700; color: #38bdf8; margin-bottom: 0.25rem;}
    .mod-fn {font-size: 0.78rem; font-weight: 600; opacity: 0.8; margin-bottom: 0.35rem;}
    .mod-body {font-size: 0.87rem; line-height: 1.45; margin-bottom: 0.45rem;}
    .mod-meta {
        display: inline-block;
        background: rgba(13, 148, 136, 0.16);
        color: #2dd4bf;
        padding: 0.18rem 0.55rem;
        border-radius: 8px;
        font-size: 0.76rem;
        font-weight: 600;
    }

    /* Cadena de trazabilidad */
    .flow-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.7rem;
        margin: 0.8rem 0 1.2rem 0;
    }
    .flow-step {
        background: var(--secondary-background-color);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 0.85rem 0.9rem;
        text-align: center;
    }
    .flow-num {
        display: inline-block;
        background: #1d4ed8;
        color: #ffffff;
        width: 26px;
        height: 26px;
        line-height: 26px;
        border-radius: 50%;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .flow-title {font-size: 0.88rem; font-weight: 700; margin-bottom: 0.2rem;}
    .flow-desc {font-size: 0.78rem; opacity: 0.84;}

    /* Pestañas estilo menú web */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.45rem;
        border-bottom: 2px solid rgba(148, 163, 184, 0.22);
        padding-bottom: 0.35rem;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 0.55rem 1.0rem;
        font-weight: 600;
        font-size: 0.90rem;
    }

    /* Botón principal de envío */
    .stFormSubmitButton button {
        background: linear-gradient(90deg, #1d4ed8 0%, #0284c7 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        width: 100%;
    }
    .stFormSubmitButton button:hover {
        opacity: 0.92;
        color: #ffffff;
    }

    .footer-web {
        margin-top: 2.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(148, 163, 184, 0.25);
        text-align: center;
        font-size: 0.84rem;
        opacity: 0.78;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# 5. FUNCIONES DE CARGA, LIMPIEZA Y ESTADÍSTICA AUTOMÁTICA
# ==============================================================================
@st.cache_data(ttl=60)
def cargar_datos(url_csv: str) -> pd.DataFrame:
    df = pd.read_csv(url_csv)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").reset_index(drop=True)
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lstrip("•·-* ")
            .str.strip()
        )
        df.loc[df[col].isin(["nan", "None", ""]), col] = np.nan
    return df


def es_columna_id_o_fecha(nombre: str) -> bool:
    low = nombre.lower().strip()
    if any(
        k in low
        for k in [
            "fecha",
            "marca temporal",
            "timestamp",
            "hora",
            "n° personas",
            "nº personas",
            "personas",
            "id_participante",
        ]
    ):
        return True
    return bool(re.search(r"\bid\b", low))


def es_columna_comentario(nombre: str, serie: pd.Series) -> bool:
    low = nombre.lower()
    if any(k in low for k in ["comentario", "sugerencia", "observaci", "adicional", "opinion"]):
        return True
    validos = serie.dropna().astype(str)
    if len(validos) == 0:
        return False
    return validos.nunique() > max(18, len(validos) * 0.45) and validos.str.len().mean() > 28


def extraer_serie_numerica(serie: pd.Series) -> pd.Series:
    directa = pd.to_numeric(serie, errors="coerce")
    if len(serie.dropna()) > 0 and directa.notna().mean() >= 0.70:
        return directa
    validos = serie.dropna().astype(str)
    if len(validos) == 0:
        return pd.Series(np.nan, index=serie.index, dtype=float)
    if validos.str.contains(r"\ba\b|\bmm\b|\bminuto", case=False, regex=True).mean() > 0.30:
        return pd.Series(np.nan, index=serie.index, dtype=float)
    extraida = validos.str.extract(r"(\d+(?:\.\d+)?)")[0]
    nums = pd.to_numeric(extraida, errors="coerce")
    if nums.notna().mean() >= 0.75:
        out = pd.Series(np.nan, index=serie.index, dtype=float)
        out.loc[nums.index] = nums
        return out
    return pd.Series(np.nan, index=serie.index, dtype=float)


def clasificar_columnas(df: pd.DataFrame) -> dict:
    fecha_cols, comentario_cols, categoricas = [], [], []
    numericas = {}

    for col in df.columns:
        if es_columna_id_o_fecha(col):
            fecha_cols.append(col)
            continue
        if es_columna_comentario(col, df[col]):
            comentario_cols.append(col)
            continue

        nums = extraer_serie_numerica(df[col])
        validos = nums.dropna()
        if len(validos) > 0 and validos.nunique() >= 2:
            numericas[col] = nums
            if validos.nunique() <= 10:
                categoricas.append(col)
        elif df[col].dropna().nunique() >= 1:
            categoricas.append(col)

    col_frustracion = None
    for col in numericas:
        if any(k in col.lower() for k in ["frustr", "dificult", "escala", "molest", "calific", "problema"]):
            col_frustracion = col
            break
    if col_frustracion is None and numericas:
        col_frustracion = next(iter(numericas.keys()))

    col_perfil = None
    for col in categoricas:
        if any(k in col.lower() for k in ["experiencia", "perfil", "nivel", "rol", "ocupaci"]):
            col_perfil = col
            break
    if col_perfil is None and categoricas:
        col_perfil = categoricas[0]

    return {
        "fecha": fecha_cols,
        "comentarios": comentario_cols,
        "numericas": numericas,
        "categoricas": categoricas,
        "frustracion": col_frustracion,
        "perfil": col_perfil,
    }


def acortar_etiqueta(texto: str, max_len: int = 38) -> str:
    t = str(texto)
    return t if len(t) <= max_len else t[: max_len - 1].rstrip() + "…"


def tabla_frecuencias(serie: pd.Series) -> pd.DataFrame:
    limpia = serie.dropna().astype(str)
    conteo = limpia.value_counts()
    total = int(conteo.sum())
    if total == 0:
        return pd.DataFrame(
            columns=["Categoría", "Etiqueta corta", "Frecuencia", "Porcentaje (%)", "Acumulado (%)", "Texto"]
        )
    pct = (conteo / total * 100).round(2)
    acum = pct.cumsum().round(2).clip(upper=100.0)
    res = pd.DataFrame(
        {
            "Categoría": conteo.index,
            "Etiqueta corta": [acortar_etiqueta(x) for x in conteo.index],
            "Frecuencia": conteo.values,
            "Porcentaje (%)": pct.values,
            "Acumulado (%)": acum.values,
        }
    )
    res["Texto"] = res.apply(
        lambda r: f"{int(r['Frecuencia'])} ({r['Porcentaje (%)']:.1f}%)", axis=1
    )
    return res


def construir_resumen_qfd(df: pd.DataFrame, cols_cat: list) -> pd.DataFrame:
    filas = []
    for col in cols_cat:
        tf = tabla_frecuencias(df[col])
        if tf.empty:
            continue
        top = tf.iloc[0]
        pct = float(top["Porcentaje (%)"])
        peso_qfd = round(1.0 + (pct / 100.0) * 4.0, 2)
        prioridad = "Alta" if pct >= 50 else ("Media" if pct >= 35 else "Moderada")
        filas.append(
            {
                "Dimensión / Pregunta": acortar_etiqueta(col, 55),
                "Preferencia dominante": str(top["Categoría"]),
                "Respuestas (n)": int(top["Frecuencia"]),
                "Consenso (%)": round(pct, 1),
                "Peso encuestas (1–5)": peso_qfd,
                "Prioridad": prioridad,
            }
        )
    res = pd.DataFrame(filas)
    if not res.empty:
        res = res.sort_values("Consenso (%)", ascending=False).reset_index(drop=True)
    return res


def estilizar_figura(fig: go.Figure, altura: int = 390) -> go.Figure:
    fig.update_layout(
        height=altura,
        margin=dict(l=15, r=15, t=48, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
    )
    return fig


# ==============================================================================
# 6. CARGA DE DATOS REALES Y BARRA LATERAL INTERACTIVA
# ==============================================================================
error_carga = None
try:
    df_original = cargar_datos(URL_CSV_HOJA)
except Exception as err:
    df_original = pd.DataFrame()
    error_carga = str(err)

meta = clasificar_columnas(df_original) if not df_original.empty else {
    "fecha": [], "comentarios": [], "numericas": {}, "categoricas": [],
    "frustracion": None, "perfil": None,
}

with st.sidebar:
    st.markdown("## 🎛️ Panel de control")
    st.caption("Facultad de Ingeniería Mecánica · EPN · GR1S4")

    if not df_original.empty and meta["perfil"]:
        st.subheader("Filtro de muestra real")
        opciones_perfil = sorted(df_original[meta["perfil"]].dropna().astype(str).unique().tolist())
        seleccion_perfil = st.multiselect(
            f"Filtrar por:\n{acortar_etiqueta(meta['perfil'], 48)}",
            options=opciones_perfil,
            default=opciones_perfil,
        )
        if seleccion_perfil:
            df_filtrado = df_original[df_original[meta["perfil"]].astype(str).isin(seleccion_perfil)].copy()
        else:
            df_filtrado = df_original.copy()
    else:
        df_filtrado = df_original.copy()

    st.divider()
    st.subheader("Visualización de encuestas")
    tipo_grafico = st.radio(
        "Estilo principal en analítica:",
        ["Dona + Barras (%)", "Solo Dona (%)", "Solo Barras horizontales (%)"],
        index=0,
    )
    umbral_consenso = st.slider(
        "Umbral de consenso alto (%)",
        min_value=30,
        max_value=75,
        value=50,
        step=5,
        help="Clasifica las preferencias dominantes de la encuesta según el porcentaje de acuerdo.",
    )

    st.divider()
    if st.button("🔄 Actualizar datos en vivo", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "Respuestas reales anonimizadas conectadas a Google Sheets + "
        "resultados trazables de los Capítulos 1, 2 y 3 (Fase 1)."
    )

meta_f = clasificar_columnas(df_filtrado) if not df_filtrado.empty else meta

# ==============================================================================
# 7. PORTADA PRINCIPAL + INDICADORES KPI SUPERIORES
# ==============================================================================
st.markdown(
    """
<div class="hero-box">
    <div class="hero-pill">ESCUELA POLITÉCNICA NACIONAL · FACULTAD DE INGENIERÍA MECÁNICA · GR1S4</div>
    <h1>Brazo Robótico Asistente de Soldadura de Placas PCB</h1>
    <p>
        Plataforma interactiva de la Primera Fase del Proyecto Integrador de Diseño de Máquinas:
        integra nuestra encuesta pública en vivo, análisis estadístico con porcentajes, ciclo de vida
        preliminar (OpenLCA), tres Casas de Calidad (QFD) y selección conceptual modular.
    </p>
    <div class="badge-row">
        <span class="badge-item">🤖 Visión Artificial + Extrusor 0,01 mm</span>
        <span class="badge-item">💵 Costo objetivo: USD 100</span>
        <span class="badge-item">🔒 Datos 100 % Anonimizados</span>
        <span class="badge-item">🏆 Concepto Elegido: Alternativa A (4,75/5)</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
total_muestra = len(df_original)
total_filtrado = len(df_filtrado)

k1.metric(
    "Respuestas reales",
    f"{total_filtrado:,}",
    delta=f"de {total_muestra:,} registradas" if total_filtrado != total_muestra else "100 % de la muestra",
)

if meta_f["frustracion"] and meta_f["frustracion"] in meta_f["numericas"]:
    serie_num = meta_f["numericas"][meta_f["frustracion"]].dropna()
    escala_max = int(max(5, round(serie_num.max()))) if len(serie_num) > 0 else 5
    prom = float(serie_num.mean()) if len(serie_num) > 0 else 0.0
    desv = float(serie_num.std()) if len(serie_num) > 1 else 0.0
    mediana = float(serie_num.median()) if len(serie_num) > 0 else 0.0
    k2.metric("Frustración promedio", f"{prom:.2f} / {escala_max}", delta=f"Mediana: {mediana:.1f} · s={desv:.2f}")
else:
    k2.metric("Preguntas evaluadas", f"{len(meta_f['categoricas'])}")

k3.metric("Puntaje competitivo QFD", "4,26 / 5", delta="2.º lugar (Apollo Seko: 4,50)")
k4.metric("Concepto ganador (Cap. 3)", "Alternativa A", delta="4,75 vs 3,45 (Alt. B)")

if error_carga:
    st.error(
        "No se pudo conectar con la hoja de cálculo. Verifica que esté compartida como Lector "
        f"y que la pestaña se llame exactamente '{NOMBRE_HOJA}'."
    )
    st.caption(f"Detalle técnico: {error_carga}")

# ==============================================================================
# 8. PESTAÑAS DE NAVEGACIÓN DE LA PÁGINA WEB
# ==============================================================================
tabs = st.tabs(
    [
        "🏠 1 · Quiénes somos y Cap. 1",
        "📝 2 · Responder Encuesta",
        "📊 3 · Gráficas y Porcentajes",
        "🔀 4 · Cruces y Mapa de Calor",
        "📐 5 · Tres Casas QFD",
        "⚙️ 6 · Módulos, Sensibilidad y Datos",
    ]
)

# ------------------------------------------------------------------------------
# PESTAÑA 1: QUIÉNES SOMOS, PLANTEAMIENTO, CICLO DE VIDA Y OPENLCA (CAP. 1)
# ------------------------------------------------------------------------------
with tabs[0]:
    st.subheader("¿Quiénes somos?")
    st.write(
        "Somos estudiantes de **Ingeniería Mecatrónica** de la **Facultad de Ingeniería Mecánica** "
        "de la **Escuela Politécnica Nacional (EPN)**, paralelo **GR1S4**. Esta plataforma digital "
        "respalda la **Primera Fase (Diseño Conceptual y Selección de Soluciones)** del proyecto "
        "**Brazo Robótico Asistente de Soldadura de Placas PCB**, garantizando trazabilidad completa "
        "desde los datos de usuarios hasta la configuración modular seleccionada."
    )

    cols_eq = st.columns(4)
    for col_ui, miembro in zip(cols_eq, EQUIPO):
        with col_ui:
            st.markdown(
                f"""
                <div class="team-card">
                    <div class="team-icon">{miembro['icono']}</div>
                    <div class="team-name">{miembro['nombre']}</div>
                    <div class="team-major">{miembro['carrera']}</div>
                    <div class="team-role">{miembro['rol']}</div>
                    <span class="team-cap">{miembro['capitulo']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("Planteamiento, alcance y exclusiones (Capítulo 1)")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="info-card">
                <h4>🎯 Objetivo general</h4>
                <p>Diseñar un brazo robótico asistente que detecte y siga la punta del cautín
                mediante visión artificial para posicionar un mecanismo extrusor capaz de
                suministrar alambre de estaño de forma controlada y coordinada con el operador.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="info-card">
                <h4>⚠️ Problema abordado</h4>
                <p>El operador usa ambas manos para manipular cautín y estaño, dificultando
                estabilizar la PCB. Esto genera errores de coordinación, dosificación irregular,
                mayor tiempo por punto, fatiga ergonómica y exposición a humos del fundente.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="info-card">
                <h4>🚧 Exclusiones claras (Fase 1)</h4>
                <p>El sistema <b>no regula la temperatura del cautín</b> ni sustituye al operador.
                Opera únicamente dentro de un área cuadrada definida; fuera de ella regresa a
                posición de control. El CAD definitivo y pruebas físicas pasan a la Fase 2.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Ruta de trazabilidad de la Fase 1")
    st.markdown(
        """
        <div class="flow-grid">
            <div class="flow-step"><div class="flow-num">1</div><div class="flow-title">Encuesta Real</div><div class="flow-desc">Datos anónimos en Python y Streamlit</div></div>
            <div class="flow-step"><div class="flow-num">2</div><div class="flow-title">Estadística</div><div class="flow-desc">Porcentajes, cruces y dispersión</div></div>
            <div class="flow-step"><div class="flow-num">3</div><div class="flow-title">3 Casas QFD</div><div class="flow-desc">14 req., 13 comp. y 12 parámetros</div></div>
            <div class="flow-step"><div class="flow-num">4</div><div class="flow-title">Módulos M1–M6</div><div class="flow-desc">10 funciones y 6 interfaces</div></div>
            <div class="flow-step"><div class="flow-num">5</div><div class="flow-title">Selección A vs B</div><div class="flow-desc">Matriz ponderada y sensibilidad</div></div>
            <div class="flow-step"><div class="flow-num">6</div><div class="flow-title">Boceto con IA</div><div class="flow-desc">Refinamiento iterativo validado</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("Ciclo de vida comercial (3 años) y análisis preliminar OpenLCA")
    cv1, cv2 = st.columns(2)
    with cv1:
        fig_cv = px.area(
            CICLO_VIDA_DF,
            x="Trimestre",
            y="Nivel relativo de ventas",
            markers=True,
            hover_data=["Año", "Etapa", "Actividad principal"],
            title="Curva conceptual del ciclo de vida (12 trimestres · 3 años)",
            color_discrete_sequence=["#1d4ed8"],
        )
        fig_cv.update_traces(line=dict(width=3), fillcolor="rgba(29, 78, 216, 0.16)")
        fig_cv.update_layout(yaxis_title="Nivel relativo (escala conceptual)", xaxis_title="Trimestre")
        st.plotly_chart(estilizar_figura(fig_cv, 360), width="stretch")

    with cv2:
        masa_total = float(OPENLCA_INV_DF["Masa (kg)"].sum())
        masa_pol = float(OPENLCA_INV_DF.loc[OPENLCA_INV_DF["Categoría"] == "Polímeros", "Masa (kg)"].sum())
        fig_lca = px.bar(
            OPENLCA_INV_DF.sort_values("Masa (kg)", ascending=True),
            x="Masa (kg)",
            y="Material",
            color="Categoría",
            orientation="h",
            text_auto=".3f",
            color_discrete_map={
                "Polímeros": "#0284c7",
                "Metales y conductores": "#1d4ed8",
                "Compuestos / otros": "#0d9488",
            },
            title=f"Inventario preliminar OpenLCA (1 unidad · {masa_total:.3f} kg)",
        )
        fig_lca.update_traces(textposition="outside")
        fig_lca.update_layout(xaxis_range=[0, 0.54], yaxis_title="")
        st.plotly_chart(estilizar_figura(fig_lca, 360), width="stretch")

    st.info(
        f"**Resumen ambiental preliminar (OpenLCA):** Unidad funcional de 1 brazo robótico "
        f"(masa estimada: {masa_total:.3f} kg; polímeros: {masa_pol / masa_total * 100:.1f} %). "
        "Incluye 0,05 kWh de electricidad inicial y 0,24 t·km de transporte. Las emisiones preliminares "
        "de CO₂ contabilizadas ascienden a **1,263 kg** (100 % aguas arriba) y deberán actualizarse "
        "con las masas CAD definitivas en la segunda fase."
    )

# ------------------------------------------------------------------------------
# PESTAÑA 2: FORMULARIO PÚBLICO OPERATIVO (9 PREGUNTAS EXACTAS)
# ------------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Cuestionario público anónimo")
    st.write(
        "Tu participación toma menos de 2 minutos. No solicitamos nombres, correos ni "
        "identificadores personales; cada envío se incorpora directamente a la base anonimizada "
        "del estudio."
    )

    with st.form("formulario_tercera_mano", clear_on_submit=True):
        st.markdown("#### Sección 1 · Perfil y experiencia")
        a1, a2 = st.columns(2)
        frecuencia = a1.selectbox(
            "1. ¿Con qué frecuencia realizas trabajos de ensamble o soldadura de componentes electrónicos?",
            ["Diario", "Semanal", "Mensual", "Rara vez", "Nunca"],
        )
        experiencia = a2.selectbox(
            "2. ¿Cuál es tu nivel de experiencia soldando placas de circuito impreso (PCBs)?",
            ["Principiante", "Intermedio", "Avanzado"],
        )

        st.divider()
        st.markdown("#### Sección 2 · Validación del problema")
        frustracion = st.radio(
            "3. El ensamblaje manual resulta complejo por la necesidad de sostener simultáneamente la placa, el componente, el cautín y el estaño. En una escala del 1 al 5, ¿qué tan frustrante te resulta esto?",
            ["1 (Nada complicado)", "2", "3", "4", "5 (Muy frustrante)"],
            horizontal=True,
        )
        errores = st.selectbox(
            "4. ¿Con qué frecuencia experimentas uniones imprecisas, quemaduras o errores por no tener una mano libre extra?",
            ["Casi siempre", "Frecuentemente", "A veces", "Nunca"],
        )

        st.divider()
        st.markdown("#### Sección 3 · Requerimientos funcionales y estructurales")
        b1, b2 = st.columns(2)
        activacion = b1.selectbox(
            "5. Para activar la alimentación automática de estaño con la máquina, ¿qué método te resultaría más ergonómico?",
            [
                "Un pedal accionado con el pie",
                "Un comando gestual (ej. mover la mano de cierta forma)",
                "Un botón de proximidad en el escritorio",
            ],
        )
        longitud_estano = b2.selectbox(
            "6. ¿Qué longitud base de estaño consideras ideal que se empuje automáticamente para un punto de soldadura estándar?",
            [
                "1 a 3 mm",
                "4 a 6 mm",
                "Más de 6 mm",
                "Prefiero que sea ajustable por el usuario",
            ],
        )
        caracteristica_clave = st.selectbox(
            "7. Considerando el ambiente de soldadura, ¿qué característica valoras más en la estructura del equipo?",
            [
                "Estabilidad y peso (que no se mueva)",
                "Resistencia térmica (ante salpicaduras o calor)",
                "Diseño compacto (que ocupe el mínimo espacio en la mesa)",
            ],
        )

        st.divider()
        st.markdown("#### Sección 4 · Visión artificial y calibración")
        c1, c2 = st.columns(2)
        privacidad = c1.selectbox(
            "8. El sistema usa una cámara superior para guiar al robot hacia el cautín. ¿Te sentirías cómodo teniendo una cámara monitoreando tu área de trabajo?",
            [
                "Sí, sin problema",
                "Sí, siempre que el procesamiento sea local y no grabe video",
                "No, prefiero un sistema cien por ciento manual",
            ],
        )
        calibracion = c2.selectbox(
            "9. ¿Estarías dispuesto a realizar un proceso de calibración inicial antes de empezar a soldar?",
            [
                "Sí, si toma menos de 2 minutos",
                "Sí, si toma menos de 5 minutos",
                "No, quiero que sea conectar y usar",
            ],
        )

        enviado = st.form_submit_button("Enviar respuesta anónima")

        if enviado:
            if "PEGA_AQUI" in URL_APPS_SCRIPT:
                st.warning(
                    "Falta pegar tu enlace de Google Apps Script en la variable URL_APPS_SCRIPT de app.py."
                )
            else:
                payload = {
                    "frecuencia": frecuencia,
                    "experiencia": experiencia,
                    "frustracion": frustracion,
                    "errores": errores,
                    "activacion": activacion,
                    "longitud_estano": longitud_estano,
                    "caracteristica_clave": caracteristica_clave,
                    "privacidad": privacidad,
                    "calibracion": calibracion,
                }
                try:
                    resp = requests.post(URL_APPS_SCRIPT, json=payload, timeout=15)
                    if resp.status_code == 200:
                        st.success("¡Gracias por participar! Tu respuesta anónima se registró correctamente.")
                        st.cache_data.clear()
                    else:
                        st.error(f"El servidor respondió con código {resp.status_code}. Intenta de nuevo.")
                except Exception as err:
                    st.error(f"Error de conexión al guardar la respuesta: {err}")

# ------------------------------------------------------------------------------
# PESTAÑA 3: GRÁFICAS INTERACTIVAS CON PORCENTAJES (DETALLE + VISTA GLOBAL)
# ------------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Análisis estadístico interactivo de la encuesta (datos reales)")

    if df_filtrado.empty or not meta_f["categoricas"]:
        st.info("No hay datos disponibles para graficar con el filtro actual.")
    else:
        col_sel = st.selectbox(
            "Selecciona una pregunta para inspeccionar en detalle:",
            options=meta_f["categoricas"],
        )
        tf = tabla_frecuencias(df_filtrado[col_sel])

        if not tf.empty:
            lider = tf.iloc[0]
            st.success(
                f"**Hallazgo principal:** La opción más elegida es **«{lider['Categoría']}»** "
                f"con **{lider['Porcentaje (%)']:.1f} %** ({int(lider['Frecuencia'])} de {int(tf['Frecuencia'].sum())} respuestas válidas)."
            )

            if tipo_grafico == "Dona + Barras (%)":
                g1, g2 = st.columns(2)
                fig_pie = px.pie(
                    tf,
                    names="Etiqueta corta",
                    values="Frecuencia",
                    hole=0.46,
                    color_discrete_sequence=PALETA,
                    custom_data=["Categoría", "Porcentaje (%)"],
                    title="Distribución porcentual (%)",
                )
                fig_pie.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate="<b>%{customdata[0]}</b><br>Respuestas: %{value}<br>Porcentaje: %{customdata[1]:.1f}%<extra></extra>",
                )
                g1.plotly_chart(estilizar_figura(fig_pie, 400), width="stretch")

                fig_bar = px.bar(
                    tf.sort_values("Porcentaje (%)", ascending=True),
                    x="Porcentaje (%)",
                    y="Etiqueta corta",
                    orientation="h",
                    text="Texto",
                    color="Porcentaje (%)",
                    color_continuous_scale="Blues",
                    custom_data=["Categoría", "Frecuencia"],
                    title="Frecuencia y porcentaje por opción",
                )
                fig_bar.update_traces(
                    textposition="outside",
                    hovertemplate="<b>%{customdata[0]}</b><br>Respuestas: %{customdata[1]}<br>Porcentaje: %{x:.1f}%<extra></extra>",
                )
                fig_bar.update_layout(
                    coloraxis_showscale=False,
                    xaxis_title="Porcentaje (%)",
                    yaxis_title="",
                    xaxis_range=[0, min(115, float(tf["Porcentaje (%)"].max()) * 1.28 + 5)],
                )
                g2.plotly_chart(estilizar_figura(fig_bar, 400), width="stretch")

            elif tipo_grafico == "Solo Dona (%)":
                fig_pie = px.pie(
                    tf,
                    names="Etiqueta corta",
                    values="Frecuencia",
                    hole=0.46,
                    color_discrete_sequence=PALETA,
                    custom_data=["Categoría", "Porcentaje (%)"],
                    title=acortar_etiqueta(col_sel, 72),
                )
                fig_pie.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    hovertemplate="<b>%{customdata[0]}</b><br>Respuestas: %{value}<br>Porcentaje: %{customdata[1]:.1f}%<extra></extra>",
                )
                st.plotly_chart(estilizar_figura(fig_pie, 430), width="stretch")

            else:
                fig_bar = px.bar(
                    tf.sort_values("Porcentaje (%)", ascending=True),
                    x="Porcentaje (%)",
                    y="Etiqueta corta",
                    orientation="h",
                    text="Texto",
                    color="Porcentaje (%)",
                    color_continuous_scale="Blues",
                    custom_data=["Categoría", "Frecuencia"],
                    title=acortar_etiqueta(col_sel, 72),
                )
                fig_bar.update_traces(
                    textposition="outside",
                    hovertemplate="<b>%{customdata[0]}</b><br>Respuestas: %{customdata[1]}<br>Porcentaje: %{x:.1f}%<extra></extra>",
                )
                fig_bar.update_layout(
                    coloraxis_showscale=False,
                    xaxis_title="Porcentaje (%)",
                    yaxis_title="",
                    xaxis_range=[0, min(115, float(tf["Porcentaje (%)"].max()) * 1.25 + 5)],
                )
                st.plotly_chart(estilizar_figura(fig_bar, 420), width="stretch")

            st.markdown("**Tabla de frecuencias absolutas y relativas**")
            st.dataframe(
                tf[["Categoría", "Frecuencia", "Porcentaje (%)", "Acumulado (%)"]],
                hide_index=True,
                width="stretch",
            )

        if meta_f["numericas"]:
            st.divider()
            st.subheader("Distribución de escala cuantitativa (Frustración 1–5)")
            col_num = st.selectbox(
                "Variable numérica detectada:",
                options=list(meta_f["numericas"].keys()),
                key="sel_num_hist",
            )
            serie_n = meta_f["numericas"][col_num].dropna()
            if len(serie_n) > 0:
                n1, n2, n3, n4 = st.columns(4)
                n1.metric("Media", f"{serie_n.mean():.2f}")
                n2.metric("Mediana", f"{serie_n.median():.2f}")
                n3.metric("Desv. estándar", f"{serie_n.std():.2f}" if len(serie_n) > 1 else "0.00")
                n4.metric("Mín / Máx", f"{serie_n.min():.0f} – {serie_n.max():.0f}")

                fig_hist = px.histogram(
                    x=serie_n,
                    nbins=min(10, int(serie_n.nunique()) + 1),
                    text_auto=True,
                    color_discrete_sequence=["#0284c7"],
                    labels={"x": acortar_etiqueta(col_num, 50), "y": "Cantidad de respuestas"},
                    title="Histograma de frecuencias",
                )
                fig_hist.update_layout(bargap=0.18)
                st.plotly_chart(estilizar_figura(fig_hist, 340), width="stretch")

        st.divider()
        st.subheader("Vista panorámica de las 9 preguntas (%)")
        st.caption("Resumen visual completo para revisar rápidamente el comportamiento de toda la encuesta.")

        cols_vista = meta_f["categoricas"]
        for i in range(0, len(cols_vista), 2):
            par = st.columns(2)
            for j in range(2):
                if i + j < len(cols_vista):
                    c_nombre = cols_vista[i + j]
                    tf_mini = tabla_frecuencias(df_filtrado[c_nombre])
                    if not tf_mini.empty:
                        with par[j]:
                            fig_m = px.pie(
                                tf_mini,
                                names="Etiqueta corta",
                                values="Frecuencia",
                                hole=0.45,
                                color_discrete_sequence=PALETA,
                                custom_data=["Categoría", "Porcentaje (%)"],
                                title=acortar_etiqueta(c_nombre, 54),
                            )
                            fig_m.update_traces(
                                textposition="inside",
                                textinfo="percent",
                                hovertemplate="<b>%{customdata[0]}</b><br>n = %{value} (%{customdata[1]:.1f}%)<extra></extra>",
                            )
                            st.plotly_chart(estilizar_figura(fig_m, 340), width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 4: CRUCES DE VARIABLES Y MAPA DE CALOR
# ------------------------------------------------------------------------------
with tabs[3]:
    st.subheader("Cruces de variables y tabla de contingencia")
    st.write(
        "Compara dos preguntas simultáneamente para detectar cómo cambian las preferencias "
        "técnicas según el perfil del usuario (por ejemplo, experiencia frente al método de activación)."
    )

    if df_filtrado.empty or len(meta_f["categoricas"]) < 2:
        st.info("Se necesitan al menos dos preguntas categóricas con datos para realizar cruces.")
    else:
        x_col, y_col, m_col = st.columns([2, 2, 1])
        var_filas = x_col.selectbox("Variable principal (filas / eje X):", meta_f["categoricas"], index=0)
        opciones_y = [c for c in meta_f["categoricas"] if c != var_filas]
        var_cols = y_col.selectbox("Variable a comparar (grupos / columnas):", opciones_y, index=0)
        modo_pct = m_col.radio("Mostrar valores en:", ["Porcentaje (%)", "Conteo (n)"])

        sub = df_filtrado[[var_filas, var_cols]].dropna().astype(str)
        if not sub.empty:
            ct_abs = pd.crosstab(sub[var_filas], sub[var_cols])
            ct_pct = (pd.crosstab(sub[var_filas], sub[var_cols], normalize="index") * 100).round(1)
            matriz = ct_pct if modo_pct == "Porcentaje (%)" else ct_abs

            largo = matriz.reset_index().melt(
                id_vars=var_filas,
                var_name="Grupo",
                value_name="Valor",
            )
            largo["Eje_X"] = largo[var_filas].map(lambda s: acortar_etiqueta(s, 26))
            largo["Grupo_corto"] = largo["Grupo"].map(lambda s: acortar_etiqueta(s, 26))

            fig_cross = px.bar(
                largo,
                x="Eje_X",
                y="Valor",
                color="Grupo_corto",
                barmode="group",
                text_auto=".1f" if modo_pct == "Porcentaje (%)" else True,
                color_discrete_sequence=PALETA,
                labels={
                    "Eje_X": acortar_etiqueta(var_filas, 40),
                    "Valor": modo_pct,
                    "Grupo_corto": acortar_etiqueta(var_cols, 30),
                },
                title="Comparación agrupada entre variables",
            )
            st.plotly_chart(estilizar_figura(fig_cross, 410), width="stretch")

            fig_heat = px.imshow(
                matriz.values,
                x=[acortar_etiqueta(c, 22) for c in matriz.columns],
                y=[acortar_etiqueta(r, 24) for r in matriz.index],
                text_auto=".1f" if modo_pct == "Porcentaje (%)" else True,
                color_continuous_scale="YlGnBu",
                aspect="auto",
                labels=dict(color=modo_pct),
                title=f"Mapa de calor ({modo_pct} por fila)",
            )
            st.plotly_chart(estilizar_figura(fig_heat, 380), width="stretch")

            st.markdown("**Tabla de contingencia lista para el informe (Sección 2.4)**")
            st.dataframe(matriz, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 5: TRES CASAS DE CALIDAD (QFD) Y ANÁLISIS COMPETITIVO (CAP. 2)
# ------------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Despliegue de la Función de Calidad (3 Casas QFD · Cap. 2)")
    st.write(
        "Visualización trazable de las **tres Casas de Calidad** del proyecto: continuidad "
        "exacta desde las 10 necesidades ponderadas hacia 14 características técnicas (Casa 1), "
        "13 componentes/subsistemas (Casa 2) y 12 parámetros de diseño (Casa 3)."
    )

    casa_sel = st.radio(
        "Selecciona la Casa de Calidad a explorar:",
        [
            "Casa 1 · Características técnicas (14)",
            "Casa 2 · Componentes y subsistemas (13)",
            "Casa 3 · Parámetros de diseño (12)",
        ],
        horizontal=True,
    )

    if "Casa 1" in casa_sel:
        q1, q2 = st.columns([3, 2])
        with q1:
            fig_c1 = px.bar(
                CASA1_DF.sort_values("Peso rel. (%)", ascending=True),
                x="Peso rel. (%)",
                y="Característica técnica",
                orientation="h",
                text="Peso rel. (%)",
                color="Peso rel. (%)",
                color_continuous_scale="Blues",
                hover_data=["Peso abs.", "Valor objetivo"],
                title="Casa 1: Priorización de características técnicas (%)",
            )
            fig_c1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_c1.update_layout(coloraxis_showscale=False, xaxis_range=[0, 16.5], yaxis_title="")
            st.plotly_chart(estilizar_figura(fig_c1, 460), width="stretch")
        with q2:
            st.markdown("**Objetivos técnicos prioritarios (Tabla II y III)**")
            st.dataframe(CASA1_DF, hide_index=True, width="stretch")
            st.caption("Las 4 características líderes (resolución de estaño, tiempo por punto, temperatura y estabilidad de PCB) concentran el 42,6 % del peso.")

    elif "Casa 2" in casa_sel:
        q1, q2 = st.columns([3, 2])
        with q1:
            fig_c2 = px.bar(
                CASA2_DF.sort_values("Peso rel. (%)", ascending=True),
                x="Peso rel. (%)",
                y="Componente / subsistema",
                orientation="h",
                text="Peso rel. (%)",
                color="Peso rel. (%)",
                color_continuous_scale="Teal",
                hover_data=["Peso abs.", "Objetivo"],
                title="Casa 2: Priorización de componentes y subsistemas (%)",
            )
            fig_c2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_c2.update_layout(coloraxis_showscale=False, xaxis_range=[0, 18.0], yaxis_title="")
            st.plotly_chart(estilizar_figura(fig_c2, 460), width="stretch")
        with q2:
            st.markdown("**Componentes priorizados (Tabla V)**")
            st.dataframe(CASA2_DF, hide_index=True, width="stretch")
            st.caption("La punta del cautín (referencia externa), el motor de paso del extrusor y el controlador reúnen el 40,0 % del peso.")

    else:
        q1, q2 = st.columns([3, 2])
        with q1:
            fig_c3 = px.bar(
                CASA3_DF.sort_values("Peso rel. (%)", ascending=True),
                x="Peso rel. (%)",
                y="Parámetro de diseño",
                orientation="h",
                text="Peso rel. (%)",
                color="Peso rel. (%)",
                color_continuous_scale="Purples",
                hover_data=["Peso abs."],
                title="Casa 3: Priorización de parámetros de diseño (%)",
            )
            fig_c3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_c3.update_layout(coloraxis_showscale=False, xaxis_range=[0, 19.0], yaxis_title="")
            st.plotly_chart(estilizar_figura(fig_c3, 460), width="stretch")
        with q2:
            st.markdown("**Parámetros críticos de ingeniería (Tabla VI)**")
            st.dataframe(CASA3_DF, hide_index=True, width="stretch")
            st.caption("El error de localización de la punta (15,6 %) y la capacidad del controlador (13,6 %) lideran con 29,2 % combinado.")

    st.divider()
    st.subheader("Evaluación competitiva frente a equipos comerciales (Tabla IV)")
    rc1, rc2 = st.columns([3, 2])
    with rc1:
        equipos_sel = st.multiselect(
            "Equipos a comparar en el gráfico radar:",
            ["Diseño Propio", "Apollo Seko", "Japan Unix", "Quick Soldering"],
            default=["Diseño Propio", "Apollo Seko", "Japan Unix", "Quick Soldering"],
        )
        colores_comp = {
            "Diseño Propio": "#0284c7",
            "Apollo Seko": "#059669",
            "Japan Unix": "#7c3aed",
            "Quick Soldering": "#d97706",
        }
        cats_short = [acortar_etiqueta(n, 22) for n in NECESIDADES_QFD_DF["Necesidad"]]
        fig_radar = go.Figure()
        for eq in equipos_sel:
            vals = NECESIDADES_QFD_DF[eq].tolist()
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=cats_short + [cats_short[0]],
                    fill="toself" if eq == "Diseño Propio" else "none",
                    name=eq,
                    line=dict(color=colores_comp[eq], width=2.5 if eq == "Diseño Propio" else 1.8),
                )
            )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            title="Comparación de desempeño por necesidad (escala 0–5)",
        )
        st.plotly_chart(estilizar_figura(fig_radar, 430), width="stretch")

    with rc2:
        st.markdown("**Puntaje ponderado global (Tabla IV)**")
        imp_vec = NECESIDADES_QFD_DF["Importancia (%)"] / 100.0
        res_comp = pd.DataFrame(
            [
                (eq, round(float((imp_vec * NECESIDADES_QFD_DF[eq]).sum()), 2))
                for eq in ["Apollo Seko", "Diseño Propio", "Japan Unix", "Quick Soldering"]
            ],
            columns=["Equipo", "Puntaje ponderado (0–5)"],
        ).sort_values("Puntaje ponderado (0–5)", ascending=False)
        st.dataframe(res_comp, hide_index=True, width="stretch")

        st.info(
            "Nuestro diseño logra **4,26/5**, superando a Japan Unix (4,02) y Quick Soldering (2,77), "
            "quedando a solo 0,24 puntos de Apollo Seko (4,50) con un costo objetivo de USD 100."
        )

    if not df_filtrado.empty and meta_f["categoricas"]:
        st.divider()
        st.subheader("Voz del Cliente desde la encuesta en vivo (Sección 2.5)")
        qfd_enc = construir_resumen_qfd(df_filtrado, meta_f["categoricas"])
        if not qfd_enc.empty:
            qfd_enc["Prioridad"] = np.where(
                qfd_enc["Consenso (%)"] >= umbral_consenso,
                "Alta (Crítica)",
                np.where(qfd_enc["Consenso (%)"] >= umbral_consenso - 15, "Media", "Moderada"),
            )
            st.dataframe(qfd_enc, hide_index=True, width="stretch")

# ------------------------------------------------------------------------------
# PESTAÑA 6: MÓDULOS, SIMULADOR DE SENSIBILIDAD (CAP. 3) Y DESCARGAS
# ------------------------------------------------------------------------------
with tabs[5]:
    st.subheader("Arquitectura modular seleccionada: Alternativa A (Capítulo 3)")
    st.write(
        "El sistema se descompone en **10 funciones** (5 principales y 5 secundarias) agrupadas en "
        "**6 módulos físicos (M1–M6)** conectados mediante **6 interfaces verificables (I1–I6)**."
    )

    for i in range(0, len(MODULOS_LIST), 3):
        cols_m = st.columns(3)
        for j in range(3):
            if i + j < len(MODULOS_LIST):
                mid, mnom, mfns, msol, mref = MODULOS_LIST[i + j]
                with cols_m[j]:
                    st.markdown(
                        f"""
                        <div class="mod-card">
                            <div class="mod-head">{mid} · {mnom}</div>
                            <div class="mod-fn">Funciones cubiertas: {mfns}</div>
                            <div class="mod-body">{msol}</div>
                            <span class="mod-meta">Meta QFD: {mref}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with st.expander("Ver interfaces entre módulos (Tabla XI) y comparación de alternativas (Tabla XIII)", expanded=False):
        st.markdown("**Interfaces M1–M6 y criterios de verificación**")
        st.dataframe(INTERFACES_DF, hide_index=True, width="stretch")
        st.markdown("**Alternativas de la matriz morfológica (A, B y C)**")
        st.dataframe(ALTERNATIVAS_DF, hide_index=True, width="stretch")

    st.divider()
    st.subheader("Simulador interactivo de Matriz de Decisión y Sensibilidad (Tablas XV y XVI)")
    st.write(
        "Ajusta los pesos de los tres criterios de ingeniería para verificar en vivo la robustez "
        "de la selección entre la **Alternativa A (QFD)** y la **Alternativa B (Industrial)**."
    )

    s1, s2 = st.columns([1, 2])
    with s1:
        st.markdown("**Pesos personalizados (se normalizan a 100 %)**")
        w_qfd_raw = st.slider("Alineación con el QFD (Base: 40 %)", 5, 80, 40, 5)
        w_fab_raw = st.slider("Fabricación y costo (Base: 35 %)", 5, 80, 35, 5)
        w_man_raw = st.slider("Mantenimiento y control (Base: 25 %)", 5, 80, 25, 5)

        suma_w = w_qfd_raw + w_fab_raw + w_man_raw
        wq = w_qfd_raw / suma_w
        wf = w_fab_raw / suma_w
        wm = w_man_raw / suma_w
        st.caption(f"Pesos normalizados → QFD: **{wq*100:.1f}%** · Fab./Costo: **{wf*100:.1f}%** · Mant.: **{wm*100:.1f}%**")

        score_a = wq * 5 + wf * 5 + wm * 4
        score_b = wq * 5 + wf * 2 + wm * 3
        st.metric("Puntaje Alternativa A (QFD)", f"{score_a:.2f} / 5", delta=f"+{score_a - score_b:.2f} sobre B")
        st.metric("Puntaje Alternativa B (Industrial)", f"{score_b:.2f} / 5")

    with s2:
        escenarios_df = pd.DataFrame(
            [
                ("Escenario actual", score_a, score_b),
                ("Base (40/35/25)", 4.75, 3.45),
                ("Prioridad QFD (60/20/20)", 4.80, 4.00),
                ("Pesos iguales (33/33/33)", 4.67, 3.33),
                ("Prioridad costo (25/50/25)", 4.75, 3.00),
                ("Prioridad mant. (25/25/50)", 4.50, 3.25),
                ("Casi solo QFD (70/10/20)", 4.80, 4.30),
            ],
            columns=["Escenario", "Concepto A (QFD)", "Concepto B (Industrial)"],
        )
        esc_long = escenarios_df.melt(id_vars="Escenario", var_name="Alternativa", value_name="Puntaje")
        fig_sens = px.bar(
            esc_long,
            x="Escenario",
            y="Puntaje",
            color="Alternativa",
            barmode="group",
            text_auto=".2f",
            color_discrete_map={
                "Concepto A (QFD)": "#1d4ed8",
                "Concepto B (Industrial)": "#d97706",
            },
            title="Análisis de sensibilidad: puntaje ponderado por escenario (1–5)",
        )
        fig_sens.update_layout(yaxis_range=[0, 5.6], xaxis_title="")
        st.plotly_chart(estilizar_figura(fig_sens, 400), width="stretch")

    st.divider()
    st.subheader("Metodología, fórmulas verificables y descarga de evidencias")

    with st.expander("Fórmulas estadísticas, QFD y decisión ponderada", expanded=False):
        st.markdown(
            """
            * **Frecuencia relativa (%):** $f_r = \\frac{n_i}{N} \\times 100$, sobre respuestas válidas no nulas ($N$).
            * **Media aritmética (escala 1–5):** $\\bar{x} = \\frac{1}{N} \\sum_{i=1}^{N} x_i$ y desviación estándar $s = \\sqrt{\\frac{1}{N-1} \\sum_{i=1}^{N} (x_i - \\bar{x})^2}$.
            * **Casas de Calidad (QFD):** $W_j = \\sum_i (I_i \\cdot r_{ij})$ y $W_{\\text{rel},j} = 100 \\cdot \\frac{W_j}{\\sum_j W_j}$ con escala 9-3-1.
            * **Evaluación competitiva:** $P = \\frac{1}{100}\\sum_i (I_i \\cdot c_i)$ en escala 0–5.
            * **Matriz de decisión ponderada:** $S_k = \\sum_i (w_i \\cdot c_{ik})$ con $\\sum w_i = 1$.
            * **Privacidad:** La base `Datos_Limpios` excluye correos, nombres e identificadores personales y utiliza únicamente respuestas reales.
            """
        )

    if not df_filtrado.empty:
        st.dataframe(df_filtrado, hide_index=True, width="stretch")

        d1, d2, d3 = st.columns(3)
        d1.download_button(
            "⬇️ Descargar encuesta anonimizada (CSV)",
            data=df_filtrado.to_csv(index=False).encode("utf-8-sig"),
            file_name="datos_encuesta_brazo_soldadura_anonimizados.csv",
            mime="text/csv",
            width="stretch",
        )

        qfd_export = construir_resumen_qfd(df_filtrado, meta_f["categoricas"])
        d2.download_button(
            "⬇️ Descargar resumen encuesta→QFD (CSV)",
            data=qfd_export.to_csv(index=False).encode("utf-8-sig"),
            file_name="resumen_necesidades_encuesta_qfd.csv",
            mime="text/csv",
            width="stretch",
        )

        metadatos = {
            "proyecto": "Brazo Robótico Asistente de Soldadura de Placas PCB",
            "institucion": "Escuela Politécnica Nacional (EPN) - Facultad de Ingeniería Mecánica",
            "grupo": "GR1S4",
            "integrantes": [m["nombre"] for m in EQUIPO],
            "respuestas_totales": int(total_muestra),
            "respuestas_filtradas": int(total_filtrado),
            "concepto_seleccionado": "Alternativa A (QFD) - 4.75/5",
            "costo_objetivo_usd": 100,
            "emisiones_preliminares_openlca_kg_co2": 1.263,
        }
        d3.download_button(
            "⬇️ Descargar metadatos del estudio (JSON)",
            data=json.dumps(metadatos, indent=2, ensure_ascii=False),
            file_name="metadatos_proyecto_fase1.json",
            mime="application/json",
            width="stretch",
        )

# ==============================================================================
# 9. PIE DE PÁGINA
# ==============================================================================
st.markdown(
    """
<div class="footer-web">
    Proyecto Integrador de Diseño de Máquinas (GR1S4) · Ingeniería Mecatrónica · Escuela Politécnica Nacional (EPN) · Aplicación pública en Python y Streamlit
</div>
""",
    unsafe_allow_html=True,
)
