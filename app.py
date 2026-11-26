import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Tercera Mano Robótica | Encuesta Oficial",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === CONFIGURACIÓN DE CONEXIÓN ===
# Mantén tu enlace de Apps Script entre comillas dobles:
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbyV4WUdP8vvEkRgqnWTvMyFdcXchyXtJXO8oKVX660rpj8SxVIbQrvO9fDp4n3FDH2Y/exec"
ID_HOJA = "1vn_id57bRE3l3dTh_ScTknJpTW3HDjmUnIA7tc4BX6M"
URL_CSV_HOJA = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=Datos_Limpios"

# === ESTILOS DE PÁGINA WEB (CSS) ===
st.markdown("""
<style>
    /* Ocultar menús y pie de página por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    header {visibility: hidden;}

    /* Contenedor centrado tipo sitio web */
    .block-container {
        max-width: 1050px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Portada superior (Hero) */
    .portada {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 60%, #0284c7 100%);
        color: #ffffff;
        padding: 2.5rem 2.2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.18);
    }
    .etiqueta-superior {
        display: inline-block;
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.25rem 0.85rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.4px;
        margin-bottom: 0.9rem;
    }
    .portada h1 {
        color: #ffffff;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0 0 0.6rem 0;
        line-height: 1.2;
    }
    .portada p {
        color: #e2e8f0;
        font-size: 1.02rem;
        margin: 0 0 1.2rem 0;
        max-width: 760px;
    }
    .insignias {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }
    .insignia {
        background: rgba(15, 23, 42, 0.35);
        color: #f8fafc;
        padding: 0.35rem 0.85rem;
        border-radius: 10px;
        font-size: 0.85rem;
    }

    /* Tarjetas informativas */
    .tarjeta {
        background: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 14px;
        padding: 1.35rem;
        height: 100%;
        margin-bottom: 1rem;
    }
    .tarjeta h3 {
        margin-top: 0;
        font-size: 1.08rem;
        color: #2563eb;
    }
    .tarjeta p {
        font-size: 0.94rem;
        margin-bottom: 0;
        opacity: 0.9;
    }

    /* Barra de navegación basada en pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.6rem;
        border-bottom: 2px solid rgba(148, 163, 184, 0.25);
        padding-bottom: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 0.6rem 1.3rem;
        font-weight: 600;
        font-size: 0.96rem;
    }

    /* Botón principal tipo web */
    .stFormSubmitButton button {
        background: linear-gradient(90deg, #1d4ed8 0%, #0284c7 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        width: 100%;
    }
    .stFormSubmitButton button:hover {
        opacity: 0.92;
        color: #ffffff;
    }

    /* Pie de página propio */
    .pie-web {
        margin-top: 2.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(148, 163, 184, 0.25);
        text-align: center;
        font-size: 0.85rem;
        opacity: 0.75;
    }
</style>
""", unsafe_allow_html=True)

# === PORTADA PRINCIPAL ===
st.markdown("""
<div class="portada">
    <div class="etiqueta-superior">PROYECTO INTEGRADOR · DISEÑO DE MÁQUINAS</div>
    <h1>Tercera Mano Robótica para Soldadura de Placas</h1>
    <p>
        Ayúdanos a definir los requerimientos técnicos de un asistente autónomo con visión
        por computadora capaz de seguir la punta del cautín y suministrar estaño con precisión.
    </p>
    <div class="insignias">
        <span class="insignia">⏱️ Duración: 2 minutos</span>
        <span class="insignia">🔒 100 % anónima</span>
        <span class="insignia">🎓 Uso estrictamente académico</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === MENÚ DE NAVEGACIÓN ===
tab_inicio, tab_encuesta, tab_resultados = st.tabs([
    "🏠 Inicio del proyecto",
    "📝 Responder encuesta",
    "📊 Resultados en vivo"
])

# === PÁGINA 1: INICIO ===
with tab_inicio:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="tarjeta">
            <h3>🎯 ¿Qué estamos diseñando?</h3>
            <p>Un asistente robótico de escritorio que identifica la posición del cautín
            y acerca el hilo de estaño al punto de soldadura, liberando tu mano libre.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="tarjeta">
            <h3>📐 ¿Para qué sirven tus datos?</h3>
            <p>Tus respuestas alimentan directamente el análisis estadístico y las Casas
            de Calidad (QFD) para priorizar precisión, ergonomía y seguridad.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="tarjeta">
            <h3>🛡️ Privacidad garantizada</h3>
            <p>No solicitamos nombres, correos ni datos personales. Todos los registros
            se almacenan y procesan de forma completamente anonimizada.</p>
        </div>
        """, unsafe_allow_html=True)

    st.info("👉 Haz clic en la pestaña **Responder encuesta** en la barra superior para participar.")

