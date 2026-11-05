import os
import re
import json
import docx


class StrictProjectEvaluatorAgent:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.text_content = ""
        self.raw_text_lower = ""
        self.desglose = {}
        self.puntos_fuertes = []
        self.areas_mejora = []
        self.fallos_criticos = []
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
        self.raw_text_lower = self.text_content.lower()

    def evaluate_linux(self):
        """ Auditoría estricta de la Capa 1: Oracle Linux (2.0 Pts) """
        nota = 0.0
        max_nota = 2.0
        detalles = []

        # 1. Usuarios, Grupos y Permisos (0.5 pt)
        has_group = "groupadd" in self.text_content or "dba_sgas" in self.text_content
        has_user = "useradd" in self.text_content or "sgas_user" in self.text_content
        has_perms = "chmod 700" in self.text_content or "chmod -R 700" in self.text_content or "rwx------" in self.text_content

        if has_group and has_user and has_perms:
            nota += 0.50
            self.puntos_fuertes.append(
                "Linux: Gestión correcta de grupos, usuarios de servicio (sgas_user) y permisos octales restrictivos (700).")
            detalles.append("Usuarios, Grupos y Permisos: 0.50/0.50 Pts (Correcto)")
        else:
            self.fallos_criticos.append(
                "Linux: Faltan comandos de creación de usuario/grupo o no se aplican permisos de seguridad estrictos (chmod 700).")
            detalles.append("Usuarios, Grupos y Permisos: 0.00/0.50 Pts (Fallo de seguridad o ausencia de comandos)")

        # 2. Almacenamiento LVM (0.5 pt)
        has_pv_vg = "pvcreate" in self.text_content and "vgcreate" in self.text_content
        has_lv = "lvcreate" in self.text_content and ("lv_db" in self.text_content or "lv_logs" in self.text_content)
        has_fs = "mkfs.ext4" in self.text_content or "ext4" in self.text_content

        if has_pv_vg and has_lv and has_fs:
            nota += 0.50
            self.puntos_fuertes.append(
                "Linux: Estructura LVM completa implementada (Physical Volume, Volume Group vg_sgas y Logical Volumes formateados en ext4).")
            detalles.append("Estructura LVM y Sistemas de Ficheros: 0.50/0.50 Pts (Correcto)")
        else:
            self.fallos_criticos.append(
                "Linux: Configuración de LVM incompleta (faltan comandos pvcreate, vgcreate, lvcreate o formateo ext4).")
            detalles.append("Estructura LVM y Sistemas de Ficheros: 0.00/0.50 Pts (Incompleto)")

        # 3. Script Bash de Monitorización (0.5 pt)
        has_shebang = "#!/bin/bash" in self.text_content
        has_metrics = "top" in self.text_content or "free" in self.text_content or "df" in self.text_content
        has_logging = "metrics.log" in self.text_content

        if has_shebang and has_metrics and has_logging:
            nota += 0.50
            self.puntos_fuertes.append(
                "Linux: Script Bash de monitorización implementado con captura de recursos del sistema y registro en log estructurado.")
            detalles.append("Script Bash Monitor: 0.50/0.50 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Linux: El script Bash de monitorización carece de comandos de recolección de métricas (top/free/df) o volcado en log.")
            detalles.append("Script Bash Monitor: 0.00/0.50 Pts (Incompleto)")

        # 4. Servicio Systemd (0.5 pt)
        has_unit = "[Unit]" in self.text_content or "description" in self.text_content.lower()
        has_service = "[Service]" in self.text_content and "ExecStart" in self.text_content
        has_restart = "restart" in self.text_content.lower()

        if has_unit and has_service and has_restart:
            nota += 0.50
            self.puntos_fuertes.append(
                "Linux: Fichero de servicio Systemd configurado correctamente con directivas de arranque y reintento.")
            detalles.append("Servicio Systemd: 0.50/0.50 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Linux: Estructura del servicio Systemd (.service) incompleta (faltan secciones [Unit], [Service] o directiva ExecStart).")
            detalles.append("Servicio Systemd: 0.00/0.50 Pts (Estructura inválida)")

        self.desglose["MF0223_3_Linux"] = {"nota": round(nota, 2), "max": max_nota, "detalles": detalles}

    def evaluate_oracle(self):
        """ Auditoría estricta de la Capa 2: Oracle Database 19c / PL/SQL (3.5 Pts) """
        nota = 0.0
        max_nota = 3.5
        detalles = []

        # 1. Diseño DDL y Normalización 3FN (1.0 pt)
        has_tables = "create table" in self.raw_text_lower and "incidencias" in self.raw_text_lower
        has_pk = "primary key" in self.raw_text_lower
        has_fk = "foreign key" in self.raw_text_lower or "references" in self.raw_text_lower
        has_index = "create index" in self.raw_text_lower

        if has_tables and has_pk and has_fk and has_index:
            nota += 1.00
            self.puntos_fuertes.append(
                "Oracle: Modelo relacional normalizado en 3FN con claves primarias, claves foráneas e índices B-Tree optimizados.")
            detalles.append("Esquema DDL, PK, FK e Índices: 1.00/1.00 Pts (Correcto)")
        else:
            self.fallos_criticos.append(
                "Oracle: Fallas estructurales en el DDL (ausencia de claves primarias, restricciones de claves foráneas o índices B-Tree).")
            detalles.append("Esquema DDL, PK, FK e Índices: 0.00/1.00 Pts (Faltan restricciones relacionales)")

        # 2. Trigger de Auditoría PL/SQL (1.25 pt)
        has_trigger_decl = "create or replace trigger" in self.raw_text_lower or "create trigger" in self.raw_text_lower
        has_pseudoregs = ":old" in self.raw_text_lower and ":new" in self.raw_text_lower
        has_trigger_dml = "insert into" in self.raw_text_lower and "historico" in self.raw_text_lower

        if has_trigger_decl and has_pseudoregs and has_trigger_dml:
            nota += 1.25
            self.puntos_fuertes.append(
                "Oracle: Trigger de auditoría PL/SQL implementado correctamente utilizando pseudoregistros :OLD y :NEW para control de cambios.")
            detalles.append("Trigger de Auditoría PL/SQL: 1.25/1.25 Pts (Correcto)")
        else:
            self.fallos_criticos.append(
                "Oracle: El trigger de auditoría PL/SQL está incompleto o no hace uso correcto de los pseudoregistros :OLD y :NEW.")
            detalles.append("Trigger de Auditoría PL/SQL: 0.00/1.25 Pts (Error en lógica de trigger)")

        # 3. Procedimiento Almacenado Transaccional (1.25 pt)
        has_sp_decl = "create or replace procedure" in self.raw_text_lower or "create procedure" in self.raw_text_lower
        has_tx_control = "commit" in self.raw_text_lower and "rollback" in self.raw_text_lower
        has_exception = "exception" in self.raw_text_lower or "raise_application_error" in self.raw_text_lower

        if has_sp_decl and has_tx_control and has_exception:
            nota += 1.25
            self.puntos_fuertes.append(
                "Oracle: Procedimiento almacenado transaccional robusto con control explícito (COMMIT/ROLLBACK) y manejo de excepciones.")
            detalles.append("Procedimiento Almacenado & Transacciones: 1.25/1.25 Pts (Correcto)")
        else:
            self.fallos_criticos.append(
                "Oracle: El procedimiento almacenado carece de control transaccional explícito (COMMIT/ROLLBACK) o bloques de excepción.")
            detalles.append("Procedimiento Almacenado & Transacciones: 0.00/1.25 Pts (Riesgo transaccional)")

        self.desglose["MF0226_3_Oracle"] = {"nota": round(nota, 2), "max": max_nota, "detalles": detalles}

    def evaluate_java(self):
        """ Auditoría estricta de la Capa 3: Java Backend / POO (3.0 Pts) """
        nota = 0.0
        max_nota = 3.0
        detalles = []

        # 1. Modelo de Dominio y Encapsulación (0.75 pt)
        has_class = "class incidenci" in self.raw_text_lower or "class servidor" in self.raw_text_lower
        has_private_fields = "private " in self.text_content
        has_getters_setters = "get" in self.text_content and "set" in self.text_content

        if has_class and has_private_fields and has_getters_setters:
            nota += 0.75
            self.puntos_fuertes.append(
                "Java: Clases del modelo de dominio correctamente encapsuladas con atributos privados y métodos de acceso.")
            detalles.append("Encapsulación y Modelo POO: 0.75/0.75 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Java: Incumplimiento del principio de encapsulamiento (atributos públicos o ausencia de getters/setters).")
            detalles.append("Encapsulación y Modelo POO: 0.00/0.75 Pts (Fallo de POO)")

        # 2. Patrón DAO y JDBC (1.25 pt)
        has_dao_pattern = "dao" in self.raw_text_lower or "repository" in self.raw_text_lower
        has_jdbc_prep = "preparedstatement" in self.raw_text_lower
        has_jdbc_res = "resultset" in self.raw_text_lower or "executequery" in self.raw_text_lower

        if has_dao_pattern and has_jdbc_prep and has_jdbc_res:
            nota += 1.25
            self.puntos_fuertes.append(
                "Java: Patrón DAO implementado correctamente mediante JDBC nativo utilizando PreparedStatement (prevención de SQL Injection) y ResultSet.")
            detalles.append("Patrón DAO e Integración JDBC: 1.25/1.25 Pts (Correcto)")
        else:
            self.fallos_criticos.append(
                "Java: Uso incorrecto o ausente de JDBC (no se utiliza PreparedStatement, exponiendo la aplicación a inyección SQL).")
            detalles.append("Patrón DAO e Integración JDBC: 0.00/1.25 Pts (Vulnerabilidad / DAO ausente)")

        # 3. Pruebas Unitarias JUnit (1.0 pt)
        has_junit_annot = "@test" in self.raw_text_lower
        has_assertions = "assert" in self.raw_text_lower

        if has_junit_annot and has_assertions:
            nota += 1.00
            self.puntos_fuertes.append(
                "Java: Batería de pruebas unitarias implementada con JUnit (@Test) y aserciones de verificación.")
            detalles.append("Pruebas Unitarias JUnit (AAA): 1.00/1.00 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Java: Ausencia de pruebas unitarias JUnit o falta de aserciones para validar el comportamiento del código.")
            detalles.append("Pruebas Unitarias JUnit (AAA): 0.00/1.00 Pts (Faltan tests)")

        self.desglose["MF0227_3_Java"] = {"nota": round(nota, 2), "max": max_nota, "detalles": detalles}

    def evaluate_web(self):
        """ Auditoría estricta de la Capa 4: Frontal Web (1.5 Pts) """
        nota = 0.0
        max_nota = 1.5
        detalles = []

        # 1. Controlador Servlet HTTP (0.75 pt)
        has_servlet_annot = "@webservlet" in self.raw_text_lower or "extends httpservlet" in self.raw_text_lower
        has_methods = "doget" in self.raw_text_lower and "dopost" in self.raw_text_lower

        if has_servlet_annot and has_methods:
            nota += 0.75
            self.puntos_fuertes.append(
                "Web: Controlador Servlet implementado correctamente procesando peticiones HTTP GET y POST.")
            detalles.append("Controlador Servlet HTTP: 0.75/0.75 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Web: Falta la implementación del Servlet HTTP o de los métodos doGet/doPost de control.")
            detalles.append("Controlador Servlet HTTP: 0.00/0.75 Pts (Incompleto)")

        # 2. Vista Dashboard HTML/JSP (0.75 pt)
        has_html_table = "<table" in self.raw_text_lower
        has_form = "<form" in self.raw_text_lower

        if has_html_table and has_form:
            nota += 0.75
            self.puntos_fuertes.append(
                "Web: Vista de Cuadro de Mando (JSP/HTML) con soporte para tablas de datos y formularios de actualización de estado.")
            detalles.append("Vista Dashboard Web: 0.75/0.75 Pts (Correcto)")
        else:
            self.areas_mejora.append(
                "Web: La vista web carece de tablas de visualización o formularios interactivos de gestión.")
            detalles.append("Vista Dashboard Web: 0.00/0.75 Pts (Incompleto)")

        self.desglose["MF0227_3_Web"] = {"nota": round(nota, 2), "max": max_nota, "detalles": detalles}

    def _generate_feedback(self, nota_total):
        if nota_total >= 9.0:
            return "Sobresaliente. El proyecto cumple rigurosamente con todas las especificaciones técnicas del certificado IFCD0112 en sus cuatro capas."
        elif nota_total >= 7.0:
            return "Notable. Excelente trabajo con alta solvencia técnica en la mayoría de los módulos. Se deben revisar mínimos detalles indicados."
        elif nota_total >= 5.0:
            return "Aprobado (Apto). El proyecto alcanza los mínimos exigidos por el estándar del SEPE, pero presenta áreas críticas mejorables."
        else:
            return "Suspenso (No Apto). La entrega contiene deficiencias graves o ausencia de componentes troncales obligatorios en las capas técnicas."

    def run_evaluation(self):
        self.evaluate_linux()
        self.evaluate_oracle()
        self.evaluate_java()
        self.evaluate_web()

        nota_final = sum(item["nota"] for item in self.desglose.values())
        nota_final = round(nota_final, 2)
        resultado = "APTO" if nota_final >= 5.0 else "NO APTO"

        return {
            "proyecto": os.path.basename(self.docx_path),
            "calificacion_global": nota_final,
            "resultado": resultado,
            "desglose_modulos": self.desglose,
            "puntos_fuertes": self.puntos_fuertes,
            "areas_de_mejora": self.areas_mejora,
            "fallos_criticos": self.fallos_criticos,
            "feedback_alumno": self._generate_feedback(nota_final)
        }