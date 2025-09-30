"""
快捷键输入控件
支持捕获键盘输入并转换为快捷键字符串
"""
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent


class HotkeyEdit(QLineEdit):
    """快捷键输入控件"""
    
    # 信号：快捷键改变
    hotkeyChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("点击后按下快捷键...")
        self.current_hotkey = ""
        
    def keyPressEvent(self, event: QKeyEvent):
        """捕获按键事件"""
        key = event.key()
        modifiers = event.modifiers()
        
        # 忽略单独的修饰键
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, 
                   Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        
        # Esc 键用于清除
        if key == Qt.Key.Key_Escape:
            self.clearHotkey()
            return
        
        # 构建快捷键字符串
        parts = []
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("Alt")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("Shift")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("Win")
        
        # 获取键名
        key_name = self._get_key_name(key)
        if key_name:
            parts.append(key_name)
        
        if parts:
            hotkey = "+".join(parts)
            # 只有当快捷键真正改变时才触发信号
            if hotkey != self.current_hotkey:
                self.setText(hotkey)
                self.current_hotkey = hotkey
                self.hotkeyChanged.emit(hotkey)
    
    def _get_key_name(self, key):
        """获取键名"""
        # 功能键
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F24:
            return f"F{key - Qt.Key.Key_F1 + 1}"
        
        # 字母键
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            return chr(key)
        
        # 数字键
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return chr(key)
        
        # 特殊键
        special_keys = {
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Return: "Enter",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Backspace: "Backspace",
            Qt.Key.Key_Delete: "Delete",
            Qt.Key.Key_Insert: "Insert",
            Qt.Key.Key_Home: "Home",
            Qt.Key.Key_End: "End",
            Qt.Key.Key_PageUp: "PageUp",
            Qt.Key.Key_PageDown: "PageDown",
            Qt.Key.Key_Up: "Up",
            Qt.Key.Key_Down: "Down",
            Qt.Key.Key_Left: "Left",
            Qt.Key.Key_Right: "Right",
            Qt.Key.Key_Escape: "Esc",
        }
        
        return special_keys.get(key, None)
    
    def setHotkey(self, hotkey):
        """设置快捷键"""
        self.current_hotkey = hotkey
        self.setText(hotkey)
    
    def getHotkey(self):
        """获取快捷键"""
        return self.current_hotkey
    
    def clearHotkey(self):
        """清除快捷键"""
        self.current_hotkey = ""
        self.clear()
