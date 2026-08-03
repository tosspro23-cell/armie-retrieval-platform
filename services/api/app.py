"""HTTP API for the interactive retrieval workbench."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from armie_retrieval.application import WorkbenchService
from armie_retrieval.application.workbench import WorkbenchError
from .schemas import CompareRequest, ComparisonResponse, QueryLabRunRequest, QueryRequest, WorkbenchResponse

ROOT = Path(__file__).resolve().parents[2]
service = WorkbenchService(ROOT)
app = FastAPI(title="ARMIE Retrieval Workbench", version="0.4.0", description="Interactive retrieval validation API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(WorkbenchError)
async def workbench_error(_: Request, exc: WorkbenchError):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}})

@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "message": "The workbench could not complete the request.", "details": {"reason": str(exc)}}})

@app.get("/")
def root():
    return {"service": "armie-retrieval-workbench", "version": "0.4.0", "docs": "/docs"}

@app.get("/api/v1/health")
def health():
    return service.health()

@app.get("/api/v1/capabilities")
def capabilities():
    return service.capabilities()

@app.get("/api/v1/datasets")
def datasets():
    return service.datasets()

@app.get("/api/v1/benchmarks")
def benchmarks():
    return service.benchmarks()

@app.post("/api/v1/sessions")
def create_session():
    return service.create_session()

@app.get("/api/v1/sessions/{session_id}")
def get_session(session_id: str):
    return service.get_session(session_id)

@app.delete("/api/v1/sessions/{session_id}")
def delete_session(session_id: str):
    service.delete_session(session_id)
    return {"deleted": True, "session_id": session_id}

@app.post("/api/v1/query", response_model=WorkbenchResponse)
def query(request: QueryRequest):
    return service.query(request.query, session_id=request.session_id, profile=request.profile, query_case_id=request.query_case_id)

@app.get("/api/v1/traces/{trace_id}")
def trace(trace_id: str):
    return service.trace(trace_id)

@app.get("/api/v1/query-lab/cases")
def query_lab_cases():
    return {"cases": service.query_cases()}

@app.post("/api/v1/query-lab/runs", response_model=WorkbenchResponse)
def query_lab_run(request: QueryLabRunRequest):
    return service.run_case(request.case_id, profile=request.profile)

@app.post("/api/v1/query-lab/compare", response_model=ComparisonResponse)
def query_lab_compare(request: CompareRequest):
    return service.compare_runs(request.left_run_id, request.right_run_id)
