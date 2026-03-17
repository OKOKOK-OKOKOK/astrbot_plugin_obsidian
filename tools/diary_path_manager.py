import os
import datetime
from astrbot.api import logger

class DiaryPathManager:

    def __init__(self, plugin_dir: str, vault_name: str = "Data") -> None:
        self.plugin_dir: str = plugin_dir
        self.vault_name: str = vault_name
        self.vault_path: str = os.path.join(plugin_dir, vault_name)
        self.diary_path: str | None = None

    def get_today_diary_path(self) -> str:
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

        logger.info(f"[DiaryPathManager] Vault路径: {self.vault_path}")
        logger.info(f"[DiaryPathManager] 今日日期: {today}")
        logger.info(f"[DiaryPathManager] 日记路径: {diary_path}")

        return diary_path

    def ensure_diary_file_exists(self) -> None:
        if self.diary_path is None:
            raise ValueError("日记路径未初始化，请先调用 get_today_diary_path()")

        os.makedirs(os.path.dirname(self.diary_path), exist_ok=True)

        if not os.path.exists(self.diary_path):
            today: datetime.date = datetime.date.today()
            with open(self.diary_path, "w", encoding="utf-8") as f:
                f.write(f"# {today}\n\n")

            logger.info(f"[DiaryPathManager] 创建新日记文件: {self.diary_path}")
