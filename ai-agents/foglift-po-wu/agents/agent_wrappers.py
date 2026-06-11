from typing import Dict, Any
from utils.supervisor import AgentState

from agents.jd_translator.jd_analyst import parse_jd
from agents.jd_translator.jargon_translator import translate_jargon
from agents.jd_translator.gap_analyst import analyze_gap
from agents.jd_translator.coordinator import coordinate as jd_coordinate

from agents.path_skill.position_resolver import resolve_position
from agents.path_skill.ladder_planner import plan_ladder
from agents.path_skill.skill_recommender import recommend_skills
from agents.path_skill.resource_retriever import retrieve_resources
from agents.path_skill.coordinator import finalize_path_skill

from agents.interview.interviewer import get_question
from agents.interview.answer_analyst import analyze_answer
from agents.interview.cheerleader import generate_encouragement
from agents.interview.coordinator import finalize_interview
from utils.session_store import session_store


def jd_analyst_node(state: AgentState) -> Dict[str, Any]:
    jd_text = state.get("jd_text") or (state.get("payload") or {}).get("jd_text", "")
    jd_parsed = parse_jd(jd_text)
    return {"jd_parsed": jd_parsed}


def jargon_translator_node(state: AgentState) -> Dict[str, Any]:
    jd_parsed = state.get("jd_parsed", {}) or {}
    jargon_list = jd_parsed.get("HR黑话", [])
    translated = translate_jargon(jargon_list)
    return {"jargon_translated": translated}


def gap_analyst_node(state: AgentState) -> Dict[str, Any]:
    jd_parsed = state.get("jd_parsed", {}) or {}
    user_profile = (state.get("payload") or {}).get("user_profile", None)
    gaps = analyze_gap(jd_parsed, user_profile)
    return {"gaps": gaps}


def coordinator_jd_node(state: AgentState) -> Dict[str, Any]:
    jd_parsed = state.get("jd_parsed", {})
    jargon_translated = state.get("jargon_translated", {})
    gaps = state.get("gaps", {})
    result = jd_coordinate(jd_parsed, jargon_translated, gaps)
    return {"result": result}


def position_resolver_node(state: AgentState) -> Dict[str, Any]:
    target_position = state.get("target_position") or (state.get("payload") or {}).get("target_position", "")
    ability_dims = resolve_position(target_position)
    return {"ability_dims": ability_dims}


def ladder_planner_node(state: AgentState) -> Dict[str, Any]:
    target_position = state.get("target_position") or (state.get("payload") or {}).get("target_position", "")
    ability_dims_dict = state.get("ability_dims", {}) or {}
    ability_dims_list = ability_dims_dict.get("能力维度", [])
    ladder = plan_ladder(target_position, ability_dims_list)
    return {"ladder": ladder}


def skill_recommender_node(state: AgentState) -> Dict[str, Any]:
    ability_dims_dict = state.get("ability_dims", {}) or {}
    ability_dims_list = ability_dims_dict.get("能力维度", [])
    skills = recommend_skills(ability_dims_list)
    return {"skills": skills}


def resource_retriever_node(state: AgentState) -> Dict[str, Any]:
    skills = state.get("skills", []) or []
    resources = retrieve_resources(skills)
    return {"resources": resources}


def coordinator_path_node(state: AgentState) -> Dict[str, Any]:
    ability_dims = state.get("ability_dims", {})
    ladder = state.get("ladder", {})
    skills = state.get("skills", [])
    resources = state.get("resources", [])
    result = finalize_path_skill(ability_dims, ladder, skills, resources)
    return {"result": result}


def interviewer_node(state: AgentState) -> Dict[str, Any]:
    target_position = state.get("target_position") or (state.get("payload") or {}).get("target_position", "")
    question_data = get_question(target_position)
    return {
        "session_id": question_data.get("session_id"),
        "question": question_data.get("question"),
        "key_points": question_data.get("key_points", []),
        "result": question_data
    }


def answer_analyst_node(state: AgentState) -> Dict[str, Any]:
    answer = state.get("answer") or (state.get("payload") or {}).get("answer", "")
    session_id = state.get("session_id") or (state.get("payload") or {}).get("session_id", "")

    # Try session_store first for full context, fall back to state
    session_data = session_store.get(session_id) if session_id else None
    question = state.get("question") or (session_data or {}).get("question", "")
    key_points = state.get("key_points") or (session_data or {}).get("key_points", [])

    # Fallback: if key_points still empty, provide generic ones based on question
    if not key_points and question:
        key_points = ["回答完整性", "逻辑清晰度", "与问题的匹配度"]

    scores = analyze_answer(question, answer, key_points)
    return {"scores": scores, "answer": answer}


def cheerleader_node(state: AgentState) -> Dict[str, Any]:
    scores = state.get("scores", {}) or {}
    total_score = scores.get("总分", 0)

    # Extract strengths from score dimensions
    strengths = []
    内容分 = scores.get("内容分", 0)
    逻辑分 = scores.get("逻辑分", 0)
    匹配分 = scores.get("匹配分", 0)
    if 内容分 >= 70:
        strengths.append("回答内容充实")
    if 逻辑分 >= 70:
        strengths.append("逻辑清晰有条理")
    if 匹配分 >= 70:
        strengths.append("与岗位要求高度匹配")
    if not strengths and total_score >= 50:
        strengths.append("有潜力，方向正确")

    encouragement = generate_encouragement(total_score, strengths)
    return {"encouragement": encouragement}


def coordinator_int_node(state: AgentState) -> Dict[str, Any]:
    scores = state.get("scores", {})
    encouragement = state.get("encouragement", {})
    result = finalize_interview(scores, encouragement)
    return {"result": result}