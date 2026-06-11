from typing import Dict, Any, Optional, List
from tools.booking import book_poi


def _bookable_pois_from_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return normalized POI entries from either canonical or planner-style plans."""
    pois = plan.get("pois")
    if isinstance(pois, list) and pois:
        normalized = []
        for poi in pois:
            if not isinstance(poi, dict):
                continue
            name = poi.get("name") or poi.get("restaurant")
            if name:
                normalized.append({
                    "name": name,
                    "time_slot": poi.get("time_slot") or plan.get("time_slot"),
                })
        return normalized

    restaurant = plan.get("restaurant") or plan.get("poi_name")
    if restaurant:
        return [{"name": restaurant, "time_slot": plan.get("time_slot")}]

    return []


class ExecutorAgent:
    def execute(self, plan: Dict, trace_id: Optional[str] = None, city: str = "上海") -> Dict[str, Any]:
        results = []
        bookable_pois = _bookable_pois_from_plan(plan)
        if not bookable_pois:
            return {
                "success": False,
                "error": "No bookable POIs in selected plan",
                "results": [],
            }

        for poi in bookable_pois:
            result = book_poi(
                poi_name=poi["name"],
                time_slot=poi.get("time_slot"),
                trace_id=trace_id,
                city=city,
            )
            results.append(result)

            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error"),
                    "results": results,
                }

        return {"success": True, "results": results}
