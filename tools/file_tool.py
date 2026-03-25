'''
read_file(path)
write_file(path)
'''
'''
以后扩展
append_file
list_notes
search_notes
obsidian_vault_tool.py
vector_search_tool.py
'''
from pathlib import Path
from astrbot.api import logger


class FileTool:

    def read_file(self, path: str) -> str:
        """
        读取文件内容
        :param path: 文件路径
        :return: 文件内容
        :raises FileNotFoundError: 文件不存在
        :raises IOError: 读取文件失败
        """
        file_path = Path(path)

        if not file_path.exists():
            logger.error(f"[FileTool] 文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
            logger.debug(f"[FileTool] 读取文件成功: {file_path}")
            return content
        except Exception as e:
            logger.error(f"[FileTool] 读取失败: {file_path}, error={e}")
            raise

    def write_file(self, path: str, content: str) -> None:
        """
        写入文件内容
        :param path: 文件路径
        :param content: 文件内容
        :raises IOError: 写入文件失败
        """
        file_path = Path(path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            logger.debug(f"[FileTool] 写入文件成功: {file_path}")
        except Exception as e:
            logger.error(f"[FileTool] 写入失败: {file_path}, error={e}")
            raise

    def ensure_file_exists(self,path: str) -> None:
        """
        确保文件存在
        如果不存在则创建
        """
        file_path = Path(path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if not file_path.exists():
                file_path.touch()
                logger.debug(f"[FileTool] 创建文件: {file_path}")

        except Exception as e:
            logger.error(f"[FileTool] 创建文件失败: {file_path}, error={e}")
            raise