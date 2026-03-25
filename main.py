import os

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig, logger
from typing import AsyncGenerator, Any

from .services.command_service import CommandService
from .tools.config_validator import ConfigValidator

@register(
    "astrbot_plugin_obsidian",
    "OKOKOK-OKOKOK",
    "自动修改 Obsidian",
    "0.0.1",
    "https://github.com/OKOKOK-OKOKOK/astrbot_plugin_obsidian"
)
class ObsidianPlugin(Star):

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)

        self.config = config

        is_valid, error_msg = ConfigValidator.validate_config(config)
        if not is_valid:
            logger.warning(f"[ObsidianPlugin] 配置验证失败: {error_msg}")

        self.command_service = CommandService(context, config)

    @filter.command_group("笔记", alias="obsidian")
    def obsidian(self):
        """
        Obsidian 插件命令组
        """
        pass

    @obsidian.command("日记",alias={"update_diary"})
    async def update_diary(self, event: AstrMessageEvent, instruction: str):
        """
        更新日记内容
        async def异步处理
        :param event: 事件对象
        :param instruction: 用户输入的修改内容,用于组建prompt
        :return: 生成器对象，用于异步处理,好像没啥用
        """
        logger.info(f"用户 {event.get_sender_name()} 请求修改日记内容")
            
        if not instruction:
                yield event.plain_result("请输入修改内容")
                return

        success: bool
        message: str
        success, message = await self.command_service.handle_update_diary(instruction)
        
        yield event.plain_result(message)
        
        if success:
            logger.info(f"已为用户 {event.get_sender_name()} 修改日记内容")
        else:
            logger.error(f"用户 {event.get_sender_name()} 修改日记内容失败")

    @obsidian.command("待办",alias={"todo"})
    async def todo(self, event: AstrMessageEvent, instruction: str):
        """
        更新待办事项
        async def异步处理
        :param event: 事件对象
        :param instruction: 用户输入的修改内容,用于组建prompt
        :return: 生成器对象，用于异步处理,好像没啥用
        """
        logger.info(f"用户 {event.get_sender_name()} 请求修改待办事项")

        if not instruction:
                yield event.plain_result("请输入修改内容")
                return
            
        success: bool
        message: str
        success, message = await self.command_service.handle_todo(instruction)
        
        yield event.plain_result(message)
        
        if success:
            logger.info(f"已为用户 {event.get_sender_name()} 修改待办事项")
        else:
            logger.error(f"用户 {event.get_sender_name()} 修改待办事项失败")

# todo 带缓存的io
# 本质上还是文件操作,真正的claude是如何做到根据ai的意思进行结构创建和结构管理的?
# 只是在文件操作的基础上添加了缓存