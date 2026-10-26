"""Consultas locales y preguntas con IA sobre una transcripción."""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.providers import ProviderError, ask_openai
from app.questions import PROMPT_VERSION, prepare, validate_answer


def timestamp(seconds):
    return f"{int(seconds) // 60:02d}:{int(seconds) % 60:02d}"


def run(question, transcript, agenda=None, provider="local", model=None, limit=6, max_chars=80000):
    started = time.perf_counter()
    candidates, context = prepare(question, transcript, agenda, limit, max_chars)
    result = {"meeting_id": transcript["meeting_id"], "question": question, "prompt_version": PROMPT_VERSION, "context_scope": context["context_scope"], "context_segment_ids": [segment["id"] for segment in context["segments"]], "gaps": context["gaps"]}
    if provider == "local":
        result.update(provider="local", mode="retrieval_only", candidates=candidates)
    elif provider == "openai":
        answer, metadata = ask_openai(context, model)
        result.update(metadata)
        result.update(mode="generated_answer", answer=validate_answer(answer, context))
    else:
        raise ValueError("Proveedor desconocido.")
    result["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    return result


def render(result):
    if result["mode"] == "retrieval_only":
        print("Búsqueda local: fragmentos candidatos, sin respuesta generada por IA.")
        if not result["candidates"]:
            print("No hay coincidencias léxicas. Esto no demuestra que el tema esté ausente.")
        for segment in result["candidates"]:
            print(f"\n[{segment['id']} · {timestamp(segment['start_seconds'])} · {segment['speaker']}] {segment['text']}")
    else:
        answer = result["answer"]
        print("Información insuficiente." if answer["status"] == "insufficient_evidence" else "Respuesta con citas verificadas literalmente:")
        for claim in answer["claims"]:
            print("\n" + claim["text"])
            for citation in claim["citations"]:
                print(f"  [{citation['segment_id']} · {timestamp(citation['start_seconds'])} · {citation['speaker']}] {citation['quote']}")
        for limitation in answer["limitations"]:
            print("\nLimitación: " + limitation)
    if result["gaps"]:
        print("\nLa transcripción contiene fragmentos ausentes; no inferir lo ocurrido en ellos.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Pregunta completa e independiente sobre la reunión")
    parser.add_argument("--transcript", type=Path, default=ROOT / "examples/transcript.json")
    parser.add_argument("--agenda", type=Path, help="Contexto previo opcional en JSON; no se considera evidencia de acuerdos")
    parser.add_argument("--provider", choices=["local", "openai"], default="local")
    parser.add_argument("--model", help="Modelo del proveedor; alternativamente OPENAI_MODEL")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--max-context-chars", type=int, default=80000)
    parser.add_argument("--output", type=Path, help="Guardar resultado JSON opcionalmente")
    args = parser.parse_args()
    if args.limit <= 0 or args.max_context_chars <= 0:
        parser.error("Los límites deben ser positivos.")
    try:
        transcript = json.loads(args.transcript.read_text(encoding="utf-8-sig"))
        agenda = json.loads(args.agenda.read_text(encoding="utf-8-sig")) if args.agenda else None
        result = run(args.question, transcript, agenda, args.provider, args.model, args.limit, args.max_context_chars)
        render(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (ProviderError, ValueError, OSError, KeyError, TypeError) as exc:
        print("No se pudo responder: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
