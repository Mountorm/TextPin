"""
配置管理模块
负责读取、保存和管理应用配置
"""
import json
import os
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "window": {
                "width": 600,
                "height": 400,
                "x": 100,
                "y": 100,
                "always_on_top": True,
                "opacity": 1.0
            },
            "clipboard": {
                "auto_monitor": True,
                "max_history": 50
            },
            "editor": {
                "font_family": "Consolas",
                "font_size": 11,
                "word_wrap": True,
                "show_line_numbers": False
            },
            "theme": "light"
        }
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
