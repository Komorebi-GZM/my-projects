import json
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent.parent / "knowledge_base"

class KnowledgeLoader:
    _instance = None
    _data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all()
        return cls._instance

    def _load_all(self):
        files = [
            "jd_library.json",
            "jargon_map.json",
            "skill_resource_map.json",
            "interview_questions.json",
            "ladder_templates.json",
            "user_profile_default.json"
        ]
        for fname in files:
            fpath = BASE_DIR / fname
            if fpath.exists():
                key = fname.replace(".json", "")
                with open(fpath, "r", encoding="utf-8") as f:
                    self._data[key] = json.load(f)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def get_jd_library(self) -> Dict:
        return self._data.get("jd_library", {})

    def get_jargon_map(self) -> Dict:
        return self._data.get("jargon_map", {}).get("mappings", {})

    def get_skill_resource_map(self) -> Dict:
        return self._data.get("skill_resource_map", {}).get("mappings", {})

    def get_interview_questions(self, position: str) -> list:
        if not position:
            return []

        questions = self._data.get("interview_questions", {}).get("questions", {})
        exact_match = questions.get(position, [])
        if exact_match:
            return exact_match

        for question_position, position_questions in questions.items():
            if position in question_position or question_position in position:
                if position_questions:
                    return position_questions

        for keyword in ("数据", "Agent", "AI", "产品", "算法", "测试"):
            if keyword in position:
                for question_position, position_questions in questions.items():
                    if keyword in question_position and position_questions:
                        return position_questions

        return []

    def get_ladder_template(self, position: str) -> Dict:
        templates = self._data.get("ladder_templates", {}).get("templates", {})
        return templates.get(position, {})

    def get_default_user_profile(self) -> Dict:
        return self._data.get("user_profile_default", {}).get("profile", {})

knowledge = KnowledgeLoader()
