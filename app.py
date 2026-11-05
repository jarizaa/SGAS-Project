import streamlit as st
from evaluator_agent import StrictProjectEvaluatorAgent
import os

# Configuración de la página web
st.set_page_config(
    page_title="Evaluador Estricto SystemGuard SGAS",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ SystemGuard & Audit System (SGAS)")
st.subheader("Plataforma de Evaluación Automática y Auditoría Técnica - IFCD0112")
st.write(
    "Sube el documento de tu proyecto final en formato **.docx** para realizar una auditoría completa "
    "y rigurosa de las capas de **Oracle Linux**, **Oracle Database 19c**, **Java POO** y **Frontal Web**."
)

uploaded_file = st.file_uploader("Selecciona o arrastra tu archivo de proyecto (.docx)", type=["docx"])

if uploaded_file is not None:
    temp_path = "temp_project.docx"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Ejecutar Auditoría Estricta"):
        with st.spinner("Realizando inspección profunda de código, permisos, transacciones y tests..."):
            try:
                # Instanciar el agente de evaluación v3.0
                evaluator = StrictProjectEvaluatorAgent(temp_path)
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

                # Alertas de Fallos Críticos de Seguridad o Estructura (si existen)
                if report.get('fallos_criticos'):
                    st.write("### 🚨 Fallos Críticos Detectados (Penalización Severa):")
                    for fallo in report['fallos_criticos']:
                        st.error(f"• {fallo}")

                # Desglose en Acordeones Desplegables por Módulo
                st.write("### 📌 Desglose y Verificación por Módulos Formativos:")
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
                    st.write("### ⚠️ Áreas de Mejora y Sugerencias de Corrección:")
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