from typing import TypedDict, List, Dict


class Plan(TypedDict):
    id: str
    name: str
    description: str
    pois: List[Dict]
    total_budget: float
    estimated_duration_minutes: int
    highlights: List[str]
