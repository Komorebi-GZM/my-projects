from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

from utils.graph_builder import build_graph
from utils.supervisor import AgentState

app = FastAPI(title="FogLift·破雾")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


class AgentInvokeRequest(BaseModel):
    intent: Optional[str] = None
    payload: Dict[str, Any] = {}


class AgentInvokeResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.post("/agent_invoke", response_model=AgentInvokeResponse)
async def agent_invoke(req: AgentInvokeRequest):
    try:
        graph = get_graph()
        state: AgentState = {"intent": req.intent, "payload": req.payload}
        
        if req.intent == "jd_translate":
            state["jd_text"] = req.payload.get("jd_text", "")
        elif req.intent == "path_skill":
            state["target_position"] = req.payload.get("target_position", "")
        elif req.intent == "interview_question":
            state["target_position"] = req.payload.get("target_position", "")
        elif req.intent == "interview_answer":
            state["answer"] = req.payload.get("answer", "")
            state["session_id"] = req.payload.get("session_id")
            # Restore question context from payload if provided
            if "question" in req.payload:
                state["question"] = req.payload["question"]
            if "key_points" in req.payload:
                state["key_points"] = req.payload["key_points"]
        
        result = graph.invoke(state)
        
        return AgentInvokeResponse(
            success=True,
            result=result.get("result")
        )
    except Exception as e:
        return AgentInvokeResponse(success=False, error=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health")
async def api_health():
    return {"status": "ok"}