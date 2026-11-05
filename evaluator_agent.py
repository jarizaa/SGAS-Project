import os
import re
import json
import docx


class AdvancedProjectEvaluatorAgent:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.text_content = ""
        self.desglose = {}
        self.puntos_fuertes = []
        self.areas_mejora = []
        self._load_document()

    def _load_document(self):
        if not os.path.exists(self.docx_path):
            raise FileNotFoundError(f"No se encontró el archivo: {self.docx_path}")
        doc = docx.Document(self.docx_path)
        full_text = []
        for p in doc.paragraphs:
            full_text.append(p.text)
        for t in doc.tables:
            for row in t.rows:
                for cell in row.cells:
                    full_text.append(cell.text)
        self.text_content = "\n".join(full_text)

    def evaluate_linux(self):
        nota = 0.0
        max_nota = 2.0
        detalles = []

        # 1. Permisos y Usuarios (0.5 pt)
        if ("chmod 700" in self.text_content or "chmod -R 700" in self.text_content) and (
                "sgas_user" in self.text_content and "dba_sgas" in self.text_content):
            nota += 0.50
            self.puntos_fuertes.append(
                "Capa Linux: Asignación correcta de usuario/grupo de servicio y permisos octales restrictivos (700).")
            detalles.append("Permisos y Usuarios: 0.50/0.50 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Linux: Revisar la asignación de permisos octales (chmod 700) y la creación de usuario/grupo (sgas_user:dba_sgas).")
            detalles.append("Permisos y Usuarios: 0.00/0.50 Pts (Incompleto)")

        # 2. Configuración LVM (0.5 pt)
        if "vgcreate" in self.text_content and "lvcreate" in self.text_content and "ext4" in self.text_content:
            nota += 0.50
            self.puntos_fuertes.append(
                "Capa Linux: Correcta estructura de volúmenes lógicos (LVM) formateados en ext4 para aislar BD y Logs.")
            detalles.append("Almacenamiento LVM: 0.50/0.50 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Linux: Falta la especificación completa de volúmenes LVM (vgcreate/lvcreate) o formateo ext4.")
            detalles.append("Almacenamiento LVM: 0.00/0.50 Pts (Faltan comandos LVM)")

        # 3. Script Bash (0.5 pt)
        if "#!/bin/bash" in self.text_content and "metrics.log" in self.text_content:
            nota += 0.50
            self.puntos_fuertes.append(
                "Capa Linux: Daemon de monitorización Bash funcional con volcado estructurado en métricas de log.")
            detalles.append("Script Bash Monitor: 0.50/0.50 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Linux: El script de monitorización Bash no está completo o no vuelca métricas en log.")
            detalles.append("Script Bash Monitor: 0.00/0.50 Pts (Incompleto)")

        # 4. Servicio Systemd (0.5 pt)
        if "[Unit]" in self.text_content and "ExecStart" in self.text_content:
            nota += 0.50
            self.puntos_fuertes.append(
                "Capa Linux: Unidad de servicio Systemd (.service) bien configurada para ejecución desatendida.")
            detalles.append("Servicio Systemd: 0.50/0.50 Pts (Correcto)")
        else:
            self.areas_mejora.append("Capa Linux: Definición de servicio Systemd ausente o sintaxis incorrecta.")
            detalles.append("Servicio Systemd: 0.00/0.50 Pts (No detectado)")

        self.desglose["MF0223_3_Linux"] = {
            "nota": round(nota, 2),
            "max": max_nota,
            "detalles": detalles
        }

    def evaluate_oracle(self):
        nota = 0.0
        max_nota = 3.5
        detalles = []

        # 1. DDL y 3FN (1.0 pt)
        if "CREATE TABLE INCIDENCIAS" in self.text_content and "FOREIGN KEY" in self.text_content and "CREATE INDEX" in self.text_content:
            nota += 1.00
            self.puntos_fuertes.append(
                "Capa Oracle: Modelo relacional normalizado en 3FN con claves foráneas e índices B-Tree.")
            detalles.append("Diseño DDL & 3FN: 1.00/1.00 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Oracle: Revisar el esquema DDL (falta definición de claves foráneas o índices B-Tree).")
            detalles.append("Diseño DDL & 3FN: 0.00/1.00 Pts (Incompleto)")

        # 2. Trigger PL/SQL (1.25 pt)
        if "CREATE OR REPLACE TRIGGER" in self.text_content and ":OLD" in self.text_content and ":NEW" in self.text_content:
            nota += 1.25
            self.puntos_fuertes.append(
                "Capa Oracle: Disparador de auditoría PL/SQL correctamente implementado con pseudoregistros :OLD y :NEW.")
            detalles.append("Trigger Auditoría PL/SQL: 1.25/1.25 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Oracle: El trigger de auditoría no utiliza adecuadamente los pseudoregistros :OLD y :NEW.")
            detalles.append("Trigger Auditoría PL/SQL: 0.00/1.25 Pts (Error en pseudoregistros)")

        # 3. Procedimiento Almacenado & Transacciones (1.25 pt)
        if "CREATE OR REPLACE PROCEDURE" in self.text_content and "COMMIT" in self.text_content and "ROLLBACK" in self.text_content:
            nota += 1.25
            self.puntos_fuertes.append(
                "Capa Oracle: Procedimiento almacenado transaccional con control explícito (COMMIT/ROLLBACK) y gestión de excepciones.")
            detalles.append("Procedimiento Almacenado: 1.25/1.25 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Oracle: Falta el control transaccional explícito (COMMIT/ROLLBACK) o bloque EXCEPTION en el SP.")
            detalles.append("Procedimiento Almacenado: 0.00/1.25 Pts (Falta control de transacciones)")

        self.desglose["MF0226_3_Oracle"] = {
            "nota": round(nota, 2),
            "max": max_nota,
            "detalles": detalles
        }

    def evaluate_java(self):
        nota = 0.0
        max_nota = 3.0
        detalles = []

        # 1. Encapsulación y Modelo (0.75 pt)
        if (
                "private int idIncidencia" in self.text_content or "private String" in self.text_content) and "getIdIncidencia" in self.text_content:
            nota += 0.75
            self.puntos_fuertes.append(
                "Capa Java: Clases de dominio correctamente encapsuladas con atributos privados y getters/setters.")
            detalles.append("Modelo de Dominio POO: 0.75/0.75 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Java: Asegurar la correcta encapsulación de los atributos privados en las clases de modelo.")
            detalles.append("Modelo de Dominio POO: 0.00/0.75 Pts (Incompleto)")

        # 2. Patrón DAO y JDBC (1.25 pt)
        if "PreparedStatement" in self.text_content and "ResultSet" in self.text_content and "executeQuery" in self.text_content:
            nota += 1.25
            self.puntos_fuertes.append(
                "Capa Java: Patrón DAO e integración JDBC nativa utilizando PreparedStatement y ResultSet de forma segura.")
            detalles.append("Patrón DAO & JDBC: 1.25/1.25 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Java: No se detectó el uso correcto de PreparedStatement y ResultSet en la capa DAO.")
            detalles.append("Patrón DAO & JDBC: 0.00/1.25 Pts (Uso incorrecto de JDBC)")

        # 3. Pruebas Unitarias JUnit (1.0 pt)
        if "@Test" in self.text_content and ("assertTrue" in self.text_content or "assertEquals" in self.text_content):
            nota += 1.00
            self.puntos_fuertes.append(
                "Capa Java: Batería de pruebas unitarias con JUnit aplicando aserciones y metodología de testeo.")
            detalles.append("Pruebas Unitarias JUnit: 1.00/1.00 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Java: Incluir pruebas unitarias JUnit explícitas con aserciones (assertTrue, assertEquals).")
            detalles.append("Pruebas Unitarias JUnit: 0.00/1.00 Pts (Faltan Tests/Aserciones)")

        self.desglose["MF0227_3_Java"] = {
            "nota": round(nota, 2),
            "max": max_nota,
            "detalles": detalles
        }

    def evaluate_web(self):
        nota = 0.0
        max_nota = 1.5
        detalles = []

        # 1. Servlet Controller (0.75 pt)
        if "@WebServlet" in self.text_content or "HttpServlet" in self.text_content:
            nota += 0.75
            self.puntos_fuertes.append("Capa Web: Controlador Servlet HTTP configurado procesando peticiones GET/POST.")
            detalles.append("Controlador Servlet HTTP: 0.75/0.75 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Web: Implementar el controlador Servlet anotado con @WebServlet para atender solicitudes HTTP.")
            detalles.append("Controlador Servlet HTTP: 0.00/0.75 Pts (No detectado)")

        # 2. Vista Dashboard (0.75 pt)
        if "<table>" in self.text_content or "dashboard.jsp" in self.text_content:
            nota += 0.75
            self.puntos_fuertes.append(
                "Capa Web: Vista gráfica (HTML/JSP) renderizando la tabla de incidencias y formulario de actualización.")
            detalles.append("Vista Dashboard Web: 0.75/0.75 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Capa Web: Construir la vista HTML/JSP del Cuadro de Mando con tabla de presentación.")
            detalles.append("Vista Dashboard Web: 0.00/0.75 Pts (No detectada)")

        self.desglose["MF0227_3_Web"] = {
            "nota": round(nota, 2),
            "max": max_nota,
            "detalles": detalles
        }

    def _generate_feedback(self, nota_total):
        if nota_total >= 9.0:
            return "¡Excelente trabajo! La entrega cumple de forma sobresaliente con todos los requisitos técnicos de la infraestructura Linux, arquitectura Oracle 19c, backend Java POO y frontal Web."
        elif nota_total >= 7.0:
            return "Muy buen proyecto. La solución es totalmente funcional y demuestra un sólido dominio técnico de los contenidos del certificado IFCD0112."
        elif nota_total >= 5.0:
            return "Proyecto Aprobado. La entrega cumple con la funcionalidad mínima requerida, aunque existen aspectos de mejora en algunas capas técnicas que deben revisarse."
        else:
            return "Proyecto No Apto. La entrega presenta carencias importantes en la implementación de las capas requeridas. Se recomienda revisar los puntos indicados en las áreas de mejora."

    def run_evaluation(self):
        self.evaluate_linux()
        self.evaluate_oracle()
        self.evaluate_java()
        self.evaluate_web()

        nota_final = sum(item["nota"] for item in self.desglose.values())
        nota_final = round(nota_final, 2)
        resultado = "APTO" if nota_final >= 5.0 else "NO APTO"

        report = {
            "proyecto": os.path.basename(self.docx_path),
            "calificacion_global": nota_final,
            "resultado": resultado,
            "desglose_modulos": self.desglose,
            "puntos_fuertes": self.puntos_fuertes,
            "areas_de_mejora": self.areas_mejora,
            "feedback_alumno": self._generate_feedback(nota_final)
        }
        return report


# Ejemplo de ejecución CLI
if __name__ == "__main__":
    import sys

    file_target = sys.argv[1] if len(sys.argv) > 1 else "Solucionario_Proyecto_Final_SystemGuard_IFCD0112.docx"

    if os.path.exists(file_target):
        agent = AdvancedProjectEvaluatorAgent(file_target)
        result = agent.run_evaluation()
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print(f"Escriba la ruta de un archivo .docx válido. Archivo '{file_target}' no encontrado.")
