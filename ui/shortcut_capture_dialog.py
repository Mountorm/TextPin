"""
快捷键捕获对话框 - 引导用户按下快捷键
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QFont


class ShortcutCaptureDialog(QDialog):
    """快捷键捕获对话框"""
    
    def __init__(self, current_shortcut="", parent=None):
        super().__init__(parent)
        self.captured_shortcut = current_shortcut
        self.key_sequence = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置快捷键")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        
        # 说明文字
        info_label = QLabel("请按下您想要设置的快捷键组合")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666; font-size: 12px; margin: 10px;")
        layout.addWidget(info_label)
        
        # 快捷键显示区域
        display_frame = QFrame()
        display_frame.setFrameShape(QFrame.Shape.StyledPanel)
        display_frame.setStyleSheet("""
            QFrame {
                background: #f5f5f5;
                border: 2px dashed #999;
                border-radius: 5px;
                padding: 20px;
            }
        """)
        display_layout = QVBoxLayout(display_frame)
        
        self.shortcut_label = QLabel(self.captured_shortcut or "等待按键...")
        self.shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.shortcut_label.setFont(font)
        self.shortcut_label.setStyleSheet("color: #333; padding: 20px;")
        display_layout.addWidget(self.shortcut_label)
        
        layout.addWidget(display_frame)
        
        # 提示文字
        hint_label = QLabel(
            "支持的按键：\n"
            "• 功能键: F1-F12\n"
            "• 修饰键: Ctrl, Alt, Shift\n"
            "• 字母/数字: A-Z, 0-9\n"
            "• 特殊键: Enter, Space, Tab, Esc 等"
        )
        hint_label.setStyleSheet("color: #999; font-size: 10px; margin: 10px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_btn = QPushButton("清除")
        clear_btn.clicked.connect(self._clear_shortcut)
        button_layout.addWidget(clear_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def keyPressEvent(self, event):
        """捕获按键"""
        key = event.key()
        modifiers = event.modifiers()
        
        # 忽略单独的修饰键
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        
        # 特殊处理：Esc键关闭对话框
        if key == Qt.Key.Key_Escape and modifiers == Qt.KeyboardModifier.NoModifier:
            self.reject()
            return
        
        # 构建快捷键序列 - PyQt6 需要使用 .value 获取整数值
        try:
            # 尝试使用 value 属性（PyQt6）
            modifier_value = modifiers.value if hasattr(modifiers, 'value') else int(modifiers)
        except:
            # 如果失败，直接转换
            modifier_value = int(modifiers)
        
        key_sequence = QKeySequence(modifier_value | key)
        shortcut_text = key_sequence.toString()
        
        # 更新显示
        self.captured_shortcut = shortcut_text
        self.shortcut_label.setText(shortcut_text)
        self.shortcut_label.setStyleSheet("color: #2196F3; padding: 20px;")
    
    def _clear_shortcut(self):
        """清除快捷键"""
        self.captured_shortcut = ""
        self.shortcut_label.setText("等待按键...")
        self.shortcut_label.setStyleSheet("color: #999; padding: 20px;")
    
    def get_shortcut(self):
        """获取捕获的快捷键"""
        return self.captured_shortcut
