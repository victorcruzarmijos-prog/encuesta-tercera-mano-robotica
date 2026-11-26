# Tercera Mano Robótica para Soldadura de PCBs — Plataforma de Encuesta y Analítica

Aplicación pública desarrollada en **Python y Streamlit** para la Primera Fase del Proyecto Integrador de **Diseño de Máquinas** (Ingeniería Mecatrónica, Facultad de Ingeniería Mecánica, Escuela Politécnica Nacional).

## Alcance
- Recolección de respuestas reales mediante formulario web anónimo conectado a Google Sheets (`Datos_Limpios`).
- Procesamiento estadístico interactivo con **Plotly** (porcentajes, frecuencias absolutas y acumuladas, histogramas, cruces de variables y mapas de calor).
- Jerarquización automática de la Voz del Cliente (VoC) con pesos normalizados (1 a 5) para alimentar la Primera Casa de Calidad (QFD).
- Exportación directa de la base anonimizada (`.csv`), resumen QFD (`.csv`) y metadatos del estudio (`.json`).

## Ejecución local
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
