"""
极速备课Agent
语音驱动全流程备课，生成乡土化教案
性能要求: ≤10秒
"""

from typing import Any, Dict, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .base import BaseAgent


class QuickLessonPrepAgent(BaseAgent):
    """极速备课Agent - 生成乡土化教案"""

    def __init__(self, llm: Optional[BaseChatModel] = None, settings=None, **kwargs):
        super().__init__(
            name="QuickLessonPrepAgent",
            description="乡村专属极速备课，10秒生成乡土化教案",
            settings=settings,
            default_temperature=0.7,
            **kwargs,
        )
        if llm is None:
            self.llm = self._create_default_llm()
        else:
            self.llm = llm

        self.lesson_plan_template = ChatPromptTemplate.from_template(
            """你是一位经验丰富的乡村教师，擅长结合乡村实际情境设计教案。请根据以下信息生成一份详细的教案：

学科：{subject}
年级：{grade}
课题：{topic}
乡村特色情境：{rural_context}
{teacher_section}
{reference_section}
教案应包含以下部分：
1. 教学目标
2. 教学重难点
3. 教学准备
4. 教学过程（导入、新授、练习、总结）
5. 作业布置
6. 板书设计

要求：
- 结合乡村实际情境，使用贴近农村生活的例子
- 语言通俗易懂，符合该年级学生的认知水平
- 教案结构清晰，可直接用于课堂教学
- 融入乡土元素，增强学生的学习兴趣
- {personalization_hint}
"""
        )
        self._chain = None

    def build_chain(self):
        """构建备课链"""
        assert self.llm is not None, "llm 必须在 build_chain() 前注入"
        if self._chain is None:
            self._chain = self.lesson_plan_template | self.llm | StrOutputParser()
        return self._chain

    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """执行备课流程（统一接口 Dict→Dict）

        流程：教师画像加载 → RAG 检索 → Prompt 组装 → LLM 调用 → 保存对话
        """
        try:
            subject = input_data.get("subject", "")
            grade = input_data.get("grade", "")
            topic = input_data.get("topic", "")
            rural_context = input_data.get("rural_context", "")
            teacher_id = input_data.get("teacher_id", "")

            # 加载教师画像
            profile = self._load_teacher_profile(teacher_id)
            has_profile = profile is not None
            teacher_section = self._format_teacher_profile_section(profile)
            personalization_hint = (
                "请根据该教师的教学风格和经验，个性化设计教案。" if has_profile else ""
            )

            # RAG 检索
            query = f"{subject} {grade} {topic}"
            reference_context = self._retrieve_context(query)
            has_rag = bool(reference_context)

            reference_section = (
                f"参考资料（请参考以下内容设计教案）：\n{reference_context}\n" if has_rag else ""
            )

            chain = self.build_chain()
            result = chain.invoke(
                {
                    "subject": subject,
                    "grade": grade,
                    "topic": topic,
                    "rural_context": rural_context or "结合乡村实际教学",
                    "teacher_section": teacher_section,
                    "reference_section": reference_section,
                    "personalization_hint": personalization_hint,
                }
            )

            output = self._format_output(
                result,
                metadata={
                    "has_rag_context": has_rag,
                    "has_teacher_profile": has_profile,
                },
            )

            # 自动保存对话上下文
            self._save_to_memory(input_data, output)

            return output
        except Exception as e:
            return self._handle_error(e)
