import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Encuesta - Tercera Mano Robótica",
    layout="centered"
)

# === 1. PEGA AQUÍ TUS DOS ENLACES ===
URL_APPS_SCRIPT = "PEGA_AQUI_LA_URL_QUE_TERMINA_EN_EXEC"
ID_HOJA = "PEGA_AQUI_EL_IDENTIFICADOR_DE_TU_HOJA"
URL_CSV_HOJA = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=Datos_Limpios"

st.title("Encuesta: Tercera Mano Robótica para Soldadura de Placas")
st.write("Tus respuestas son totalmente anónimas y se usan solo con fines académicos.")

pestana_encuesta, pestana_resultados = st.tabs([
    "Responder encuesta",
    "Panel estadístico"
])

# === PESTAÑA 1: FORMULARIO OPERATIVO ===
with pestana_encuesta:
    with st.form("formulario_tercera_mano", clear_on_submit=True):
        st.subheader("Sección 1: Perfil del usuario")
        experiencia = st.selectbox(
            "1. Nivel de experiencia soldando placas electrónicas:",
            ["Principiante", "Intermedio", "Avanzado / Técnico"]
        )
        frecuencia = st.selectbox(
            "2. ¿Con qué frecuencia sueldas placas?",
            ["Esporádicamente (pocas veces al año)", "Mensualmente", "Semanalmente o a diario"]
        )

        st.subheader("Sección 2: Validación del problema")
        frustracion = st.slider(
            "3. Nivel de frustración al sujetar la placa, el cautín y el estaño al mismo tiempo (1 = baja, 5 = muy alta):",
            min_value=1, max_value=5, value=3
        )
        problema_principal = st.selectbox(
            "4. ¿Cuál es tu mayor dificultad al soldar?",
            [
                "Falta de una tercera mano para acercar el estaño",
                "Movimiento de la placa o componente",
                "Falta de precisión en puntos pequeños",
                "Quemaduras o fatiga en la mano"
            ]
        )

        st.subheader("Sección 3: Requerimientos funcionales")
        activacion = st.selectbox(
            "5. ¿Qué método prefieres para activar la alimentación de estaño?",
            ["Pedal de pie", "Botón manual", "Detección automática con cámara"]
        )
        caracteristica_clave = st.selectbox(
            "6. ¿Qué característica estructural consideras más importante?",
            ["Estabilidad de la base", "Resistencia térmica", "Diseño compacto"]
        )

        st.subheader("Sección 4: Interfaz y visión por computadora")
        calibracion = st.selectbox(
            "7. Tiempo máximo que aceptarías para calibrar el equipo antes de usarlo:",
            ["Menos de 1 minuto", "Entre 1 y 2 minutos", "Más de 2 minutos"]
        )
        privacidad = st.selectbox(
            "8. Respecto al uso de cámara para seguir la punta del cautín, prefieres:",
            ["Procesamiento local sin grabar video", "No me preocupa si requiere conexión"]
        )
        comentario = st.text_area(
            "9. Comentario o sugerencia adicional (opcional):",
            placeholder="Escribe aquí cualquier requerimiento extra..."
        )

        enviado = st.form_submit_button("Enviar respuesta")

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
                    st.success("¡Gracias! Tu respuesta anónima se guardó correctamente.")
                    st.cache_data.clear()
                else:
                    st.error("No se pudo guardar la respuesta. Intenta nuevamente.")
            except Exception as error:
                st.error(f"Error de conexión al guardar: {error}")

# === PESTAÑA 2: ANÁLISIS ESTADÍSTICO Y EXPORTACIÓN ===
with pestana_resultados:
    st.subheader("Resultados en tiempo real (datos anonimizados)")

    @st.cache_data(ttl=60)
    def cargar_datos():
        return pd.read_csv(URL_CSV_HOJA)

    try:
        tabla = cargar_datos()
        st.metric("Total de respuestas reales registradas", len(tabla))

        if len(tabla) > 0:
            if "Frustracion" in tabla.columns:
                promedio = tabla["Frustracion"].mean()
                desviacion = tabla["Frustracion"].std()
                st.write(f"**Nivel de frustración promedio:** {promedio:.2f} / 5 (desviación estándar: {desviacion:.2f})")

            columnas_graficar = [
                col for col in tabla.columns
                if col not in ["Fecha", "Comentario"]
            ]
            columna_elegida = st.selectbox(
                "Selecciona una variable para ver su distribución:",
                columnas_graficar
            )
            conteo = tabla[columna_elegida].value_counts()
            st.bar_chart(conteo)

            st.write("**Tabla de frecuencias y porcentajes:**")
            resumen = pd.DataFrame({
                "Frecuencia": conteo,
                "Porcentaje (%)": (conteo / len(tabla) * 100).round(1)
            })
            st.dataframe(resumen, use_container_width=True)

            csv_anonimo = tabla.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Descargar datos anonimizados (CSV)",
                data=csv_anonimo,
                file_name="datos_encuesta_anonimizados.csv",
                mime="text/csv"
            )
        else:
            st.info("Aún no existen respuestas registradas en la hoja.")
    except Exception as error:
        st.warning("Verifica que la hoja esté compartida como lector y el nombre de la pestaña sea Datos_Limpios.")
        st.caption(f"Detalle técnico: {error}")
