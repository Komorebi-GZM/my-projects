from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class KnowledgeDoc:
    """Flattened knowledge-base document for retrieval."""

    id: str
    domain: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeHit:
    """Retrieval hit with explainable scoring details."""

    doc: KnowledgeDoc
    score: float
    match_reasons: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.doc.id

    @property
    def domain(self) -> str:
        return self.doc.domain

    @property
    def title(self) -> str:
        return self.doc.title

    @property
    def content(self) -> str:
        return self.doc.content

    @property
    def metadata(self) -> dict[str, Any]:
        return self.doc.metadata
