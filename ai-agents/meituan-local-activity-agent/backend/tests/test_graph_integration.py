import pytest
from graph.builder import build_graph
from graph.state import BrainstormState, TripState
from graph.nodes import _collect_vetoed_candidates


def test_build_graph():
    graph = build_graph()
    assert graph is not None


def test_collect_vetoed_candidates_handles_flat_veto():
    state = {
        "candidates": [{"id": "plan_1"}, {"id": "plan_2"}],
        "round1_reviews": {
            "round": 1,
            "reviews": {
                "安全Agent": {"agent": "安全Agent", "score": 2, "veto": True}
            },
        },
        "round2_reviews": None,
    }

    assert sorted(_collect_vetoed_candidates(state)) == ["plan_1", "plan_2"]


def test_full_flow_success():
    graph = build_graph()
    initial_state = BrainstormState(
        session_id="test_sess_001",
        trip_state=TripState.IDLE.value,
        user_input="周末想带父母和孩子去玩，预算 300 左右",
        intent=None,
        candidates=None,
        round=0,
        round1_reviews={"reviews": {"安全视角": {"score": 85, "feedback": "安全", "veto": False}}},
        round2_reviews=None,
        final_score=None,
        best_plan=None,
        replan_count=0,
        error=None,
        trace_id="test_trace_001",
        parent_trace_id=None,
        latency_ms=None,
        execution_result=None,
        city_override=None
    )
    final_state = graph.invoke(initial_state)
    assert final_state["trip_state"] in [TripState.EXECUTING.value, TripState.COMPLETED.value, TripState.FAILED.value]


def test_graph_final_state_contains_execution_result(monkeypatch):
    from graph.builder import build_graph
    from graph.state import TripState

    monkeypatch.setattr(
        "graph.nodes.IntentAgent.parse",
        lambda self, user_input, trace_id=None: {
            "time": {"range": "今晚", "flexibility": "±1h"},
            "location": {"city": "上海", "district": ""},
            "group": {"type": "friends", "count": 2, "children": []},
            "scene": "friends",
            "constraints": {"budget": 300, "max_distance_km": 5},
            "preferences": {"food": "火锅", "activity": "无偏好"},
            "missing_fields": [],
        },
    )
    monkeypatch.setattr(
        "graph.nodes.get_weather",
        lambda city, trace_id=None: {"city": city, "weather": "晴", "temperature": "22°C"},
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.generate",
        lambda self, intent, trace_id=None: [{"id": "plan_1", "restaurant": "测试火锅"}],
    )
    monkeypatch.setattr(
        "graph.nodes.run_brainstorm_round",
        lambda candidates, round_num, intent, trace_id=None: {
            "round": round_num,
            "reviews": {
                "体验Agent": {"plan_1": {"score": 8, "veto": False}},
                "安全Agent": {"plan_1": {"score": 8, "veto": False}},
                "效率Agent": {"plan_1": {"score": 8, "veto": False}},
                "预算Agent": {"plan_1": {"score": 8, "veto": False}},
            },
            "summary": "ok",
        },
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.revise",
        lambda self, candidates, reviews: candidates,
    )
    monkeypatch.setattr(
        "graph.nodes.ExecutorAgent.execute",
        lambda self, plan, trace_id=None, city="上海": {
            "success": True,
            "results": [{"poi_name": plan["restaurant"], "booking_id": "book_1"}],
        },
    )

    graph = build_graph()
    final_state = graph.invoke({
        "session_id": "test_sess",
        "trip_state": TripState.IDLE.value,
        "user_input": "今晚想吃火锅",
        "intent": None,
        "candidates": None,
        "round": 0,
        "round1_reviews": None,
        "round2_reviews": None,
        "final_score": None,
        "best_plan": None,
        "replan_count": 0,
        "error": None,
        "trace_id": "trace_graph",
        "parent_trace_id": None,
        "latency_ms": None,
        "execution_result": None,
        "city_override": None,
    })

    assert final_state["trip_state"] == TripState.COMPLETED.value
    assert final_state["execution_result"]["success"] is True
    assert final_state["execution_result"]["results"][0]["booking_id"] == "book_1"


