import streamlit as st
from evaluator_agent import RigorousProjectEvaluatorAgent
import os

# Configuración de la página web Streamlit
st.set_page_config(
    page_title="Evaluador Estricto SystemGuard SGAS (v4.0)",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ SystemGuard & Audit System (SGAS)")
st.subheader("Plataforma de Auditoría Técnica Rigurosa - Certificado IFCD0112")
st.write(
    "Sube la entrega del proyecto final en formato **.docx** para ejecutar una auditoría estricta "
    "sin suposiciones sobre las capas de **Oracle Linux**, **Oracle Database 19c**, **Java POO** y **Frontal Web**."
)

uploaded_file = st.file_uploader("Selecciona o arrastra el archivo .docx del proyecto", type=["docx"])

if uploaded_file is not None:
    temp_path = "temp_project.docx"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Ejecutar Auditoría Estricta v4.0"):
        with st.spinner("Inspeccionando comandos Linux, restricciones DDL/PLSQL, patrones DAO y tests JUnit..."):
            try:
                # Instanciar el agente de evaluación estricta v4.0
                evaluator = RigorousProjectEvaluatorAgent(temp_path)
                report = evaluator.run_evaluation()

                st.markdown("---")
                st.header("📊 Informe Diagnóstico de Resultados")

                # Resumen de Nota Global y Resultado (APTO / NO APTO)
                if report['calificacion_global'] >= 5.0:
                    st.success(
                        f"### Calificación Global: {report['calificacion_global']} / 10.0 — **{report['resultado']}**")
                else:
                    st.error(
                        f"### Calificación Global: {report['calificacion_global']} / 10.0 — **{report['resultado']}**")

                # Dictamen o Feedback Docente
                st.info(f"💡 **Dictamen del Evaluador:** {report['feedback_alumno']}")

                # Alertas de Fallos Críticos de Seguridad o Estructura
                if report.get('fallos_criticos'):
                    st.write("### 🚨 Fallos Críticos Detectados (Penalización Severa):")
                    for fallo in report['fallos_criticos']:
                        st.error(f"• {fallo}")

                # Desglose por Módulos Formativos
                st.write("### 📌 Desglose y Verificación por Módulos:")
                for modulo, datos in report['desglose_modulos'].items():
                    titulo_modulo = f"📁 {modulo} — Nota: {datos['nota']} / {datos['max']} Pts"
                    with st.expander(titulo_modulo):
                        for detalle in datos['detalles']:
                            if "Correcto" in detalle:
                                st.success(f"✔ {detalle}")
                            else:
                                st.warning(f"✖ {detalle}")

                # Puntos Fuertes
                if report['puntos_fuertes']:
                    st.write("### ✅ Puntos Fuertes e Implementaciones Correctas:")
                    for fuerte in report['puntos_fuertes']:
                        st.success(f"• {fuerte}")

                # Áreas de Mejora y Sugerencias de Corrección
                if report['areas_de_mejora']:
                    st.write("### ⚠️ Áreas de Mejora y Sugerencias:")
                    for mejora in report['areas_de_mejora']:
                        st.warning(f"• {mejora}")

                if not report['fallos_criticos'] and not report['areas_de_mejora']:
                    st.balloons()
                    st.success(
                        "¡Enhorabuena! La entrega no presenta ninguna deficiencia técnica ni fallo de seguridad.")

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)