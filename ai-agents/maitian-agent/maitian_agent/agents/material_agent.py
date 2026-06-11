"""
具象化素材Agent
自动匹配科普视频/3D模型/动画素材
RAG 深度集成：检索结果融入 Prompt 模板，LLM 基于参考资料生成推荐
"""

from typing import Any, Dict, Optional, Tuple

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .base import BaseAgent


class MaterialAgent(BaseAgent):
    """具象化素材Agent

    通过 RAG 检索知识库中的已有素材，将检索结果融入 Prompt 模板，
    让 LLM 基于参考资料生成更精准的素材推荐。
    """

    def __init__(self, llm: Optional[BaseChatModel] = None, settings=None, **kwargs):
        super().__init__(
            name="MaterialAgent",
            description="具象化素材匹配，自动推荐教学视频/3D模型/动画",
            settings=settings,
            default_temperature=0.7,
            **kwargs,
        )
        if llm is None:
            self.llm = self._create_default_llm()
        else:
            self.llm = llm

        self.material_template = ChatPromptTemplate.from_template(
            """你是一位教育资源专家，请为以下教学内容推荐具象化素材：

学科：{subject}
年级：{grade}
课题：{topic}
知识点：{knowledge_points}
乡村情境：{rural_context}
{reference_section}
请推荐适合的素材类型：
1. 科普视频 - 简短有趣的知识讲解视频
2. 3D模型 - 可视化展示抽象概念
3. 动画演示 - 生动有趣的动画说明
4. 图片素材 - 贴近乡村生活的实例图片

要求：
- 素材应贴近乡村学生的生活经验
- 趣味性强，能激发学习兴趣
- 简短精炼，适合课堂使用
- 标注素材来源和获取方式
- 优先推荐与参考资料相关的素材
"""
        )
        self._chain = None

    def build_chain(self):
        """构建素材推荐链"""
        assert self.llm is not None, "llm 必须在 build_chain() 前注入"
        if self._chain is None:
            self._chain = self.material_template | self.llm | StrOutputParser()
        return self._chain

    def _build_reference_section(self, reference_context: str) -> str:
        """将 RAG 检索结果格式化为 Prompt 可用的参考段落。

        Args:
            reference_context: _retrieve_context() 返回的格式化检索文本

        Returns:
            Prompt 参考段落，无检索结果时返回空字符串
        """
        if not reference_context:
            return ""
        return f"参考资料（请优先参考以下已有素材进行推荐）：\n{reference_context}\n"

    def recommend_materials(
        self,
        subject: str,
        grade: str,
        topic: str,
        knowledge_points: str = "",
        rural_context: str = "",
        **kwargs,
    ) -> Tuple[str, bool]:
        """推荐教学素材（RAG 深度集成版）

        流程：RAG 检索 -> Prompt 组装（含 reference_section）-> LLM 调用

        Args:
            subject: 学科
            grade: 年级
            topic: 课题
            knowledge_points: 知识点
            rural_context: 乡村情境

        Returns:
            (素材推荐结果, has_rag_context) 元组
        """
        # RAG 检索：从知识库获取已有素材参考
        query = f"{subject} {grade} {topic} {knowledge_points}"
        reference_context = self._retrieve_context(query)
        has_rag = bool(reference_context)

        # 将检索结果融入 Prompt 模板
        reference_section = self._build_reference_section(reference_context)

        chain = self.build_chain()
        result = chain.invoke(
            {
                "subject": subject,
                "grade": grade,
                "topic": topic,
                "knowledge_points": knowledge_points or "本课主要内容",
                "rural_context": rural_context or "乡村实际情境",
                "reference_section": reference_section,
            }
        )

        return result, has_rag

    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """执行素材推荐（统一接口 Dict->Dict）

        流程：RAG 检索 -> Prompt 组装 -> LLM 调用 -> 保存对话
        """
        try:
            result, has_rag = self.recommend_materials(**input_data)
            output = self._format_output(
                result,
                metadata={
                    "has_rag_context": has_rag,
                },
            )
            self._save_to_memory(input_data, output)
            return output
        except Exception as e:
            return self._handle_error(e)
