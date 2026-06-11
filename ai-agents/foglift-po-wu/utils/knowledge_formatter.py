from utils.knowledge_types import KnowledgeHit


EMPTY_EVIDENCE_TEXT = "未检索到匹配知识库证据。"


def _truncate(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}..."


def format_evidence_blocks(
    hits: list[KnowledgeHit],
    max_content_chars: int = 500,
) -> str:
    """Format retrieval hits into prompt-ready evidence blocks."""

    if not hits:
        return EMPTY_EVIDENCE_TEXT

    blocks = []
    for index, hit in enumerate(hits, start=1):
        reasons = ", ".join(hit.match_reasons) if hit.match_reasons else "unknown"
        blocks.append(
            "\n".join(
                [
                    f"[证据 {index}] {hit.domain} / {hit.title}",
                    f"id: {hit.id}",
                    f"score: {hit.score:.2f}",
                    f"match_reasons: {reasons}",
                    "content:",
                    _truncate(hit.content, max_content_chars),
                ]
            )
        )
    return "\n\n".join(blocks)
