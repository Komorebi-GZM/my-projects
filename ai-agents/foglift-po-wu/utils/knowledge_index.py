from __future__ import annotations

import json
from typing import Any, Iterable

from utils.knowledge_loader import knowledge
from utils.knowledge_types import KnowledgeDoc


DOMAIN_ORDER = (
    "jd_library",
    "jargon_map",
    "skill_resource_map",
    "interview_questions",
    "ladder_templates",
    "user_profile_default",
)


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _content_from_parts(*parts: Any) -> str:
    return "\n".join(str(part) for part in parts if part not in (None, "", [], {}))


def _iter_jd_docs(data: dict[str, Any]) -> Iterable[KnowledgeDoc]:
    for position in data.get("positions", []):
        title = position.get("name") or f"JD {position.get('number', '')}".strip()
        doc_id = f"jd_library:{position.get('number', title)}"
        content = _content_from_parts(
            title,
            position.get("company"),
            position.get("city"),
            position.get("summary"),
            position.get("keywords"),
            position.get("硬技能"),
            position.get("软技能"),
            position.get("ai_analysis_summary"),
        )
        yield KnowledgeDoc(doc_id, "jd_library", title, content, position)


def _iter_jargon_docs(data: dict[str, Any]) -> Iterable[KnowledgeDoc]:
    for section in ("mappings", "common_jargons", "interview_decode"):
        for phrase, meaning in data.get(section, {}).items():
            yield KnowledgeDoc(
                id=f"jargon_map:{section}:{phrase}",
                domain="jargon_map",
                title=phrase,
                content=_content_from_parts(phrase, meaning),
                metadata={"section": section, "phrase": phrase, "meaning": meaning},
            )


def _iter_skill_resource_docs(data: dict[str, Any]) -> Iterable[KnowledgeDoc]:
    for skill, resources in data.get("mappings", {}).items():
        resource_text = [
            _content_from_parts(resource.get("name"), resource.get("url"))
            for resource in resources
        ]
        yield KnowledgeDoc(
            id=f"skill_resource_map:{skill}",
            domain="skill_resource_map",
            title=skill,
            content=_content_from_parts(skill, *resource_text),
            metadata={"skill": skill, "resources": resources},
        )


def _iter_interview_docs(data: dict[str, Any]) -> Iterable[KnowledgeDoc]:
    for position, questions in data.get("questions", {}).items():
        yield KnowledgeDoc(
            id=f"interview_questions:{position}",
            domain="interview_questions",
            title=position,
            content=_content_from_parts(position, _stable_json(questions)),
            metadata={"position": position, "questions": questions},
        )


def _iter_ladder_docs(data: dict[str, Any]) -> Iterable[KnowledgeDoc]:
    for position, template in data.get("templates", {}).items():
        yield KnowledgeDoc(
            id=f"ladder_templates:{position}",
            domain="ladder_templates",
            title=position,
            content=_content_from_parts(position, _stable_json(template)),
            metadata={"position": position, "template": template},
        )


def _iter_profile_docs(data: dict[str, Any]) -> Iterable[KnowledgeDoc]:
    profile = data.get("profile", {})
    if profile:
        yield KnowledgeDoc(
            id="user_profile_default:profile",
            domain="user_profile_default",
            title="默认用户画像",
            content=_content_from_parts("默认用户画像", _stable_json(profile)),
            metadata=profile,
        )


def build_knowledge_docs(loader=knowledge) -> list[KnowledgeDoc]:
    """Build deterministic retrieval documents from raw JSON knowledge."""

    builders = {
        "jd_library": _iter_jd_docs,
        "jargon_map": _iter_jargon_docs,
        "skill_resource_map": _iter_skill_resource_docs,
        "interview_questions": _iter_interview_docs,
        "ladder_templates": _iter_ladder_docs,
        "user_profile_default": _iter_profile_docs,
    }

    docs: list[KnowledgeDoc] = []
    for domain in DOMAIN_ORDER:
        raw_data = loader.get(domain) or {}
        docs.extend(builders[domain](raw_data))
    return docs
