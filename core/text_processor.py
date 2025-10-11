"""
文本处理器 - 执行自定义规则
"""
import re
from typing import Dict, Any, List


class TextProcessor:
    """文本处理引擎"""
    
    def __init__(self):
        # 注册步骤处理器
        self.handlers = {
            'find_replace': self._handle_find_replace,
            'regex_replace': self._handle_regex_replace,
            'remove_empty_lines': self._handle_remove_empty_lines,
            'case_transform': self._handle_case_transform,
            'strip_lines': self._handle_strip_lines,
            'add_prefix': self._handle_add_prefix,
            'add_suffix': self._handle_add_suffix,
        }
    
    def process(self, text: str, rule: Dict[str, Any]) -> str:
        """
        执行规则处理文本
        
        Args:
            text: 输入文本
            rule: 规则对象
            
        Returns:
            处理后的文本
        """
        if not rule or 'steps' not in rule:
            return text
        
        result = text
        
        for step in rule['steps']:
            try:
                result = self._execute_step(result, step)
            except Exception as e:
                print(f"✗ 步骤执行失败: {step.get('type', 'unknown')} - {str(e)}")
                # 继续执行下一步，不中断整个流程
                continue
        
        return result
    
    def _execute_step(self, text: str, step: Dict[str, Any]) -> str:
        """执行单个步骤"""
        step_type = step.get('type')
        params = step.get('params', {})
        
        handler = self.handlers.get(step_type)
        if not handler:
            print(f"✗ 未知的步骤类型: {step_type}")
            return text
        
        return handler(text, params)
    
    # ==================== 步骤处理器 ====================
    
    def _handle_find_replace(self, text: str, params: Dict[str, Any]) -> str:
        """查找替换"""
        find = params.get('find', '')
        replace = params.get('replace', '')
        case_sensitive = params.get('case_sensitive', True)
        
        if not find:
            return text
        
        if case_sensitive:
            return text.replace(find, replace)
        else:
            # 不区分大小写的替换
            pattern = re.compile(re.escape(find), re.IGNORECASE)
            return pattern.sub(replace, text)
    
    def _handle_regex_replace(self, text: str, params: Dict[str, Any]) -> str:
        """正则替换"""
        pattern = params.get('pattern', '')
        replacement = params.get('replacement', '')
        flags = params.get('flags', [])
        
        if not pattern:
            return text
        
        # 构建正则标志
        regex_flags = 0
        if 'IGNORECASE' in flags or 'I' in flags:
            regex_flags |= re.IGNORECASE
        if 'MULTILINE' in flags or 'M' in flags:
            regex_flags |= re.MULTILINE
        if 'DOTALL' in flags or 'S' in flags:
            regex_flags |= re.DOTALL
        
        try:
            return re.sub(pattern, replacement, text, flags=regex_flags)
        except re.error as e:
            print(f"✗ 正则表达式错误: {e}")
            return text
    
    def _handle_remove_empty_lines(self, text: str, params: Dict[str, Any]) -> str:
        """移除空行"""
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)
    
    def _handle_case_transform(self, text: str, params: Dict[str, Any]) -> str:
        """大小写转换"""
        mode = params.get('mode', 'upper')
        
        if mode == 'upper':
            return text.upper()
        elif mode == 'lower':
            return text.lower()
        elif mode == 'title':
            return text.title()
        elif mode == 'capitalize':
            return text.capitalize()
        else:
            return text
    
    def _handle_strip_lines(self, text: str, params: Dict[str, Any]) -> str:
        """去除行首尾空格"""
        mode = params.get('mode', 'both')  # left/right/both
        
        lines = text.split('\n')
        
        if mode == 'left':
            lines = [line.lstrip() for line in lines]
        elif mode == 'right':
            lines = [line.rstrip() for line in lines]
        else:  # both
            lines = [line.strip() for line in lines]
        
        return '\n'.join(lines)
    
    def _handle_add_prefix(self, text: str, params: Dict[str, Any]) -> str:
        """添加前缀"""
        prefix = params.get('prefix', '')
        per_line = params.get('per_line', True)
        
        if not prefix:
            return text
        
        if per_line:
            lines = text.split('\n')
            lines = [prefix + line for line in lines]
            return '\n'.join(lines)
        else:
            return prefix + text
    
    def _handle_add_suffix(self, text: str, params: Dict[str, Any]) -> str:
        """添加后缀"""
        suffix = params.get('suffix', '')
        per_line = params.get('per_line', True)
        
        if not suffix:
            return text
        
        if per_line:
            lines = text.split('\n')
            lines = [line + suffix for line in lines]
            return '\n'.join(lines)
        else:
            return text + suffix
    
    # ==================== 辅助方法 ====================
    
    def validate_rule(self, rule: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证规则是否有效
        
        Returns:
            (是否有效, 错误信息)
        """
        if not rule:
            return False, "规则为空"
        
        if 'name' not in rule or not rule['name']:
            return False, "规则名称不能为空"
        
        if 'steps' not in rule or not isinstance(rule['steps'], list):
            return False, "规则必须包含步骤列表"
        
        if len(rule['steps']) == 0:
            return False, "至少需要一个处理步骤"
        
        if len(rule['steps']) > 20:
            return False, "步骤数量不能超过20个"
        
        # 验证每个步骤
        for i, step in enumerate(rule['steps']):
            if 'type' not in step:
                return False, f"步骤 {i+1} 缺少类型"
            
            if step['type'] not in self.handlers:
                return False, f"步骤 {i+1} 类型无效: {step['type']}"
        
        return True, ""
    
    @staticmethod
    def get_step_types() -> List[Dict[str, str]]:
        """获取所有可用的步骤类型"""
        return [
            {'id': 'find_replace', 'name': '查找替换', 'icon': '🔍'},
            {'id': 'regex_replace', 'name': '正则替换', 'icon': '🔣'},
            {'id': 'remove_empty_lines', 'name': '移除空行', 'icon': '📝'},
            {'id': 'case_transform', 'name': '大小写转换', 'icon': 'Aa'},
            {'id': 'strip_lines', 'name': '去除空格', 'icon': '✂️'},
            {'id': 'add_prefix', 'name': '添加前缀', 'icon': '⬅️'},
            {'id': 'add_suffix', 'name': '添加后缀', 'icon': '➡️'},
        ]
