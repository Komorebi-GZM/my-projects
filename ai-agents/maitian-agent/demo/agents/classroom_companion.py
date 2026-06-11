"""
[LEGACY] 课堂实时伴教 Agent — 早期演示版本

⚠️  此文件为项目初期的最小可运行演示代码，仅供概念验证。
    生产环境请使用 maitian_agent.agents.classroom_companion.ClassroomCompanionAgent。

与主项目的主要差异：
    - 不继承 BaseAgent，无 build_chain() 抽象方法
    - 直接导入 ChatOpenAI（主项目使用 BaseChatModel 抽象）
    - 无 RAG 知识库检索（主项目通过 KnowledgeBase 集成）
    - 无依赖注入、无对话记忆
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


class ClassroomCompanionAgent:
    """课堂实时伴教 Agent - Demo 版本"""

    def __init__(self, llm=None):
        if llm is None:
            self.llm = ChatOpenAI(
                model=os.getenv("MODEL_NAME", "deepseek-v2"),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_API_BASE"),
                temperature=0.7,
            )
        else:
            self.llm = llm

    def generate_quiz(self, subject, grade, topic, knowledge_points,
                      question_count=5, question_types=None):
        """生成练习题"""
        if question_types is None:
            question_types = ["选择题", "填空题"]
        types_str = "、".join(question_types)
        prompt = ChatPromptTemplate.from_template("""
        你是一位经验丰富的{grade}{subject}教师。请根据以下信息生成练习题：

        课题：{topic}
        知识点：{knowledge_points}
        题目数量：{question_count} 道
        题目类型：{types_str}

        要求：
        1. 题目难度适合{grade}学生
        2. 结合乡村生活情境出题（如农田、集市、家庭等场景）
        3. 每道题附标准答案和解析
        4. 格式清晰，编号规范
        """)
        messages = prompt.format_messages(
            subject=subject, grade=grade, topic=topic,
            knowledge_points=knowledge_points or "本课主要内容",
            question_count=question_count, types_str=types_str,
        )
        result = self.llm.invoke(messages)
        return result.content

    def retrieve_classic_questions(self, subject, grade, topic):
        """检索经典题目（Demo 版本使用 LLM 推荐，完整版将接入 RAG 知识库）"""
        prompt = ChatPromptTemplate.from_template("""
        你是一位资深{grade}{subject}教师，拥有丰富的教学经验。

        课题：{topic}

        请推荐 3-5 道经典练习题，要求：
        1. 这些题目是该课题的"必做题"，能帮助学生掌握核心概念
        2. 难度由易到难排列
        3. 结合乡村生活情境
        4. 每道题附答案和教学建议

        注：当前为 Demo 版本，题目由大模型推荐。完整版将接入 RAG 知识库检索真实经典题库。
        """)
        messages = prompt.format_messages(
            subject=subject, grade=grade, topic=topic
        )
        result = self.llm.invoke(messages)
        return result.content
