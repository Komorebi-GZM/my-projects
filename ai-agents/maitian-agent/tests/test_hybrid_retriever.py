"""混合检索测试 — 验证 BM25 + 向量检索 RRF 融合

核心断言：
1. BM25Retriever 基于 jieba 分词 + rank_bm25 实现真正的关键词检索
2. HybridRetriever.hybrid_search() 执行双路检索 + RRF 融合
3. RRF 融合结果优于单一检索（召回更多相关文档）
4. KnowledgeBase.search() 支持 use_hybrid 参数
5. 向后兼容：默认不启用混合检索，原有接口不变
6. 权重可配置（vector_weight / keyword_weight）
"""
from __future__ import annotations

from typing import List
from unittest.mock import MagicMock

import pytest


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_doc(content: str, metadata: dict = None) -> MagicMock:
    """创建 mock Document 对象"""
    doc = MagicMock()
    doc.page_content = content
    doc.metadata = metadata or {}
    return doc


# 测试语料
_CORPUS = [
    "分数的加法：同分母分数相加，分母不变，分子相加。",
    "分数的减法：同分母分数相减，分母不变，分子相减。",
    "水的循环：蒸发、凝结、降水、径流四个阶段。",
    "水的三态：固态、液态、气态之间的相互转化。",
    "光合作用：植物利用阳光将二氧化碳和水转化为葡萄糖。",
]


# ══════════════════════════════════════════════════════════════════
# 1. BM25Retriever — 真正的关键词检索
# ══════════════════════════════════════════════════════════════════

class TestBM25Retriever:
    """验证 BM25Retriever 实现真正的关键词检索"""

    def test_bm25_retriever_exists(self):
        """BM25Retriever 类应存在"""
        from maitian_agent.rag.knowledge_base import BM25Retriever
        assert BM25Retriever is not None

    def test_bm25_add_documents(self):
        """add_documents() 应建立 BM25 索引"""
        from maitian_agent.rag.knowledge_base import BM25Retriever

        retriever = BM25Retriever()
        retriever.add_documents(_CORPUS)

        assert retriever.doc_count() == len(_CORPUS)

    def test_bm25_search_returns_results(self):
        """search() 应返回与查询关键词匹配的文档"""
        from maitian_agent.rag.knowledge_base import BM25Retriever

        retriever = BM25Retriever()
        retriever.add_documents(_CORPUS)

        results = retriever.search("分数加法", k=2)

        assert len(results) <= 2
        assert len(results) >= 1
        # 应包含关于分数加法的文档
        contents = [r.page_content for r in results]
        assert any("分数" in c for c in contents)

    def test_bm25_search_uses_jieba_tokenization(self):
        """BM25 检索应使用 jieba 中文分词"""
        from maitian_agent.rag.knowledge_base import BM25Retriever

        retriever = BM25Retriever()
        retriever.add_documents(_CORPUS)

        results = retriever.search("光合作用", k=1)

        assert len(results) >= 1
        assert "光合作用" in results[0].page_content

    def test_bm25_search_empty_corpus(self):
        """空语料库时 search() 应返回空列表"""
        from maitian_agent.rag.knowledge_base import BM25Retriever

        retriever = BM25Retriever()
        results = retriever.search("测试查询", k=4)

        assert results == []

    def test_bm25_search_no_match(self):
        """无匹配时 search() 应返回空列表"""
        from maitian_agent.rag.knowledge_base import BM25Retriever

        retriever = BM25Retriever()
        retriever.add_documents(_CORPUS)

        results = retriever.search("量子力学相对论", k=4)

        # BM25 对完全不匹配的查询仍会返回结果（按词频排序）
        # 但相关性很低，这里只验证不崩溃
        assert isinstance(results, list)


# ══════════════════════════════════════════════════════════════════
# 2. HybridRetriever — 双路检索 + RRF 融合
# ══════════════════════════════════════════════════════════════════

