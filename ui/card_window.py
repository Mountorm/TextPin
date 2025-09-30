"""
贴卡窗口 - 卡片式显示剪贴板内容
类似 PixPin 的浮动卡片效果
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QApplication)
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor
import pyperclip


class CardWindow(QWidget):
    """贴卡窗口 - 浮动卡片式显示"""
    
    # 信号
    closed = pyqtSignal()  # 窗口关闭信号
    
    def __init__(self, content="", clipboard_monitor=None, parent=None):
        super().__init__(parent)
        self.content = content
        self.clipboard_monitor = clipboard_monitor  # 剪贴板监听器引用
        self.is_internal_copy = False  # 标记是否是内部复制操作
        
        # 窗口设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.WindowStaysOnTopHint |  # 置顶
            Qt.WindowType.Tool  # 工具窗口，不显示在任务栏
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        
        # 拖动相关
        self.dragging = False
        self.drag_position = QPoint()
        
        # 调整大小相关
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 8  # 边缘检测范围
        
        # 固定状态
        self.is_pinned = False
        
        self._init_ui()
        self._apply_style()
        
        # 启用鼠标追踪以实时更新光标样式
        self.setMouseTracking(True)
        self.content_widget.setMouseTracking(True)
        self.text_edit.setMouseTracking(True)
        
        # 安装事件过滤器以捕获所有鼠标移动
        self.content_widget.installEventFilter(self)
        self.text_edit.installEventFilter(self)
        
        # 注册到剪贴板监听器
        if self.clipboard_monitor:
            self.clipboard_monitor.register_card(self)
        
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 内容容器（带圆角和阴影效果）
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(10, 20, 10, 10)  # 增加上边距到20
        content_layout.setSpacing(0)
        
        # 文本显示区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.content)
        self.text_edit.setReadOnly(False)  # 允许编辑
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 设置字体（从配置加载）
        from utils import ConfigManager
        config = ConfigManager()
        font_size = config.get('card.font_size', 10)
        font = QFont("Consolas", font_size)
        self.text_edit.setFont(font)
        
        # 保存配置引用
        self.config = config
        
        # 自定义右键菜单
        self.text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self._show_context_menu)
        
        # 覆盖复制/剪切快捷键
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Ctrl+C 复制
        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.text_edit)
        copy_shortcut.activated.connect(self._handle_copy)
        
        # Ctrl+X 剪切
        cut_shortcut = QShortcut(QKeySequence.StandardKey.Cut, self.text_edit)
        cut_shortcut.activated.connect(self._handle_cut)
        
        content_layout.addWidget(self.text_edit, 1)
        
        main_layout.addWidget(self.content_widget)
        self.setLayout(main_layout)
        
        # 设置默认大小
        self.resize(300, 200)
        
    def _apply_style(self):
        """应用样式"""
        # 从配置加载颜色
        font_color = self.config.get('card.font_color', '#000000')
        bg_color = self.config.get('card.bg_color', '#FFFFFF')
        
        # 计算半透明背景色
        from PyQt6.QtGui import QColor
        bg_qcolor = QColor(bg_color)
        bg_rgba = f"rgba({bg_qcolor.red()}, {bg_qcolor.green()}, {bg_qcolor.blue()}, 250)"
        
        self.setStyleSheet(f"""
            #contentWidget {{
                background-color: {bg_rgba};
                border-radius: 10px;
                border: 1px solid #ddd;
            }}
            
            QTextEdit {{
                background-color: transparent;
                border: none;
                selection-background-color: #B3D9FF;
                color: {font_color};
            }}
            
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px 5px;
                font-size: 10px;
            }}
            
            QPushButton:hover {{
                background-color: #e0e0e0;
                border: 1px solid #999;
            }}
            
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            
            QPushButton:checked {{
                background-color: #4CAF50;
                color: white;
                border: 1px solid #45a049;
            }}
        """)
    
    
    def _get_resize_edge(self, pos):
        """获取鼠标所在的边缘"""
        rect = self.rect()
        margin = self.resize_margin
        
        left = pos.x() <= margin
        right = pos.x() >= rect.width() - margin
        top = pos.y() <= margin
        bottom = pos.y() >= rect.height() - margin
        
        # 上边框不用于调整大小，只用于拖动
        # 只检测左、右、下三个边和角
        if bottom and left:
            return 'bottom_left'
        elif bottom and right:
            return 'bottom_right'
        elif bottom:
            return 'bottom'
        elif left:
            return 'left'
        elif right:
            return 'right'
        return None
    
    def _update_cursor(self, edge):
        """根据边缘更新鼠标样式"""
        if edge == 'bottom_right':
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        elif edge == 'bottom_left':
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        elif edge == 'bottom':
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        elif edge == 'left' or edge == 'right':
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def mousePressEvent(self, event):
        """鼠标按下 - 开始拖动或调整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_resize_edge(event.pos())
            
            if edge:
                # 在边缘，开始调整大小
                self.resizing = True
                self.resize_edge = edge
                self.drag_position = event.globalPosition().toPoint()
                self.original_geometry = self.geometry()
                event.accept()
            else:
                # 检查是否在文本编辑区域
                text_edit_rect = self.text_edit.geometry()
                # 转换为窗口坐标
                text_edit_global = self.content_widget.mapTo(self, text_edit_rect.topLeft())
                text_edit_window_rect = text_edit_rect.translated(text_edit_global)
                
                if not text_edit_window_rect.contains(event.pos()):
                    # 不在文本编辑区域，可以拖动
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                    event.accept()
                else:
                    # 在文本编辑区域，传递事件
                    super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖动窗口或调整大小"""
        if self.resizing and event.buttons() == Qt.MouseButton.LeftButton:
            # 调整大小
            delta = event.globalPosition().toPoint() - self.drag_position
            geo = self.original_geometry
            
            # 计算新的尺寸和位置
            new_x = geo.x()
            new_y = geo.y()
            new_width = geo.width()
            new_height = geo.height()
            
            # 水平方向调整
            if 'right' in self.resize_edge:
                new_width = max(200, geo.width() + delta.x())  # 最小宽度200
            elif 'left' in self.resize_edge:
                new_width = max(200, geo.width() - delta.x())
                new_x = geo.x() + geo.width() - new_width
            
            # 垂直方向调整
            if 'bottom' in self.resize_edge:
                new_height = max(150, geo.height() + delta.y())  # 最小高度150
            elif 'top' in self.resize_edge:
                new_height = max(150, geo.height() - delta.y())
                new_y = geo.y() + geo.height() - new_height
            
            # 应用新的几何形状
            self.setGeometry(new_x, new_y, new_width, new_height)
            
            event.accept()
        elif self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # 拖动窗口
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            # 更新鼠标样式
            edge = self._get_resize_edge(event.pos())
            self._update_cursor(edge)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放 - 结束拖动或调整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_edge = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            event.accept()
    
    def keyPressEvent(self, event):
        """键盘事件"""
        key = event.key()
        mods = event.modifiers()
        
        # Esc 关闭
        if key == Qt.Key.Key_Escape:
            self.close()
        # Ctrl+F 搜索
        elif key == Qt.Key.Key_F and mods == Qt.KeyboardModifier.ControlModifier:
            self._on_search()
        # Ctrl+H 替换
        elif key == Qt.Key.Key_H and mods == Qt.KeyboardModifier.ControlModifier:
            self._on_replace()
        # F3 查找下一个
        elif key == Qt.Key.Key_F3:
            if hasattr(self, 'last_search_text'):
                self._find_next(mods == Qt.KeyboardModifier.ShiftModifier)
        # Ctrl+N 清空
        elif key == Qt.Key.Key_N and mods == Qt.KeyboardModifier.ControlModifier:
            self._on_clear()
        else:
            super().keyPressEvent(event)
    
    def _on_copy(self):
        """复制内容到剪贴板"""
        text = self.text_edit.toPlainText()
        if text:
            # 使用剪贴板监听器的内部复制方法
            if self.clipboard_monitor:
                self.clipboard_monitor.set_text(text, is_internal=True)
            else:
                pyperclip.copy(text)
            
            # 短暂提示
            original_text = self.copy_btn.text()
            self.copy_btn.setText("✓ 已复制")
            self.copy_btn.setEnabled(False)
            
            # 500ms 后恢复
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, lambda: self._reset_copy_button(original_text))
    
    def _reset_copy_button(self, text):
        """重置复制按钮"""
        self.copy_btn.setText(text)
        self.copy_btn.setEnabled(True)
        self.is_internal_copy = False
    
    def _handle_copy(self):
        """处理复制操作（Ctrl+C）"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            # 直接复制到剪贴板（焦点监听会自动过滤）
            if self.clipboard_monitor:
                self.clipboard_monitor.set_text(selected_text)
            else:
                import pyperclip
                pyperclip.copy(selected_text)
    
    def _handle_cut(self):
        """处理剪切操作（Ctrl+X）"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            # 直接复制到剪贴板（焦点监听会自动过滤）
            if self.clipboard_monitor:
                self.clipboard_monitor.set_text(selected_text)
            else:
                import pyperclip
                pyperclip.copy(selected_text)
            # 删除选中文本
            cursor.removeSelectedText()
    
    def _show_context_menu(self, pos):
        """显示自定义右键菜单"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        
        # 撤销/重做
        undo_action = QAction("撤销", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.text_edit.undo)
        undo_action.setEnabled(self.text_edit.document().isUndoAvailable())
        menu.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.text_edit.redo)
        redo_action.setEnabled(self.text_edit.document().isRedoAvailable())
        menu.addAction(redo_action)
        
        menu.addSeparator()
        
        # 剪切/复制/粘贴
        cut_action = QAction("剪切", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self._handle_cut)
        cut_action.setEnabled(self.text_edit.textCursor().hasSelection())
        menu.addAction(cut_action)
        
        copy_action = QAction("复制", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self._handle_copy)
        copy_action.setEnabled(self.text_edit.textCursor().hasSelection())
        menu.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.text_edit.paste)
        menu.addAction(paste_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.text_edit.textCursor().removeSelectedText())
        delete_action.setEnabled(self.text_edit.textCursor().hasSelection())
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # 全选
        select_all_action = QAction("全选", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.text_edit.selectAll)
        menu.addAction(select_all_action)
        
        menu.addSeparator()
        
        # 搜索和替换
        search_action = QAction("🔍 搜索...", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self._on_search)
        menu.addAction(search_action)
        
        replace_action = QAction("🔄 替换...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self._on_replace)
        menu.addAction(replace_action)
        
        menu.addSeparator()
        
        # 工具功能
        format_action = QAction("📋 JSON格式化", self)
        format_action.triggered.connect(self._on_format_json)
        menu.addAction(format_action)
        
        stats_action = QAction("📊 文本统计", self)
        stats_action.triggered.connect(self._show_stats)
        menu.addAction(stats_action)
        
        menu.addSeparator()
        
        # 复制全部内容
        copy_all_action = QAction("📄 复制全部到剪贴板", self)
        copy_all_action.triggered.connect(self._on_copy)
        menu.addAction(copy_all_action)
        
        clear_action = QAction("🗑️ 清空内容", self)
        clear_action.setShortcut("Ctrl+N")
        clear_action.triggered.connect(self._on_clear)
        menu.addAction(clear_action)
        
        menu.addSeparator()
        
        # 窗口控制
        pin_action = QAction("📌 固定窗口", self)
        pin_action.setCheckable(True)
        pin_action.setChecked(self.is_pinned)
        pin_action.triggered.connect(self._toggle_pin)
        menu.addAction(pin_action)
        
        close_action = QAction("✖ 关闭贴卡", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        # 在鼠标位置显示菜单
        menu.exec(self.text_edit.mapToGlobal(pos))
    
    def _toggle_pin(self, checked):
        """固定/取消固定窗口"""
        self.is_pinned = checked
        if checked:
            print("窗口已固定")
        else:
            print("窗口已取消固定")
    
    def _on_clear(self):
        """清空内容"""
        self.text_edit.clear()
    
    def _on_search(self):
        """搜索文本 - 使用统一对话框"""
        from .find_replace_dialog import FindReplaceDialog
        
        dialog = FindReplaceDialog(self.text_edit, self)
        dialog.setWindowTitle("查找")  # 默认为查找模式
        dialog.exec()
    
    def _on_replace(self):
        """查找替换 - 使用统一对话框"""
        from .find_replace_dialog import FindReplaceDialog
        
        dialog = FindReplaceDialog(self.text_edit, self)
        dialog.toggle_replace_btn.setChecked(True)  # 展开替换选项
        dialog._toggle_replace(True)
        dialog.exec()
    
    def _show_stats(self):
        """显示文本统计"""
        from PyQt6.QtWidgets import QMessageBox
        
        text = self.text_edit.toPlainText()
        
        # 统计
        char_count = len(text)
        char_no_spaces = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
        word_count = len(text.split())
        line_count = text.count('\n') + 1 if text else 0
        
        QMessageBox.information(
            self,
            "文本统计",
            f"字符数: {char_count}\n"
            f"字符数(不含空格): {char_no_spaces}\n"
            f"单词数: {word_count}\n"
            f"行数: {line_count}"
        )
    
    def _on_format_json(self):
        """JSON 格式化"""
        import json
        from PyQt6.QtWidgets import QMessageBox
        
        text = self.text_edit.toPlainText()
        
        try:
            # 尝试解析 JSON
            data = json.loads(text)
            
            # 格式化输出
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            
            self.text_edit.setPlainText(formatted)
            QMessageBox.information(self, "格式化成功", "JSON 已格式化")
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self, 
                "格式化失败", 
                f"JSON 解析错误:\n{str(e)}\n\n请确保内容是有效的 JSON 格式"
            )
    
    def set_content(self, content):
        """设置内容"""
        self.content = content
        self.text_edit.setPlainText(content)
    
    def get_content(self):
        """获取内容"""
        return self.text_edit.toPlainText()
    
    def apply_appearance(self, font_size, font_color, bg_color):
        """应用外观设置"""
        # 更新字体大小
        font = self.text_edit.font()
        font.setPointSize(font_size)
        self.text_edit.setFont(font)
        
        # 更新配置
        self.config.set('card.font_size', font_size)
        self.config.set('card.font_color', font_color)
        self.config.set('card.bg_color', bg_color)
        
        # 重新应用样式
        self._apply_style()
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 捕获子部件的鼠标移动"""
        if event.type() == event.Type.MouseMove:
            # 将子部件的坐标转换为窗口坐标
            global_pos = obj.mapToGlobal(event.pos())
            local_pos = self.mapFromGlobal(global_pos)
            
            # 检查是否在边缘
            edge = self._get_resize_edge(local_pos)
            self._update_cursor(edge)
        
        return super().eventFilter(obj, event)
    
    def closeEvent(self, event):
        """关闭事件"""
        # 从剪贴板监听器注销
        if self.clipboard_monitor:
            self.clipboard_monitor.unregister_card(self)
        
        self.closed.emit()
        super().closeEvent(event)
