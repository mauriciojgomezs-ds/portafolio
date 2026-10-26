import hashlib
import json
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

FIELDS = {"supplier": "Proveedor", "invoice_id": "Número", "date": "Fecha", "currency": "Moneda", "net": "Neto", "tax": "IVA", "total": "Total"}


def ocr_pages(path, language="es"):
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        raise RuntimeError("OCR requiere paddleocr y un motor PaddlePaddle compatible; consulta la guía de instalación.") from None
    engine = PaddleOCR(lang=language, use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False)
    pages = []
    for i, result in enumerate(engine.predict(str(path)), 1):
        payload = result.json
        if isinstance(payload, str):
            payload = json.loads(payload)
        data = payload.get("res", payload)
        texts = data.get("rec_texts", [])
        if not texts:
            raise ValueError(f"OCR sin texto en página {i}; no se inventarán campos.")
        pages.append({"page": (data.get("page_index") + 1) if isinstance(data.get("page_index"), int) else i, "text": "\n".join(texts), "ocr_details": data})
    return pages


def convert(path, ocr=False):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        pages = [{"page": None, "text": path.read_text(encoding="utf-8-sig")}]
        method = "native_text"
    elif ext in {".png", ".jpg", ".jpeg"} or (ext == ".pdf" and ocr):
        pages, method = ocr_pages(path), "paddleocr"
    else:
        if ext not in {".pdf", ".docx", ".xlsx", ".pptx"}:
            raise ValueError("Formato no admitido en este MVP.")
        try:
            from markitdown import MarkItDown
        except ImportError:
            raise RuntimeError("Conversión requiere instalar requirements-conversion.txt en el entorno del proyecto.") from None
        result = MarkItDown(enable_plugins=False).convert_local(str(path))
        pages, method = [{"page": None, "text": result.markdown}], "markitdown"
    if not pages or not any(page["text"].strip() for page in pages):
        raise ValueError("Documento sin texto utilizable; prueba OCR explícito para un escaneo.")
    return {"source": path.name, "source_sha256": digest, "method": method, "pages": pages}


def extract_rules(document):
    fields = {}
    for key, label in FIELDS.items():
        matches = []
        for page in document["pages"]:
            for line_number, line in enumerate(page["text"].splitlines(), 1):
                match = re.fullmatch(r"\s*" + re.escape(label) + r"\s*:\s*(.+?)\s*", line, re.IGNORECASE)
                if match:
                    matches.append({"value": match[1], "quote": line, "page": page["page"], "line": line_number})
        if len(matches) > 1:
            raise ValueError(f"Campo {key} repetido; requiere revisión antes de elegir una versión.")
        fields[key] = matches[0] if matches else None
    return fields


def field_schema():
    item = {"anyOf": [{"type": "null"}, {"type": "object", "additionalProperties": False, "properties": {"value": {"type": "string"}, "quote": {"type": "string"}, "page": {"type": ["integer", "null"]}, "line": {"type": "integer"}}, "required": ["value", "quote", "page", "line"]}]}
    return {"type": "object", "additionalProperties": False, "properties": {key: item for key in FIELDS}, "required": list(FIELDS)}


def validate_fields(document, fields):
    if not isinstance(fields, dict) or set(fields) != set(FIELDS):
        raise ValueError("Campos extraídos inválidos.")
    for field in fields.values():
        if field is None:
            continue
        if not isinstance(field, dict) or set(field) != {"value", "quote", "page", "line"} or not isinstance(field["value"], str) or not field["value"].strip() or not isinstance(field["quote"], str) or not field["quote"].strip() or not isinstance(field["line"], int) or isinstance(field["line"], bool):
            raise ValueError("Campo sin valor o cita válida.")
        valid = False
        for page in document["pages"]:
            lines = page["text"].splitlines()
            if page["page"] == field["page"] and 1 <= field["line"] <= len(lines) and field["quote"] in lines[field["line"] - 1] and field["value"] in field["quote"]:
                valid = True
        if not valid:
            raise ValueError("Valor o cita no respaldados literalmente en la página y línea indicadas.")
    return fields


def amount(raw):
    # Convención chilena explícita: punto de miles y coma decimal.
    if not re.fullmatch(r"-?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{1,2})?", raw):
        raise ValueError("Importe inválido para la convención chilena.")
    return Decimal(raw.replace(".", "").replace(",", "."))


def validate_invoice(fields):
    issues = ["missing:" + key for key, value in fields.items() if value is None]
    values = {}
    for key in ("net", "tax", "total"):
        if fields[key]:
            try:
                values[key] = amount(fields[key]["value"])
            except ValueError:
                issues.append("invalid_amount:" + key)
    if fields["date"]:
        try:
            date.fromisoformat(fields["date"]["value"])
        except ValueError:
            issues.append("invalid_date")
    discrepancy = None
    if len(values) == 3:
        discrepancy = values["total"] - values["net"] - values["tax"]
        if discrepancy != 0:
            issues.append("total_mismatch")
    return {"issues": issues, "amounts": {key: str(value) for key, value in values.items()}, "total_discrepancy": str(discrepancy) if discrepancy is not None else None, "check": "net + tax = total; no se infiere tasa de IVA ni se convierten monedas"}


def summarize(records):
    seen = {}
    totals = {}
    for record in records:
        fields = record["fields"]
        identity = tuple(fields[key]["value"] if fields[key] else None for key in ("supplier", "invoice_id", "currency"))
        duplicate = all(identity) and identity in seen
        record["duplicate_of"] = seen.get(identity) if duplicate else None
        if all(identity) and not duplicate:
            seen[identity] = record["document"]["source"]
        # Excluir duplicados y documentos con cualquier aviso de validación.
        if not duplicate and not record["validation"]["issues"]:
            currency = fields["currency"]["value"]
            totals[currency] = totals.get(currency, Decimal(0)) + Decimal(record["validation"]["amounts"]["total"])
    return {"validated_total_by_currency": {key: str(value) for key, value in totals.items()}, "included_count": sum(not record["duplicate_of"] and not record["validation"]["issues"] for record in records), "policy": "Solo documentos completos, con importes válidos y sin discrepancias; duplicados excluidos; agrupación por moneda."}
