"""FastAPI lifespan 事件处理器测试 — 验证 on_event 迁移为 lifespan

核心断言：
1. create_app() 返回的 FastAPI 实例可正常启动（lifespan 无异常）
2. 启动后 app.state.agents 包含全部 6 个 Agent
3. /health 端点返回所有 Agent 名称
4. 无 DeprecationWarning（on_event 废弃语法已消除）
5. API 端点功能兼容（/api/route 正常路由）
6. create_app() 接口不变，返回 FastAPI 实例
"""
from __future__ import annotations

import warnings
import inspect
import ast
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

import pytest


# ── 辅助 ──────────────────────────────────────────────────────────

def _make_mock_llm(response_text: str = "quick_lesson_prep"):
    """创建 mock LLM，返回指定意图名称"""
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage
    llm = MagicMock(spec=BaseChatModel)
    llm.invoke.return_value = AIMessage(content=response_text)
    return llm


# ══════════════════════════════════════════════════════════════════
# 1. lifespan 启动正常
# ══════════════════════════════════════════════════════════════════

class TestLifespanStartup:
    """验证 lifespan 上下文管理器正常启动"""

    @pytest.mark.anyio
    async def test_create_app_returns_fastapi_instance(self):
        """create_app() 应返回 FastAPI 实例"""
        from fastapi import FastAPI
        from maitian_agent.api.routes import create_app

        app = create_app()
        assert isinstance(app, FastAPI)

    @pytest.mark.anyio
    async def test_app_startup_initializes_agents(self):
        """应用启动后，app.state.agents 应包含全部 6 个 Agent"""
        from maitian_agent.api.routes import create_app

        with patch("maitian_agent.api.routes.AgentFactory") as MockFactory:
            mock_factory = MagicMock()
            mock_factory.create_all.return_value = {
                "quick_lesson_prep": MagicMock(),
                "wisdom_transfer": MagicMock(),
                "classroom_companion": MagicMock(),
                "material": MagicMock(),
                "meeting_notes": MagicMock(),
                "router": MagicMock(),
            }
            MockFactory.return_value = mock_factory

            app = create_app()

            # lifespan 在 async with 中执行
            async with app.router.lifespan_context(app):
                assert hasattr(app.state, "agents")
                assert len(app.state.agents) == 6
                assert "quick_lesson_prep" in app.state.agents
                assert "router" in app.state.agents

    @pytest.mark.anyio
    async def test_factory_create_all_called_on_startup(self):
        """启动时应调用 AgentFactory().create_all()"""
        from maitian_agent.api.routes import create_app

        with patch("maitian_agent.api.routes.AgentFactory") as MockFactory:
            mock_factory = MagicMock()
            mock_factory.create_all.return_value = {
                "quick_lesson_prep": MagicMock(),
                "wisdom_transfer": MagicMock(),
                "classroom_companion": MagicMock(),
                "material": MagicMock(),
                "meeting_notes": MagicMock(),
                "router": MagicMock(),
            }
            MockFactory.return_value = mock_factory

            app = create_app()
            async with app.router.lifespan_context(app):
                MockFactory.assert_called_once()
                mock_factory.create_all.assert_called_once()


# ══════════════════════════════════════════════════════════════════
# 2. 无 DeprecationWarning
# ══════════════════════════════════════════════════════════════════

class TestNoDeprecationWarning:
    """验证 on_event 废弃语法已消除"""

    @pytest.mark.anyio
    async def test_no_on_event_deprecation_warning(self):
        """导入 routes 模块时不应产生 on_event DeprecationWarning"""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            # 强制重新导入
            import importlib
            import maitian_agent.api.routes as routes_module
            importlib.reload(routes_module)

            deprecation_warnings = [
                w for w in caught
                if issubclass(w.category, DeprecationWarning)
                and "on_event" in str(w.message)
            ]
            assert len(deprecation_warnings) == 0, (
                f"发现 {len(deprecation_warnings)} 个 on_event 废弃警告: "
                f"{[str(w.message) for w in deprecation_warnings]}"
            )

    def test_routes_source_no_on_event_string(self):
        """routes.py 源码中不应包含 'on_event' 字符串"""
        import inspect
        import maitian_agent.api.routes as routes_module

        source = inspect.getsource(routes_module)
        assert "on_event" not in source, \
            "routes.py 仍包含废弃的 on_event 语法"


