import os
import docx

class ProjectEvaluatorAgent:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.text_content = ""
        self.scores = {
            "linux": 0.0,
            "oracle": 0.0,
            "java": 0.0,
            "web": 0.0
        }
        self.feedback = []
        self._load_document()

    def _load_document(self):
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
        score = 0.0
        if "chmod 700" in self.text_content or "chmod -R 700" in self.text_content:
            score += 0.25
        if "sgas_user" in self.text_content and "dba_sgas" in self.text_content:
            score += 0.25
        if "vgcreate" in self.text_content and "lvcreate" in self.text_content and "ext4" in self.text_content:
            score += 0.50
        else:
            self.feedback.append("Capa Linux: Falta la especificación completa de volúmenes LVM (vgcreate/lvcreate).")
        if "#!/bin/bash" in self.text_content and "metrics.log" in self.text_content:
            score += 0.50
        if "[Unit]" in self.text_content and "ExecStart" in self.text_content:
            score += 0.50
        self.scores["linux"] = score

    def evaluate_oracle(self):
        score = 0.0
        if "CREATE TABLE INCIDENCIAS" in self.text_content and "FOREIGN KEY" in self.text_content:
            score += 1.00
        if "CREATE OR REPLACE TRIGGER" in self.text_content and ":OLD" in self.text_content and ":NEW" in self.text_content:
            score += 1.25
        else:
            self.feedback.append("Capa Oracle: El trigger de auditoría no implementa adecuadamente los pseudoregistros :OLD y :NEW.")
        if "CREATE OR REPLACE PROCEDURE" in self.text_content and "COMMIT" in self.text_content and "ROLLBACK" in self.text_content:
            score += 1.25
        else:
            self.feedback.append("Capa Oracle: Falta el control transaccional explícito (COMMIT/ROLLBACK) en el SP.")
        self.scores["oracle"] = score

    def evaluate_java(self):
        score = 0.0
        if "private int idIncidencia" in self.text_content or "class Incidencia" in self.text_content:
            score += 0.75
        if "PreparedStatement" in self.text_content and "ResultSet" in self.text_content:
            score += 1.25
        else:
            self.feedback.append("Capa Java: No se detectó el uso correcto de PreparedStatement y ResultSet en el DAO.")
        if "@Test" in self.text_content:
            score += 1.00
        else:
            self.feedback.append("Capa Java: No se detectaron pruebas unitarias JUnit estructuradas (@Test).")
        self.scores["java"] = score

    def evaluate_web(self):
        score = 0.0
        if "@WebServlet" in self.text_content or "HttpServlet" in self.text_content:
            score += 0.75
        if "<table>" in self.text_content or "dashboard.jsp" in self.text_content:
            score += 0.75
        self.scores["web"] = score

    def run_evaluation(self):
        self.evaluate_linux()
        self.evaluate_oracle()
        self.evaluate_java()
        self.evaluate_web()

        nota_final = sum(self.scores.values())
        resultado = "APTO (Aprobado)" if nota_final >= 5.0 else "NO APTO (Suspenso)"

        return {
            "calificacion_final": round(nota_final, 2),
            "resultado": resultado,
            "desglose": {
                "MF0223_3 (Linux)": f"{self.scores['linux']} / 2.0 Pts",
                "MF0226_3 (Oracle BD)": f"{self.scores['oracle']} / 3.5 Pts",
                "MF0227_3 (Java POO)": f"{self.scores['java']} / 3.0 Pts",
                "MF0227_3 (Capa Web)": f"{self.scores['web']} / 1.5 Pts"
            },
            "observaciones_mejora": self.feedback
        }