def test_graph_marks_failed_when_executor_returns_unsuccessful_result(monkeypatch):
    from graph.builder import build_graph
    from graph.state import TripState

    monkeypatch.setattr(
        "graph.nodes.IntentAgent.parse",
        lambda self, user_input, trace_id=None: {
            "time": {"range": "今晚", "flexibility": "±1h"},
            "location": {"city": "上海", "district": ""},
            "group": {"type": "friends", "count": 2, "children": []},
            "scene": "friends",
            "constraints": {"budget": 300, "max_distance_km": 5},
            "preferences": {"food": "火锅", "activity": "无偏好"},
            "missing_fields": [],
        },
    )
    monkeypatch.setattr(
        "graph.nodes.get_weather",
        lambda city, trace_id=None: {"city": city, "weather": "晴", "temperature": "22°C"},
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.generate",
        lambda self, intent, trace_id=None: [{"id": "plan_1", "restaurant": "测试火锅"}],
    )
    monkeypatch.setattr(
        "graph.nodes.run_brainstorm_round",
        lambda candidates, round_num, intent, trace_id=None: {
            "round": round_num,
            "reviews": {
                "体验Agent": {"plan_1": {"score": 8, "veto": False}},
                "安全Agent": {"plan_1": {"score": 8, "veto": False}},
                "效率Agent": {"plan_1": {"score": 8, "veto": False}},
                "预算Agent": {"plan_1": {"score": 8, "veto": False}},
            },
            "summary": "ok",
        },
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.revise",
        lambda self, candidates, reviews: candidates,
    )
    monkeypatch.setattr(
        "graph.nodes.ExecutorAgent.execute",
        lambda self, plan, trace_id=None, city="上海": {
            "success": False,
            "error": "No bookable POIs in selected plan",
            "results": [],
        },
    )

    graph = build_graph()
    final_state = graph.invoke({
        "session_id": "test_sess",
        "trip_state": TripState.IDLE.value,
        "user_input": "今晚想吃火锅",
        "intent": None,
        "candidates": None,
        "round": 0,
        "round1_reviews": None,
        "round2_reviews": None,
        "final_score": None,
        "best_plan": None,
        "replan_count": 0,
        "error": None,
        "trace_id": "trace_graph_failure",
        "parent_trace_id": None,
        "latency_ms": None,
        "execution_result": None,
        "city_override": None,
    })

    assert final_state["trip_state"] == TripState.FAILED.value
    assert final_state["execution_result"]["success"] is False
    assert final_state["error"] == "No bookable POIs in selected plan"


def test_graph_stops_after_parse_intent_failure(monkeypatch):
    from graph.builder import build_graph
    from graph.state import TripState

    def fail_parse(self, user_input, trace_id=None):
        raise RuntimeError("parse exploded")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("generate_plans should not run after parse failure")

    monkeypatch.setattr("graph.nodes.IntentAgent.parse", fail_parse)
    monkeypatch.setattr("graph.nodes.PlannerAgent.generate", fail_if_called)

    graph = build_graph()
    final_state = graph.invoke({
        "session_id": "test_sess",
        "trip_state": TripState.IDLE.value,
        "user_input": "坏输入",
        "intent": None,
        "candidates": None,
        "round": 0,
        "round1_reviews": None,
        "round2_reviews": None,
        "final_score": None,
        "best_plan": None,
        "replan_count": 0,
        "error": None,
        "trace_id": "trace_parse_failure",
        "parent_trace_id": None,
        "latency_ms": None,
        "execution_result": None,
        "city_override": None,
    })

    assert final_state["error"] == "意图解析失败: parse exploded"
    assert final_state["trip_state"] == TripState.FAILED.value
    assert final_state["candidates"] is None


