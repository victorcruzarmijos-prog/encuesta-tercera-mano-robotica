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
    page_title="Tercera Mano Robótica | Diseño de Máquinas EPN",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CONEXIÓN CON GOOGLE SHEETS Y APPS SCRIPT
# ==============================================================================
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbyV4WUdP8vvEkRgqnWTvMyFdcXchyXtJXO8oKVX660rpj8SxVIbQrvO9fDp4n3FDH2Y/exec"
ID_HOJA = "1vn_id57bRE3l3dTh_ScTknJpTW3HDjmUnIA7tc4BX6M"
NOMBRE_HOJA = "Datos_Limpios"
URL_CSV_HOJA = (
    f"https://docs.google.com/spreadsheets/d/{ID_HOJA}"
    f"/gviz/tq?tqx=out:csv&sheet={NOMBRE_HOJA}"
)

# ==============================================================================
# 3. DATOS DEL EQUIPO (EDITA LOS NOMBRES DE LOS INTEGRANTES 1 Y 4 AQUÍ)
# ==============================================================================
EQUIPO = [
    {
        "nombre": "Estalin Boada",
        "carrera": "Ingeniería Mecatrónica · EPN",
        "rol": "Planteamiento, Metodología y Ciclo de Vida (OpenLCA)",
        "capitulo": "Capítulo 1 · Secciones 1.1 a 1.7",
        "icono": "🌱",
    },
    {
        "nombre": "Victor Cruz",
        "carrera": "Ingeniería Mecatrónica · EPN",
        "rol": "Encuesta Python/Streamlit, Analítica e IA de Bocetos",
        "capitulo": "Cap. 2 (2.1–2.5) y Cap. 3 (3.7–3.8)",
        "icono": "💻",
    },
    {
        "nombre": "Alan Villamarin",
        "carrera": "Ingeniería Mecatrónica · EPN",
        "rol": "Arquitectura Funcional, Modularidad y Selección",
        "capitulo": "Capítulo 3 · Secciones 3.1 a 3.6 y 3.9",
        "icono": "⚙️",
    },
    {
        "nombre": "Maverick Cadena",
        "carrera": "Ingeniería Mecatrónica · EPN",
        "rol": "Casas de Calidad (QFD) e Integración Técnica",
        "capitulo": "Capítulo 2 · Secciones 2.6 a 2.9",
        "icono": "📐",
    },
]

PALETA = [
    "#1d4ed8", "#0284c7", "#0d9488", "#2563eb",
    "#7c3aed", "#d97706", "#059669", "#dc2626",
]

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
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0 0 0.55rem 0;
        line-height: 1.2;
    }
    .hero-box p {
        color: #e2e8f0 !important;
        font-size: 1.01rem;
        margin: 0 0 1.15rem 0;
        max-width: 880px;
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
        font-size: 0.92rem;
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
    .team-icon {font-size: 1.65rem; margin-bottom: 0.3rem;}
    .team-name {font-size: 1.03rem; font-weight: 700; margin-bottom: 0.15rem;}
    .team-major {font-size: 0.8rem; color: #38bdf8; font-weight: 600; margin-bottom: 0.35rem;}
    .team-role {font-size: 0.87rem; opacity: 0.88; margin-bottom: 0.5rem; line-height: 1.4;}
    .team-cap {
        display: inline-block;
        background: rgba(2, 132, 199, 0.16);
        color: #38bdf8;
        padding: 0.2rem 0.6rem;
        border-radius: 8px;
        font-size: 0.77rem;
        font-weight: 600;
    }

    /* Cadena de trazabilidad metodológica */
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
        padding: 0.55rem 1.05rem;
        font-weight: 600;
        font-size: 0.91rem;
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
    # Evita confundir rangos como "1 a 3 mm" o "menos de 2 minutos" con escalas numéricas
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
                "Peso QFD (1–5)": peso_qfd,
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
    st.caption("Facultad de Ingeniería Mecánica · EPN · Diseño de Máquinas")

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
    st.subheader("Visualización")
    tipo_grafico = st.radio(
        "Estilo principal en analítica:",
        ["Dona + Barras (%)", "Solo Dona (%)", "Solo Barras horizontales (%)"],
        index=0,
    )
    umbral_consenso = st.slider(
        "Umbral de prioridad alta QFD (%)",
        min_value=30,
        max_value=75,
        value=50,
        step=5,
        help="Define a partir de qué porcentaje de consenso una necesidad se clasifica como crítica.",
    )

    st.divider()
    if st.button("🔄 Actualizar datos en vivo", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "Los datos mostrados provienen en tiempo real de respuestas reales anonimizadas "
        "almacenadas en Google Sheets."
    )

meta_f = clasificar_columnas(df_filtrado) if not df_filtrado.empty else meta

# ==============================================================================
# 7. PORTADA PRINCIPAL + INDICADORES KPI SUPERIORES
# ==============================================================================
st.markdown(
    """
<div class="hero-box">
    <div class="hero-pill">ESCUELA POLITÉCNICA NACIONAL · INGENIERÍA MECATRÓNICA · DISEÑO DE MÁQUINAS</div>
    <h1>Tercera Mano Robótica para Soldadura de Placas (PCBs)</h1>
    <p>
        Plataforma interactiva de levantamiento de requerimientos y análisis estadístico en tiempo real
        para el diseño conceptual de un asistente robótico con visión por computadora capaz de rastrear
        la punta del cautín y suministrar estaño en frío con precisión.
    </p>
    <div class="badge-row">
        <span class="badge-item">🤖 Asistente con Visión Artificial</span>
        <span class="badge-item">📊 Analítica Real con Porcentajes</span>
        <span class="badge-item">🔒 Datos 100 % Anonimizados</span>
        <span class="badge-item">📐 Trazabilidad hacia QFD · Fase 1</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
total_muestra = len(df_original)
total_filtrado = len(df_filtrado)

k1.metric(
    "Respuestas analizadas",
    f"{total_filtrado:,}",
    delta=f"de {total_muestra:,} reales" if total_filtrado != total_muestra else "100 % de la muestra",
)

if meta_f["frustracion"] and meta_f["frustracion"] in meta_f["numericas"]:
    serie_num = meta_f["