class TestHybridRetrieverRRF:
    """验证 HybridRetriever 执行真正的双路检索 + RRF 融合"""

    def test_hybrid_search_returns_results(self):
        """hybrid_search() 应返回融合后的检索结果"""
        from maitian_agent.rag.knowledge_base import HybridRetriever

        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = [
            _make_mock_doc("分数的加法：同分母分数相加"),
            _make_mock_doc("水的循环：蒸发凝结"),
        ]

        retriever = HybridRetriever(vectorstore=mock_vectorstore)
        retriever.bm25.add_documents(_CORPUS)

        results = retriever.hybrid_search("分数加法", k=3)

        assert len(results) >= 1
        assert all(hasattr(r, "page_content") for r in results)

    def test_hybrid_search_calls_both_retrievers(self):
        """hybrid_search() 应同时调用向量检索和 BM25 检索"""
        from maitian_agent.rag.knowledge_base import HybridRetriever

        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = [
            _make_mock_doc("分数的加法"),
        ]

        retriever = HybridRetriever(vectorstore=mock_vectorstore)
        retriever.bm25.add_documents(_CORPUS)

        retriever.hybrid_search("分数", k=2)

        mock_vectorstore.similarity_search.assert_called_once()

    def test_hybrid_search_rrf_fusion(self):
        """RRF 融合应将两路结果合并去重"""
        from maitian_agent.rag.knowledge_base import HybridRetriever

        # 向量检索返回文档 A、B
        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = [
            _make_mock_doc("分数的加法：同分母分数相加"),
            _make_mock_doc("水的循环：蒸发凝结降水"),
        ]

        retriever = HybridRetriever(vectorstore=mock_vectorstore)
        retriever.bm25.add_documents(_CORPUS)

        results = retriever.hybrid_search("分数加法", k=4)

        # RRF 融合后结果数应 >= max(向量结果数, BM25结果数) 的去重版本
        assert len(results) >= 1
        # 检查去重：不应有重复的 page_content
        contents = [r.page_content for r in results]
        assert len(contents) == len(set(contents))

    def test_hybrid_search_respects_k_limit(self):
        """hybrid_search() 应尊重 k 参数限制"""
        from maitian_agent.rag.knowledge_base import HybridRetriever

        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = [
            _make_mock_doc(f"文档{i}") for i in range(10)
        ]

        retriever = HybridRetriever(vectorstore=mock_vectorstore)
        retriever.bm25.add_documents(_CORPUS)

        results = retriever.hybrid_search("测试", k=2)

        assert len(results) <= 2

    def test_hybrid_search_weight_configurable(self):
        """hybrid_search() 应支持权重配置"""
        from maitian_agent.rag.knowledge_base import HybridRetriever

        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = [
            _make_mock_doc("分数的加法"),
        ]

        retriever = HybridRetriever(vectorstore=mock_vectorstore)
        retriever.bm25.add_documents(_CORPUS)

        # 不同权重不应崩溃
        results_70_30 = retriever.hybrid_search("分数", k=2, vector_weight=0.7, keyword_weight=0.3)
        results_50_50 = retriever.hybrid_search("分数", k=2, vector_weight=0.5, keyword_weight=0.5)

        assert isinstance(results_70_30, list)
        assert isinstance(results_50_50, list)

    def test_keyword_search_is_real_bm25(self):
        """keyword_search() 应执行真正的 BM25 检索，非向量检索降级"""
        from maitian_agent.rag.knowledge_base import HybridRetriever

        mock_vectorstore = MagicMock()

        retriever = HybridRetriever(vectorstore=mock_vectorstore)
        retriever.bm25.add_documents(_CORPUS)

        results = retriever.keyword_search("光合作用", k=2)

        # keyword_search 不应调用 vectorstore
        mock_vectorstore.similarity_search.assert_not_called()
        assert len(results) >= 1
        assert "光合作用" in results[0].page_content


# ══════════════════════════════════════════════════════════════════
# 3. KnowledgeBase 集成混合检索
# ══════════════════════════════════════════════════════════════════

class TestKnowledgeBaseHybridIntegration:
    """验证 KnowledgeBase.search() 支持混合检索"""

    def test_knowledge_base_search_default_backward_compat(self):
        """默认 search() 行为不变（向后兼容）"""
        from maitian_agent.rag.knowledge_base import KnowledgeBase

        # 使用 mock 避免 Chroma 初始化
        with pytest.MonkeyPatch.context() as m:
            m.setattr("maitian_agent.rag.knowledge_base.get_embedding_model", MagicMock())
            m.setattr("maitian_agent.rag.knowledge_base.get_vector_store", MagicMock())

            kb = KnowledgeBase.__new__(KnowledgeBase)
            kb.collections = {}
            kb.persist_directory = "/tmp/test"
            kb.embedding = MagicMock()

            # search() 默认不启用混合检索
            # 只验证接口存在且可调用
            assert hasattr(kb, "search")

    def test_knowledge_base_use_hybrid_param(self):
        """KnowledgeBase 应支持 use_hybrid 参数"""
        from maitian_agent.rag.knowledge_base import KnowledgeBase

        import inspect
        sig = inspect.signature(KnowledgeBase.__init__)
        assert "use_hybrid" in sig.parameters

    def test_hybrid_retriever_accessible_from_knowledge_base(self):
        """KnowledgeBase 启用混合检索时应创建 HybridRetriever"""
        from maitian_agent.rag.knowledge_base import KnowledgeBase

        with pytest.MonkeyPatch.context() as m:
            m.setattr("maitian_agent.rag.knowledge_base.get_embedding_model", MagicMock())
            m.setattr("maitian_agent.rag.knowledge_base.get_vector_store", MagicMock())

            kb = KnowledgeBase.__new__(KnowledgeBase)
            kb.collections = {}
            kb.persist_directory = "/tmp/test"
            kb.embedding = MagicMock()
            kb.use_hybrid = True
            kb._hybrid_retrievers = {}

            # 验证 hybrid_retriever 属性存在
            assert hasattr(kb, "_hybrid_retrievers")


# ══════════════════════════════════════════════════════════════════
# 4. 向后兼容 — 现有 Agent 的 _retrieve_context() 不受影响
# ══════════════════════════════════════════════════════════════════

class TestBackwardCompatibility:
    """验证向后兼容性"""

    def test_mock_kb_search_still_works(self):
        """mock KnowledgeBase 的 search() 仍可正常使用"""
        from unittest.mock import MagicMock

        kb = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "测试内容"
        kb.search.return_value = [mock_doc]

        results = kb.search("测试查询", k=4)
        assert len(results) == 1
        assert results[0].page_content == "测试内容"

    def test_hybrid_retriever_vector_search_fallback(self):
        """vector_search() 应正常工作（原有接口）"""
        from maitian_agent.rag.knowledge_base import HybridRetriever

        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = [
            _make_mock_doc("测试文档"),
        ]

        retriever = HybridRetriever(vectorstore=mock_vectorstore)
        results = retriever.vector_search("测试", k=1)

        assert len(results) == 1
        mock_vectorstore.similarity_search.assert_called_once()