# === PÁGINA 2: ENCUESTA ===
with tab_encuesta:
    with st.form("formulario_tercera_mano", clear_on_submit=True):
        st.subheader("1. Perfil y contexto de uso")
        c1, c2 = st.columns(2)
        with c1:
            experiencia = st.selectbox(
                "Nivel de experiencia soldando placas electrónicas:",
                ["Principiante", "Intermedio", "Avanzado / Técnico"]
            )
        with c2:
            frecuencia = st.selectbox(
                "¿Con qué frecuencia sueldas placas?",
                ["Esporádicamente (pocas veces al año)", "Mensualmente", "Semanalmente o a diario"]
            )

        st.divider()
        st.subheader("2. Validación del problema")
        frustracion = st.slider(
            "Nivel de frustración al sujetar la placa, el cautín y el estaño al mismo tiempo (1 = baja, 5 = muy alta):",
            min_value=1, max_value=5, value=3
        )
        problema_principal = st.selectbox(
            "¿Cuál es tu mayor dificultad al soldar?",
            [
                "Falta de una tercera mano para acercar el estaño",
                "Movimiento de la placa o componente",
                "Falta de precisión en puntos pequeños",
                "Quemaduras o fatiga en la mano"
            ]
        )

        st.divider()
        st.subheader("3. Requerimientos funcionales")
        c3, c4 = st.columns(2)
        with c3:
            activacion = st.selectbox(
                "Método preferido para activar la alimentación de estaño:",
                ["Pedal de pie", "Botón manual", "Detección automática con cámara"]
            )
        with c4:
            caracteristica_clave = st.selectbox(
                "Característica estructural más importante:",
                ["Estabilidad de la base", "Resistencia térmica", "Diseño compacto"]
            )

        st.divider()
        st.subheader("4. Interfaz y visión por computadora")
        c5, c6 = st.columns(2)
        with c5:
            calibracion = st.selectbox(
                "Tiempo máximo aceptable de calibración inicial:",
                ["Menos de 1 minuto", "Entre 1 y 2 minutos", "Más de 2 minutos"]
            )
        with c6:
            privacidad = st.selectbox(
                "Respecto a la cámara para seguir la punta del cautín:",
                ["Procesamiento local sin grabar video", "No me preocupa si requiere conexión"]
            )

        comentario = st.text_area(
            "Comentario o sugerencia adicional (opcional):",
            placeholder="Cuéntanos qué función o mejora considerarías indispensable..."
        )

        enviado = st.form_submit_button("Enviar respuesta anónima")

        if enviado:
            datos = {
                "experiencia": experiencia,
                "frecuencia": frecuencia,
                "frustracion": frustracion,
                "problema_principal": problema_principal,
                "activacion": activacion,
                "caracteristica_clave": caracteristica_clave,
                "calibracion": calibracion,
                "privacidad": privacidad,
                "comentario": comentario
            }
            try:
                respuesta = requests.post(URL_APPS_SCRIPT, json=datos, timeout=15)
                if respuesta.status_code == 200:
                    st.success("¡Gracias por participar! Tu respuesta anónima fue registrada correctamente.")
                    st.cache_data.clear()
                else:
                    st.error("No se pudo guardar la respuesta. Intenta de nuevo en unos segundos.")
            except Exception as error:
                st.error(f"Error de conexión al guardar: {error}")

# === PÁGINA 3: PANEL ESTADÍSTICO ===
with tab_resultados:
    st.subheader("Análisis estadístico en tiempo real")

    @st.cache_data(ttl=60)
    def cargar_datos():
        return pd.read_csv(URL_CSV_HOJA)

    try:
        tabla = cargar_datos()
        total = len(tabla)

        m1, m2, m3 = st.columns(3)
        m1.metric("Respuestas reales", total)
        if total > 0 and "Frustracion" in tabla.columns:
            m2.metric("Frustración promedio", f"{tabla['Frustracion'].mean():.2f} / 5")
            desv = tabla["Frustracion"].std()
            m3.metric("Desviación estándar", f"{0.0 if pd.isna(desv) else desv:.2f}")
        else:
            m2.metric("Frustración promedio", "—")
            m3.metric("Desviación estándar", "—")

        if total > 0:
            st.divider()
            columnas_graficar = [
                col for col in tabla.columns
                if col not in ["Fecha", "Comentario"]
            ]
            columna_elegida = st.selectbox(
                "Selecciona una pregunta para analizar su distribución:",
                columnas_graficar
            )
            conteo = tabla[columna_elegida].value_counts()

            g1, g2 = st.columns([3, 2])
            with g1:
                st.bar_chart(conteo)
            with g2:
                resumen = pd.DataFrame({
                    "Frecuencia": conteo,
                    "Porcentaje (%)": (conteo / total * 100).round(1)
                })
                st.dataframe(resumen, use_container_width=True)

            csv_anonimo = tabla.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar base de datos anonimizada (CSV)",
                data=csv_anonimo,
                file_name="datos_encuesta_anonimizados.csv",
                mime="text/csv"
            )
        else:
            st.info("Todavía no hay respuestas registradas en la hoja.")
    except Exception as error:
        st.warning("Verifica que la hoja esté compartida como lector y que la pestaña se llame exactamente Datos_Limpios.")
        st.caption(f"Detalle técnico: {error}")

# === PIE DE PÁGINA ===
st.markdown("""
<div class="pie-web">
    Proyecto Integrador de Diseño de Máquinas · Encuesta pública desarrollada en Python y Streamlit · Datos 100 % anonimizados
</div>
""", unsafe_allow_html=True)
