# Evalúa la salida estructurada de un agente, campo por campo, con Strands Evals

Demo del artículo "Evalúa la salida estructurada de tu agente, campo por campo, con Strands Evals".
Un agente en Amazon Bedrock (Amazon Nova) extrae los datos de una factura electrónica de LATAM y
`StructuredOutputSimilarity` califica cada campo contra una etiqueta, sin LLM como juez en el scoring.

Adapta, en español y con un caso propio, el post original de Strands:
[Evaluating structured agent output, field by field, with Strands Evals](https://strandsagents.com/blog/structured-output-similarity-strands-evals/).

## Qué hay aquí

| Archivo | Para qué sirve |
| --- | --- |
| `models.py` | El modelo Pydantic `Invoice`: lo usa el agente como salida y el evaluador como esquema |
| `extractor.py` | El agente (Amazon Nova en Bedrock) y dos versiones del prompt, `v1` y `v2` |
| `cases.py` | Carga `datos/facturas/*.txt` como casos, con `datos/etiquetas/*.json` como salida esperada |
| `evaluate.py` | El experimento: corre el agente, califica y muestra el puntaje por factura y los campos más débiles |
| `igualdad.py` | `Equals` contra `StructuredOutputSimilarity` con predicciones alteradas a mano. No llama a ningún modelo |
| `pesos.py` | Cómo cambian los pesos y el umbral el veredicto. No llama a ningún modelo |
| `compare_models.py` | El mismo experimento con Nova Micro, Lite y Pro, con los tokens consumidos |
| `datos/` | 8 facturas **ficticias** (México, Perú, Chile, Colombia, Argentina, Ecuador y Costa Rica) y sus etiquetas |

## Requisitos

- Python 3.10 o superior (probado en 3.13).
- Credenciales de AWS con acceso a los modelos Amazon Nova en Amazon Bedrock. Por defecto usa la región `us-east-2`
  y los perfiles de inferencia `us.amazon.nova-*`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Cómo correrlo

```bash
python evaluate.py                         # prompt v1, Nova Lite, sin pesos
PROMPT_VERSION=v2 python evaluate.py       # el prompt con la línea sobre los montos
python evaluate.py --weights               # con weight_hints=True
python pesos.py                            # pesos y umbral, sin llamar a ningún modelo
python compare_models.py v1                # Micro, Lite y Pro con el prompt v1
```

Variables opcionales: `MODEL_ID` (por defecto `us.amazon.nova-lite-v1:0`), `AWS_REGION`, `AWS_PROFILE`
y `PROMPT_VERSION` (`v1` o `v2`).

## Qué salió en mis corridas

Promedio del puntaje sobre las 8 facturas, con `temperature=0`. Entre paréntesis, cuántas corridas hice.

| Modelo | Prompt v1 | Prompt v2 |
| --- | --- | --- |
| Nova Micro | 1.000 (4) | 1.000 (4) |
| Nova Lite | 0.964 (7) | 1.000 (6) |
| Nova Pro | 1.000 (4) | 0.964 en 5 de 6 corridas, 0.982 en una |

- Con Nova Lite y el prompt v1, la factura chilena (`factura-04-cl`, en pesos sin decimales) saca 0.71: el modelo lee
  `$ 531.359` como `531.359` y `tax_amount` y `total` quedan mal. `v2` agrega una línea sobre los separadores de montos.
- Con Nova Pro, esa misma línea hace que a veces devuelva los identificadores fiscales sin puntos (`76482159-K`), y
  `issuer_tax_id` falla.
- El puntaje es determinista: las mismas dos salidas siempre dan el mismo número. El agente no lo es del todo, y Nova Pro
  con `v2` cambió entre corridas aunque `temperature` sea 0.

Son 8 facturas ficticias de 7 países, así que los números sirven para ver cómo funciona la evaluación y no como una medida
general de la exactitud de Nova.

## Nota

`report.to_file()` falla con salidas que contienen fechas (`datetime.date` no es serializable), así que `evaluate.py`
guarda el reporte con `model_dump_json()`. `StructuredOutputReport.from_file()` lo recarga sin problema.
