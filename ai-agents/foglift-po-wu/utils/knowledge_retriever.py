from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Protocol

from utils.knowledge_index import build_knowledge_docs
from utils.knowledge_types import KnowledgeDoc, KnowledgeHit


class SemanticBackend(Protocol):
    def search(
        self,
        query: str,
        docs: list[KnowledgeDoc],
        top_k: int,
    ) -> list[KnowledgeHit]:
        ...


def _tokens(text: str) -> list[str]:
    lowered = text.lower()
    ascii_tokens = re.findall(r"[a-z0-9_+#.]+", lowered)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", lowered)
    chinese_grams = []
    for size in (2, 3):
        chinese_grams.extend(
            "".join(chinese_chars[index:index + size])
            for index in range(0, max(len(chinese_chars) - size + 1, 0))
        )
    return [token for token in [*ascii_tokens, *chinese_grams] if token]


def _score_doc(query: str, query_tokens: set[str], doc: KnowledgeDoc) -> KnowledgeHit | None:
    title = doc.title.lower()
    content = doc.content.lower()
    metadata_text = str(doc.metadata).lower()
    lowered_query = query.lower()
    score = 0.0
    reasons: list[str] = []

    if lowered_query == title:
        score += 10.0
        reasons.append("exact_title")
    if lowered_query and lowered_query in title:
        score += 6.0
        reasons.append("title_substring")
    if lowered_query and lowered_query in content:
        score += 3.0
        reasons.append("content_substring")
    if lowered_query and lowered_query in metadata_text:
        score += 2.0
        reasons.append("metadata_substring")

    title_tokens = set(_tokens(doc.title))
    content_tokens = set(_tokens(doc.content))
    metadata_tokens = set(_tokens(metadata_text))
    title_matches = query_tokens & title_tokens
    content_matches = query_tokens & content_tokens
    metadata_matches = query_tokens & metadata_tokens

    if title_matches:
        score += len(title_matches) * 2.0
        reasons.append("title_token")
    if content_matches:
        score += len(content_matches) * 1.0
        reasons.append("content_token")
    if metadata_matches:
        score += len(metadata_matches) * 0.5
        reasons.append("metadata_token")

    if score <= 0:
        return None
    return KnowledgeHit(doc=doc, score=score, match_reasons=reasons)


def _merge_hit(existing: KnowledgeHit, incoming: KnowledgeHit) -> KnowledgeHit:
    reasons = list(dict.fromkeys([*existing.match_reasons, *incoming.match_reasons]))
    return KnowledgeHit(
        doc=existing.doc,
        score=existing.score + incoming.score,
        match_reasons=reasons,
    )


class KnowledgeRetriever:
    def __init__(
        self,
        docs: Sequence[KnowledgeDoc] | None = None,
        semantic_backend: SemanticBackend | None = None,
    ):
        self.docs = list(docs) if docs is not None else build_knowledge_docs()
        self.semantic_backend = semantic_backend

    def retrieve(
        self,
        query: str,
        domains: list[str] | None = None,
        top_k: int = 5,
    ) -> list[KnowledgeHit]:
        query = query.strip()
        if not query or top_k <= 0:
            return []

        allowed_domains = set(domains) if domains else None
        filtered_docs = [
            doc for doc in self.docs
            if allowed_domains is None or doc.domain in allowed_domains
        ]
        allowed_ids = {doc.id for doc in filtered_docs}
        query_tokens = set(_tokens(query))

        hits_by_id: dict[str, KnowledgeHit] = {}
        for doc in filtered_docs:
            hit = _score_doc(query, query_tokens, doc)
            if hit:
                hits_by_id[doc.id] = hit

        if self.semantic_backend:
            for hit in self.semantic_backend.search(query, filtered_docs, top_k):
                if hit.id not in allowed_ids or hit.score <= 0:
                    continue
                if hit.id in hits_by_id:
                    hits_by_id[hit.id] = _merge_hit(hits_by_id[hit.id], hit)
                else:
                    hits_by_id[hit.id] = hit

        index_by_id = {doc.id: index for index, doc in enumerate(self.docs)}
        ranked = sorted(
            hits_by_id.values(),
            key=lambda hit: (-hit.score, index_by_id[hit.id]),
        )
        return ranked[:top_k]
