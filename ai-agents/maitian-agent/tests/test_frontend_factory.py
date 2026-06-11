"""Frontend Factory 接入测试 — 验证 streamlit_app 通过 AgentFactory 统一创建 Agent

测试策略：
- 验证 init_agents() 使用 AgentFactory 而非直接实例化
- 验证所有 6 个 Agent 均通过工厂创建并注入依赖
- 验证 RAG/记忆/工具依赖注入生效
- 验证 Agent.run(Dict) → Dict 接口契约不变
"""
from unittest.mock import MagicMock, patch
import pytest


class _SessionStateDict(dict):
    """模拟 Streamlit session_state：同时支持 dict 和属性访问。"""

    def __getattr__(self, key: str):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: str, value):
        self[key] = value

    def __contains__(self, key):
        return dict.__contains__(self, key)


class TestFrontendFactoryIntegration:
    """验证 streamlit_app 的 init_agents() 通过 AgentFactory 创建所有 Agent"""

    def test_init_agents_uses_factory_not_direct_instantiation(self):
        """init_agents 应调用 AgentFactory.create_all()，而非直接 import Agent 类"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="测试结果")

        with patch(
            "maitian_agent.frontend.streamlit_app.AgentFactory"
        ) as MockFactory:
            mock_factory_instance = MockFactory.return_value
            mock_factory_instance.create_all.return_value = {
                "quick_lesson_prep": MagicMock(),
                "wisdom_transfer": MagicMock(),
                "classroom_companion": MagicMock(),
                "material": MagicMock(),
                "meeting_notes": MagicMock(),
                "router": MagicMock(),
            }

            from maitian_agent.frontend.streamlit_app import init_agents

            # 模拟 Streamlit session_state（支持属性访问）
            with patch(
                "maitian_agent.frontend.streamlit_app.st"
            ) as mock_st:
                mock_st.session_state = _SessionStateDict()

                init_agents()

            # 验证 AgentFactory 被调用
            MockFactory.assert_called_once()
            mock_factory_instance.create_all.assert_called_once()

    def test_init_agents_populates_session_state_with_all_agents(self):
        """init_agents 应在 session_state 中填充所有 6 个 Agent"""
        mock_agents = {
            "quick_lesson_prep": MagicMock(name="QuickLessonPrepAgent"),
            "wisdom_transfer": MagicMock(name="WisdomTransferAgent"),
            "classroom_companion": MagicMock(name="ClassroomCompanionAgent"),
            "material": MagicMock(name="MaterialAgent"),
            "meeting_notes": MagicMock(name="MeetingNotesAgent"),
            "router": MagicMock(name="RouterAgent"),
        }

        with patch(
            "maitian_agent.frontend.streamlit_app.AgentFactory"
        ) as MockFactory:
            MockFactory.return_value.create_all.return_value = mock_agents

            from maitian_agent.frontend.streamlit_app import init_agents

            with patch(
                "maitian_agent.frontend.streamlit_app.st"
            ) as mock_st:
                mock_st.session_state = _SessionStateDict()
                init_agents()

            # 验证 session_state 包含所有 Agent
            expected_keys = {
                "quick_lesson_prep_agent",
                "wisdom_transfer_agent",
                "classroom_companion_agent",
                "material_agent",
                "meeting_notes_agent",
                "router_agent",
                "agents",  # 工厂创建的完整 agents 字典也应缓存
            }
            assert expected_keys.issubset(set(mock_st.session_state.keys()))

    def test_init_agents_caches_factory_result(self):
        """重复调用 init_agents 不应重复创建 Agent（session_state 缓存）"""
        mock_agents = {
            "quick_lesson_prep": MagicMock(),
            "wisdom_transfer": MagicMock(),
            "classroom_companion": MagicMock(),
            "material": MagicMock(),
            "meeting_notes": MagicMock(),
            "router": MagicMock(),
        }

        with patch(
            "maitian_agent.frontend.streamlit_app.AgentFactory"
        ) as MockFactory:
            MockFactory.return_value.create_all.return_value = mock_agents

            from maitian_agent.frontend.streamlit_app import init_agents

            with patch(
                "maitian_agent.frontend.streamlit_app.st"
            ) as mock_st:
                mock_st.session_state = _SessionStateDict()
                init_agents()
                init_agents()  # 第二次调用

            # create_all 只应被调用一次
            mock_factory_instance = MockFactory.return_value
            assert mock_factory_instance.create_all.call_count == 1

    def test_factory_injected_agents_have_run_method(self):
        """通过工厂创建的 Agent 必须具备 run(Dict) → Dict 接口"""
        from maitian_agent.agents.factory import AgentFactory

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "测试输出"

        factory = AgentFactory(llm=mock_llm)
        agents = factory.create_all()

        for agent_type, agent in agents.items():
            assert hasattr(agent, "run"), (
                f"Agent '{agent_type}' 缺少 run 方法"
            )
            assert callable(agent.run), (
                f"Agent '{agent_type}'.run 不可调用"
            )

    def test_factory_injected_knowledge_base_reaches_agent(self):
        """通过工厂注入的 KnowledgeBase 应到达每个 Agent 实例"""
        from maitian_agent.agents.factory import AgentFactory

        mock_kb = MagicMock(name="KnowledgeBase")
        mock_llm = MagicMock()

        factory = AgentFactory(llm=mock_llm, knowledge_base=mock_kb)
        agents = factory.create_all()

        for agent_type, agent in agents.items():
            assert agent.knowledge_base is mock_kb, (
                f"Agent '{agent_type}' 未接收到 knowledge_base 注入"
            )

    def test_factory_injected_conversation_memory_reaches_agent(self):
        """通过工厂注入的 ConversationMemory 应到达每个 Agent 实例"""
        from maitian_agent.agents.factory import AgentFactory

        mock_memory = MagicMock(name="ConversationMemory")
        mock_llm = MagicMock()

        factory = AgentFactory(llm=mock_llm, conversation_memory=mock_memory)
        agents = factory.create_all()

        for agent_type, agent in agents.items():
            assert agent.conversation_memory is mock_memory, (
                f"Agent '{agent_type}' 未接收到 conversation_memory 注入"
            )

    def test_factory_injected_teacher_profile_reaches_agent(self):
        """通过工厂注入的 TeacherProfileManager 应到达每个 Agent 实例"""
        from maitian_agent.agents.factory import AgentFactory

        mock_profile = MagicMock(name="TeacherProfileManager")
        mock_llm = MagicMock()

        factory = AgentFactory(llm=mock_llm, teacher_profile=mock_profile)
        agents = factory.create_all()

        for agent_type, agent in agents.items():
            assert agent.teacher_profile is mock_profile, (
                f"Agent '{agent_type}' 未接收到 teacher_profile 注入"
            )

    def test_factory_injected_ocr_reaches_wisdom_transfer(self):
        """OCR 依赖应仅注入 WisdomTransferAgent"""
        from maitian_agent.agents.factory import AgentFactory

        mock_ocr = MagicMock(name="BaseOCR")
        mock_llm = MagicMock()

        factory = AgentFactory(llm=mock_llm, ocr=mock_ocr)
        agents = factory.create_all()

        assert agents["wisdom_transfer"].ocr is mock_ocr

    def test_factory_injected_asr_reaches_meeting_notes(self):
        """ASR 依赖应仅注入 MeetingNotesAgent"""
        from maitian_agent.agents.factory import AgentFactory

        mock_asr = MagicMock(name="BaseASR")
        mock_llm = MagicMock()

        factory = AgentFactory(llm=mock_llm, asr=mock_asr)
        agents = factory.create_all()

        assert agents["meeting_notes"].asr is mock_asr

    def test_no_direct_agent_imports_in_streamlit_app(self):
        """streamlit_app.py 不应直接 import 任何具体 Agent 类"""
        import ast
        import inspect

        from maitian_agent.frontend import streamlit_app

        source = inspect.getsource(streamlit_app)
        tree = ast.parse(source)

        # 收集所有 import 语句
        direct_agent_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # 允许 factory 导入，禁止具体 Agent 类导入
                if module.startswith("agents."):
                    for alias in node.names:
                        name = alias.name
                        if name not in ("factory", "AgentFactory") and not module.endswith(
                            "factory"
                        ):
                            direct_agent_imports.append(f"from {module} import {name}")

        assert len(direct_agent_imports) == 0, (
            f"streamlit_app.py 存在直接 Agent 导入（应通过 AgentFactory）："
            f"\n{chr(10).join(direct_agent_imports)}"
        )

    def test_agent_run_returns_dict_with_success_key(self):
        """所有 Agent 的 run(Dict) → Dict 返回值必须包含 'success' 键"""
        from maitian_agent.agents.factory import AgentFactory

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "测试结果"

        factory = AgentFactory(llm=mock_llm)
        agents = factory.create_all()

        # 测试每个 Agent 的 run 接口
        test_inputs = {
            "quick_lesson_prep": {
                "subject": "数学", "grade": "三年级", "topic": "分数"
            },
            "wisdom_transfer": {"image_path": "/tmp/test.png"},
            "classroom_companion": {
                "action": "quiz", "subject": "数学",
                "grade": "三年级", "topic": "分数",
            },
            "material": {
                "subject": "科学", "grade": "四年级", "topic": "水的循环"
            },
            "meeting_notes": {"transcript": "会议记录内容"},
            "router": {"user_input": "帮我备课"},
        }

        for agent_type, agent in agents.items():
            if agent_type == "wisdom_transfer":
                # WisdomTransfer 需要 OCR，注入 mock
                agent.ocr = MagicMock()
                agent.ocr.recognize.return_value = "OCR测试文本"
            result = agent.run(test_inputs[agent_type])
            assert isinstance(result, dict), (
                f"Agent '{agent_type}'.run() 应返回 dict，实际返回 {type(result)}"
            )
            assert "success" in result, (
                f"Agent '{agent_type}'.run() 返回值缺少 'success' 键"
            )
