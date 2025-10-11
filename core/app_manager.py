"""
应用管理器 - 统一管理所有窗口和功能
"""
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from .clipboard_monitor import ClipboardMonitor
from .storage import StorageManager
from .hotkey_manager import HotkeyManager
from utils import ConfigManager


class AppManager(QObject):
    """应用管理器"""
    
    def __init__(self):
        super().__init__()
        
        # 管理器
        self.config = ConfigManager()
        self.storage = StorageManager()
        self.clipboard_monitor = ClipboardMonitor()
        self.hotkey_manager = HotkeyManager()
        
        # 窗口
        self.settings_window = None
        self.card_windows = []  # 所有贴卡窗口
        
        # 连接信号
        self._connect_signals()
        
        # 初始化
        self._init_settings()
    
    def _connect_signals(self):
        """连接信号"""
        # 剪贴板变化
        self.clipboard_monitor.clipboard_changed.connect(self._on_clipboard_changed)
        
        # 快捷键
        self.hotkey_manager.hotkey_pressed.connect(self._on_hotkey_pressed)
    
    def _init_settings(self):
        """初始化设置"""
        # 加载配置
        auto_monitor = self.config.get('clipboard.auto_monitor', True)
        ignore_self = self.config.get('clipboard.ignore_self', True)
        hotkey = self.config.get('hotkey.create_card', 'F4')
        
        # 应用配置
        self.clipboard_monitor.set_ignore_self(ignore_self)
        
        # 根据设置启动剪贴板监听
        if auto_monitor:
            self.clipboard_monitor.start_monitoring()
            print("剪贴板自动监听已启动（自动保存到历史）")
        else:
            print("剪贴板自动监听已关闭（不自动保存历史）")
        
        # 注册快捷键
        if hotkey:
            success = self.hotkey_manager.register_from_string(hotkey)
            if success:
                print(f"全局快捷键已注册: {hotkey}")
            else:
                print(f"全局快捷键注册失败: {hotkey}")
    
    def show_settings(self):
        """显示设置窗口"""
        if not self.settings_window:
            from ui import SettingsWindow
            # 传递共享的配置管理器和存储管理器
            self.settings_window = SettingsWindow(config=self.config, storage=self.storage)
            
            # 连接设置窗口的信号
            self.settings_window.auto_monitor_changed.connect(
                self._on_auto_monitor_changed
            )
            self.settings_window.ignore_self_changed.connect(
                self._on_ignore_self_changed
            )
            self.settings_window.hotkey_changed.connect(
                self._on_hotkey_changed
            )
            self.settings_window.create_card_requested.connect(
                lambda: self.create_card()
            )
            self.settings_window.card_style_changed.connect(
                self._on_card_style_changed
            )
            self.settings_window.card_appearance_changed.connect(
                self._on_card_appearance_changed
            )
            self.settings_window.load_to_card_requested.connect(
                self.create_card
            )
            self.settings_window.menu_config_changed.connect(
                self._on_menu_config_changed
            )
        
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
    
    def create_card(self, content=None):
        """
        创建新贴卡
        
        Args:
            content: 贴卡内容，如果为 None 则从历史记录读取最新内容
        """
        from ui import CardWindow
        
        if content is None:
            # 始终从历史记录读取最新内容
            history = self.storage.get_history(1)
            if history:
                content = history[0]['content']
                print(f"从历史记录读取内容: {content[:30]}...")
            else:
                print("历史记录为空，无法创建贴卡")
                return
        
        if not content:
            print("内容为空，无法创建贴卡")
            return
        
        # 创建贴卡窗口（传递剪贴板监听器）
        card = CardWindow(content, clipboard_monitor=self.clipboard_monitor)
        
        # 应用配置
        default_width = self.config.get('card.default_width', 300)
        default_height = self.config.get('card.default_height', 200)
        auto_height = self.config.get('card.auto_height', False)
        opacity = self.config.get('card.opacity', 0.95)
        
        print(f"配置读取: 自动高度={auto_height}, 默认高度={default_height}")
        
        # 计算高度
        if auto_height:
            # 根据内容自动计算高度
            line_count = content.count('\n') + 1
            font_size = self.config.get('card.font_size', 10)
            line_height = font_size * 2.2  # 行高约为字号的2.2倍（更真实）
            content_height = line_count * line_height + 80  # 加上边距和内边距
            actual_height = max(150, min(600, int(content_height)))  # 限制在150-600之间
            print(f"自动高度: {line_count}行 × {line_height}px = {actual_height}px")
        else:
            actual_height = default_height
        
        card.resize(default_width, actual_height)
        card.setWindowOpacity(opacity)
        
        # 定位窗口（鼠标位置附近）
        from PyQt6.QtGui import QCursor
        cursor_pos = QCursor.pos()
        offset = len(self.card_windows) * 25  # 多个贴卡时的偏移
        x = cursor_pos.x() + 1 + offset
        y = cursor_pos.y() + 1 + offset
        card.move(x, y)
        
        # 连接关闭信号
        card.closed.connect(lambda: self._on_card_closed(card))
        
        # 保存引用并显示
        self.card_windows.append(card)
        card.show()
        
        # 设置焦点到新创建的卡片
        card.activateWindow()  # 激活窗口
        card.raise_()  # 置于最前
        card.setFocus()  # 设置焦点
        
        print(f"已创建贴卡，当前贴卡数量: {len(self.card_windows)}")
    
    def _on_clipboard_changed(self, text):
        """剪贴板内容改变 - 保存到历史"""
        print(f"检测到剪贴板变化: {text[:50]}...")
        
        # 保存到历史记录
        self.storage.add_history(text)
        print("→ 已保存到历史记录")
        
        # 如果设置窗口已打开，实时刷新历史列表
        if self.settings_window and self.settings_window.isVisible():
            self.settings_window.refresh_history()
    
    def _on_hotkey_pressed(self, hotkey_name):
        """快捷键按下"""
        print(f"快捷键触发: {hotkey_name}")
        
        if hotkey_name == "create_card":
            self.create_card()
    
    def _on_card_closed(self, card):
        """贴卡窗口关闭"""
        if card in self.card_windows:
            self.card_windows.remove(card)
            print(f"贴卡已关闭，剩余贴卡数量: {len(self.card_windows)}")
    
    def _on_auto_monitor_changed(self, enabled):
        """自动监听剪贴板设置改变 - 立即生效"""
        print(f"自动监听剪贴板设置改变: {enabled}")
        if enabled:
            self.clipboard_monitor.start_monitoring()
            print("✓ 剪贴板监听已启动（自动保存到历史）")
        else:
            self.clipboard_monitor.stop_monitoring()
            print("✓ 剪贴板监听已停止（不自动保存历史）")
    
    def _on_ignore_self_changed(self, enabled):
        """忽略自身复制设置改变 - 立即生效"""
        print(f"忽略自身复制设置改变: {enabled}")
        self.clipboard_monitor.set_ignore_self(enabled)
        print(f"✓ 忽略自身复制: {enabled}")
    
    def _on_hotkey_changed(self, hotkey):
        """快捷键设置改变 - 立即生效"""
        print(f"正在更新快捷键: {hotkey}")
        
        # 注销旧快捷键
        self.hotkey_manager.unregister_all()
        
        # 注册新快捷键
        success = self.hotkey_manager.register_from_string(hotkey)
        if success:
            print(f"✓ 快捷键已更新并生效: {hotkey}")
        else:
            print(f"✗ 快捷键更新失败: {hotkey}")
            print("  提示: 可能需要管理员权限或快捷键已被占用")
    
    def _on_card_style_changed(self, width, height, opacity):
        """贴卡样式改变 - 立即应用到所有现有贴卡"""
        print(f"贴卡样式改变: 宽度={width}, 高度={height}, 透明度={opacity}")
        
        # 应用到所有现有贴卡
        for card in self.card_windows:
            card.resize(width, height)
            card.setWindowOpacity(opacity)
        
        if self.card_windows:
            print(f"✓ 已更新 {len(self.card_windows)} 个贴卡的样式")
    
    def _on_card_appearance_changed(self, font_size, font_color, bg_color):
        """贴卡外观改变 - 立即应用到所有现有贴卡"""
        print(f"贴卡外观改变: 字号={font_size}, 字色={font_color}, 背景色={bg_color}")
        
        # 应用到所有现有贴卡
        for card in self.card_windows:
            card.apply_appearance(font_size, font_color, bg_color)
        
        if self.card_windows:
            print(f"✓ 已更新 {len(self.card_windows)} 个贴卡的外观")
    
    def _on_menu_config_changed(self):
        """菜单配置改变 - 立即应用到所有现有贴卡"""
        print("菜单配置改变，刷新所有贴卡")
        
        # 通知所有现有贴卡重新加载菜单配置
        for card in self.card_windows:
            card.reload_menu_config()
        
        if self.card_windows:
            print(f"✓ 已刷新 {len(self.card_windows)} 个贴卡的菜单配置")
    
    def cleanup(self):
        """清理资源"""
        print("正在清理资源...")
        
        # 关闭所有贴卡
        for card in self.card_windows[:]:
            card.close()
        
        # 关闭设置窗口
        if self.settings_window:
            self.settings_window.close()
        
        # 清理管理器
        self.hotkey_manager.cleanup()
        self.storage.close()
        
        print("资源清理完成")
