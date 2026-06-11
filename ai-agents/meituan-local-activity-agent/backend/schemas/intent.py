from typing import TypedDict, List, Dict, Optional


class Intent(TypedDict):
    time: Dict[str, str]
    location: Dict[str, str]
    group: Dict
    scene: str
    constraints: Dict
    preferences: Dict
    missing_fields: List[str]
