import json
import os
import urllib.error
import urllib.request

from .questions import INSTRUCTIONS, SCHEMA


class ProviderError(RuntimeError):
    pass


def parse_response(response):
    if response.get("status") != "completed":
        raise ProviderError("La respuesta del proveedor no está completa; no se publicará como una respuesta válida.")
    content = [part for item in response.get("output", []) if item.get("type") == "message" for part in item.get("content", [])]
    if any(part.get("type") == "refusal" for part in content):
        raise ProviderError("El proveedor rechazó la consulta.")
    text = "".join(part.get("text", "") for part in content if part.get("type") == "output_text")
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ProviderError("El proveedor no devolvió el JSON esperado.") from exc


def ask_openai(context, model=None, timeout=60):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = (model or os.environ.get("OPENAI_MODEL", "")).strip()
    if not api_key:
        raise ProviderError("Falta OPENAI_API_KEY. Configúrala en tu entorno; no la escribas en archivos del proyecto ni en el chat.")
    if not model:
        raise ProviderError("Indica --model o configura OPENAI_MODEL con un modelo compatible con Responses y salidas estructuradas.")
    payload = {
        "model": model, "store": False, "max_output_tokens": 4000,
        "instructions": INSTRUCTIONS,
        "input": json.dumps(context, ensure_ascii=False),
        "text": {"format": {"type": "json_schema", "name": "meeting_answer", "strict": True, "schema": SCHEMA}},
    }
    request = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(payload).encode("utf-8"), headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as result:
            response = json.load(result)
    except urllib.error.HTTPError as exc:
        messages = {401: "Credencial rechazada", 403: "Acceso no autorizado al modelo", 429: "Límite de uso o cuota alcanzado", 400: "Modelo o petición incompatibles"}
        raise ProviderError(f"{messages.get(exc.code, 'Error del proveedor')} (HTTP {exc.code}).") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ProviderError("No se pudo completar la conexión con el proveedor.") from None
    except (json.JSONDecodeError, UnicodeError):
        raise ProviderError("El proveedor devolvió una respuesta ilegible.") from None
    return parse_response(response), {"provider": "openai", "model": response.get("model", model), "response_id": response.get("id"), "usage": response.get("usage")}
