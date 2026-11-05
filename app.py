import streamlit as st
from evaluator_agent import AdvancedProjectEvaluatorAgent
import os

st.set_page_config(page_title="Evaluador SystemGuard SGAS", page_icon="💻", layout="centered")

st.title("🛡️ SystemGuard & Audit System (SGAS)")
st.subheader("Evaluador Automático Inteligente - Certificado IFCD0112")
st.write(
    "Sube el documento de tu proyecto final en formato **.docx** para obtener una auditoría detallada de las capas de Linux, Oracle 19c, Java y Web.")

uploaded_file = st.file_uploader("Selecciona o arrastra tu archivo de proyecto (.docx)", type=["docx"])

if uploaded_file is not None:
    # Guardar temporalmente el archivo subido
    temp_path = "temp_project.docx"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Ejecutar Evaluación Avanzada"):
        with st.spinner("Analizando código, scripts y estructura de capas..."):
            try:
                # Instanciar el agente avanzado
                evaluator = AdvancedProjectEvaluatorAgent(temp_path)
                report = evaluator.run_evaluation()

                st.markdown("---")
                st.header("📊 Informe de Resultados del Proyecto")

                # Calificación Global y Resultado Apto / No Apto
                if report['calificacion_global'] >= 5.0:
                    st.success(
                        f"### Calificación Global: {report['calificacion_global']} / 10.0 — **{report['resultado']}**")
                else:
                    st.error(
                        f"### Calificación Global: {report['calificacion_global']} / 10.0 — **{report['resultado']}**")

                # Feedback Pedagógico
                st.info(f"💡 **Evaluación Docente:** {report['feedback_alumno']}")

                # Desglose Detallado por Módulos
                st.write("### 📌 Desglose Detallado por Módulos:")
                for modulo, datos in report['desglose_modulos'].items():
                    with st.expander(f"📁 {modulo} (Nota: {datos['nota']} / {datos['max']} Pts)"):
                        for detalle in datos['detalles']:
                            st.write(f"- {detalle}")

                # Puntos Fuertes
                if report['puntos_fuertes']:
                    st.write("### ✅ Puntos Fuertes Detectados:")
                    for fuerte in report['puntos_fuertes']:
                        st.success(f"• {fuerte}")

                # Áreas de Mejora
                if report['areas_de_mejora']:
                    st.write("### ⚠️ Áreas de Mejora / Correcciones:")
                    for mejora in report['areas_de_mejora']:
                        st.warning(f"• {mejora}")
                else:
                    st.balloons()
                    st.success("¡Enhorabuena! La entrega cubre todos los requerimientos de evaluación sin incidencias.")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el fichero: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)