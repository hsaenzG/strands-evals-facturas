"""Por qué la igualdad exacta no alcanza: Equals contra StructuredOutputSimilarity, sin llamar a ningún modelo."""
from strands_evals import Case, Experiment
from strands_evals.evaluators import Equals, StructuredOutputSimilarity

from cases import load_cases
from models import Invoice

original = load_cases()[0]  # factura-01-mx, con su etiqueta como salida esperada
expected: Invoice = original.expected_output

predicciones = {
    "igual a la etiqueta": expected,
    "partidas en otro orden": expected.model_copy(update={"line_items": list(reversed(expected.line_items))}),
    "total con 0.0001 de diferencia": expected.model_copy(update={"total": expected.total + 0.0001}),
    "un solo campo mal (total)": expected.model_copy(update={"total": expected.total / 1000}),
    "todo mal": Invoice(
        issuer_name="x", issuer_tax_id="x", invoice_uuid="x", issue_date="2000-01-01", tax_amount=0, total=0, line_items=[]
    ),
}
cases = [Case[str, Invoice](name=n, input=original.input, expected_output=expected) for n in predicciones]


def tarea(case: Case) -> Invoice:
    return predicciones[case.name]


reportes = {
    "Equals": Experiment(cases=cases, evaluators=[Equals()]).run_evaluations(tarea),
    "StructuredOutputSimilarity": Experiment(cases=cases, evaluators=[StructuredOutputSimilarity(Invoice)]).run_evaluations(tarea),
}

print(f"{'predicción':<34}" + "".join(f"{nombre:<30}" for nombre in reportes))
for i, nombre in enumerate(predicciones):
    fila = f"{nombre:<34}"
    for reporte in reportes.values():
        fila += f"{reporte.scores[i]:.2f} {'PASS' if reporte.test_passes[i] else 'FAIL':<24}"
    print(fila)
