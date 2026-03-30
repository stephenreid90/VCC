"""FastAPI web playground — mounts at /playground/valuations."""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from models.dcf import DCFModel, DCFAssumptions
from models.three_statement import ThreeStatementModel, ThreeStatementAssumptions

app = FastAPI(title="VCC Valuations Playground", root_path="/playground/valuations")

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


class ValuationRequest(BaseModel):
    model_type: str = "dcf"  # "dcf" | "three_statement"
    assumptions: dict


@app.get("/")
async def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static/index.html"))


@app.post("/api/valuations/calculate")
async def calculate_valuation(req: ValuationRequest):
    try:
        if req.model_type == "dcf":
            assumptions = DCFAssumptions(**req.assumptions)
            result = DCFModel(assumptions).calculate()
            return result.model_dump()
        elif req.model_type == "three_statement":
            assumptions = ThreeStatementAssumptions(**req.assumptions)
            result = ThreeStatementModel(assumptions).calculate()
            return result.model_dump()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model_type: {req.model_type}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
