"""
FastAPI应用
REST API封装
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from maitian_agent.agents.factory import AgentFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化所有 Agent，关闭时清理资源"""
    factory = AgentFactory()
    app.state.agents = factory.create_all()
    yield
    # 关闭时清理（当前无需特殊清理）


app = FastAPI(
    title="麦田智囊API",
    description="乡村教育Agent系统REST API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LessonPrepRequest(BaseModel):
    subject: str
    grade: str
    topic: str
    rural_context: Optional[str] = ""


class WisdomTransferRequest(BaseModel):
    image_path: str


class QuizRequest(BaseModel):
    subject: str
    grade: str
    topic: str
    knowledge_points: Optional[str] = ""
    question_count: Optional[int] = 5
    question_types: Optional[str] = "选择题、填空题"


class MaterialRequest(BaseModel):
    subject: str
    grade: str
    topic: str
    knowledge_points: Optional[str] = ""
    rural_context: Optional[str] = ""


class MeetingNotesRequest(BaseModel):
    transcript: str


class RouteRequest(BaseModel):
    user_input: str


@app.get("/")
async def root():
    """根路径"""
    return {"message": "麦田智囊 API v1.0.0", "status": "running"}


@app.get("/health")
async def health_check(request: Request):
    """健康检查"""
    return {"status": "healthy", "agents": list(request.app.state.agents.keys())}


@app.post("/api/lesson-prep")
async def lesson_prep(request: LessonPrepRequest, req: Request):
    """极速备课"""
    try:
        result = req.app.state.agents["quick_lesson_prep"].run(
            {
                "subject": request.subject,
                "grade": request.grade,
                "topic": request.topic,
                "rural_context": request.rural_context,
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wisdom-transfer")
async def wisdom_transfer(request: WisdomTransferRequest, req: Request):
    """智慧传承"""
    try:
        result = req.app.state.agents["wisdom_transfer"].run({"image_path": request.image_path})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz")
async def generate_quiz(request: QuizRequest, req: Request):
    """生成练习题"""
    try:
        result = req.app.state.agents["classroom_companion"].run(
            {
                "action": "quiz",
                "subject": request.subject,
                "grade": request.grade,
                "topic": request.topic,
                "knowledge_points": request.knowledge_points,
                "question_count": request.question_count,
                "question_types": request.question_types,
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/material")
async def recommend_material(request: MaterialRequest, req: Request):
    """素材推荐"""
    try:
        result = req.app.state.agents["material"].run(
            {
                "subject": request.subject,
                "grade": request.grade,
                "topic": request.topic,
                "knowledge_points": request.knowledge_points,
                "rural_context": request.rural_context,
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/meeting-notes")
async def process_meeting_notes(request: MeetingNotesRequest, req: Request):
    """教研纪要"""
    try:
        result = req.app.state.agents["meeting_notes"].run(
            {"transcript": request.transcript, "action": "process"}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/route")
async def route_intent(request: RouteRequest, req: Request):
    """意图路由"""
    try:
        result = req.app.state.agents["router"].run({"user_input": request.user_input})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    return app
