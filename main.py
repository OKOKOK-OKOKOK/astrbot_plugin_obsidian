import os

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import AstrBotConfig
from typing import AsyncGenerator, Any

from .tools.diary_path_manager import DiaryPathManager
from .services.command_service import CommandService

@register(
    "astrbot_plugin_obsidian",
    "OKOKOK-OKOKOK",
    "自动修改 Obsidian",
    "0.0.1",
    "https://github.com/OKOKOK-OKOKOK/astrbot_plugin_obsidian"
)
class ObsidianPlugin(Star):

    def __init__(self, context: Context,config:AstrBotConfig) :
        super().__init__(context)

        plugin_dir: str = os.path.dirname(__file__)

        self.path_manager: DiaryPathManager = DiaryPathManager(plugin_dir)

        diary_path: str = self.path_manager.get_today_diary_path()

        self.path_manager.ensure_diary_file_exists()

        self.command_service: CommandService = CommandService(context, diary_path)

        self.config = config

@filter.event_message_type(filter.EventMessageType.ALL)
async def on_message(self, event: AstrMessageEvent) -> AsyncGenerator[Any, None]:
    user_text: str = (event.message_str or "").strip()

    if not user_text.startswith("更新测试日记"):
        return

    if ":" not in user_text:
        yield event.plain_result("命令格式：更新测试日记: 内容")
        return

    instruction: str = user_text.split(":", 1)[1].strip()

    if not instruction:
        yield event.plain_result("请输入修改内容")
        return

    success: bool
    message: str
    success, message = await self.command_service.handle_update_diary(instruction)
    yield event.plain_result(message)