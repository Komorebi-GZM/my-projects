"""
知识库管理
三层知识库架构实现 + BM25/向量混合检索（RRF 融合）
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .embeddings import BGEEmbeddings, get_embedding_model
from .vectorstore import BaseVectorStore, get_vector_store

logger = logging.getLogger(__name__)


class KnowledgeLevel(str, Enum):
    """知识库层级"""

    UNIVERSAL = "universal"  # 通用基础库（教材）
    SCHOOL = "school"  # 学校共享库（校本教案）
    TEACHER = "teacher"  # 教师专属库（个人风格）


# ── BM25 关键词检索器 ─────────────────────────────────────────────


class BM25Retriever:
    """BM25 关键词检索器

    基于 jieba 中文分词 + rank_bm25 实现真正的关键词检索。
    与向量检索互补：向量检索擅长语义匹配，BM25 擅长精确关键词匹配。
    """

    def __init__(self):
        self._corpus: List[str] = []
        self._tokenized_corpus: List[List[str]] = []
        self._bm25 = None

    def add_documents(self, documents: List[str]) -> None:
        """添加文档到 BM25 索引

        Args:
            documents: 文档文本列表
        """
        import jieba
        from rank_bm25 import BM25Okapi

        self._corpus = list(documents)
        self._tokenized_corpus = [list(jieba.cut(doc)) for doc in self._corpus]
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    def doc_count(self) -> int:
        """返回已索引的文档数量"""
        return len(self._corpus)

    def search(self, query: str, k: int = 4) -> List[Any]:
        """BM25 关键词检索

        Args:
            query: 查询文本
            k: 返回数量

        Returns:
            检索结果列表（mock Document 对象，含 page_content）
        """
        if self._bm25 is None or len(self._corpus) == 0:
            return []

        import jieba

        tokenized_query = list(jieba.cut(query))
        scores = self._bm25.get_scores(tokenized_query)

        # 按分数降序排列，取 top-k
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )[:k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = _make_text_document(self._corpus[idx])
                results.append(doc)

        return results


def _make_text_document(text: str, metadata: Optional[Dict] = None) -> Any:
    """创建轻量 Document 对象（无需 langchain Document 依赖）"""
    doc = type("Document", (), {})()
    doc.page_content = text
    doc.metadata = metadata or {}
    return doc


# ── RRF 融合排序 ─────────────────────────────────────────────────


def _rrf_fusion(
    results_list: List[List[Any]],
    weights: Optional[List[float]] = None,
    k: int = 60,
) -> List[Any]:
    """Reciprocal Rank Fusion（倒数排名融合）

    将多路检索结果按 RRF 公式融合排序：
        score(d) = Σ weight_i / (k + rank_i(d))

    Args:
        results_list: 多路检索结果列表
        weights: 各路权重（默认等权）
        k: RRF 常数（默认 60）

    Returns:
        融合后的去重结果列表，按 RRF 分数降序
    """
    if not results_list:
        return []

    if weights is None:
        weights = [1.0] * len(results_list)

    rrf_scores: Dict[str, Tuple[float, Any]] = {}

    for results, weight in zip(results_list, weights, strict=True):
        for rank, doc in enumerate(results):
            key = doc.page_content
            current_score = rrf_scores.get(key, (0.0, doc))
            new_score = current_score[0] + weight / (k + rank + 1)
            rrf_scores[key] = (new_score, doc)

    # 按 RRF 分数降序排列
    sorted_results = sorted(
        rrf_scores.values(),
        key=lambda x: x[0],
        reverse=True,
    )

    return [doc for _, doc in sorted_results]


# ── 混合检索器 ────────────────────────────────────────────────────


class HybridRetriever:
    """混合检索器

    结合向量检索（语义匹配）和 BM25 关键词检索（精确匹配），
    通过 RRF（Reciprocal Rank Fusion）加权融合两路结果。
    """

    def __init__(
        self,
        vectorstore: BaseVectorStore,
        embedding_model: Optional[BGEEmbeddings] = None,
    ):
        self.vectorstore = vectorstore
        self.embedding_model = embedding_model
        self.bm25 = BM25Retriever()

    def vector_search(self, query: str, k: int = 4) -> List[Any]:
        """向量检索（语义匹配）"""
        return self.vectorstore.similarity_search(query, k=k)

    def keyword_search(self, query: str, k: int = 4) -> List[Any]:
        """BM25 关键词检索（精确匹配）"""
        return self.bm25.search(query, k=k)

    def hybrid_search(
        self,
        query: str,
        k: int = 4,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> List[Any]:
        """混合检索：向量 + BM25 双路检索 → RRF 融合

        Args:
            query: 查询文本
            k: 最终返回数量
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重

        Returns:
            RRF 融合后的 top-k 结果
        """
        # 双路检索（各取较多候选，融合后再截断）
        fetch_k = max(k * 3, 10)
        vector_results = self.vector_search(query, k=fetch_k)
        keyword_results = self.keyword_search(query, k=fetch_k)

        # RRF 融合
        fused = _rrf_fusion(
            [vector_results, keyword_results],
            weights=[vector_weight, keyword_weight],
        )

        return fused[:k]


# ── 知识库管理器 ──────────────────────────────────────────────────


class KnowledgeBase:
    """知识库管理器

    三层知识库架构：
    1. 通用基础库 - 教材内容、标准教案
    2. 学校共享库 - 校本教案、共享资源
    3. 教师专属库 - 个人风格画像、偏好设置

    可选启用混合检索（向量 + BM25 RRF 融合）。
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        embedding_model_name: str = "BAAI/bge-large-zh",
        use_hybrid: bool = False,
    ):
        self.persist_directory = persist_directory
        self.embedding = get_embedding_model("bge", embedding_model_name)
        self.collections: Dict[KnowledgeLevel, BaseVectorStore] = {}
        self.use_hybrid = use_hybrid
        self._hybrid_retrievers: Dict[KnowledgeLevel, HybridRetriever] = {}

        self._init_collections()

    def _init_collections(self):
        """初始化知识库集合"""
        for level in KnowledgeLevel:
            self.collections[level] = get_vector_store(
                store_type="chroma",
                collection_name=f"knowledge_{level.value}",
                persist_directory=self.persist_directory,
                embedding_function=self.embedding,
            )

    def _get_or_create_hybrid_retriever(self, level: KnowledgeLevel) -> Optional[HybridRetriever]:
        """获取或创建指定层级的混合检索器"""
        if not self.use_hybrid:
            return None

        if level not in self._hybrid_retrievers:
            vectorstore = self.collections[level]
            retriever = HybridRetriever(
                vectorstore=vectorstore,
                embedding_model=self.embedding,
            )
            self._hybrid_retrievers[level] = retriever

        return self._hybrid_retrievers[level]

    def add_document(
        self, text: str, level: KnowledgeLevel, metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """添加文档到指定层级知识库

        Args:
            text: 文档内容
            level: 知识库层级
            metadata: 元数据

        Returns:
            文档ID列表
        """
        if level not in self.collections:
            raise ValueError(f"未知的知识库层级: {level}")

        doc_metadata = metadata or {}
        doc_metadata["level"] = level.value

        vectorstore = self.collections[level]
        return vectorstore.add_texts([text], metadatas=[doc_metadata])

    def add_documents(
        self,
        texts: List[str],
        level: KnowledgeLevel,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """批量添加文档

        Args:
            texts: 文档内容列表
            level: 知识库层级
            metadatas: 元数据列表

        Returns:
            文档ID列表
        """
        if level not in self.collections:
            raise ValueError(f"未知的知识库层级: {level}")

        docs_metadata = []
        for i, metadata in enumerate(metadatas or [{} for _ in texts]):
            doc_metadata = metadata.copy()
            doc_metadata["level"] = level.value
            docs_metadata.append(doc_metadata)

        vectorstore = self.collections[level]
        return vectorstore.add_texts(texts, metadatas=docs_metadata)

    def search(self, query: str, level: Optional[KnowledgeLevel] = None, k: int = 4) -> List[Any]:
        """搜索知识库

        启用混合检索时，使用向量 + BM25 RRF 融合；
        否则使用纯向量检索（向后兼容）。

        Args:
            query: 查询内容
            level: 指定层级（None表示所有层级）
            k: 返回数量

        Returns:
            搜索结果列表
        """
        if level:
            if level not in self.collections:
                raise ValueError(f"未知的知识库层级: {level}")
            return self._search_single_level(level, query, k)

        results = []
        for lvl in self.collections:
            level_results = self._search_single_level(lvl, query, k)
            results.extend(level_results)
        return results

    def _search_single_level(
        self,
        level: KnowledgeLevel,
        query: str,
        k: int,
    ) -> List[Any]:
        """搜索单个层级"""
        hybrid = self._get_or_create_hybrid_retriever(level)
        if hybrid is not None:
            return hybrid.hybrid_search(query, k=k)

        return self.collections[level].similarity_search(query, k=k)

    def search_with_filter(self, query: str, filter_dict: Dict[str, Any], k: int = 4) -> List[Any]:
        """带过滤条件的搜索

        Args:
            query: 查询内容
            filter_dict: 过滤条件
            k: 返回数量

        Returns:
            搜索结果列表
        """
        results = []
        for level_vectorstore in self.collections.values():
            try:
                level_results = level_vectorstore.similarity_search(query, k=k, filter=filter_dict)
                results.extend(level_results)
            except Exception as e:
                logger.warning(f"层级检索失败 (filter={filter_dict}): {e}")
                continue
        return results

    def delete_by_level(self, level: KnowledgeLevel, ids: List[str]) -> None:
        """删除指定层级的文档

        Args:
            level: 知识库层级
            ids: 文档ID列表
        """
        if level not in self.collections:
            raise ValueError(f"未知的知识库层级: {level}")
        self.collections[level].delete(ids)

    def get_collection_info(self, level: KnowledgeLevel) -> Dict[str, Any]:
        """获取知识库集合信息

        Args:
            level: 知识库层级

        Returns:
            集合信息
        """
        if level not in self.collections:
            raise ValueError(f"未知的知识库层级: {level}")

        self.collections[level]
        return {
            "level": level.value,
            "name": f"knowledge_{level.value}",
            "persist_directory": self.persist_directory,
        }
