from typing import Any
from astrbot.api import logger
import datetime

def get_prompt_config(config: Any) -> dict:
    '''
    从配置中获取提示词配置，提供默认值
    :param config: AstrBotConfig 对象
    :return: 提示词配置字典
    '''
    if config is None:
        logger.info("[diary_prompt] 配置为空，使用默认提示词配置")
        return get_default_prompt_config()

    try:
        prompts = config.get("prompts", {})
        result = {
            "system_prompt": prompts.get("system_prompt", "你是一名日记编辑助手，根据用户指令修改日记内容。"),
            "rewrite_prompt": prompts.get("rewrite_prompt", "根据用户的修改指令，对日记进行合理修改。"),
            "insert_prompt": prompts.get("insert_prompt", "根据用户的指令，在日记合适位置插入内容。"),
            "summary_prompt": prompts.get("summary_prompt", "总结今天的日记内容。"),
            "style_prompt": prompts.get("style_prompt", "保持日记口语化、自然的表达风格。"),
            "strict_mode_prompt": prompts.get("strict_mode_prompt", "只根据用户提供的信息修改日记，不要添加任何未提及的事实，不要猜测人物背景，不要扩展故事。")
        }
        logger.info("[diary_prompt] 成功获取提示词配置")
        return result
    except Exception as e:
        logger.error(f"[diary_prompt] 获取提示词配置失败: {e}，使用默认配置")
        return get_default_prompt_config()

def get_default_prompt_config() -> dict:
    '''
    获取默认的提示词配置
    :return: 默认提示词配置字典
    '''
    return {
        "system_prompt": "你是一名日记编辑助手，根据用户指令修改日记内容。",
        "rewrite_prompt": "根据用户的修改指令，对日记进行合理修改。",
        "insert_prompt": "根据用户的指令，在日记合适位置插入内容。",
        "summary_prompt": "总结今天的日记内容。",
        "style_prompt": "保持日记口语化、自然的表达风格。",
        "strict_mode_prompt": "只根据用户提供的信息修改日记，不要添加任何未提及的事实，不要猜测人物背景，不要扩展故事。"
    }

def get_length_config(config: Any) -> dict:
    '''
    从配置中获取长度限制配置，提供默认值
    :param config: AstrBotConfig 对象
    :return: 长度限制配置字典
    '''
    if config is None:
        logger.info("[diary_prompt] 配置为空，使用默认长度限制配置")
        return get_default_length_config()

    try:
        length_limits = config.get("length_limits", {})
        result = {
            "max_diary_length": length_limits.get("max_diary_length", 2000),
            "max_insert_length": length_limits.get("max_insert_length", 200),
            "max_summary_length": length_limits.get("max_summary_length", 100),
            "min_diary_length": length_limits.get("min_diary_length", 50),
            "max_context_length": length_limits.get("max_context_length", 1500)
        }
        logger.info(f"[diary_prompt] 成功获取长度限制配置: {result}")
        return result
    except Exception as e:
        logger.error(f"[diary_prompt] 获取长度限制配置失败: {e}，使用默认配置")
        return get_default_length_config()

def get_default_length_config() -> dict:
    '''
    获取默认的长度限制配置
    :return: 默认长度限制配置字典
    '''
    return {
        "max_diary_length": 2000,
        "max_insert_length": 200,
        "max_summary_length": 100,
        "min_diary_length": 50,
        "max_context_length": 1500
    }

def get_features_config(config: Any) -> dict:
    '''
    从配置中获取功能开关配置，提供默认值
    :param config: AstrBotConfig 对象
    :return: 功能开关配置字典
    '''
    if config is None:
        logger.info("[diary_prompt] 配置为空，使用默认功能开关配置")
        return get_default_features_config()

    try:
        features = config.get("features", {})
        result = {
            "allow_rewrite": features.get("allow_rewrite", True),
            "allow_insert": features.get("allow_insert", True),
            "allow_delete": features.get("allow_delete", False),
            "auto_summary": features.get("auto_summary", False),
            "auto_time_tag": features.get("auto_time_tag", True),
            "rewrite_strategy": features.get("rewrite_strategy", "partial")
        }
        logger.info(f"[diary_prompt] 成功获取功能开关配置: {result}")
        return result
    except Exception as e:
        logger.error(f"[diary_prompt] 获取功能开关配置失败: {e}，使用默认配置")
        return get_default_features_config()

