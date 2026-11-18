"""Mismo experimento con Nova Micro, Lite y Pro: exactitud por campo y tokens consumidos."""
import sys

from strands import Agent
from strands.models import BedrockModel
from strands_evals import Case, Experiment, StructuredOutputReport
from strands_evals.evaluators import StructuredOutputSimilarity

from cases import load_cases
from extractor import PROMPTS, REGION
from models import Invoice

MODELOS = {
    "Nova Micro": "us.amazon.nova-micro-v1:0",
    "Nova Lite": "us.amazon.nova-lite-v1:0",
    "Nova Pro": "us.amazon.nova-pro-v1:0",
}
prompt_version = sys.argv[1] if len(sys.argv) > 1 else "v1"

print(f"Prompt {prompt_version}\n")
print(f"{'modelo':<12}{'promedio':>9}  {'facturas 1.00':>13}  {'tokens in':>10}  {'tokens out':>10}  campo más débil (f1)")
for nombre, model_id in MODELOS.items():
    tokens = {"in": 0, "out": 0}

    def extract(case: Case) -> Invoice:
        agent = Agent(
            model=BedrockModel(model_id=model_id, region_name=REGION, temperature=0),
            system_prompt=PROMPTS[prompt_version],
            callback_handler=None,
        )
        result = agent(case.input, structured_output_model=Invoice)
        uso = result.metrics.accumulated_usage
        tokens["in"] += uso["inputTokens"]
        tokens["out"] += uso["outputTokens"]
        return result.structured_output

    experiment = Experiment(
        cases=load_cases(), evaluators=[StructuredOutputSimilarity(Invoice)], report_cls=StructuredOutputReport
    )
    report = experiment.run_evaluations(extract)
    promedio = sum(report.scores) / len(report.scores)
    perfectas = sum(1 for s in report.scores if s == 1.0)
    peor = min(report.metrics().field_metrics.items(), key=lambda kv: kv[1]["cm_f1"])
    print(
        f"{nombre:<12}{promedio:>9.3f}  {perfectas:>10}/{len(report.scores)}  "
        f"{tokens['in']:>10}  {tokens['out']:>10}  {peor[0]} ({peor[1]['cm_f1']:.2f})"
    )
