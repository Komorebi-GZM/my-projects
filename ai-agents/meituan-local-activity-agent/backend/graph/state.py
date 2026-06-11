from typing import TypedDict, Optional, List, Dict
from enum import Enum

from schemas.review import RoundReviews


class TripState(str, Enum):
    IDLE = "IDLE"
    INTENT_PARSING = "INTENT_PARSING"
    PLANNING = "PLANNING"
    BRAINSTORMING = "BRAINSTORMING"
    REPLANNING = "REPLANNING"
    CONFIRMING = "CONFIRMING"
    BOOKING = "BOOKING"  # N2: 预留状态，当前流程未使用，后续扩展预订功能时启用
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BrainstormState(TypedDict):
    """LangGraph 状态机全局状态。"""
    session_id: str
    trip_state: str
    user_input: str
    intent: Optional[Dict]
    candidates: Optional[List[Dict]]
    round: int
    round1_reviews: Optional[RoundReviews]
    round2_reviews: Optional[RoundReviews]
    final_score: Optional[float]
    best_plan: Optional[Dict]
    replan_count: int
    error: Optional[str]
    trace_id: str
    parent_trace_id: Optional[str]
    latency_ms: Optional[int]
    execution_result: Optional[Dict]
    city_override: Optional[str]


class Intent(TypedDict):
    time: Dict
    location: Dict
    group: Dict
    scene: str
    constraints: Dict
    preferences: Dict
    missing_fields: List[str]
