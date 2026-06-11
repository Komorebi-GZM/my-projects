"""
智慧传承Agent
手写教案OCR识别→结构化→入库→风格学习
性能要求: ≤5秒/张
"""

from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .base import BaseAgent


class WisdomTransferAgent(BaseAgent):
    """智慧传承Agent - 手写教案数字化传承"""

    def __init__(
        self, llm: Optional[BaseChatModel] = None, ocr_reader=None, settings=None, **kwargs
    ):
        super().__init__(
            name="WisdomTransferAgent",
            description="老教师经验一键传承，手写教案识别与结构化",
            settings=settings,
            default_temperature=0.3,
            **kwargs,
        )
        if llm is None:
            self.llm = self._create_default_llm()
        else:
            self.llm = llm

        # OCR 工具：通过 AgentFactory 或构造函数注入，不再直接创建 EasyOCR Reader
        self.ocr = ocr_reader

        self.structure_template = ChatPromptTemplate.from_template(
            """你是一位教育专家，请将以下手写教案的OCR识别结果结构化处理：

{ocr_text}

请按照以下格式进行结构化：
1. 学科：
2. 年级：
3. 课题：
4. 教学目标：
5. 教学重难点：
6. 教学过程：
7. 作业布置：
8. 教学反思：

要求：
- 提取关键信息，忽略无关内容
- 保持原文意，语言通顺
- 结构清晰，层次分明
"""
        )
        self._chain = None

    def build_chain(self):
        """构建结构化处理链"""
        assert self.llm is not None, "llm 必须在 build_chain() 前注入"
        if self._chain is None:
            self._chain = self.structure_template | self.llm | StrOutputParser()
        return self._chain

    def recognize_handwriting(self, image_path: str) -> str:
        """识别手写文字（通过注入的 OCR 工具）

        Args:
            image_path: 图片路径

        Returns:
            识别出的文本

        Raises:
            RuntimeError: 未注入 OCR 工具或识别失败
        """
        if self.ocr is None:
            raise RuntimeError(
                "OCR 工具未注入。请通过 AgentFactory(ocr=...) "
                "或 WisdomTransferAgent(ocr_reader=...) 注入 OCR 工具。"
            )

        try:
            # 优先使用 BaseOCR 接口的 recognize() 方法
            if hasattr(self.ocr, "recognize"):
                return self.ocr.recognize(image_path)
            # 兼容旧的 EasyOCR Reader 接口（readtext）
            result = self.ocr.readtext(image_path, detail=1)
            ocr_text = ""
            for detection in result:
                ocr_text += detection[1] + "\n"
            return ocr_text.strip()
        except Exception as e:
            raise RuntimeError(f"OCR识别失败: {str(e)}")

    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """执行手写教案识别与结构化（统一接口 Dict→Dict）

        Args:
            input_data: 输入字典，包含 image_path

        Returns:
            Dict 格式的执行结果
        """
        try:
            image_path = input_data.get("image_path", "")
            if not image_path:
                return {"success": False, "error": "缺少 image_path 参数", "agent": self.name}

            ocr_text = self.recognize_handwriting(image_path)
            if not ocr_text:
                return self._format_output("未能识别出文字，请确保图片清晰")

            chain = self.build_chain()
            structured_result = chain.invoke({"ocr_text": ocr_text})

            result = f"### OCR识别结果\n{ocr_text}\n\n### 结构化结果\n{structured_result}"
            output = self._format_output(result)
            self._save_to_memory(input_data, output)
            return output
        except Exception as e:
            return self._handle_error(e)

    def run_batch(self, image_paths: List[str], **kwargs) -> List[Dict[str, Any]]:
        """批量处理多张手写教案

        Args:
            image_paths: 图片路径列表

        Returns:
            处理结果列表
        """
        results = []
        for image_path in image_paths:
            result = self.run({"image_path": image_path})
            results.append(
                {
                    "image_path": image_path,
                    "result": result,
                    "success": result.get("success", False),
                }
            )
        return results
