from fastapi import FastAPI, HTTPException
from src.flows.report_generation_flow import graph
from src.models.report_models import ReportStateInput
from typing import Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="GA4 Analytics Report API")

@app.post("/generate-report")
async def generate_report(input_data: Dict):
    try:
        # Convert input to ReportStateInput
        state_input = ReportStateInput(**input_data)
        # Invoke graph
        result = await graph.ainvoke(state_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
