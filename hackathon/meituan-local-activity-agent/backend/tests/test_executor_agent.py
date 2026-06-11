from agents.executor_agent import ExecutorAgent


def test_execute_books_each_poi(monkeypatch):
    booked = []

    def fake_book_poi(poi_name, time_slot=None, trace_id=None, city="上海"):
        booked.append((poi_name, time_slot, trace_id, city))
        return {"success": True, "poi_name": poi_name, "booking_id": f"book_{len(booked)}"}

    monkeypatch.setattr("agents.executor_agent.book_poi", fake_book_poi)

    plan = {
        "id": "plan_1",
        "pois": [
            {"name": "咖啡馆", "time_slot": "14:00-15:00"},
            {"name": "展览馆", "time_slot": "15:30-17:00"},
        ],
    }

    result = ExecutorAgent().execute(plan, trace_id="trace_1", city="杭州")

    assert result["success"] is True
    assert [item["poi_name"] for item in result["results"]] == ["咖啡馆", "展览馆"]
    assert booked == [
        ("咖啡馆", "14:00-15:00", "trace_1", "杭州"),
        ("展览馆", "15:30-17:00", "trace_1", "杭州"),
    ]


def test_execute_normalizes_single_restaurant_candidate(monkeypatch):
    booked = []

    def fake_book_poi(poi_name, time_slot=None, trace_id=None, city="上海"):
        booked.append((poi_name, time_slot, trace_id, city))
        return {"success": True, "poi_name": poi_name, "booking_id": "book_1"}

    monkeypatch.setattr("agents.executor_agent.book_poi", fake_book_poi)

    plan = {
        "id": "plan_1",
        "restaurant": "望京小腰烤肉店（三里屯店）",
        "time_slot": "18:00-20:00",
    }

    result = ExecutorAgent().execute(plan, trace_id="trace_2", city="北京")

    assert result["success"] is True
    assert result["results"][0]["poi_name"] == "望京小腰烤肉店（三里屯店）"
    assert booked == [("望京小腰烤肉店（三里屯店）", "18:00-20:00", "trace_2", "北京")]


def test_execute_returns_failure_when_no_bookable_pois():
    result = ExecutorAgent().execute({"id": "plan_empty"}, trace_id="trace_3", city="上海")

    assert result == {
        "success": False,
        "error": "No bookable POIs in selected plan",
        "results": [],
    }


def test_execute_does_not_book_descriptive_plan_name():
    result = ExecutorAgent().execute(
        {"id": "plan_title_only", "name": "亲子悠闲半日游"},
        trace_id="trace_title",
        city="上海",
    )

    assert result == {
        "success": False,
        "error": "No bookable POIs in selected plan",
        "results": [],
    }


def test_execute_stops_on_first_booking_failure(monkeypatch):
    def fake_book_poi(poi_name, time_slot=None, trace_id=None, city="上海"):
        if poi_name == "第二站":
            return {"success": False, "poi_name": poi_name, "error": "订满"}
        return {"success": True, "poi_name": poi_name, "booking_id": "book_ok"}

    monkeypatch.setattr("agents.executor_agent.book_poi", fake_book_poi)

    plan = {"pois": [{"name": "第一站"}, {"name": "第二站"}, {"name": "第三站"}]}

    result = ExecutorAgent().execute(plan, trace_id="trace_4", city="上海")

    assert result["success"] is False
    assert result["error"] == "订满"
    assert [item["poi_name"] for item in result["results"]] == ["第一站", "第二站"]
