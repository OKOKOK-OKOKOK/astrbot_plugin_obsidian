from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import LLMResponse
from astrbot.api import logger

import os



'''
运行会报错
重载失败: 加载插件「astrbot_plugin_obsidian」(目录: astrbot_plugin_obsidian, 版本: v0.0.1) 
时出现问题，原因：module 'astrbot.api.event.filter' has no attribute 'on_user_message
'''
@register(
    "astrbot_plugin_obsidian",
    "OKOKOK-OKOKOK",
    "自动修改 Obsidian",
    "0.0.1",
    "https://github.com/OKOKOK-OKOKOK/astrbot_plugin_obsidian"
)
class ObsidianPlugin(Star):

    def __init__(self, context: Context):
        super().__init__(context)

        # 插件目录
        self.plugin_dir = os.path.dirname(__file__)

        # 硬编码测试文件
        self.diary_path = os.path.join(self.plugin_dir, "test_diary.md")

        logger.info(f"[ObsidianPlugin] 日记文件路径: {self.diary_path}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):

        user_text = event.message_str.strip()

        if not user_text.startswith("更新测试日记"):
            return

        if ":" not in user_text:
            yield event.plain_result("命令格式：更新测试日记: 内容")
            return

        instruction = user_text.split(":", 1)[1].strip()

        if not instruction:
            yield event.plain_result("请输入内容")
            return

        # 读取原始日记
        try:
            with open(self.diary_path, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            logger.error(f"读取日记失败: {e}")
            await event.reply("读取日记失败")
            return

        logger.info("[ObsidianPlugin] 成功读取日记")

        # 构造 prompt
        prompt = f"""
你是一个日记编辑助手。

原始日记内容：

{original_content}

用户希望修改：
{instruction}

请根据用户要求修改日记。

要求：
1 保留原有内容
2 合理添加用户内容
3 输出完整 Markdown
"""

        # 调用 LLM
        try:
            provider = self.context.get_using_provider()
            
            resp=await provider.text_chat(prompt)
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            yield event.plain_result("LLM 调用失败")
            return

        if not resp or not resp.completion_text:
            yield event.plain_result("LLM 没有返回内容")
            return

        new_content = resp.completion_text.strip()

        # 写回文件
        try:
            with open(self.diary_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            logger.error(f"写入日记失败: {e}")
            yield event.plain_result("写入日记失败")
            return

        logger.info("[ObsidianPlugin] 日记更新成功")

        yield event.plain_result("测试日记已更新")
