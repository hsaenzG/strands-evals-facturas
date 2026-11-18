"""Corre el experimento: el agente extrae cada factura y StructuredOutputSimilarity la califica campo por campo."""
import sys

from strands_evals import Experiment, StructuredOutputReport
from strands_evals.evaluators import StructuredOutputSimilarity

from cases import load_cases
from extractor import MODEL_ID, PROMPT_VERSION, extract
from models import Invoice

weight_hints = "--weights" in sys.argv

evaluator = StructuredOutputSimilarity(Invoice, weight_hints=weight_hints)
experiment = Experiment(cases=load_cases(), evaluators=[evaluator], report_cls=StructuredOutputReport)
report = experiment.run_evaluations(extract)

print(f"Modelo: {MODEL_ID} | prompt: {PROMPT_VERSION} | weight_hints={weight_hints}\n")
for case, score, passed, reason in zip(report.cases, report.scores, report.test_passes, report.reasons):
    print(f"{case['name']:<16} {score:.2f}  {'PASS' if passed else 'FAIL'}  {reason}")
print(f"\nPromedio: {sum(report.scores) / len(report.scores):.3f}")

print("\nCampos más débiles en toda la corrida (por F1):")
field_metrics = report.metrics().field_metrics
for path, m in sorted(field_metrics.items(), key=lambda kv: kv[1]["cm_f1"])[:5]:
    print(f"  {path:<24} f1={m['cm_f1']:.2f}  precision={m['cm_precision']:.2f}  recall={m['cm_recall']:.2f}")

print("\nQué leyó mal el agente:")
for case, fila in zip(report.cases, report.per_case()):
    for campo, puntaje in fila["field_scores"].items():
        if puntaje < 1.0:
            print(f"  {case['name']}.{campo}: esperado={case['expected_output'][campo]} obtenido={case['actual_output'][campo]}")

# to_file() no serializa las fechas; model_dump_json() sí, y from_file() lo recarga
with open("reporte.json", "w", encoding="utf-8") as archivo:
    archivo.write(report.model_dump_json(indent=2))
