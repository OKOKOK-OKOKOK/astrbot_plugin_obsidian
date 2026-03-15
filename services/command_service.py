from astrbot.api.star import Context
from astrbot.api import logger

from ..tools.file_tool import FileTool
from ..prompts.diary_prompt import build_update_prompt

class CommandService:

    def __init__(self, context: Context, diary_path: str) -> None:
        self.context: Context = context
        self.diary_path: str = diary_path
        self.file_tool: FileTool = FileTool()

    async def handle_update_diary(self, instruction: str) -> tuple[bool, str]:
        try:
            original_content: str = self.file_tool.read_file(self.diary_path)
            logger.info("[CommandService] 读取日记成功")
        except FileNotFoundError:
            logger.error(f"[CommandService] 日记文件不存在: {self.diary_path}")
            return False, f"日记文件不存在: {self.diary_path}"
        except IOError as e:
            logger.error(f"[CommandService] 读取日记失败: {e}")
            return False, f"读取日记失败: {e}"

        prompt: str = build_update_prompt(original_content, instruction)

        try:
            provider = self.context.get_using_provider()
            resp = await provider.text_chat(prompt)
        except Exception as e:
            logger.error(f"[CommandService] LLM调用失败: {e}")
            return False, f"LLM调用失败: {e}"

        if not resp or not resp.completion_text:
            logger.error("[CommandService] LLM没有返回内容")
            return False, "LLM没有返回内容"

        new_content: str = resp.completion_text.strip()

        try:
            self.file_tool.write_file(self.diary_path, new_content)
            logger.info("[CommandService] 写入日记成功")
        except IOError as e:
            logger.error(f"[CommandService] 写入失败: {e}")
            return False, f"写入失败: {e}"

        return True, "日记已更新"
