from typing import Any
from astrbot.api.star import Context
from astrbot.api import logger

from ..tools.file_tool import FileTool
from ..prompts.prompt import (
    build_update_prompt,
    build_summary_prompt,
    get_length_config,
    get_features_config
)
from ..tools.path_manager import PathManager

class CommandService:

    def __init__(self, context: Context, config: Any = None) -> None:
        '''
        初始化命令服务
        :param context: AstrBot 上下文
        :param diary_path: 日记文件路径
        :param config: 配置字典
        '''
        # 初始化变量
        self.context: Context = context
        self.diary_path: str
        self.todo_path: str 
        self.config: Any = config

        # 初始化工具类
        self.file_tool: FileTool = FileTool()
        self.path_manager: PathManager = PathManager()
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
            return False, f"笔记内容超过最大长度限制 ({max_diary_length} 字符)"

        if len(content) < min_diary_length:
            return False, f"笔记内容低于最小长度要求 ({min_diary_length} 字符)"

        return True, ""

    async def handle_update_diary(self, instruction: str) -> tuple[bool, str]:
        '''
        处理更新笔记指令
        :param instruction: 更新指令
        :return: (是否成功, 消息)
        '''

        # 获取日记文件路径
        self.diary_path = self.path_manager.get_today_diary_path()
        # 确保日记文件存在
        self.file_tool.ensure_file_exists(self.diary_path)
        
        # 读取笔记文件内容
        try:
            original_content: str = self.file_tool.read_file(self.diary_path)
            logger.info("[CommandService] 读取笔记成功")
        except FileNotFoundError:
            logger.error(f"[CommandService] 笔记文件不存在: {self.diary_path}") 
            return False, f"笔记文件不存在: {self.diary_path}"
        except IOError as e:
            logger.error(f"[CommandService] 读取笔记失败: {e}")
            return False, f"读取笔记失败: {e}"

        # 构建更新提示,生成llm结果
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

        # 验证内容长度
        is_valid, error_msg = self.validate_content_length(new_content)
        if not is_valid:
            logger.warning(f"[CommandService] 内容长度验证失败: {error_msg}")
            return False, error_msg

        try:
            self.file_tool.write_file(self.diary_path, new_content)
            logger.info("[CommandService] 写入日记成功")
        except IOError as e:
            logger.error(f"[CommandService] 写入失败: {e}")
            return False, f"写入失败: {e}"

        return True, "日记已更新"

        
    async def handle_todo(self, instruction: str) -> tuple[bool, str]:
        '''
        处理待办事项
        :param instruction: 待办事项指令
        :param instruction: 待办事项指令
        :return: (是否成功, 消息)
        '''

        # 获取待办事项文件路径
        self.todo_path = self.path_manager.get_todo_path()
        # 确保待办事项文件存在
        self.file_tool.ensure_file_exists(self.todo_path)

         # 读取todo文件内容
        try:
            original_content: str = self.file_tool.read_file(self.todo_path)
            logger.info("[CommandService] 读取待办事项成功")
        except FileNotFoundError:
            logger.error(f"[CommandService]待办事项文件不存在: {self.todo_path}")
            return False, f"待办事项文件不存在: {self.todo_path}"
        except IOError as e:
            logger.error(f"[CommandService] 读取待办事项失败: {e}")
            return False, f"读取待办事项失败: {e}"

        # 构建更新提示,生成llm结果
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

        # 验证内容长度
        is_valid, error_msg = self.validate_content_length(new_content)
        if not is_valid:
            logger.warning(f"[CommandService] 内容长度验证失败: {error_msg}")
            return False, error_msg

        try:
            self.file_tool.write_file(self.todo_path, new_content)
            logger.info("[CommandService] 写入待办事项成功")
        except IOError as e:
            logger.error(f"[CommandService] 写入待办事项失败: {e}")
            return False, f"写入待办事项失败: {e}"

        return True, "待办事项已更新"
       

    async def generate_summary(self, content: str) -> str:
        '''
        生成笔记总结
        :param content: 笔记内容
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
            logger.info("[CommandService] 成功生成笔记总结")
            return summary

        except Exception as e:
            logger.error(f"[CommandService] 生成总结失败: {e}")
            return ""