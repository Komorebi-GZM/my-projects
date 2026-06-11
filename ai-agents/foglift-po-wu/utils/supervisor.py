from typing import TypedDict, Optional, List, Dict, Any

VALID_INTENTS = ["jd_translate", "path_skill", "interview_question", "interview_answer"]

INTENT_ROUTE_MAP = {
    "jd_translate": "jd_analyst",
    "path_skill": "position_resolver",
    "interview_question": "interviewer",
    "interview_answer": "answer_analyst"
}


class AgentState(TypedDict, total=False):
    intent: Optional[str]
    payload: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    next_node: Optional[str]
    
    jd_text: Optional[str]
    jd_parsed: Optional[Dict[str, Any]]
    jargon_translated: Optional[Dict[str, Any]]
    gaps: Optional[Dict[str, Any]]
    
    target_position: Optional[str]
    ability_dims: Optional[Dict[str, Any]]
    ladder: Optional[Dict[str, Any]]
    skills: Optional[List[Dict[str, Any]]]
    resources: Optional[List[Dict[str, Any]]]
    
    session_id: Optional[str]
    question: Optional[str]
    key_points: Optional[List[str]]
    answer: Optional[str]
    scores: Optional[Dict[str, int]]
    encouragement: Optional[Dict[str, Any]]
    
    error: Optional[str]


def supervisor_node(state: AgentState) -> Dict[str, str]:
    intent = state.get("intent")
    
    if not intent or intent not in VALID_INTENTS:
        intent = "jd_translate"
    
    next_node = INTENT_ROUTE_MAP.get(intent, "jd_analyst")
    
    return {"intent": intent, "next_node": next_node}