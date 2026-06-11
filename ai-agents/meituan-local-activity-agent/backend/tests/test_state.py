from graph.state import BrainstormState, TripState, Intent


def test_state_initialization():
    state = BrainstormState(
        session_id="sess_001",
        trip_state=TripState.IDLE,
        user_input="测试输入",
        intent=None,
        candidates=None,
        round=0,
        round1_reviews=None,
        round2_reviews=None,
        final_score=None,
        best_plan=None,
        replan_count=0,
        error=None,
        trace_id="trace_001",
        parent_trace_id=None,
        latency_ms=None,
    )
    assert state["session_id"] == "sess_001"
    assert state["trip_state"] == TripState.IDLE


def test_intent_structure():
    intent = Intent(
        time={"range": "14:00-18:00", "flexibility": "±1h"},
        group={"type": "family", "count": 3, "children": []},
        scene="parent_child",
        constraints={"max_distance_km": 10, "budget": 200},
        preferences={"food": "healthy"},
        missing_fields=[],
    )
    assert intent["time"]["range"] == "14:00-18:00"
    assert intent["constraints"]["budget"] == 200
