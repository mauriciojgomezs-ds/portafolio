"""Validación del caso y cálculo desde una revisión explícita, sin IA ni red."""

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = {"fulfilled": 1.0, "partial": 0.5, "not_fulfilled": 0.0}
COVERAGE = {"discussed", "not_discussed", "unknown"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(agenda, transcript, review, qa):
    meeting_id = agenda["meeting_id"]
    require(all(item["meeting_id"] == meeting_id for item in (transcript, review, qa)), "Los archivos deben pertenecer a la misma reunión")
    objectives = {obj["id"]: obj for obj in agenda["objectives"]}
    require(bool(objectives) and len(objectives) == len(agenda["objectives"]), "Objetivos vacíos o repetidos")
    for obj in objectives.values():
        require(isinstance(obj["weight"], (int, float)) and not isinstance(obj["weight"], bool) and math.isfinite(obj["weight"]) and obj["weight"] > 0, "Peso inválido")
        require(bool(obj["fulfilled_criterion"]) and bool(obj["partial_criterion"]), "Faltan criterios previos")
    segments = {seg["id"]: seg for seg in transcript["segments"]}
    require(bool(segments) and len(segments) == len(transcript["segments"]), "Intervenciones vacías o repetidas")
    gaps = {gap["id"]: gap for gap in transcript["gaps"]}
    require(len(gaps) == len(transcript["gaps"]), "Lagunas repetidas")
    intervals = sorted([*segments.values(), *gaps.values()], key=lambda item: item["start_seconds"])
    previous_end = 0
    for interval in intervals:
        start, end = interval["start_seconds"], interval["end_seconds"]
        require(0 <= start < end <= transcript["duration_seconds"], "Tiempo fuera de rango")
        require(start == previous_end, "El caso debe declarar lagunas y no solapar intervenciones")
        previous_end = end
    require(previous_end == transcript["duration_seconds"], "Final sin transcribir ni declarar")
    review_ids = [row["objective_id"] for row in review["objectives"]]
    require(len(review_ids) == len(set(review_ids)) and set(review_ids) == set(objectives), "Revisión incompleta o duplicada")
    for row in review["objectives"]:
        require(row["coverage"] in COVERAGE, "Cobertura inválida")
        require(row["fulfillment"] in {*VALUES, "not_evaluable"}, "Cumplimiento inválido")
        require(bool(row["reason"]), "Falta explicación")
        if row["fulfillment"] in {"fulfilled", "partial"}:
            require(row["coverage"] == "discussed", "Un resultado acreditado requiere tratamiento del tema")
        if row["coverage"] == "unknown":
            require(row["fulfillment"] == "not_evaluable", "Cobertura desconocida no acredita cumplimiento")
        require(set(row.get("gap_ids", [])) <= set(gaps), "Laguna citada inexistente")
    question_ids = [case["id"] for case in qa["cases"]]
    require(len(question_ids) == len(set(question_ids)), "Preguntas repetidas")
    for row in [*review["objectives"], *qa["cases"]]:
        require(bool(row["evidence"]), "Falta evidencia")
        for evidence in row["evidence"]:
            require(evidence["segment_id"] in segments, "Intervención citada inexistente")
            require(bool(evidence["quote"]) and evidence["quote"] in segments[evidence["segment_id"]]["text"], "La cita no está en la intervención")


def calculate(agenda, review):
    weights = {obj["id"]: obj["weight"] for obj in agenda["objectives"]}
    rows = review["objectives"]
    total = sum(weights.values())
    evaluable = sum(weights[row["objective_id"]] for row in rows if row["fulfillment"] in VALUES)
    earned = sum(weights[row["objective_id"]] * VALUES[row["fulfillment"]] for row in rows if row["fulfillment"] in VALUES)
    known = [row for row in rows if row["coverage"] != "unknown"]
    discussed = [row for row in known if row["coverage"] == "discussed"]
    known_weight = sum(weights[row["objective_id"]] for row in known)
    discussed_weight = sum(weights[row["objective_id"]] for row in discussed)

    def percent(value, denominator):
        return round(100 * value / denominator, 2) if denominator else None

    return {
        "fulfillment_evaluable_pct": percent(earned, evaluable),
        "evaluable_weight_pct": percent(evaluable, total),
        "coverage_known_weight_pct": percent(discussed_weight, known_weight),
        "coverage_known_count_pct": percent(len(discussed), len(known)),
        "full_agenda_sensitivity_pct": [percent(earned, total), percent(earned + total - evaluable, total)],
        "earned_points": earned,
        "total_weight": total,
        "evaluable_weight": evaluable,
        "known_topics": len(known),
        "discussed_topics": len(discussed),
    }


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=ROOT / "examples/reference_review.json", help="Revisión explícita a validar y calcular")
    parser.add_argument("--output", type=Path, default=ROOT / "reports", help="Carpeta de resultados")
    args = parser.parse_args()
    agenda = load(ROOT / "examples/agenda.json")
    transcript = load(ROOT / "examples/transcript.json")
    qa = load(ROOT / "examples/reference_qa.json")
    review = load(args.review)
    validate(agenda, transcript, review, qa)
    metrics = calculate(agenda, review)
    result = {"meeting_id": agenda["meeting_id"], "synthetic": True, "review_origin": review["origin"], "generated_by": "Cálculo determinista desde revisión explícita; sin modelo de IA", "metrics": metrics, "objectives": review["objectives"]}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "demo.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def display(value):
        return f"{value:.2f} %" if value is not None else "No calculable"

    lines = ["# Resultado del caso sintético", "", "Calculado desde una revisión explícita. No es una evaluación producida por IA ni una medición de precisión del modelo.", "", f"Origen de la revisión: `{review['origin']}`.", "", "| Indicador | Resultado |", "| --- | --- |", f"| Cumplimiento ponderado evaluable | {display(metrics['fulfillment_evaluable_pct'])} |", f"| Peso evaluable de la agenda | {display(metrics['evaluable_weight_pct'])} |", f"| Cobertura ponderada conocida | {display(metrics['coverage_known_weight_pct'])} |", f"| Cobertura por temas conocidos | {display(metrics['coverage_known_count_pct'])} ({metrics['discussed_topics']} de {metrics['known_topics']}) |", f"| Sensibilidad sobre toda la agenda | {display(metrics['full_agenda_sensitivity_pct'][0])} a {display(metrics['full_agenda_sensitivity_pct'][1])} |", "", "La sensibilidad supone resultados mínimo y máximo para los objetivos no evaluables; no es un intervalo estadístico.", "", "| Objetivo | Cobertura | Cumplimiento | Evidencia |", "| --- | --- | --- | --- |"]
    for row in review["objectives"]:
        references = ", ".join(evidence["segment_id"] for evidence in row["evidence"])
        lines.append(f"| {row['objective_id']} | {row['coverage']} | {row['fulfillment']} | {references} |")
    lines += ["", "## Justificación", ""]
    for row in review["objectives"]:
        lines += [f"- **{row['objective_id']}:** {row['reason']}"]
    lines += ["", "Las citas literales se conservan en el JSON. La validación confirma su existencia, no su respaldo semántico. Una propuesta automática futura requerirá revisión y comparación con anotaciones independientes.", ""]
    (args.output / "demo.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Caso validado. Cumplimiento evaluable: {display(metrics['fulfillment_evaluable_pct'])}; peso evaluable: {display(metrics['evaluable_weight_pct'])}.")
    print(f"Resultados: {args.output.resolve()}")


if __name__ == "__main__":
    main()
