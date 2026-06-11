from agents.planner_agent import PlannerAgent


def test_revise_uses_llm_feedback(monkeypatch):
    agent = PlannerAgent()
    candidates = [
        {
            "id": "plan_1",
            "name": "Original",
            "restaurant": "旧餐厅",
            "price_per_person": 220,
        }
    ]
    reviews = {
        "预算Agent": {
            "plan_1": {
                "score": 5,
                "veto": False,
                "concerns": ["人均价格偏高"],
                "suggestions": ["换成套餐或降低预算"],
            }
        }
    }

    calls = []

    def fake_call_llm(prompt, system_prompt):
        calls.append((prompt, system_prompt))
        return str({
            "id": "wrong_id_from_llm",
            "name": "Revised",
            "restaurant": "新餐厅",
            "price_per_person": 180,
        })

    monkeypatch.setattr("agents.planner_agent.call_llm", fake_call_llm)

    revised = agent.revise(candidates, reviews)

    assert revised == [
        {
            "id": "plan_1",
            "name": "Revised",
            "restaurant": "新餐厅",
            "price_per_person": 180,
        }
    ]
    assert "人均价格偏高" in calls[0][0]
    assert "换成套餐或降低预算" in calls[0][0]


def test_revise_keeps_original_candidate_when_llm_revision_fails(monkeypatch):
    agent = PlannerAgent()
    candidate = {
        "id": "plan_1",
        "name": "Original",
        "restaurant": "旧餐厅",
    }
    reviews = {
        "体验Agent": {
            "plan_1": {
                "score": 6,
                "veto": False,
                "concerns": ["排队时间长"],
                "suggestions": ["换到非高峰时段"],
            }
        }
    }

    def fake_call_llm(prompt, system_prompt):
        raise RuntimeError("LLM unavailable")

    monkeypatch.setattr("agents.planner_agent.call_llm", fake_call_llm)

    revised = agent.revise([candidate], reviews)

    assert revised == [candidate]


def test_revise_ignores_review_shaped_llm_response(monkeypatch):
    agent = PlannerAgent()
    candidate = {
        "id": "plan_1",
        "name": "Original",
        "restaurant": "旧餐厅",
    }
    reviews = {
        "体验Agent": {
            "plan_1": {
                "score": 6,
                "veto": False,
                "concerns": ["排队时间长"],
                "suggestions": ["换到非高峰时段"],
            }
        }
    }

    def fake_call_llm(prompt, system_prompt):
        return str({
            "candidate_id": "plan_1",
            "score": 7.5,
            "veto": False,
            "comment": "这是一条评审，不是修订后的方案。",
        })

    monkeypatch.setattr("agents.planner_agent.call_llm", fake_call_llm)

    revised = agent.revise([candidate], reviews)

    assert revised == [candidate]


def test_revise_ignores_review_shaped_llm_response_with_matching_id(monkeypatch):
    agent = PlannerAgent()
    candidate = {
        "id": "plan_1",
        "name": "Original",
        "restaurant": "旧餐厅",
    }
    reviews = {
        "体验Agent": {
            "plan_1": {
                "score": 6,
                "veto": False,
                "concerns": ["排队时间长"],
                "suggestions": ["换到非高峰时段"],
            }
        }
    }

    def fake_call_llm(prompt, system_prompt):
        return str({
            "id": "plan_1",
            "score": 7.5,
            "veto": False,
            "comment": "这是一条带 id 的评审，不是修订后的方案。",
        })

    monkeypatch.setattr("agents.planner_agent.call_llm", fake_call_llm)

    revised = agent.revise([candidate], reviews)

    assert revised == [candidate]


def test_revise_accepts_list_response_matching_candidate(monkeypatch):
    agent = PlannerAgent()
    candidates = [
        {"id": "plan_1", "name": "Original 1", "restaurant": "旧餐厅1"},
        {"id": "plan_2", "name": "Original 2", "restaurant": "旧餐厅2"},
    ]
    reviews = {
        "预算Agent": {
            "plan_1": {
                "score": 5,
                "veto": False,
                "concerns": ["预算偏高"],
                "suggestions": ["降低人均"],
            }
        }
    }

    def fake_call_llm(prompt, system_prompt):
        return str([
            {"id": "plan_1", "name": "Revised 1", "restaurant": "新餐厅1"},
            {"id": "plan_999", "name": "Other", "restaurant": "其他餐厅"},
        ])

    monkeypatch.setattr("agents.planner_agent.call_llm", fake_call_llm)

    revised = agent.revise(candidates, reviews)

    assert revised == [
        {"id": "plan_1", "name": "Revised 1", "restaurant": "新餐厅1"},
        {"id": "plan_2", "name": "Original 2", "restaurant": "旧餐厅2"},
    ]
