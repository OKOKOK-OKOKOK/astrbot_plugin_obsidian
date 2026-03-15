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
import os


class FileTool:

    def read_file(self, path: str) -> str:
        '''
        读取文件内容
        :param path: 文件路径
        :return: 文件内容
        :raises FileNotFoundError: 文件不存在
        :raises IOError: 读取文件失败
        '''
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, path: str, content: str) -> None:
        '''
        写入文件内容
        :param path: 文件路径
        :param content: 文件内容
        :raises IOError: 写入文件失败
        '''
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)