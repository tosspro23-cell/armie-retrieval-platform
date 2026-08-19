"""HTTP API for the interactive retrieval workbench."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from armie_retrieval.application import WorkbenchService
from armie_retrieval import __version__
from armie_retrieval.application.workbench import WorkbenchError
from .schemas import BenchmarkRunRequest, ClarificationResolutionRequest, CompareRequest, ComparisonResponse, InterpretRequest, InterpretationExecutionRequest, QueryLabRunRequest, QueryRequest, StructuredQueryRequest, WorkbenchResponse

ROOT = Path(__file__).resolve().parents[2]
service = WorkbenchService(ROOT)
app = FastAPI(title="ARMIE Retrieval Workbench", version=__version__, description="Interactive retrieval validation API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(WorkbenchError)
async def workbench_error(_: Request, exc: WorkbenchError):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}})

@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "message": "The workbench could not complete the request.", "details": {"reason": str(exc)}}})

@app.get("/")
def root():
    return {"service": "armie-retrieval-workbench", "version": __version__, "docs": "/docs"}

@app.get("/api/v1/health")
def health():
    return service.health()

@app.get("/api/v1/capabilities")
def capabilities():
    return service.capabilities()

@app.get("/api/v1/constraints/registry")
def constraint_registry():
    return service.constraint_registry()

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

@app.post("/api/v1/query")
def query(request: QueryRequest):
    return service.query(request.query, session_id=request.session_id, profile=request.profile, governed=request.governed, query_case_id=request.query_case_id, benchmark_query_id=request.benchmark_query_id)

@app.post("/api/v1/structured-query", response_model=WorkbenchResponse)
def structured_query(request: StructuredQueryRequest):
    return service.structured_query(request.query, request.contract, requested_k=request.requested_k)

@app.post("/api/v1/interpret")
def interpret(request: InterpretRequest):
    return service.interpret(request.query)

@app.get("/api/v1/interpretations/{session_id}")
def interpretation(session_id: str):
    return service.interpretation(session_id)

@app.post("/api/v1/interpretations/{session_id}/resolutions")
def resolve_interpretation(session_id: str, request: ClarificationResolutionRequest):
    return service.resolve_interpretation(session_id, request.model_dump())

@app.put("/api/v1/interpretations/{session_id}/resolutions")
def edit_interpretation(session_id: str, request: ClarificationResolutionRequest):
    return service.resolve_interpretation(session_id, request.model_dump(), edit=True)

@app.post("/api/v1/interpretations/{session_id}/confirm")
def confirm_interpretation(session_id: str):
    return service.confirm_interpretation(session_id)

@app.post("/api/v1/interpretations/{session_id}/execute", response_model=WorkbenchResponse)
def execute_interpretation(session_id: str, request: InterpretationExecutionRequest):
    return service.execute_interpretation(session_id, contract_fingerprint=request.contract_fingerprint, requested_k=request.requested_k)

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

@app.get("/api/v1/benchmark/manifest")
def benchmark_manifest():
    return service.benchmark_manifest()

@app.get("/api/v1/benchmark/profiles")
def benchmark_profiles():
    return {"profiles": service.benchmark_profiles()}

@app.get("/api/v1/benchmark/queries")
def benchmark_queries():
    return {"queries": service.benchmark_queries()}

@app.get("/api/v1/benchmark/queries/{query_id}")
def benchmark_query(query_id: str):
    return service.benchmark_query(query_id)

@app.post("/api/v1/benchmark/execute", response_model=WorkbenchResponse)
def benchmark_execute(request: BenchmarkRunRequest):
    return service.run_benchmark_query(request.query_id, profile=request.profile)
