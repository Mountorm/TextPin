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
    
    # 功能定义（id, 名称, 图标, 默认快捷键, 方法名, 提示文字）
    MENU_FEATURES = [
        ('copy_all', '复制全部', '📋', '', '_on_copy', '复制所有内容到剪贴板'),
        ('clear', '清空内容', '🗑️', 'Ctrl+N', '_on_clear', '清空所有内容'),
        ('clear_format', '清除格式', '🧹', '', '_on_clear_format', '移除所有文本格式，保留纯文本'),
        ('clear_empty_lines', '清除空行', '📝', '', '_on_clear_empty_lines', '移除所有空白行'),
        ('separator1', '---', '', '', '', ''),  # 分隔符
        ('search', '搜索', '🔍', 'Ctrl+F', '_on_search', '查找文本'),
        ('replace', '替换', '🔄', 'Ctrl+H', '_on_replace', '查找并替换文本'),
        ('stats', '文本统计', '📊', '', '_show_stats', '显示字符、行数等统计信息'),
        ('json_format', 'JSON格式化', '{ }', '', '_on_json_format', '格式化JSON内容'),
        ('separator2', '---', '', '', '', ''),  # 分隔符
        ('pin', '固定位置', '📌', 'Ctrl+P', '_toggle_pin', '固定窗口位置和尺寸，禁止拖动和调整'),
        ('always_on_top', '窗口置顶', '🔺', 'Ctrl+T', '_toggle_always_on_top', '切换窗口是否始终置顶'),
        ('close', '关闭贴卡', '✖', 'Ctrl+W', 'close', '关闭当前贴卡'),
    ]
    
    def __init__(self, content="", clipboard_monitor=None, parent=None):
        super().__init__(parent)
        self.content = content
        self.clipboard_monitor = clipboard_monitor  # 剪贴板监听器引用
        self.is_internal_copy = False  # 标记是否是内部复制操作
        
        # 初始化配置（需要在使用前初始化）
        from utils import ConfigManager
        self.config = ConfigManager()
        
        # 状态变量（必须在使用前定义）
        # 固定状态（位置和尺寸）
        self.is_pinned = False
        # 置顶状态（默认开启）
        self.is_always_on_top = self.config.get('card.always_on_top', True)
        
        # 窗口设置
        window_flags = (
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.Tool  # 工具窗口，不显示在任务栏
        )
        # 如果默认置顶，添加置顶标志
        if self.is_always_on_top:
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        
        # 拖动相关
        self.dragging = False
        self.drag_position = QPoint()
        
        # 调整大小相关
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 8  # 边缘检测范围
        
        # 快捷键列表（用于管理和清理）
        self.shortcuts = []
        
        self._init_ui()
        self._register_shortcuts()
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
        font_size = self.config.get('card.font_size', 10)
        font_family = self.config.get('card.font_family', 'Consolas')
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
        
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
        font_family = self.config.get('card.font_family', 'Consolas')
        
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
                font-family: {font_family};
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
        # 如果窗口已固定，不显示调整大小光标
        if self.is_pinned:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            return
            
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
            # 如果窗口已固定，禁止拖动和调整大小
            if self.is_pinned:
                super().mousePressEvent(event)
                return
                
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
                self.clipboard_monitor.set_text(text, mark_internal=True)
            else:
                pyperclip.copy(text)
            
            # 简单提示（无按钮版本）
            print("✓ 已复制全部内容到剪贴板")
    
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
        """显示自定义右键菜单（根据配置动态生成）"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        
        # 获取启用的功能配置
        enabled_features = self.config.get('menu.enabled_features', None)
        if enabled_features is None:
            # 默认全部启用
            enabled_features = [f[0] for f in self.MENU_FEATURES]
        
        # 获取快捷键配置
        shortcuts = self.config.get('menu.shortcuts', {})
        
        # 动态生成菜单
        for feature_id, name, icon, default_shortcut, method_name, tooltip in self.MENU_FEATURES:
            # 检查是否启用
            if feature_id not in enabled_features:
                continue
            
            # 分隔符
            if feature_id.startswith('separator'):
                menu.addSeparator()
                continue
            
            # 创建动作
            action_text = f"{icon} {name}" if icon else name
            action = QAction(action_text, self)
            
            # 设置快捷键
            shortcut = shortcuts.get(feature_id, default_shortcut)
            if shortcut:
                action.setShortcut(shortcut)
            
            # 设置提示
            if tooltip:
                action.setToolTip(tooltip)
            
            # 连接方法
            if method_name:
                if method_name == 'close':
                    action.triggered.connect(self.close)
                elif method_name == '_toggle_pin':
                    # 固定位置需要特殊处理（可选中状态）
                    action.setCheckable(True)
                    action.setChecked(self.is_pinned)
                    action.triggered.connect(self._toggle_pin)
                elif method_name == '_toggle_always_on_top':
                    # 窗口置顶需要特殊处理（可选中状态）
                    action.setCheckable(True)
                    action.setChecked(self.is_always_on_top)
                    action.triggered.connect(self._toggle_always_on_top)
                else:
                    # 动态获取方法
                    method = getattr(self, method_name, None)
                    if method:
                        action.triggered.connect(method)
            
            menu.addAction(action)
        
        # 添加自定义规则
        custom_rules = self.config.get('custom_rules', [])
        enabled_custom_rules = [r for r in custom_rules if r.get('enabled', True)]
        
        if enabled_custom_rules:
            menu.addSeparator()
            menu.addAction("─ 自定义规则 ─").setEnabled(False)
            
            for rule in enabled_custom_rules:
                icon = rule.get('icon', '🧰')
                name = rule.get('name', '未命名')
                shortcut = rule.get('shortcut', '')
                
                action = QAction(f"{icon} {name}", self)
                if shortcut:
                    action.setShortcut(shortcut)
                
                # 使用 lambda 捕获 rule，避免闭包问题
                action.triggered.connect(lambda checked=False, r=rule: self._execute_custom_rule(r))
                menu.addAction(action)
        
        # 在鼠标位置显示菜单
        menu.exec(self.text_edit.mapToGlobal(pos))
    
    def _register_shortcuts(self):
        """注册所有快捷键"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # 清除旧的快捷键
        for shortcut in self.shortcuts:
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self.shortcuts.clear()
        
        # 获取快捷键配置
        shortcuts_config = self.config.get('menu.shortcuts', {})
        enabled_features = self.config.get('menu.enabled_features', None)
        if enabled_features is None:
            enabled_features = [f[0] for f in self.MENU_FEATURES]
        
        # 为每个启用的功能注册快捷键
        for feature_id, name, icon, default_shortcut, method_name, tooltip in self.MENU_FEATURES:
            # 跳过分隔符和未启用的功能
            if feature_id.startswith('separator') or feature_id not in enabled_features:
                continue
            
            # 获取快捷键（优先使用用户配置，否则使用默认）
            shortcut_key = shortcuts_config.get(feature_id, default_shortcut)
            if not shortcut_key:
                continue
            
            # 获取方法
            if method_name == 'close':
                method = self.close
            elif method_name == '_toggle_pin':
                # 使用专门的切换方法
                method = self._shortcut_toggle_pin
            elif method_name == '_toggle_always_on_top':
                # 使用专门的切换方法
                method = self._shortcut_toggle_always_on_top
            else:
                method = getattr(self, method_name, None)
            
            if method:
                # 创建快捷键
                shortcut = QShortcut(QKeySequence(shortcut_key), self)
                shortcut.activated.connect(method)
                self.shortcuts.append(shortcut)
                print(f"✓ 注册快捷键: {name} = {shortcut_key}")
        
        # 注册自定义规则的快捷键
        custom_rules = self.config.get('custom_rules', [])
        for rule in custom_rules:
            if not rule.get('enabled', True):
                continue
            
            shortcut_key = rule.get('shortcut', '')
            if not shortcut_key:
                continue
            
            rule_name = rule.get('name', '未命名')
            shortcut = QShortcut(QKeySequence(shortcut_key), self)
            shortcut.activated.connect(lambda r=rule: self._execute_custom_rule(r))
            self.shortcuts.append(shortcut)
            print(f"✓ 注册自定义规则快捷键: {rule_name} = {shortcut_key}")
    
    def _shortcut_toggle_pin(self):
        """快捷键触发的固定切换（不需要 checked 参数）"""
        self._toggle_pin(not self.is_pinned)
    
    def _shortcut_toggle_always_on_top(self):
        """快捷键触发的置顶切换（不需要 checked 参数）"""
        self._toggle_always_on_top(not self.is_always_on_top)
    
    def _execute_custom_rule(self, rule):
        """执行自定义规则"""
        from core import TextProcessor
        from PyQt6.QtWidgets import QMessageBox
        
        # 获取当前文本
        text = self.text_edit.toPlainText()
        
        if not text:
            QMessageBox.warning(self, "提示", "文本为空，无需处理")
            return
        
        # 执行处理
        processor = TextProcessor()
        try:
            result = processor.process(text, rule)
            
            # 更新文本
            self.text_edit.clear()
            self.text_edit.setPlainText(result)
            
            rule_name = rule.get('name', '未命名')
            print(f"✓ 已执行自定义规则: {rule_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行规则失败: {str(e)}")
            print(f"✗ 执行自定义规则失败: {str(e)}")
    
    def reload_menu_config(self):
        """重新加载菜单配置（用于设置更改后立即生效）"""
        # 重新注册快捷键
        self._register_shortcuts()
        print("✓ 菜单配置已重新加载")
    
    def _toggle_pin(self, checked):
        """固定/取消固定位置和尺寸"""
        self.is_pinned = checked
        if checked:
            print("✓ 窗口已固定（锁定位置和尺寸）")
        else:
            print("✓ 窗口已取消固定（可移动和调整大小）")
    
    def _toggle_always_on_top(self, checked):
        """切换窗口置顶状态"""
        self.is_always_on_top = checked
        
        # 更新窗口标志
        window_flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        if self.is_always_on_top:
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        
        self.setWindowFlags(window_flags)
        self.show()  # 重新显示窗口以应用标志
        
        if checked:
            print("✓ 窗口已置顶")
        else:
            print("✓ 窗口已取消置顶")
    
    def _on_clear(self):
        """清空内容"""
        self.text_edit.clear()
    
    def _on_clear_format(self):
        """清除格式 - 移除所有文本格式，保留纯文本"""
        import html
        import re
        
        # 获取 HTML 格式的内容
        html_text = self.text_edit.toHtml()
        
        # 步骤1: 移除 <style> 标签及其内容（包括 CSS 代码）
        # 使用 DOTALL 模式让 . 匹配换行符
        text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        
        # 步骤2: 移除 <script> 标签及其内容
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 步骤3: 移除 HTML 注释
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # 步骤4: 先解码 HTML 实体（必须在移除标签前做，否则 &lt;p&gt; 无法被识别）
        text = html.unescape(text)
        
        # 步骤5: 移除所有 HTML 标签（解码后才能正确匹配）
        text = re.sub(r'<[^>]+>', '', text)
        
        # 步骤6: 清除 Markdown 语法
        # 6.1 移除图片语法 ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
        
        # 6.2 移除链接语法 [text](url) 保留文本
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # 6.3 移除代码块 ```code```
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # 6.4 移除行内代码 `code`
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # 6.5 移除粗体 **text** 或 __text__
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        
        # 6.6 移除斜体 *text* 或 _text_
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # 6.7 移除删除线 ~~text~~
        text = re.sub(r'~~([^~]+)~~', r'\1', text)
        
        # 6.8 移除标题标记 # ## ###
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # 6.9 移除引用标记 >
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        
        # 6.10 移除无序列表标记 - 或 * 或 +
        text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)
        
        # 6.11 移除有序列表标记 1. 2. 3.
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 6.12 移除分隔线 --- 或 *** 或 ___
        text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
        
        # 6.13 移除表格语法（简单处理，移除 | 分隔符）
        text = re.sub(r'\|', '', text)
        
        # 步骤7: 清理空白字符
        # 移除零宽字符和其他不可见字符
        text = re.sub(r'[\u200b-\u200f\ufeff]', '', text)
        
        # 步骤8: 规范化换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 步骤9: 压缩多个连续空行为最多两个空行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 步骤10: 去除每行末尾的空白
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        text = '\n'.join(cleaned_lines)
        
        # 步骤11: 去除文本首尾空白
        final_text = text.strip()
        
        # 应用清理后的纯文本
        self.text_edit.clear()
        self.text_edit.setPlainText(final_text)
        
        print(f"✓ 已清除格式，保留纯文本内容（{len(final_text)} 字符）")
    
    def _on_clear_empty_lines(self):
        """清除空行 - 移除所有空白行"""
        import re
        
        # 获取当前文本
        text = self.text_edit.toPlainText()
        
        # 移除所有空白行（包括只有空格/制表符的行）
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # 重新组合文本
        cleaned_text = '\n'.join(non_empty_lines)
        
        # 更新文本
        self.text_edit.clear()
        self.text_edit.setPlainText(cleaned_text)
        
        removed_count = len(lines) - len(non_empty_lines)
        print(f"✓ 已清除 {removed_count} 个空行")
    
    def _on_search(self):
        """搜索文本 - 使用统一对话框"""
        from .find_replace_dialog import FindReplaceDialog
        
        dialog = FindReplaceDialog(self.text_edit, self)
        dialog.setWindowTitle("查找")  # 默认为查找模式
        dialog.show()  # 使用 show() 而不是 exec() 以允许非模态
    
    def _on_replace(self):
        """查找替换 - 使用统一对话框"""
        from .find_replace_dialog import FindReplaceDialog
        
        dialog = FindReplaceDialog(self.text_edit, self)
        dialog.toggle_replace_btn.setChecked(True)  # 展开替换选项
        dialog._toggle_replace(True)
        dialog.show()  # 使用 show() 而不是 exec() 以允许非模态
    
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
    
    def _on_json_format(self):
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
        # 更新字体（包括字体族和大小）
        font_family = self.config.get('card.font_family', 'Consolas')
        font = QFont(font_family, font_size)
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
