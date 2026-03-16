from typing import Any
from astrbot.api.star import Context
from astrbot.api import logger

from ..tools.file_tool import FileTool
from ..prompts.diary_prompt import (
    build_update_prompt,
    build_summary_prompt,
    add_time_tag_to_content,
    get_length_config,
    get_features_config
)

class CommandService:

    def __init__(self, context: Context, diary_path: str, config: Any = None) -> None:
        self.context: Context = context
        self.diary_path: str = diary_path
        self.file_tool: FileTool = FileTool()
        self.config: Any = config

        self.length_config: dict = get_length_config(config)
        self.features_config: dict = get_features_config(config)

    def validate_content_length(self, content: str) -> tuple[bool, str]:
        '''
        验证内容长度是否符合配置要求
        :param content: 要验证的内容
        :return: (是否通过, 错误信息)
        '''
        max_diary_length = self.length_config["max_diary_length"]
        min_diary_length = self.length_config["min_diary_length"]

        if len(content) > max_diary_length:
            return False, f"日记内容超过最大长度限制 ({max_diary_length} 字符)"

        if len(content) < min_diary_length:
            return False, f"日记内容低于最小长度要求 ({min_diary_length} 字符)"

        return True, ""

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

        prompt: str = build_update_prompt(original_content, instruction, self.config)

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

        is_valid, error_msg = self.validate_content_length(new_content)
        if not is_valid:
            logger.warning(f"[CommandService] 内容长度验证失败: {error_msg}")
            return False, error_msg

        new_content = add_time_tag_to_content(new_content, self.config)

        if self.features_config["auto_summary"]:
            summary = await self.generate_summary(new_content)
            if summary:
                new_content = f"{new_content}\n\n---\n\n**今日总结：**\n{summary}"
                logger.info("[CommandService] 自动总结已添加")

        try:
            self.file_tool.write_file(self.diary_path, new_content)
            logger.info("[CommandService] 写入日记成功")
        except IOError as e:
            logger.error(f"[CommandService] 写入失败: {e}")
            return False, f"写入失败: {e}"

        return True, "日记已更新"

    async def generate_summary(self, content: str) -> str:
        '''
        生成日记总结
        :param content: 日记内容
        :return: 总结内容
        '''
        try:
            prompt: str = build_summary_prompt(content, self.config)

            provider = self.context.get_using_provider()
            resp = await provider.text_chat(prompt)

            if not resp or not resp.completion_text:
                logger.warning("[CommandService] 生成总结失败：LLM没有返回内容")
                return ""

            summary = resp.completion_text.strip()
            logger.info("[CommandService] 成功生成日记总结")
            return summary

        except Exception as e:
            logger.error(f"[CommandService] 生成总结失败: {e}")
            return ""