def test_graph_stops_when_planner_returns_no_candidates(monkeypatch):
    from graph.builder import build_graph
    from graph.state import TripState

    monkeypatch.setattr(
        "graph.nodes.IntentAgent.parse",
        lambda self, user_input, trace_id=None: {
            "time": {"range": "今晚", "flexibility": "±1h"},
            "location": {"city": "上海", "district": ""},
            "group": {"type": "friends", "count": 2, "children": []},
            "scene": "friends",
            "constraints": {"budget": 300, "max_distance_km": 5},
            "preferences": {"food": "火锅", "activity": "无偏好"},
            "missing_fields": [],
        },
    )
    monkeypatch.setattr(
        "graph.nodes.get_weather",
        lambda city, trace_id=None: {"city": city, "weather": "晴", "temperature": "22°C"},
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.generate",
        lambda self, intent, trace_id=None: [],
    )
    monkeypatch.setattr(
        "graph.nodes.run_brainstorm_round",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("brainstorm should not run")),
    )

    graph = build_graph()
    final_state = graph.invoke({
        "session_id": "test_sess",
        "trip_state": TripState.IDLE.value,
        "user_input": "今晚想吃火锅",
        "intent": None,
        "candidates": None,
        "round": 0,
        "round1_reviews": None,
        "round2_reviews": None,
        "final_score": None,
        "best_plan": None,
        "replan_count": 0,
        "error": None,
        "trace_id": "trace_no_candidates",
        "parent_trace_id": None,
        "latency_ms": None,
        "execution_result": None,
        "city_override": None,
    })

    assert final_state["trip_state"] == TripState.FAILED.value
    assert final_state["candidates"] == []
    assert final_state["error"] == "No plan available"


def test_graph_stops_after_brainstorm_round1_failure(monkeypatch):
    from graph.builder import build_graph
    from graph.state import TripState

    monkeypatch.setattr(
        "graph.nodes.IntentAgent.parse",
        lambda self, user_input, trace_id=None: {
            "time": {"range": "今晚", "flexibility": "±1h"},
            "location": {"city": "上海", "district": ""},
            "group": {"type": "friends", "count": 2, "children": []},
            "scene": "friends",
            "constraints": {"budget": 300, "max_distance_km": 5},
            "preferences": {"food": "火锅", "activity": "无偏好"},
            "missing_fields": [],
        },
    )
    monkeypatch.setattr(
        "graph.nodes.get_weather",
        lambda city, trace_id=None: {"city": city, "weather": "晴", "temperature": "22°C"},
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.generate",
        lambda self, intent, trace_id=None: [{"id": "plan_1", "restaurant": "测试火锅"}],
    )
    monkeypatch.setattr(
        "graph.nodes.run_brainstorm_round",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("brainstorm exploded")),
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.revise",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("round2 should not run")),
    )

    graph = build_graph()
    final_state = graph.invoke({
        "session_id": "test_sess",
        "trip_state": TripState.IDLE.value,
        "user_input": "今晚想吃火锅",
        "intent": None,
        "candidates": None,
        "round": 0,
        "round1_reviews": None,
        "round2_reviews": None,
        "final_score": None,
        "best_plan": None,
        "replan_count": 0,
        "error": None,
        "trace_id": "trace_brainstorm_failure",
        "parent_trace_id": None,
        "latency_ms": None,
        "execution_result": None,
        "city_override": None,
    })

    assert final_state["trip_state"] == TripState.FAILED.value
    assert final_state["error"] == "第1轮评审失败: brainstorm exploded"
    assert final_state["round2_reviews"] is None


