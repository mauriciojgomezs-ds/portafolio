import csv
import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

OPERATIONS = {"sum", "mean", "group_sum", "missing", "duplicates", "unsupported"}


def number(value):
    # Contrato CSV: punto decimal, sin separadores de miles.
    if not value.strip():
        return None
    try:
        result = Decimal(value)
        return result if result.is_finite() else None
    except InvalidOperation:
        return None


def read_table(path):
    raw = Path(path).read_bytes()
    with Path(path).open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        if not columns or len(set(columns)) != len(columns) or any(not column for column in columns):
            raise ValueError("Encabezados vacíos o duplicados.")
        rows = list(reader)
    if not rows:
        raise ValueError("El CSV no contiene filas.")
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("Filas con cantidad de columnas distinta del encabezado.")
    return columns, rows, hashlib.sha256(raw).hexdigest()


def profile(columns, rows):
    result = {"rows": len(rows), "columns": {}, "duplicate_rows": sum(count - 1 for count in Counter(tuple(row[column] for column in columns) for row in rows).values())}
    for column in columns:
        missing = sum(not row[column].strip() for row in rows)
        valid = [number(row[column]) for row in rows if number(row[column]) is not None]
        result["columns"][column] = {"missing": missing, "numeric_valid": len(valid), "non_numeric_nonempty": len(rows) - missing - len(valid)}
    return result


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower().strip().rstrip("?.")) if unicodedata.category(c) != "Mn")


def local_plan(question, columns):
    text = normalize(question).lstrip("¿")
    if text in {"cuantas filas duplicadas hay", "duplicados"}:
        return {"operation": "duplicates", "column": None, "group_by": None}
    if text in {"cuantos valores faltantes hay", "faltantes"}:
        return {"operation": "missing", "column": None, "group_by": None}
    names = {normalize(column): column for column in columns}
    match = re.fullmatch(r"(?:cual es el )?(total|promedio) de ([\w ]+?)(?: por ([\w ]+))?", text)
    if match and match[2] in names and (not match[3] or match[3] in names):
        op = "group_sum" if match[3] and match[1] == "total" else "mean" if match[1] == "promedio" and not match[3] else "sum" if not match[3] else "unsupported"
        return {"operation": op, "column": names[match[2]], "group_by": names.get(match[3])}
    return {"operation": "unsupported", "column": None, "group_by": None}


def plan_schema(columns):
    nullable = {"type": ["string", "null"], "enum": [*columns, None]}
    return {"type": "object", "additionalProperties": False, "properties": {"operation": {"type": "string", "enum": sorted(OPERATIONS)}, "column": nullable, "group_by": nullable}, "required": ["operation", "column", "group_by"]}


def execute(plan, columns, rows):
    if not isinstance(plan, dict) or set(plan) != {"operation", "column", "group_by"} or plan["operation"] not in OPERATIONS:
        raise ValueError("Plan de análisis inválido.")
    op, col, group = plan["operation"], plan["column"], plan["group_by"]
    if op in {"missing", "duplicates", "unsupported"}:
        if col is not None or group is not None:
            raise ValueError("Esta operación no admite columnas ni agrupación.")
        if op == "unsupported":
            return {"status": "unsupported", "message": "Pregunta fuera del alcance: no se ejecutará código generado ni se inferirán causas."}
        p = profile(columns, rows)
        return {"status": "calculated", "value": p["duplicate_rows"] if op == "duplicates" else {column: p["columns"][column]["missing"] for column in columns}}
    if col not in columns or (op == "group_sum" and group not in columns) or (op != "group_sum" and group is not None):
        raise ValueError("Columnas o agrupación no permitidas.")
    valid = [(i + 2, row, number(row[col])) for i, row in enumerate(rows) if number(row[col]) is not None]
    invalid = [i + 2 for i, row in enumerate(rows) if row[col].strip() and number(row[col]) is None]
    missing = [i + 2 for i, row in enumerate(rows) if not row[col].strip()]
    if not valid:
        raise ValueError("La columna no contiene valores numéricos válidos.")
    if op == "group_sum":
        groups = defaultdict(Decimal)
        for _, row, value in valid:
            groups[row[group]] += value
        value = {key: str(amount) for key, amount in sorted(groups.items())}
    else:
        total = sum((value for _, _, value in valid), Decimal(0))
        value = str(total if op == "sum" else total / len(valid))
    return {"status": "calculated", "value": value, "valid_rows": len(valid), "missing_line_numbers": missing, "invalid_line_numbers": invalid, "policy": "Cálculo sobre valores válidos; filas duplicadas conservadas; faltantes y no numéricos excluidos y declarados. Importes sin conversión de moneda."}
