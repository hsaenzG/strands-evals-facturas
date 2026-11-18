"""Agente que extrae los datos de una factura electrónica con Amazon Nova en Amazon Bedrock."""
import os

from strands import Agent
from strands.models import BedrockModel
from strands_evals import Case

from models import Invoice

MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")
REGION = os.environ.get("AWS_REGION", "us-east-2")

PROMPTS = {
    "v1": (
        "Extrae los datos de la factura electrónica que recibes.\n"
        "Devuelve solo lo que dice el documento y no inventes ningún dato.\n"
    ),
    # v2 = v1 + una línea sobre los formatos de montos
    "v2": (
        "Extrae los datos de la factura electrónica que recibes.\n"
        "Devuelve solo lo que dice el documento y no inventes ningún dato.\n"
        "Los montos pueden venir con punto o coma como separador (1.234,50 o 1,234.50): "
        "devuélvelos siempre como número, sin separadores de miles.\n"
    ),
}
PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v1")


def extract(case: Case) -> Invoice:
    # Un agente nuevo por factura: así ninguna comparte historial con otra
    agent = Agent(
        model=BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0),
        system_prompt=PROMPTS[PROMPT_VERSION],
        callback_handler=None,
    )
    result = agent(case.input, structured_output_model=Invoice)
    return result.structured_output
