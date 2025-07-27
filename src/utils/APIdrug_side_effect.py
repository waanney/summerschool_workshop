from pydantic_ai.tools import Tool
import requests
from pydantic import BaseModel, Field

class DrugSideEffectInput(BaseModel):
    drug_name: str

class DrugSideEffectOutput(BaseModel):
    reports: list

class DrugSideEffectTool(Tool):
    name = "drug_side_effect_tool"
    description = "Get side effect reports for a drug from the openFDA API."
    input_model = DrugSideEffectInput
    output_model = DrugSideEffectOutput

def _run(self, input: DrugSideEffectInput) -> DrugSideEffectOutput:
    url = "https://api.fda.gov/drug/event.json"
    params = {
            "search": f"patient.drug.medicinalproduct:{input.drug_name}",
            "limit": 5
    }
    response = requests.get(url, params=params)
    reports = []
    if response.status_code == 200:
        data = response.json()
        for record in data.get("results", []):
            reports.append({
                "safetyreportid": record.get("safetyreportid"),
                "receiptdate": record.get("receiptdate"),
                "side_effects": record.get("patient", {}).get("reaction", "Unknown")
            })
    return DrugSideEffectOutput(reports=reports)