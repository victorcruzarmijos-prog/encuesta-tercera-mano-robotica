import json
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
# Reemplaza esta línea con tu enlace /exec que ya tienes en tu app.py anterior:
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbyV4WUdP8vvEkRgqnWTvMyFdcXchyXtJXO8oKVX660rpj8SxVIbQrvO9fDp4n3FDH2Y/exec"
ID_HOJA = "1vn_id57bRE3l3dTh_ScTknJpTW3HDjmUnIA7tc4BX6M"
NOMBRE_HOJA = "Datos_Limpios"
URL_CSV_HOJA = (
    f"https://docs.google.com/spreadsheets/d/{ID_HOJA}"
    f"/gviz/tq?tqx=out:csv&sheet={NOMBRE_HOJA}"
)

# ==============================================================================
# 3. DATOS DEL EQUIPO (EDITA LOS NOMBRES DE LOS COMPAÑEROS 1 Y 4 AQUÍ)
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
        df[col] = df[col].astype(str).str.strip()
        df.loc[df[col].isin(["nan", "None", ""]), col] = np.nan
    return df


def es_columna_fecha(nombre: str) -> bool:
    low = nombre.lower()
    return any(k in low for k in ["fecha", "marca temporal", "timestamp", "hora"])


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
    extraida = validos.str.extract(r"^\s*(\d+(?:\.\d+)?)")[0]
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
        if es_columna_fecha(col):
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
    serie_num = meta_f["numericas"][meta_f["frustracion"]].dropna()
    escala_max = int(max(5, round(serie_num.max()))) if len(serie_num) > 0 else 5
    prom = float(serie_num.mean()) if len(serie_num) > 0 else 0.0
    desv = float(serie_num.std()) if len(serie_num) > 1 else 0.0
    mediana = float(serie_num.median()) if len(serie_num) > 0 else 0.0
    k2.metric("Índice numérico promedio", f"{prom:.2f} / {escala_max}", delta=f"Mediana: {mediana:.1f}")
    k3.metric("Desviación estándar", f"{desv:.2f}", delta=f"n válido: {len(serie_num)}")
else:
    k2.metric("Preguntas evaluadas", f"{len(meta_f['categoricas'])}")
    k3.metric("Columnas en la base", f"{len(df_filtrado.columns)}")

if not df_filtrado.empty and meta_f["perfil"]:
    tf_perfil = tabla_frecuencias(df_filtrado[meta_f["perfil"]])
    if not tf_perfil.empty:
        k4.metric(
            "Perfil predominante",
            acortar_etiqueta(tf_perfil.iloc[0]["Categoría"], 18),
            delta=f"{tf_perfil.iloc[0]['Porcentaje (%)']:.1f} % ({int(tf_perfil.iloc[0]['Frecuencia'])})",
        )
    else:
        k4.metric("Perfil predominante", "—")
else:
    k4.metric("Estado de conexión", "Sin datos" if error_carga else "En espera")

if error_carga:
    st.error(
        "No se pudo conectar con la hoja de cálculo. Verifica que esté compartida como Lector "
        f"y que la pestaña se llame '{NOMBRE_HOJA}'."
    )
    st.caption(f"Detalle técnico: {error_carga}")

# ==============================================================================
# 8. PESTAÑAS DE NAVEGACIÓN DE LA PÁGINA WEB
# ==============================================================================
tabs = st.tabs(
    [
        "🏠 1 · Quiénes somos y Proyecto",
        "📝 2 · Responder Encuesta",
        "📊 3 · Gráficas y Porcentajes",
        "🔀 4 · Cruces y Mapa de Calor",
        "📐 5 · Del Dato al QFD",
        "📑 6 · Metodología y Descargas",
    ]
)