def test_graph_stops_after_brainstorm_round2_failure(monkeypatch):
    from graph.builder import build_graph
    from graph.state import TripState

    monkeypatch.setattr(
        "graph.nodes.IntentAgent.parse",
        lambda self, user_input, trace_id=None: {
            "time": {"range": "今晚", "flexibility": "±1h"},
            "location": {"city": "上海", "district": ""},
            "group": {"type": "friends", "count": 2, "children": []},
            "scene": "friends",
            "constraints": {"budget": 300, "max_distance_km": 5},
            "preferences": {"food": "火锅", "activity": "无偏好"},
            "missing_fields": [],
        },
    )
    monkeypatch.setattr(
        "graph.nodes.get_weather",
        lambda city, trace_id=None: {"city": city, "weather": "晴", "temperature": "22°C"},
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.generate",
        lambda self, intent, trace_id=None: [{"id": "plan_1", "restaurant": "测试火锅"}],
    )

    def fake_brainstorm(candidates, round_num, intent, trace_id=None):
        if round_num == 2:
            raise RuntimeError("round2 exploded")
        return {
            "round": round_num,
            "reviews": {"体验Agent": {"plan_1": {"score": 8, "veto": False}}},
            "summary": "ok",
        }

    monkeypatch.setattr("graph.nodes.run_brainstorm_round", fake_brainstorm)
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.revise",
        lambda self, candidates, reviews: candidates,
    )

    graph = build_graph()
    final_state = graph.invoke({
        "session_id": "test_sess",
        "trip_state": TripState.IDLE.value,
        "user_input": "今晚想吃火锅",
        "intent": None,
        "candidates": None,
        "round": 0,
        "round1_reviews": None,
        "round2_reviews": None,
        "final_score": None,
        "best_plan": None,
        "replan_count": 0,
        "error": None,
        "trace_id": "trace_round2_failure",
        "parent_trace_id": None,
        "latency_ms": None,
        "execution_result": None,
        "city_override": None,
    })

    assert final_state["trip_state"] == TripState.FAILED.value
    assert final_state["error"] == "第2轮评审失败: round2 exploded"
    assert final_state["best_plan"] is None


def test_graph_marks_failed_when_replan_attempts_are_exhausted(monkeypatch):
    from graph.builder import build_graph
    from graph.state import TripState

    monkeypatch.setattr(
        "graph.nodes.IntentAgent.parse",
        lambda self, user_input, trace_id=None: {
            "time": {"range": "今晚", "flexibility": "±1h"},
            "location": {"city": "上海", "district": ""},
            "group": {"type": "friends", "count": 2, "children": []},
            "scene": "friends",
            "constraints": {"budget": 300, "max_distance_km": 5},
            "preferences": {"food": "火锅", "activity": "无偏好"},
            "missing_fields": [],
        },
    )
    monkeypatch.setattr(
        "graph.nodes.get_weather",
        lambda city, trace_id=None: {"city": city, "weather": "晴", "temperature": "22°C"},
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.generate",
        lambda self, intent, trace_id=None: [{"id": "plan_1", "restaurant": "测试火锅"}],
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.revise",
        lambda self, candidates, reviews: candidates,
    )
    monkeypatch.setattr(
        "graph.nodes.PlannerAgent.regenerate",
        lambda self, intent, exclude_options: [{"id": "plan_2", "restaurant": "新火锅"}],
    )
    monkeypatch.setattr(
        "graph.nodes.run_brainstorm_round",
        lambda candidates, round_num, intent, trace_id=None: {
            "round": round_num,
            "reviews": {
                "安全Agent": {
                    candidates[0]["id"]: {"agent": "安全Agent", "score": 2, "veto": True}
                }
            },
            "summary": "veto",
        },
    )

    graph = build_graph()
    final_state = graph.invoke({
        "session_id": "test_sess",
        "trip_state": TripState.IDLE.value,
        "user_input": "今晚想吃火锅",
        "intent": None,
        "candidates": None,
        "round": 0,
        "round1_reviews": None,
        "round2_reviews": None,
        "final_score": None,
        "best_plan": None,
        "replan_count": 0,
        "error": None,
        "trace_id": "trace_replan_exhausted",
        "parent_trace_id": None,
        "latency_ms": None,
        "execution_result": None,
        "city_override": None,
    })

    assert final_state["trip_state"] == TripState.FAILED.value
    assert final_state["replan_count"] == 2
    assert final_state["error"] == "Replan attempts exhausted"
    assert final_state["execution_result"]["success"] is False
