'''
update_diary(instruction)
读取原日记
构造prompt
调用LLM
写入日记
'''

'''
以后新加
note_service.py
todo_service.py
search_service.py
'''
from astrbot.api.star import Context
from astrbot.api import logger

from ..tools.file_tool import FileTool
from ..prompts.diary_prompt import build_update_prompt

class DiaryService:

    def __init__(self, context: Context, diary_path: str):
        '''
        初始化日记服务
        :param context: 消息上下文
        :param diary_path: 日记文件路径
        '''

        self.context = context
        self.diary_path = diary_path

        self.file_tool = FileTool()

    async def update_diary(self, instruction: str):
        '''
        更新日记
        :param instruction: 更新指令
        :return: 是否更新成功
        '''

        try:
            # 读取原本文件内容
            original_content = self.file_tool.read_file(self.diary_path)
            # todo 日志算不算该加一项这是在执行哪一个文件里的代码的信息?
            logger.info("[DiaryService] 读取日记成功")
        except Exception as e:
            logger.error(f"[DiaryService] 读取日记失败: {e}")
            return False

        # 构建更新提示
        prompt = build_update_prompt(original_content, instruction)

        try:
            # provider接收当前当前调用的模型
            provider = self.context.get_using_provider()
            # resp接收来自provider的回答
            resp = await provider.text_chat(prompt)
        # 如果直接返回错误消息,比如余额不足之类的
        except Exception as e:
            logger.error(f"[DiaryService] LLM调用失败: {e}")
            return False

        #如果没有消息
        if not resp or not resp.completion_text:
            logger.error("[DiaryService] LLM没有返回内容")
            return False

        # 提取LLM返回的内容,去掉前后空格
        new_content = resp.completion_text.strip()

        try:
            # 写入新日记
            self.file_tool.write_file(self.diary_path, new_content)
            logger.info("[DiaryService] 写入日记成功")
        except Exception as e:
            logger.error(f"[DiaryService] 写入失败: {e}")
            return False

        return True