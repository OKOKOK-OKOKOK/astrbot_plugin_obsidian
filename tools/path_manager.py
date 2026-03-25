import os
import datetime
from astrbot.api import logger
from astrbot.core.utils.astrbot_path import get_astrbot_plugin_data_path
from typing import Optional
from pathlib import Path
        

class PathManager:

    def __init__(self, vault_name: str = "Data") -> None:

        # 插件数据路径
        self.plugin_data_path: Path
        # 数据库名字
        self.vault_name: str = vault_name
        # 数据库路径
        self.vault_path: Path
        # 日记路径
        self.diary_path: Optional[str] = None

    def get_today_diary_path(self) -> str:
        """
        获取今日日记文件路径
        :return: 今日日记文件路径
        确保文件存在和创建
        """

        # 插件数据路径存在
        self.plugin_data_path = Path(get_astrbot_plugin_data_path())

        # 插件的数据库路径
        self.vault_path = self.plugin_data_path / self.vault_name

        today: datetime.date = datetime.date.today()
        year: int = today.year
        month: int = today.month
        day: int = today.day

        file_name: str = f"{month}.{day}.md"

        diary_path: str = os.path.join(
            self.vault_path,
            "Diary",
            str(year),
            str(month),
            file_name
        )

        self.diary_path = diary_path

        logger.info(f"[PathManager] Vault路径: {self.vault_path}")
        logger.info(f"[PathManager] 今日日期: {today}")
        logger.info(f"[PathManager] 日记路径: {diary_path}")

        return diary_path

    def get_todo_path(self) -> str:
        """
        获取待办事项文件路径
        :return: 待办事项文件路径
        """
        
        # 插件数据路径存在
        self.plugin_data_path = Path(get_astrbot_plugin_data_path())

        # 插件的数据库路径存在
        self.vault_path = self.plugin_data_path / self.vault_name

        todo_path = os.path.join(
            self.vault_path,
            "todo",
            "todo.md"
        )

        logger.info(f"[PathManager] 待办事项路径: {todo_path}")

        return todo_path
