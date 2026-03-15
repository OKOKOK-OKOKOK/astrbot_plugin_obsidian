import datetime
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

import os
import difflib
from .services.diary_service import DiaryService

# 生成diff
def generate_diff(old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="old",
        tofile="new",
        lineterm=""
    )

    return "\n".join(diff)

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

        '''
        现在来处理日记路径
        先硬编码数据库的根目录,这个之后可以从配置文件读取,
        硬编码在test_vault目录下,
        然后年份,月份,日期等等也许可以交给llm,然后拼接出日记文件路径?
        我自己的日记目录有点奇怪,先满足的需求,之后再考虑满足别人的兼容,
        Diary / 年份 / 月份 / 月份.日期.md
        2026-03-15 → 2026 → 3 → 3.15.md
        '''
        # 数据库根目录
        vault_path = os.path.join(plugin_dir, "test_vault")

        # 日期
        today = datetime.date.today()
        year_full = today.year
        month = today.month
        day = today.day

        # 3.15.md
        file_name = f"{month}.{day}.md"

        # 日记文件路径
        diary_path = os.path.join(
            vault_path,
            "Diary",
            str(year_full),
            str(month),
            file_name
        )

        # 存下来,后续确认修改时会用到
        self.diary_path = diary_path

        logger.info(f"[main] Vault路径: {vault_path}")
        logger.info(f"[main] 今日日期: {today}")
        logger.info(f"[main] 日记路径: {diary_path}")

        # 上面只是拼出来了文件路径,但是不确定实际上究竟存不存在
        os.makedirs(os.path.dirname(diary_path), exist_ok=True)

        if not os.path.exists(diary_path):
            # 如果文件不存在,则创建一个空文件
            with open(diary_path, "w", encoding="utf-8") as f:
                f.write(f"# {today}\n\n")

        # 初始化 Service,两个参数：消息和日记路径
        self.diary_service = DiaryService(context, diary_path)

        # 等待确认的修改
        # todo
        self.pending_changes = {}

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        '''
        注册监听消息事件
        处理所有消息事件
        :param event: 消息事件
        :return: 处理结果
        '''

        # todo 这两个函数不一定存在
        user_text = (event.message_str or "").strip()
        user_id= event.get_sender_id()

        # 确认阶段
        if user_text == "/confirm":

            if user_id not in self.pending_changes:
                yield event.plain_result("没有待确认的修改")
                return

            change = self.pending_changes.pop(user_id)

            try:
                with open(change["file"], "w", encoding="utf-8") as f:
                    f.write(change["content"])
            except Exception as e:
                yield event.plain_result(f"写入失败: {e}")
                return

            yield event.plain_result("日记已更新")
            return

        if user_text == "/cancel":

            if user_id in self.pending_changes:
                self.pending_changes.pop(user_id)

            yield event.plain_result("修改已取消")
            return
        
        # 提出命令阶段
        if not user_text.startswith("更新测试日记"):
            return

        if ":" not in user_text:
            yield event.plain_result("命令格式：更新测试日记: 内容")
            return

        instruction = user_text.split(":", 1)[1].strip()

        if not instruction:
            yield event.plain_result("请输入修改内容")
            return

        try:
            with open(self.diary_path, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            yield event.plain_result(f"读取日记失败: {e}")
            return

        prompt = f"""
你是一个日记编辑助手。

原始日记：

{original_content}

用户要求：

{instruction}

请修改日记。

要求：

1 保留原内容
2 合理添加用户内容
3 输出完整 Markdown
"""

        try:
            provider = self.context.get_using_provider()
            resp = await provider.text_chat(prompt)
        except Exception as e:
            yield event.plain_result(f"LLM调用失败: {e}")
            return

        if not resp or not resp.completion_text:
            yield event.plain_result("LLM没有返回内容")
            return

        new_content = resp.completion_text.strip()

        diff_text = generate_diff(original_content, new_content)

        if not diff_text:
            yield event.plain_result("没有检测到修改")
            return

        self.pending_changes[user_id] = {
            "file": self.diary_path,
            "content": new_content
        }

        preview_message = f"""
AI准备修改日记：
diff
{diff_text}
确认修改：
/confirm
取消修改：
/cancel
"""
        yield event.plain_result(preview_message)


        