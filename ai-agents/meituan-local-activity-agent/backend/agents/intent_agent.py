import os
from typing import Dict, Any
from agents.llm_client import call_llm_dict


class IntentAgent:
    def __init__(self):
        self.prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "prompts", "intent_agent.txt"
        )

    def parse(self, user_input: str, trace_id: str = None) -> Dict[str, Any]:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        intent = call_llm_dict(user_input, system_prompt)
        return self._fill_defaults(intent)

    def _fill_defaults(self, intent: Dict) -> Dict:
        defaults = {
            "time": {"range": "全天", "flexibility": "±2h"},
            "location": {"city": "上海", "district": ""},
            "group": {"type": "friends", "count": 2, "children": []},
            "scene": "friends",
            "constraints": {"max_distance_km": 10, "budget": 500},
            "preferences": {"food": "无偏好", "activity": "无偏好"},
            "missing_fields": []
        }
        for key, value in defaults.items():
            if key not in intent or intent[key] is None:
                intent[key] = value
            elif isinstance(value, dict) and isinstance(intent[key], dict):
                for sub_key, sub_val in value.items():
                    if sub_key not in intent[key] or intent[key][sub_key] is None:
                        intent[key][sub_key] = sub_val
        return intent