# ------------------------------------------------------------------------------
# PESTAÑA 1: QUIÉNES SOMOS, PROBLEMA Y ARQUITECTURA DIDÁCTICA
# ------------------------------------------------------------------------------
with tabs[0]:
    st.subheader("¿Quiénes somos?")
    st.write(
        "Somos un equipo de estudiantes de **Ingeniería Mecatrónica** de la "
        "**Facultad de Ingeniería Mecánica** de la **Escuela Politécnica Nacional (EPN)**. "
        "Esta plataforma forma parte de la **Primera Fase del Proyecto Integrador de Diseño de Máquinas**, "
        "orientada a transformar necesidades reales de usuarios en especificaciones técnicas auditables."
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
    st.subheader("¿Qué máquina estamos diseñando?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="info-card">
                <h4>⚠️ El problema real al soldar</h4>
                <p>Soldar placas electrónicas exige coordinar tres elementos simultáneos:
                sujetar el componente o PCB, controlar el cautín caliente y acercar el hilo
                de estaño con precisión, generando fatiga, soldaduras frías y riesgo de quemaduras.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="info-card">
                <h4>👁️ Visión artificial y automatización</h4>
                <p>El concepto integra una cámara superior con procesamiento local para
                identificar la posición de la punta del cautín, coordinando un mecanismo
                alimentador de estaño en frío y un sistema de extracción de humos.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="info-card">
                <h4>🎯 Propósito de esta plataforma</h4>
                <p>Recopilar respuestas reales de estudiantes, técnicos y aficionados,
                analizarlas estadísticamente en vivo y derivar pesos objetivos para las
                tres Casas de Calidad (QFD) y la arquitectura modular de la máquina.</p>
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
            <div class="flow-step"><div class="flow-num">3</div><div class="flow-title">Necesidades</div><div class="flow-desc">Jerarquización de la Voz del Cliente</div></div>
            <div class="flow-step"><div class="flow-num">4</div><div class="flow-title">3 Casas QFD</div><div class="flow-desc">Parámetros y subsistemas críticos</div></div>
            <div class="flow-step"><div class="flow-num">5</div><div class="flow-title">Módulos</div><div class="flow-desc">Matriz morfológica y selección</div></div>
            <div class="flow-step"><div class="flow-num">6</div><div class="flow-title">Boceto IA</div><div class="flow-desc">Refinamiento iterativo validado</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("👉 Selecciona la pestaña **2 · Responder Encuesta** para participar o **3 · Gráficas y Porcentajes** para explorar el análisis interactivo.")

# ------------------------------------------------------------------------------
# PESTAÑA 2: FORMULARIO PÚBLICO OPERATIVO
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
        experiencia = a1.selectbox(
            "1. ¿Cuál es tu nivel de experiencia soldando placas de circuito impreso (PCBs)?",
            ["Principiante", "Intermedio", "Avanzado"],
        )
        frecuencia = a2.selectbox(
            "2. ¿Con qué frecuencia realizas soldadura de componentes electrónicos?",
            ["Esporádicamente (pocas veces al año)", "Mensualmente", "Semanalmente o a diario"],
        )

        st.divider()
        st.markdown("#### Sección 2 · Validación del problema")
        frustracion = st.slider(
            "3. En una escala de 1 a 5, ¿qué tan frustrante resulta coordinar placa, cautín y estaño al mismo tiempo?",
            min_value=1,
            max_value=5,
            value=4,
        )
        problema_principal = st.selectbox(
            "4. ¿Cuál es tu mayor dificultad al soldar PCBs?",
            [
                "Falta de una tercera mano para acercar el estaño",
                "Movimiento involuntario de la placa o componente",
                "Falta de precisión en pads o pines pequeños",
                "Quemaduras, humo o fatiga en la mano",
            ],
        )

        st.divider()
        st.markdown("#### Sección 3 · Requerimientos funcionales y estructurales")
        b1, b2 = st.columns(2)
        activacion = b1.selectbox(
            "5. ¿Qué método prefieres para activar la alimentación de estaño?",
            ["Pedal de pie", "Detección automática con cámara", "Botón manual en la base"],
        )
        caracteristica_clave = b2.selectbox(
            "6. ¿Qué característica estructural consideras más importante?",
            ["Estabilidad de la base", "Resistencia térmica", "Diseño compacto de escritorio"],
        )

        st.divider()
        st.markdown("#### Sección 4 · Interfaz, calibración y visión artificial")
        c1, c2 = st.columns(2)
        calibracion = c1.selectbox(
            "7. Tiempo máximo que aceptarías para calibrar el sistema antes de soldar:",
            ["Menos de 1 minuto", "Entre 1 y 2 minutos", "Más de 2 minutos"],
        )
        privacidad = c2.selectbox(
            "8. Respecto al uso de cámara para rastrear la punta del cautín, prefieres:",
            ["Procesamiento 100 % local sin grabar video", "No me preocupa si requiere conexión"],
        )
        comentario = st.text_area(
            "9. Comentario o requerimiento adicional (opcional):",
            placeholder="Ejemplo: compatibilidad con estaño de 0.8 mm, iluminación LED integrada, extractor de humo...",
        )

        enviado = st.form_submit_button("Enviar respuesta anónima")

        if enviado:
            if "PEGA_AQUI" in URL_APPS_SCRIPT:
                st.warning(
                    "Falta pegar tu enlace de Google Apps Script en la variable URL_APPS_SCRIPT de app.py."
                )
            else:
                payload = {
                    "experiencia": experiencia,
                    "frecuencia": frecuencia,
                    "frustracion": frustracion,
                    "problema_principal": problema_principal,
                    "activacion": activacion,
                    "caracteristica_clave": caracteristica_clave,
                    "calibracion": calibracion,
                    "privacidad": privacidad,
                    "comentario": comentario,
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
    st.subheader("Análisis estadístico interactivo con porcentajes")

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
            st.subheader("Distribución de variables cuantitativas / escalas")
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
        st.subheader("Vista panorámica de todas las preguntas (%)")
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
        "Compara dos preguntas simultáneamente para detectar cómo varían las preferencias "
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
# PESTAÑA 5: DEL DATO AL DISEÑO CONCEPTUAL Y QFD (SECCIONES 2.5 – 2.9)
# ------------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Jerarquización de necesidades y puente hacia el QFD")
    st.write(
        "Esta sección traduce automáticamente las respuestas reales de la encuesta en pesos "
        "relativos de la Voz del Cliente (sección 2.5) para alimentar la **Primera Casa de Calidad**."
    )

    if not df_filtrado.empty and meta_f["categoricas"]:
        qfd_df = construir_resumen_qfd(df_filtrado, meta_f["categoricas"])
        if not qfd_df.empty:
            qfd_df["Prioridad"] = np.where(
                qfd_df["Consenso (%)"] >= umbral_consenso,
                "Alta (Crítica)",
                np.where(qfd_df["Consenso (%)"] >= umbral_consenso - 15, "Media", "Moderada"),
            )

            col_q1, col_q2 = st.columns([3, 2])
            with col_q1:
                st.markdown("**Tabla priorizada de necesidades (entrada directa a Casa 1 del QFD)**")
                st.dataframe(qfd_df, hide_index=True, width="stretch")

            with col_q2:
                fig_qfd = px.bar(
                    qfd_df.sort_values("Peso QFD (1–5)", ascending=True),
                    x="Peso QFD (1–5)",
                    y="Dimensión / Pregunta",
                    orientation="h",
                    color="Prioridad",
                    text="Peso QFD (1–5)",
                    color_discrete_map={
                        "Alta (Crítica)": "#1d4ed8",
                        "Media": "#0284c7",
                        "Moderada": "#64748b",
                    },
                    title="Peso relativo normalizado (1 a 5)",
                )
                fig_qfd.update_traces(textposition="outside")
                fig_qfd.update_layout(xaxis_range=[0, 5.6], yaxis_title="")
                st.plotly_chart(estilizar_figura(fig_qfd, 400), width="stretch")

            st.divider()
            st.subheader("Simulador interactivo del perfil de requerimientos (Radar de Diseño)")
            st.caption(
                "Ajusta la importancia de los 6 ejes de ingeniería para explorar el equilibrio "
                "conceptual de la Tercera Mano Robótica antes de fijar las ponderaciones definitivas."
            )

            r_col1, r_col2 = st.columns([1, 2])
            with r_col1:
                w_prec = st.slider("Precisión de posicionamiento (mm)", 1, 5, 5)
                w_seg = st.slider("Seguridad térmica y estabilidad", 1, 5, 5)
                w_erg = st.slider("Ergonomía y manos libres", 1, 5, 4)
                w_vel = st.slider("Rapidez de calibración (< 2 min)", 1, 5, 4)
                w_priv = st.slider("Visión artificial 100 % local", 1, 5, 4)
                w_cost = st.slider("Costo accesible / fabricabilidad", 1, 5, 3)

            with r_col2:
                categorias_radar = [
                    "Precisión",
                    "Seguridad térmica",
                    "Ergonomía",
                    "Calibración rápida",
                    "Visión local",
                    "Accesibilidad",
                ]
                valores_radar = [w_prec, w_seg, w_erg, w_vel, w_priv, w_cost]
                fig_radar = go.Figure(
                    data=go.Scatterpolar(
                        r=valores_radar + [valores_radar[0]],
                        theta=categorias_radar + [categorias_radar[0]],
                        fill="toself",
                        line_color="#0284c7",
                        fillcolor="rgba(2, 132, 199, 0.25)",
                        name="Perfil objetivo",
                    )
                )
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    showlegend=False,
                    title="Equilibrio conceptual de requerimientos técnicos",
                )
                st.plotly_chart(estilizar_figura(fig_radar, 390), width="stretch")

            st.divider()
            st.markdown("**Traducción preliminar de requerimientos técnicos (puente hacia Sección 2.6 y Capítulo 3)**")
            matriz_puente = pd.DataFrame(
                [
                    ["Alimentación asistida de estaño", "Encuesta · Problema principal", "Extrusor de hilo en frío (0.6–1.0 mm)", "Motor paso a paso + boquilla resistente al calor"],
                    ["Seguimiento de la punta del cautín", "Encuesta · Visión artificial", "Procesamiento local en tiempo real", "Cámara cenital + modelo de detección local sin nube"],
                    ["Activación ergonómica", "Encuesta · Interfaz de disparo", "Control manos libres", "Pedal / disparo automático sincronizado"],
                    ["Estabilidad y seguridad térmica", "Encuesta · Estructura", "Base antideslizante resistente a >250 °C", "Sujeción de PCB + zona segura para cautín"],
                    ["Calibración ágil", "Encuesta · Usabilidad", "Puesta a punto < 2 minutos", "Referencia visual fija en el área de trabajo"],
                ],
                columns=["Necesidad del usuario", "Origen trazable", "Objetivo preliminar", "Subsistema o módulo asociado"],
            )
            st.dataframe(matriz_puente, hide_index=True, width="stretch")
    else:
        st.info("Carga datos reales en la hoja para generar la matriz QFD preliminar.")

# ------------------------------------------------------------------------------
# PESTAÑA 6: METODOLOGÍA, COMENTARIOS ABIERTOS Y DESCARGAS VERIFICABLES
# ------------------------------------------------------------------------------
with tabs[5]:
    st.subheader("Metodología, rigor técnico y exportación de evidencias")

    with st.expander("Fórmulas estadísticas y criterios de trazabilidad", expanded=True):
        st.markdown(
            """
            * **Frecuencia relativa (%):** $f_r = \\frac{n_i}{N} \\times 100$, calculada sobre respuestas válidas no nulas ($N$).
            * **Media aritmética (escalas cuantitativas):** $\\bar{x} = \\frac{1}{N} \\sum_{i=1}^{N} x_i$.
            * **Desviación estándar muestral:** $s = \\sqrt{\\frac{1}{N-1} \\sum_{i=1}^{N} (x_i - \\bar{x})^2}$.
            * **Peso relativo preliminar QFD (escala 1–5):** $P_{QFD} = 1 + 4 \\cdot \\left(\\frac{\\text{Consenso \\%}}{100}\\right)$, empleado como insumo auditable para priorizar la Voz del Cliente en la Primera Casa de Calidad.
            * **Privacidad y anonimización:** La hoja conectada (`Datos_Limpios`) excluye correos electrónicos, nombres y datos personales. Todas las respuestas corresponden a registros reales; no se emplean datos sintéticos.
            """
        )

    if not df_filtrado.empty:
        if meta_f["comentarios"]:
            st.subheader("Comentarios abiertos de los encuestados")
            col_com = st.selectbox("Columna de texto abierto:", meta_f["comentarios"])
            textos = df_filtrado[col_com].dropna().astype(str)
            busqueda = st.text_input("Buscar palabra clave en comentarios:", placeholder="Ej: humo, precisión, pedal, precio...")
            if busqueda:
                textos = textos[textos.str.contains(busqueda, case=False, na=False)]
            st.caption(f"Mostrando {len(textos)} comentarios coincidentes.")
            st.dataframe(pd.DataFrame({"Comentario anónimo": textos.values}), hide_index=True, width="stretch")

        st.divider()
        st.subheader("Vista de base de datos anonimizada y descargas")
        st.dataframe(df_filtrado, hide_index=True, width="stretch")

        d1, d2, d3 = st.columns(3)
        d1.download_button(
            "⬇️ Descargar datos anonimizados (CSV)",
            data=df_filtrado.to_csv(index=False).encode("utf-8-sig"),
            file_name="datos_encuesta_tercera_mano_anonimizados.csv",
            mime="text/csv",
            width="stretch",
        )

        qfd_export = construir_resumen_qfd(df_filtrado, meta_f["categoricas"])
        d2.download_button(
            "⬇️ Descargar resumen para QFD (CSV)",
            data=qfd_export.to_csv(index=False).encode("utf-8-sig"),
            file_name="resumen_necesidades_qfd.csv",
            mime="text/csv",
            width="stretch",
        )

        metadatos = {
            "proyecto": "Tercera Mano Robótica para Soldadura de PCBs",
            "institucion": "Escuela Politécnica Nacional (EPN) - Facultad de Ingeniería Mecánica",
            "carrera": "Ingeniería Mecatrónica",
            "respuestas_totales": int(total_muestra),
            "respuestas_filtradas": int(total_filtrado),
            "preguntas_categoricas": meta_f["categoricas"],
            "variables_numericas": list(meta_f["numericas"].keys()),
            "umbral_prioridad_alta_pct": int(umbral_consenso),
        }
        d3.download_button(
            "⬇️ Descargar metadatos del estudio (JSON)",
            data=json.dumps(metadatos, indent=2, ensure_ascii=False),
            file_name="metadatos_encuesta_fase1.json",
            mime="application/json",
            width="stretch",
        )

# ==============================================================================
# 9. PIE DE PÁGINA
# ==============================================================================
st.markdown(
    """
<div class="footer-web">
    Proyecto Integrador de Diseño de Máquinas · Ingeniería Mecatrónica · Escuela Politécnica Nacional (EPN) · Aplicación pública en Python y Streamlit
</div>
""",
    unsafe_allow_html=True,
)