# ══════════════════════════════════════════════════════════════════
# 3. API 端点功能兼容
# ══════════════════════════════════════════════════════════════════

class TestAPIEndpointCompatibility:
    """验证 API 端点功能完全兼容"""

    @pytest.mark.anyio
    async def test_health_endpoint_returns_agents(self):
        """/health 端点应返回所有 Agent 名称"""
        from maitian_agent.api.routes import create_app

        with patch("maitian_agent.api.routes.AgentFactory") as MockFactory:
            mock_router = MagicMock()
            mock_router.run.return_value = {
                "success": True,
                "result": {"intent": "general_chat", "info": {}},
                "agent": "RouterAgent",
                "metadata": {},
            }
            mock_factory = MagicMock()
            mock_factory.create_all.return_value = {
                "quick_lesson_prep": MagicMock(),
                "wisdom_transfer": MagicMock(),
                "classroom_companion": MagicMock(),
                "material": MagicMock(),
                "meeting_notes": MagicMock(),
                "router": mock_router,
            }
            MockFactory.return_value = mock_factory

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                async with app.router.lifespan_context(app):
                    response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "agents" in data
            assert len(data["agents"]) == 6

    @pytest.mark.anyio
    async def test_root_endpoint(self):
        """/ 根路径应返回 API 信息"""
        from maitian_agent.api.routes import create_app

        with patch("maitian_agent.api.routes.AgentFactory") as MockFactory:
            mock_factory = MagicMock()
            mock_factory.create_all.return_value = {
                "quick_lesson_prep": MagicMock(),
                "wisdom_transfer": MagicMock(),
                "classroom_companion": MagicMock(),
                "material": MagicMock(),
                "meeting_notes": MagicMock(),
                "router": MagicMock(),
            }
            MockFactory.return_value = mock_factory

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                async with app.router.lifespan_context(app):
                    response = await client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert "麦田智囊" in data["message"]

    @pytest.mark.anyio
    async def test_route_endpoint_compatible(self):
        """/api/route 端点应正常工作"""
        from maitian_agent.api.routes import create_app

        mock_router = MagicMock()
        mock_router.run.return_value = {
            "success": True,
            "result": {"intent": "quick_lesson_prep", "info": {}},
            "agent": "RouterAgent",
            "metadata": {"routed_intent": "quick_lesson_prep"},
        }

        with patch("maitian_agent.api.routes.AgentFactory") as MockFactory:
            mock_factory = MagicMock()
            mock_factory.create_all.return_value = {
                "quick_lesson_prep": MagicMock(),
                "wisdom_transfer": MagicMock(),
                "classroom_companion": MagicMock(),
                "material": MagicMock(),
                "meeting_notes": MagicMock(),
                "router": mock_router,
            }
            MockFactory.return_value = mock_factory

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                async with app.router.lifespan_context(app):
                    response = await client.post(
                        "/api/route",
                        json={"user_input": "帮我备一节数学课"},
                    )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


# ══════════════════════════════════════════════════════════════════
# 4. 无 global 关键字
# ══════════════════════════════════════════════════════════════════

class TestNoGlobalKeyword:
    """验证模块级 global 已消除"""

    def test_routes_source_no_global_keyword(self):
        """routes.py 源码中不应包含 'global' 关键字"""
        import ast
        import maitian_agent.api.routes as routes_module

        source = inspect.getsource(routes_module)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                pytest.fail(
                    f"routes.py 仍包含 global 关键字（第 {node.lineno} 行），"
                    f"应使用 app.state.agents 替代模块级 global 变量"
                )
