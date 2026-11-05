import streamlit as st
from evaluator_agent import ProjectEvaluatorAgent
import os

st.set_page_config(page_title="Evaluador SystemGuard SGAS", page_icon="💻", layout="centered")

st.title("🛡️ SystemGuard & Audit System (SGAS)")
st.subheader("Evaluador Automático en Tiempo Real - Certificado IFCD0112")
st.write(
    "Sube el documento de tu proyecto final en formato **.docx** para evaluar de forma instantánea el cumplimiento de las capas de Linux, Oracle 19c, Java y Web.")

uploaded_file = st.file_uploader("Selecciona o arrastra tu archivo de proyecto (.docx)", type=["docx"])

if uploaded_file is not None:
    # Guardar temporalmente el archivo
    temp_path = "temp_project.docx"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Ejecutar Evaluación Automática"):
        with st.spinner("Analizando código, scripts y estructura de capas..."):
            try:
                evaluator = ProjectEvaluatorAgent(temp_path)
                report = evaluator.run_evaluation()

                st.markdown("---")
                st.header("📊 Informe de Resultados")

                # Mostrar Nota Global
                if report['calificacion_final'] >= 5.0:
                    st.success(
                        f"### Calificación Final: {report['calificacion_final']} / 10.0 — **{report['resultado']}**")
                else:
                    st.error(
                        f"### Calificación Final: {report['calificacion_final']} / 10.0 — **{report['resultado']}**")

                # Desglose
                st.write("### 📌 Desglose por Módulos Formatívos:")
                col1, col2 = st.columns(2)
                for i, (mod, nota) in enumerate(report['desglose'].items()):
                    if i % 2 == 0:
                        col1.metric(label=mod, value=nota)
                    else:
                        col2.metric(label=mod, value=nota)

                # Observaciones y Feedback
                if report['observaciones_mejora']:
                    st.write("### ⚠️ Áreas de Mejora Detectadas:")
                    for obs in report['observaciones_mejora']:
                        st.warning(obs)
                else:
                    st.balloons()
                    st.success("¡Excelente trabajo! No se han detectado errores críticos en las capas evaluadas.")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el fichero: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)