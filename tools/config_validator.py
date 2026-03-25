from typing import Any

class ConfigValidator:

    @staticmethod
    def validate_prompts_config(prompts: dict) -> tuple[bool, str]:
        '''
        验证提示词配置
        :param prompts: 提示词配置字典
        :return: (是否有效, 错误信息)
        '''
        required_fields = [
            "system_prompt",
            "rewrite_prompt",
            "insert_prompt",
            "summary_prompt",
            "style_prompt",
            "strict_mode_prompt"
        ]

        for field in required_fields:
            if field not in prompts:
                return False, f"缺少必需的提示词字段: {field}"

            if not isinstance(prompts[field], str):
                return False, f"提示词字段 {field} 必须是字符串类型"

            if len(prompts[field].strip()) == 0:
                return False, f"提示词字段 {field} 不能为空"

        return True, ""

    @staticmethod
    def validate_length_config(length_limits: dict) -> tuple[bool, str]:
        '''
        验证长度限制配置
        :param length_limits: 长度限制配置字典
        :return: (是否有效, 错误信息)
        '''
        required_fields = [
            "max_note_length",
            "max_insert_length",
            "max_summary_length",
            "min_note_length",
            "max_context_length"
        ]

        for field in required_fields:
            if field not in length_limits:
                return False, f"缺少必需的长度限制字段: {field}"

            if not isinstance(length_limits[field], int):
                return False, f"长度限制字段 {field} 必须是整数类型"

            if length_limits[field] <= 0:
                return False, f"长度限制字段 {field} 必须大于 0"

        max_note_length = length_limits["max_note_length"]
        min_note_length = length_limits["min_note_length"]
        max_context_length = length_limits["max_context_length"]

        if min_note_length > max_note_length:
            return False, "最小笔记长度不能大于最大笔记长度"

        if max_context_length > max_note_length:
            return False, "最大上下文长度不能大于最大笔记长度"

        return True, ""

    @staticmethod
    def validate_features_config(features: dict) -> tuple[bool, str]:
        '''
        验证功能开关配置
        :param features: 功能开关配置字典
        :return: (是否有效, 错误信息)
        '''
        required_fields = [
            "allow_rewrite",
            "allow_insert",
            "allow_delete",
            "auto_summary",
            "auto_time_tag",
            "rewrite_strategy"
        ]

        for field in required_fields:
            if field not in features:
                return False, f"缺少必需的功能开关字段: {field}"

        bool_fields = [
            "allow_rewrite",
            "allow_insert",
            "allow_delete",
            "auto_summary",
            "auto_time_tag"
        ]

        for field in bool_fields:
            if not isinstance(features[field], bool):
                return False, f"功能开关字段 {field} 必须是布尔类型"

        if features["rewrite_strategy"] not in ["partial", "full"]:
            return False, "rewrite_strategy 必须是 'partial' 或 'full'"

        return True, ""

    @staticmethod
    def validate_config(config: Any) -> tuple[bool, str]:
        '''
        验证完整的配置对象
        :param config: 配置对象
        :return: (是否有效, 错误信息)
        '''
        if config is None:
            return True, ""

        try:
            if not hasattr(config, "get"):
                return False, "配置对象必须支持 get 方法"

            prompts = config.get("prompts", {})
            if prompts:
                is_valid, error_msg = ConfigValidator.validate_prompts_config(prompts)
                if not is_valid:
                    return False, f"提示词配置错误: {error_msg}"

            length_limits = config.get("length_limits", {})
            if length_limits:
                is_valid, error_msg = ConfigValidator.validate_length_config(length_limits)
                if not is_valid:
                    return False, f"长度限制配置错误: {error_msg}"

            features = config.get("features", {})
            if features:
                is_valid, error_msg = ConfigValidator.validate_features_config(features)
                if not is_valid:
                    return False, f"功能开关配置错误: {error_msg}"

            return True, ""

        except Exception as e:
            return False, f"配置验证时发生异常: {str(e)}"
