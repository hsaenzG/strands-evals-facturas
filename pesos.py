"""Cómo cambian los pesos el veredicto. No llama a ningún modelo: altera a mano un campo de una factura correcta."""
import datetime

from stickler import ComparableField, StructuredModel
from stickler.comparators import (
    DateComparator,
    ExactComparator,
    FuzzyComparator,
    LevenshteinComparator,
    NumericComparator,
)
from strands_evals import Case, Experiment
from strands_evals.evaluators import StructuredOutputSimilarity

from cases import load_cases
from models import Invoice


class WeightedLineItem(StructuredModel):
    description: str = ComparableField(comparator=FuzzyComparator(), threshold=0.6)
    quantity: int = ComparableField(comparator=NumericComparator(), threshold=1.0)
    unit_price: float = ComparableField(comparator=NumericComparator(relative_tolerance=0.001), threshold=0.95)


class WeightedInvoice(StructuredModel):
    # Un StructuredModel se usa tal cual: cada campo lleva su comparador, aunque solo cambies los pesos
    issuer_name: str = ComparableField(comparator=LevenshteinComparator(), threshold=0.85, weight=0.5)
    issuer_tax_id: str = ComparableField(comparator=ExactComparator(), weight=6.0)
    invoice_uuid: str = ComparableField(comparator=ExactComparator(), weight=6.0)
    issue_date: datetime.date = ComparableField(comparator=DateComparator(), threshold=0.95, weight=1.0)
    tax_amount: float = ComparableField(comparator=NumericComparator(relative_tolerance=0.001), threshold=0.95, weight=2.0)
    total: float = ComparableField(comparator=NumericComparator(relative_tolerance=0.001), threshold=0.95, weight=4.0)
    line_items: list[WeightedLineItem] = ComparableField(weight=1.0)


original = load_cases()[0]  # factura-01-mx, con su etiqueta como salida esperada
expected: Invoice = original.expected_output

# Un campo equivocado por escenario, todo lo demás igual a la etiqueta
equivocados = {
    "nombre-casi-igual": expected.model_copy(update={"issuer_name": "Distribuidora Aurora del Norte SA CV"}),
    "rfc-con-un-digito-mal": expected.model_copy(update={"issuer_tax_id": "DAN140822KP5"}),
    "uuid-con-un-digito-mal": expected.model_copy(update={"invoice_uuid": "3f9c1a52-7b8e-4d06-a1c3-9e2f5b7d4a19"}),
    "total-en-miles-mal": expected.model_copy(update={"total": expected.total / 1000}),
}
cases = [Case[str, Invoice](name=n, input=original.input, expected_output=expected) for n in equivocados]


def tarea(case: Case) -> Invoice:
    return equivocados[case.name]


configuraciones = {
    "sin pesos": StructuredOutputSimilarity(Invoice),
    "weight_hints=True": StructuredOutputSimilarity(Invoice, weight_hints=True),
    "pesos propios": StructuredOutputSimilarity(WeightedInvoice),
    "pesos + umbral 0.9": StructuredOutputSimilarity(WeightedInvoice, match_threshold=0.9),
}

print(f"{'escenario':<26}" + "".join(f"{nombre:<24}" for nombre in configuraciones))
resultados = {}
for nombre, evaluator in configuraciones.items():
    report = Experiment(cases=cases, evaluators=[evaluator]).run_evaluations(tarea)
    resultados[nombre] = list(zip(report.scores, report.test_passes))
for i, escenario in enumerate(equivocados):
    fila = f"{escenario:<26}"
    for nombre in configuraciones:
        score, passed = resultados[nombre][i]
        fila += f"{score:.2f} {'PASS' if passed else 'FAIL':<18}"
    print(fila)
