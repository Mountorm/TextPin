"""
查找替换对话框 - 类似 Word 风格
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QGroupBox,
                             QRadioButton, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor


class FindReplaceDialog(QDialog):
    """查找替换对话框"""
    
    def __init__(self, text_edit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit
        self.current_match_index = 0
        self.matches = []
        
        self.setWindowTitle("查找和替换")
        self.setFixedWidth(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 查找输入
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("查找内容:"))
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("输入要查找的文本")
        self.find_input.textChanged.connect(self._on_find_text_changed)
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # 替换选项（可折叠）
        self.replace_widget = QWidget()
        replace_main_layout = QVBoxLayout(self.replace_widget)
        replace_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 替换展开/折叠按钮
        toggle_layout = QHBoxLayout()
        self.toggle_replace_btn = QPushButton("▼ 显示替换选项")
        self.toggle_replace_btn.setCheckable(True)
        self.toggle_replace_btn.clicked.connect(self._toggle_replace)
        toggle_layout.addWidget(self.toggle_replace_btn)
        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)
        
        # 替换输入（初始隐藏）
        self.replace_content = QWidget()
        replace_content_layout = QVBoxLayout(self.replace_content)
        replace_content_layout.setContentsMargins(0, 5, 0, 0)
        
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("替换为:  "))
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("输入替换后的文本")
        replace_layout.addWidget(self.replace_input)
        replace_content_layout.addLayout(replace_layout)
        
        self.replace_content.hide()
        layout.addWidget(self.replace_content)
        
        # 搜索选项
        options_group = QGroupBox("搜索选项")
        options_layout = QVBoxLayout()
        
        # 复选框选项
        self.case_sensitive = QCheckBox("区分大小写")
        self.whole_word = QCheckBox("全词匹配")
        self.use_regex = QCheckBox("使用正则表达式")
        
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.whole_word)
        options_layout.addWidget(self.use_regex)
        
        # 搜索方向
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("方向:"))
        self.search_up = QRadioButton("向上")
        self.search_down = QRadioButton("向下")
        self.search_down.setChecked(True)
        direction_layout.addWidget(self.search_up)
        direction_layout.addWidget(self.search_down)
        direction_layout.addStretch()
        
        options_layout.addLayout(direction_layout)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.find_next_btn = QPushButton("查找下一个(F3)")
        self.find_next_btn.clicked.connect(self._find_next)
        self.find_next_btn.setDefault(True)
        
        self.replace_btn = QPushButton("替换")
        self.replace_btn.clicked.connect(self._replace)
        self.replace_btn.hide()  # 初始隐藏
        
        self.replace_all_btn = QPushButton("全部替换")
        self.replace_all_btn.clicked.connect(self._replace_all)
        self.replace_all_btn.hide()  # 初始隐藏
        
        self.count_btn = QPushButton("计数")
        self.count_btn.clicked.connect(self._count_matches)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.find_next_btn)
        button_layout.addWidget(self.replace_btn)
        button_layout.addWidget(self.replace_all_btn)
        button_layout.addWidget(self.count_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 应用样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                padding: 5px 15px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:default {
                background-color: #007ACC;
                color: white;
                border: 1px solid #005A9E;
            }
            QPushButton:default:hover {
                background-color: #005A9E;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #007ACC;
            }
        """)
    
    def _toggle_replace(self, checked):
        """切换替换选项显示"""
        if checked:
            self.replace_content.show()
            self.replace_btn.show()
            self.replace_all_btn.show()
            self.toggle_replace_btn.setText("▲ 隐藏替换选项")
            self.setWindowTitle("查找和替换")
        else:
            self.replace_content.hide()
            self.replace_btn.hide()
            self.replace_all_btn.hide()
            self.toggle_replace_btn.setText("▼ 显示替换选项")
            self.setWindowTitle("查找")
    
    def _on_find_text_changed(self, text):
        """查找文本改变"""
        if text:
            self.status_label.setText("")
        
    def _find_next(self):
        """查找下一个"""
        find_text = self.find_input.text()
        if not find_text:
            self.status_label.setText("请输入查找内容")
            return
        
        content = self.text_edit.toPlainText()
        cursor = self.text_edit.textCursor()
        
        # 构建搜索标志
        flags = QTextCursor.FindFlag(0)
        if self.case_sensitive.isChecked():
            flags |= QTextCursor.FindFlag.FindCaseSensitively
        if self.whole_word.isChecked():
            flags |= QTextCursor.FindFlag.FindWholeWords
        if self.search_up.isChecked():
            flags |= QTextCursor.FindFlag.FindBackward
        
        # 从当前位置查找
        if self.use_regex.isChecked():
            import re
            pattern = re.compile(find_text, re.IGNORECASE if not self.case_sensitive.isChecked() else 0)
            
            if self.search_down.isChecked():
                pos = cursor.position()
                match = pattern.search(content, pos)
                if not match:
                    # 从头开始
                    match = pattern.search(content, 0)
                
                if match:
                    new_cursor = self.text_edit.textCursor()
                    new_cursor.setPosition(match.start())
                    new_cursor.setPosition(match.end(), QTextCursor.MoveMode.KeepAnchor)
                    self.text_edit.setTextCursor(new_cursor)
                    self.status_label.setText(f"找到匹配项")
                else:
                    self.status_label.setText("未找到匹配项")
        else:
            found_cursor = self.text_edit.document().find(find_text, cursor, flags)
            
            if found_cursor.isNull():
                # 从头/尾开始查找
                if self.search_down.isChecked():
                    found_cursor = self.text_edit.document().find(find_text, 0, flags)
                else:
                    found_cursor = self.text_edit.document().find(find_text, len(content), flags)
            
            if not found_cursor.isNull():
                self.text_edit.setTextCursor(found_cursor)
                self.status_label.setText("找到匹配项")
            else:
                self.status_label.setText("未找到匹配项")
    
    def _replace(self):
        """替换当前匹配"""
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not find_text:
            self.status_label.setText("请输入查找内容")
            return
        
        cursor = self.text_edit.textCursor()
        
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            # 检查选中的是否是要查找的文本
            if (self.case_sensitive.isChecked() and selected_text == find_text) or \
               (not self.case_sensitive.isChecked() and selected_text.lower() == find_text.lower()):
                cursor.insertText(replace_text)
                self.status_label.setText("已替换 1 处")
                # 查找下一个
                self._find_next()
                return
        
        # 如果没有选中或选中的不匹配，先查找
        self._find_next()
    
    def _replace_all(self):
        """全部替换"""
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not find_text:
            self.status_label.setText("请输入查找内容")
            return
        
        content = self.text_edit.toPlainText()
        
        if self.use_regex.isChecked():
            import re
            flags = re.IGNORECASE if not self.case_sensitive.isChecked() else 0
            try:
                new_content, count = re.subn(find_text, replace_text, content, flags=flags)
                if count > 0:
                    self.text_edit.setPlainText(new_content)
                    self.status_label.setText(f"已替换 {count} 处")
                    QMessageBox.information(self, "替换完成", f"共替换 {count} 处")
                else:
                    self.status_label.setText("未找到匹配项")
            except re.error as e:
                QMessageBox.warning(self, "正则表达式错误", str(e))
        else:
            if self.case_sensitive.isChecked():
                count = content.count(find_text)
                new_content = content.replace(find_text, replace_text)
            else:
                import re
                pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                matches = pattern.findall(content)
                count = len(matches)
                new_content = pattern.sub(replace_text, content)
            
            if count > 0:
                self.text_edit.setPlainText(new_content)
                self.status_label.setText(f"已替换 {count} 处")
                QMessageBox.information(self, "替换完成", f"共替换 {count} 处")
            else:
                self.status_label.setText("未找到匹配项")
    
    def _count_matches(self):
        """统计匹配数量"""
        find_text = self.find_input.text()
        if not find_text:
            self.status_label.setText("请输入查找内容")
            return
        
        content = self.text_edit.toPlainText()
        
        if self.use_regex.isChecked():
            import re
            flags = re.IGNORECASE if not self.case_sensitive.isChecked() else 0
            try:
                matches = re.findall(find_text, content, flags=flags)
                count = len(matches)
            except re.error as e:
                QMessageBox.warning(self, "正则表达式错误", str(e))
                return
        else:
            if self.case_sensitive.isChecked():
                count = content.count(find_text)
            else:
                count = content.lower().count(find_text.lower())
        
        self.status_label.setText(f"找到 {count} 个匹配项")
        QMessageBox.information(self, "计数结果", f"找到 {count} 个匹配项")
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key.Key_F3:
            self._find_next()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
