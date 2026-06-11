from agents import orchestrator


def test_run_planning_flow_returns_frontend_response_shape(monkeypatch):
    class FakeGraph:
        def invoke(self, initial_state):
            return {
                **initial_state,
                "intent": {"location": {"city": "上海"}, "weather": {"weather": "晴"}},
                "candidates": [{"id": "plan_1", "restaurant": "测试餐厅"}],
                "round1_reviews": {"round": 1, "reviews": {}},
                "round2_reviews": {"round": 2, "reviews": {}},
                "best_plan": {"id": "plan_1", "restaurant": "测试餐厅"},
                "final_score": 8.0,
                "execution_result": {"success": True, "results": [{"booking_id": "book_1"}]},
                "error": None,
                "trip_state": "COMPLETED",
            }

    monkeypatch.setattr(orchestrator, "build_graph", lambda: FakeGraph())

    result = orchestrator.run_planning_flow(
        "今晚想吃饭",
        trace_id="trace_orchestrator",
        city_override="上海",
    )

    assert result["session_id"]
    assert result["trace_id"] == "trace_orchestrator"
    assert result["intent"]["location"]["city"] == "上海"
    assert result["best_plan"]["id"] == "plan_1"
    assert result["final_score"] == 8.0
    assert result["execution_result"]["success"] is True
    assert result["error"] is None


def test_run_planning_flow_passes_city_override_to_initial_state(monkeypatch):
    captured = {}

    class FakeGraph:
        def invoke(self, initial_state):
            captured.update(initial_state)
            return {
                **initial_state,
                "intent": {"location": {"city": "北京"}},
                "candidates": [],
                "round1_reviews": None,
                "round2_reviews": None,
                "best_plan": None,
                "final_score": 0.0,
                "execution_result": {"success": False, "error": "No plan available", "results": []},
                "error": None,
            }

    monkeypatch.setattr(orchestrator, "build_graph", lambda: FakeGraph())

    orchestrator.run_planning_flow("明天安排活动", trace_id="trace_city", city_override="北京")

    assert captured["city_override"] == "北京"
