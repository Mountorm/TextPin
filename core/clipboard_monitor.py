"""
剪贴板监听模块
监听系统剪贴板变化并发出信号
"""
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication


class ClipboardMonitor(QObject):
    """剪贴板监听器"""
    
    # 信号：当剪贴板内容改变时发出
    clipboard_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.clipboard = QApplication.clipboard()
        self.last_text = ""
        self.monitoring = False
        self.ignore_self = True  # 是否忽略自身复制操作
        self.card_windows = []  # 保存所有贴卡窗口的引用
        self.internal_copy_flag = False  # 内部复制标记
        
        # 连接剪贴板信号（主要机制）
        self.clipboard.dataChanged.connect(self._on_clipboard_changed)
        
        # 轮询定时器（备用机制，解决信号不触发的问题）
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_clipboard)
        self.poll_interval = 500  # 轮询间隔（毫秒）
    
    def start_monitoring(self):
        """开始监听剪贴板"""
        self.monitoring = True
        # 获取当前剪贴板内容作为初始值
        self.last_text = self.clipboard.text()
        # 启动轮询定时器（备用机制）
        self.poll_timer.start(self.poll_interval)
        print(f"✓ 剪贴板监听已启动（信号 + {self.poll_interval}ms轮询）")
    
    def stop_monitoring(self):
        """停止监听剪贴板"""
        self.monitoring = False
        # 停止轮询定时器
        self.poll_timer.stop()
        print("✓ 剪贴板监听已停止")
    
    def is_monitoring(self):
        """检查是否正在监听"""
        return self.monitoring
    
    def _on_clipboard_changed(self):
        """剪贴板内容改变时的回调（信号机制）"""
        if not self.monitoring:
            return
        
        self._check_and_emit_change(source="信号")
    
    def _poll_clipboard(self):
        """轮询检查剪贴板（备用机制）"""
        if not self.monitoring:
            return
        
        self._check_and_emit_change(source="轮询")
    
    def _check_and_emit_change(self, source="未知"):
        """检查剪贴板变化并发射信号
        
        Args:
            source: 触发源（信号/轮询），用于调试
        """
        # 检查标记位（优先级最高）
        if self.ignore_self and self.internal_copy_flag:
            # print(f"✓ [{source}] 检测到内部复制标记，已忽略")
            return
        
        # 检查焦点（双重保险）
        if self.ignore_self and self._is_internal_copy():
            # print(f"✓ [{source}] 检测到焦点在贴卡内，已忽略")
            return
        
        # 获取剪贴板文本
        text = self.clipboard.text()
        
        # 检查是否为文本内容且与上次不同
        if text and text != self.last_text:
            self.last_text = text
            print(f"[{source}] 检测到剪贴板变化: {text[:50]}...")
            self.clipboard_changed.emit(text)
    
    def _is_internal_copy(self):
        """检查当前焦点是否在贴卡窗口中"""
        focused_widget = QApplication.focusWidget()
        if not focused_widget:
            return False
        
        # 检查焦点窗口是否是贴卡窗口
        for card in self.card_windows:
            if focused_widget.window() == card:
                return True
        
        return False
    
    def get_current_text(self):
        """获取当前剪贴板文本"""
        return self.clipboard.text()
    
    def set_text(self, text, mark_internal=True):
        """设置剪贴板文本
        
        Args:
            text: 文本内容
            mark_internal: 是否标记为内部操作
        """
        if mark_internal:
            self.internal_copy_flag = True
        
        self.clipboard.setText(text)
        self.last_text = text
        
        # 延迟重置标记
        if mark_internal:
            QTimer.singleShot(300, self._reset_flag)
    
    def _reset_flag(self):
        """重置标记"""
        self.internal_copy_flag = False
    
    def register_card(self, card):
        """注册贴卡窗口"""
        if card not in self.card_windows:
            self.card_windows.append(card)
    
    def unregister_card(self, card):
        """注销贴卡窗口"""
        if card in self.card_windows:
            self.card_windows.remove(card)
    
    def set_ignore_self(self, ignore):
        """设置是否忽略自身复制操作"""
        self.ignore_self = ignore
