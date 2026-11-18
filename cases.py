"""Carga las facturas de datos/facturas como casos de evaluación, con su etiqueta como salida esperada."""
import json
from pathlib import Path

from strands_evals import Case

from models import Invoice

DATOS = Path(__file__).parent / "datos"


def load_cases() -> list[Case]:
    cases = []
    for texto in sorted((DATOS / "facturas").glob("*.txt")):
        etiqueta = json.loads((DATOS / "etiquetas" / f"{texto.stem}.json").read_text(encoding="utf-8"))
        cases.append(
            Case[str, Invoice](
                name=texto.stem,
                input=texto.read_text(encoding="utf-8"),
                expected_output=Invoice(**etiqueta),
            )
        )
    return cases
