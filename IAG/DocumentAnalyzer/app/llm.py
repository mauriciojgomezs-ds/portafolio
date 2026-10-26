import json
import os
import urllib.error
import urllib.request


def request_json(instructions, context, schema, model=None):
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = (model or os.environ.get("OPENAI_MODEL", "")).strip()
    if not key or not model:
        raise RuntimeError("Configura OPENAI_API_KEY y OPENAI_MODEL en tu entorno; no pegues la clave en el chat ni en archivos versionados.")
    text = json.dumps(context, ensure_ascii=False)
    if len(text) > 80000:
        raise ValueError("Contexto superior a 80.000 caracteres; divide el documento antes de enviarlo.")
    payload = {"model": model, "store": False, "max_output_tokens": 4000, "instructions": instructions, "input": text, "text": {"format": {"type": "json_schema", "name": "analysis_result", "strict": True, "schema": schema}}}
    request = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Error HTTP {error.code} del proveedor; verifica modelo, acceso y cuota.") from None
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        raise RuntimeError("No se pudo completar la consulta al proveedor.") from None
    if not isinstance(result, dict) or result.get("status") != "completed":
        raise RuntimeError("Respuesta incompleta del proveedor.")
    parts = [part for item in result.get("output", []) if item.get("type") == "message" for part in item.get("content", [])]
    if any(part.get("type") == "refusal" for part in parts):
        raise RuntimeError("El proveedor rechazó la consulta.")
    try:
        return json.loads("".join(part.get("text", "") for part in parts if part.get("type") == "output_text"))
    except json.JSONDecodeError:
        raise RuntimeError("Respuesta sin el JSON esperado.") from None
