from utils.knowledge_loader import knowledge


def test_get_interview_questions_matches_broad_data_position():
    questions = knowledge.get_interview_questions("数据分析师")

    assert questions
    assert any("数据" in question["question"] for question in questions)


def test_get_interview_questions_returns_empty_for_blank_position():
    assert knowledge.get_interview_questions("") == []