def get_default_features_config() -> dict:
    '''
    获取默认的功能开关配置
    :return: 默认功能开关配置字典
    '''
    return {
        "allow_rewrite": True,
        "allow_insert": True,
        "allow_delete": False,
        "auto_summary": False,
        "auto_time_tag": True,
        "rewrite_strategy": "partial"
    }

def build_update_prompt(original: str, instruction: str, config: Any = None) -> str:
    '''
    构建更新日记提示
    :param original: 原始日记内容
    :param instruction: 更新指令
    :param config: AstrBotConfig 对象
    :return: 完整更新提示
    '''
    prompt_config = get_prompt_config(config)
    features_config = get_features_config(config)
    length_config = get_length_config(config)

    system_prompt = prompt_config["system_prompt"]
    rewrite_prompt = prompt_config["rewrite_prompt"]
    insert_prompt = prompt_config["insert_prompt"]
    style_prompt = prompt_config["style_prompt"]
    strict_mode_prompt = prompt_config["strict_mode_prompt"]

    max_context_length = length_config["max_context_length"]

    if len(original) > max_context_length:
        original = original[:max_context_length] + "\n... (内容过长，已截断)"

    requirements = []

    if features_config["allow_rewrite"]:
        requirements.append(f"1 {rewrite_prompt}")

    if features_config["allow_insert"]:
        requirements.append(f"2 {insert_prompt}")

    if features_config["allow_delete"]:
        requirements.append("3 可以根据用户指令删除不合适的内容")

    requirements.append(f"4 {style_prompt}")
    requirements.append(f"5 {strict_mode_prompt}")
    requirements.append("6 输出完整 Markdown")

    requirements_text = "\n".join(requirements)

    return f"""
{system_prompt}

原始日记内容：

{original}

用户希望修改：
{instruction}

请根据用户要求修改日记。

要求：
{requirements_text}
"""

def build_summary_prompt(diary_content: str, config: Any = None) -> str:
    '''
    构建生成日记总结的提示
    :param diary_content: 日记内容
    :param config: AstrBotConfig 对象
    :return: 完整总结提示
    '''
    prompt_config = get_prompt_config(config)
    length_config = get_length_config(config)

    summary_prompt = prompt_config["summary_prompt"]
    max_summary_length = length_config["max_summary_length"]

    return f"""
你是一个日记总结助手。

日记内容：

{diary_content}

请总结今天的日记内容。

要求：
1 {summary_prompt}
2 总结长度不超过 {max_summary_length} 字
3 保持简洁明了
4 输出纯文本，不需要 Markdown 格式
"""

def get_time_tag() -> str:
    '''
    根据当前时间生成时间标签
    :return: 时间标签字符串
    '''
    now = datetime.datetime.now()
    hour = now.hour

    if 5 <= hour < 9:
        return "早上"
    elif 9 <= hour < 12:
        return "上午"
    elif 12 <= hour < 14:
        return "中午"
    elif 14 <= hour < 18:
        return "下午"
    elif 18 <= hour < 22:
        return "晚上"
    else:
        return "深夜"

def add_time_tag_to_content(content: str, config: Any = None) -> str:
    '''
    为日记内容添加时间标签
    :param content: 原始内容
    :param config: AstrBotConfig 对象
    :return: 添加时间标签后的内容
    '''
    features_config = get_features_config(config)

    if not features_config["auto_time_tag"]:
        return content

    time_tag = get_time_tag()
    time_str = datetime.datetime.now().strftime("%H:%M")

    return f"\n\n### {time_tag} {time_str}\n\n{content}"
