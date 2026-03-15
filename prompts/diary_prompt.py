'''
构造 LLM prompt
'''

'''
以后可以增加
build_summary_prompt
build_todo_prompt
build_search_prompt
'''
def build_update_prompt(original: str, instruction: str) -> str:
    '''
    构建更新日记提示
    :param original: 原始日记内容
    :param instruction: 更新指令
    :return: 完整更新提示
    '''
    return f"""
你是一个 Obsidian 日记编辑助手。

原始日记内容：

{original}

用户希望修改：
{instruction}

请根据用户要求修改日记。

要求：
1 保留原有内容
2 合理加入新内容
3 输出完整 Markdown
"""