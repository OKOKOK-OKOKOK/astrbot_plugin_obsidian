from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

import os

from .services.diary_service import DiaryService


@register(
    "astrbot_plugin_obsidian",
    "OKOKOK-OKOKOK",
    "自动修改 Obsidian",
    "0.0.1",
    "https://github.com/OKOKOK-OKOKOK/astrbot_plugin_obsidian"
)
class ObsidianPlugin(Star):

    def __init__(self, context: Context):
        # 固定步骤初始化
        super().__init__(context)

        # 插件目录
        plugin_dir = os.path.dirname(__file__)
        # 测试用硬编码日记路径
        diary_path = os.path.join(plugin_dir, "test_diary.md")

        logger.info(f"[main] 日记路径: {diary_path}")

        # 初始化 Service,两个参数：消息和日记路径
        self.diary_service = DiaryService(context, diary_path)

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        '''
        注册监听消息事件
        处理所有消息事件
        :param event: 消息事件
        :return: 处理结果
        '''


        # 去除开头结尾空格
        text = event.message_str.strip()

        # 固定开头命令,后面肯定需要修改
        if not text.startswith("更新测试日记"):
            return

        # 检查是否有冒号,是否是命令格式
        # todo 中英文冒号都支持
        if ":" not in text:
            yield event.plain_result("命令格式：更新测试日记: 内容")
            return

        # 提取指令内容,从冒号剪切,保存后半段的命令
        instruction = text.split(":", 1)[1].strip()

        if not instruction:
            yield event.plain_result("请输入日记内容")
            return

        logger.info("[main]收到更新日记请求")

        # 调用日记服务更新日记
        result = await self.diary_service.update_diary(instruction)
    
        if result:
            yield event.plain_result("测试日记已更新")
        else:
            yield event.plain_result("更新日记失败")