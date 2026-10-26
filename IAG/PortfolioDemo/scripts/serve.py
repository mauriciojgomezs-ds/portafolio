"""Demo local que invoca las aplicaciones reales, sin respuestas precargadas."""

import argparse
import base64
import json
import subprocess
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IAG = ROOT.parent
RUNS = ROOT / ".local" / "runs"
PROJECTS = {"data": "DataCopilot", "documents": "DocumentAnalyzer", "meetings": "MeetingCopilot"}


def query(body):
    if not isinstance(body, dict):
        raise ValueError("La consulta debe ser un objeto JSON.")
    project = body.get("project")
    if project not in PROJECTS:
        raise ValueError("Selecciona un proyecto válido.")
    question = body.get("question", "").strip()
    if not question or len(question) > 2000:
        raise ValueError("Escribe una pregunta de hasta 2.000 caracteres.")
    provider = body.get("provider", "local")
    if provider not in {"local", "openai"}:
        raise ValueError("Proveedor desconocido.")
    run_path = RUNS / str(uuid.uuid4())
    run_path.mkdir(parents=True)
    project_path = IAG / PROJECTS[project]
    uploads = []
    allowed = {"data": {".csv"}, "documents": {".md", ".txt", ".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg"}, "meetings": {".json"}}
    files = body.get("files", [])
    if len(files) > 10:
        raise ValueError("Máximo diez archivos por consulta.")
    for index, file in enumerate(files):
        suffix = Path(file["name"]).suffix.lower()
        if suffix not in allowed[project]:
            raise ValueError("Formato de archivo no admitido para este proyecto.")
        content = base64.b64decode(file["content"], validate=True)
        if len(content) > 5 * 1024 * 1024:
            raise ValueError("Cada archivo debe ocupar menos de 5 MB.")
        path = run_path / f"input_{index}{suffix}"
        path.write_bytes(content)
        uploads.append(path)
    if project in {"data", "meetings"} and len(uploads) > 1:
        raise ValueError("Este flujo admite un archivo por consulta.")
    if project == "data":
        output = run_path / "answer.json"
        command = [sys.executable, str(project_path / "scripts/analyze.py"), "--question", question, "--provider", provider, "--output", str(output)]
        if uploads:
            command += ["--csv", str(uploads[0])]
    elif project == "meetings":
        output = run_path / "answer.json"
        command = [sys.executable, str(project_path / "scripts/ask.py"), question, "--provider", provider, "--output", str(output)]
        if uploads:
            command += ["--transcript", str(uploads[0])]
        else:
            command += ["--agenda", str(project_path / "examples/agenda.json")]
    else:
        if provider != "local":
            raise ValueError("Esta demo documental solo ejecuta extracción y validación locales; no incluye chat documental generativo.")
        output = run_path / "result" / "demo.json"
        command = [sys.executable, str(project_path / "scripts/analyze.py"), *map(str, uploads), "--output", str(output.parent)]
        if body.get("ocr") is True:
            command.append("--ocr")
    completed = subprocess.run(command, cwd=project_path, capture_output=True, text=True, encoding="utf-8", timeout=65, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    if completed.returncode:
        message = completed.stderr.strip()
        if message.startswith("Traceback"):
            message = "El motor no pudo procesar la entrada. Revisa el formato o las dependencias opcionales del proyecto."
        raise ValueError(message or "No se pudo completar el análisis.")
    record = {"project": project, "question": question, "provider": provider, "result": json.loads(output.read_text(encoding="utf-8")), "run_id": run_path.name}
    (run_path / "conversation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, value):
        payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path != "/":
            return self.send_json(404, {"error": "Ruta no disponible"})
        content = (ROOT / "web/index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path != "/api/ask":
            return self.send_json(404, {"error": "Ruta no disponible"})
        # Evitar que otras páginas invoquen la API local sin interacción aquí.
        if self.headers.get("X-Portfolio-Demo") != "1":
            return self.send_json(403, {"error": "Petición ajena a la demo"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 8 * 1024 * 1024:
                raise ValueError("Petición vacía o superior a 8 MB.")
            body = json.loads(self.rfile.read(length))
            self.send_json(200, query(body))
        except subprocess.TimeoutExpired:
            self.send_json(504, {"error": "Se agotó el tiempo de análisis; no se mostrará un resultado anterior."})
        except (ValueError, KeyError, TypeError, OSError) as error:
            self.send_json(400, {"error": str(error)})

    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print(f"Demo disponible en http://127.0.0.1:{args.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
