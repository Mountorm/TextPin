"""
路径管理器 - 处理应用程序的所有路径
"""
import os
import sys
from pathlib import Path


class PathManager:
    """路径管理器"""
    
    def __init__(self):
        # 获取应用程序根目录
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            self.app_dir = Path(sys.executable).parent
        else:
            # 开发环境
            self.app_dir = Path(__file__).parent.parent
        
        # 读取或创建数据目录配置
        self._load_data_dir()
    
    def _load_data_dir(self):
        """加载数据目录配置"""
        # 配置文件路径（与可执行文件在同一目录）
        self.config_file = self.app_dir / 'data_path.txt'
        
        # 如果配置文件存在，读取自定义路径
        if self.config_file.exists():
            try:
                custom_path = self.config_file.read_text(encoding='utf-8').strip()
                if custom_path and Path(custom_path).exists():
                    self.data_dir = Path(custom_path)
                else:
                    self.data_dir = self._get_default_data_dir()
            except:
                self.data_dir = self._get_default_data_dir()
        else:
            self.data_dir = self._get_default_data_dir()
        
        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_default_data_dir(self):
        """获取默认数据目录"""
        # Windows: %APPDATA%\TextPin
        # 其他系统: ~/.textpin
        if sys.platform == 'win32':
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata) / 'TextPin'
        
        # 默认使用用户主目录
        return Path.home() / '.textpin'
    
    def set_data_dir(self, path):
        """设置数据目录"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # 保存配置
        self.config_file.write_text(str(path), encoding='utf-8')
        self.data_dir = path
    
    @property
    def config_path(self):
        """配置文件路径"""
        return self.data_dir / 'config.json'
    
    @property
    def database_path(self):
        """数据库路径"""
        return self.data_dir / 'textpin.db'
    
    @property
    def log_dir(self):
        """日志目录"""
        log_dir = self.data_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        return log_dir
    
    def get_info(self):
        """获取路径信息"""
        return {
            '应用程序目录': str(self.app_dir),
            '数据目录': str(self.data_dir),
            '配置文件': str(self.config_path),
            '数据库': str(self.database_path),
            '日志目录': str(self.log_dir),
        }


# 全局实例
_path_manager = None

def get_path_manager():
    """获取路径管理器实例（单例）"""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager
