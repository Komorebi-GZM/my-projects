from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config import config
from logging_config import configure_logging
from agents.orchestrator import run_planning_flow, session_manager
from middleware.trace import generate_trace_id

configure_logging(config.LOG_LEVEL)

app = FastAPI(title="本地生活短时活动规划 Agent", version="1.0.0")

# D3 修复：添加 CORS 中间件，允许 Streamlit 前端跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP 阶段允许所有来源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    user_input: str
    trace_id: Optional[str] = None
    city: Optional[str] = None


class PlanResponse(BaseModel):
    session_id: Optional[str]
    trace_id: str
    intent: Optional[dict]
    candidates: Optional[list]
    round1_reviews: Optional[dict]
    round2_reviews: Optional[dict]
    best_plan: Optional[dict]
    final_score: Optional[float]
    execution_result: dict
    error: Optional[str]


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest):
    try:
        trace_id = request.trace_id or generate_trace_id()
        result = run_planning_flow(request.user_input, trace_id, city_override=request.city)

        return PlanResponse(
            session_id=result.get("session_id"),
            trace_id=result.get("trace_id", trace_id),
            intent=result.get("intent"),
            candidates=result.get("candidates"),
            round1_reviews=result.get("round1_reviews"),
            round2_reviews=result.get("round2_reviews"),
            best_plan=result.get("best_plan"),
            final_score=result.get("final_score"),
            execution_result=result.get("execution_result", {}),
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=True
    )
