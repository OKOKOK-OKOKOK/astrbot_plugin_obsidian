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
class FileTool:

    def read_file(self, path: str) -> str:
        '''
        读取文件内容
        :param path: 文件路径
        :return: 文件内容
        '''
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # todo 意外情况处理,如果文件不存在或者路径错误,是否需要新建文件或者抛出异常?
    def write_file(self, path: str, content: str):
        '''
        写入文件内容
        :param path: 文件路径
        :param content: 文件内容
        :return: None
        '''
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)