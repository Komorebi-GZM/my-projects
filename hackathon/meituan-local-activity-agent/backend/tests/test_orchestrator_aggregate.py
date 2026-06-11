from agents.orchestrator import aggregate_reviews


def test_aggregate_reviews_handles_flat_veto_without_crashing():
    round1 = {
        "round": 1,
        "reviews": {
            "安全Agent": {"agent": "安全Agent", "score": 2, "veto": True}
        },
        "summary": "",
    }
    candidates = [{"id": "plan_1", "restaurant": "测试餐厅"}]

    final_score, best_plan = aggregate_reviews(round1, None, candidates)

    assert final_score == 0.0
    assert best_plan == candidates[0]


def test_aggregate_reviews_ignores_malformed_nested_review_values():
    round1 = {
        "round": 1,
        "reviews": {
            "安全Agent": {
                "agent": "安全Agent",
                "plan_1": {"agent": "安全Agent", "score": 8, "veto": False},
            }
        },
        "summary": "",
    }
    candidates = [{"id": "plan_1", "restaurant": "测试餐厅"}]

    final_score, best_plan = aggregate_reviews(round1, None, candidates)

    assert final_score == 8.0
    assert best_plan == candidates[0]
