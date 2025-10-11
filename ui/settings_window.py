"""
设置窗口 - 应用配置和管理
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QCheckBox, QSpinBox, 
                             QGroupBox, QFormLayout, QLineEdit, QTabWidget,
                             QListWidget, QMessageBox, QSystemTrayIcon, QMenu, QComboBox,
                             QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QIcon, QKeySequence
from core import StorageManager
from utils import ConfigManager
from .hotkey_edit import HotkeyEdit


class SettingsWindow(QMainWindow):
    """设置窗口"""
    
    # 信号
    hotkey_changed = pyqtSignal(str)  # 快捷键改变
    auto_monitor_changed = pyqtSignal(bool)  # 自动监听改变
    ignore_self_changed = pyqtSignal(bool)  # 忽略自身复制改变
    create_card_requested = pyqtSignal()  # 请求创建贴卡
    card_style_changed = pyqtSignal(int, int, float)  # 贴卡样式改变 (width, height, opacity)
    card_appearance_changed = pyqtSignal(int, str, str)  # 贴卡外观改变 (font_size, font_color, bg_color)
    load_to_card_requested = pyqtSignal(str)  # 请求加载内容到贴卡
    menu_config_changed = pyqtSignal()  # 菜单配置改变
    
    def __init__(self, config=None, storage=None):
        super().__init__()
        
        # 管理器（使用传入的实例或创建新的）
        self.config = config if config else ConfigManager()
        self.storage = storage if storage else StorageManager()
        
        self._init_ui()
        self._load_settings()
        self._init_system_tray()
        
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("TextPin - 设置")
        self.setMinimumSize(600, 700)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title_label = QLabel("⚙️ TextPin 设置")
        title_label.setFont(QFont("", 16, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 常规设置
        self.tab_widget.addTab(self._create_general_tab(), "常规")
        
        # 功能设置（替换原快捷键Tab）
        self.tab_widget.addTab(self._create_features_tab(), "功能")
        
        # 历史记录
        self.tab_widget.addTab(self._create_history_tab(), "历史记录")
        
        # 关于
        self.tab_widget.addTab(self._create_about_tab(), "关于")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("应用")
        self.apply_btn.clicked.connect(lambda: self._apply_settings(show_message=True))
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self._ok_clicked)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def _create_general_tab(self):
        """创建常规设置标签"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 剪贴板监听
        clipboard_group = QGroupBox("剪贴板监听")
        clipboard_layout = QVBoxLayout()
        
        self.auto_monitor_check = QCheckBox("自动监听剪贴板")
        self.auto_monitor_check.setToolTip("启动时自动开始监听剪贴板变化")
        clipboard_layout.addWidget(self.auto_monitor_check)
        
        self.ignore_self_check = QCheckBox("忽略自身复制操作")
        self.ignore_self_check.setToolTip("不监听从贴卡窗口中复制的内容")
        self.ignore_self_check.setChecked(True)
        clipboard_layout.addWidget(self.ignore_self_check)
        
        clipboard_group.setLayout(clipboard_layout)
        layout.addWidget(clipboard_group)
        
        # 贴卡设置
        card_group = QGroupBox("贴卡设置")
        card_layout = QFormLayout()
        
        self.card_width_spin = QSpinBox()
        self.card_width_spin.setRange(200, 800)
        self.card_width_spin.setValue(300)
        self.card_width_spin.setSuffix(" px")
        card_layout.addRow("默认宽度:", self.card_width_spin)
        
        # 高度设置（带自动选项）
        height_layout = QHBoxLayout()
        self.card_height_spin = QSpinBox()
        self.card_height_spin.setRange(100, 600)
        self.card_height_spin.setValue(200)
        self.card_height_spin.setSuffix(" px")
        height_layout.addWidget(self.card_height_spin)
        
        self.auto_height_check = QCheckBox("自动")
        self.auto_height_check.setToolTip("根据内容自动调整高度")
        self.auto_height_check.toggled.connect(self._on_auto_height_toggled)
        height_layout.addWidget(self.auto_height_check)
        
        card_layout.addRow("默认高度:", height_layout)
        
        self.card_opacity_spin = QSpinBox()
        self.card_opacity_spin.setRange(50, 100)
        self.card_opacity_spin.setValue(95)
        self.card_opacity_spin.setSuffix(" %")
        card_layout.addRow("透明度:", self.card_opacity_spin)
        
        # 字体选择
        from PyQt6.QtGui import QFontDatabase
        font_layout = QHBoxLayout()
        self.font_family_combo = QComboBox()
        # 获取系统所有字体（PyQt6 使用静态方法）
        fonts = QFontDatabase.families()
        self.font_family_combo.addItems(fonts)
        self.font_family_combo.setCurrentText("Consolas")
        font_layout.addWidget(self.font_family_combo)
        card_layout.addRow("字体:", font_layout)
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(" pt")
        card_layout.addRow("字体大小:", self.font_size_spin)
        
        # 文字颜色
        font_color_layout = QHBoxLayout()
        self.font_color_input = QLineEdit()
        self.font_color_input.setText("#000000")
        self.font_color_input.setMaxLength(7)
        font_color_layout.addWidget(self.font_color_input)
        
        self.font_color_btn = QPushButton("选择颜色")
        self.font_color_btn.clicked.connect(self._choose_font_color)
        font_color_layout.addWidget(self.font_color_btn)
        card_layout.addRow("文字颜色:", font_color_layout)
        
        # 背景颜色
        bg_color_layout = QHBoxLayout()
        self.bg_color_input = QLineEdit()
        self.bg_color_input.setText("#FFFFFF")
        self.bg_color_input.setMaxLength(7)
        bg_color_layout.addWidget(self.bg_color_input)
        
        self.bg_color_btn = QPushButton("选择颜色")
        self.bg_color_btn.clicked.connect(self._choose_bg_color)
        bg_color_layout.addWidget(self.bg_color_btn)
        card_layout.addRow("背景颜色:", bg_color_layout)
        
        
        card_group.setLayout(card_layout)
        layout.addWidget(card_group)
        
        # 历史记录
        history_group = QGroupBox("历史记录")
        history_layout = QFormLayout()
        
        self.max_history_spin = QSpinBox()
        self.max_history_spin.setRange(10, 500)
        self.max_history_spin.setValue(50)
        self.max_history_spin.setSuffix(" 条")
        history_layout.addRow("最大保存数量:", self.max_history_spin)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        return widget
    
    def _create_features_tab(self):
        """创建功能设置标签"""
        from .card_window import CardWindow
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_label = QLabel("配置贴卡右键菜单中显示的功能和快捷键")
        info_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 全局快捷键
        global_hotkey_group = QGroupBox("全局快捷键")
        global_hotkey_layout = QHBoxLayout()
        
        global_hotkey_layout.addWidget(QLabel("创建贴卡:"))
        
        self.global_hotkey_edit = QLineEdit()
        self.global_hotkey_edit.setText("F4")
        self.global_hotkey_edit.setPlaceholderText("点击设置")
        self.global_hotkey_edit.setReadOnly(True)
        self.global_hotkey_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.global_hotkey_edit.mousePressEvent = lambda e: self._set_global_hotkey()
        global_hotkey_layout.addWidget(self.global_hotkey_edit)
        
        clear_global_btn = QPushButton("清除")
        clear_global_btn.setMaximumWidth(60)
        clear_global_btn.clicked.connect(lambda: self.global_hotkey_edit.setText(""))
        global_hotkey_layout.addWidget(clear_global_btn)
        
        global_hotkey_layout.addStretch()
        
        global_hotkey_group.setLayout(global_hotkey_layout)
        layout.addWidget(global_hotkey_group)
        
        # 功能列表
        features_group = QGroupBox("右键菜单功能")
        features_layout = QVBoxLayout()
        
        # 创建滚动区域
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 存储功能控件的字典
        self.feature_checkboxes = {}
        self.feature_shortcuts = {}
        
        # 为每个功能创建控件
        for feature_id, name, icon, default_shortcut, method_name, tooltip in CardWindow.MENU_FEATURES:
            # 跳过分隔符
            if feature_id.startswith('separator'):
                continue
            
            # 创建水平布局
            feature_layout = QHBoxLayout()
            
            # 启用复选框
            checkbox = QCheckBox(f"{icon} {name}")
            checkbox.setChecked(True)  # 默认启用
            checkbox.setToolTip(tooltip)
            self.feature_checkboxes[feature_id] = checkbox
            feature_layout.addWidget(checkbox, 2)
            
            # 快捷键输入
            shortcut_edit = QLineEdit()
            shortcut_edit.setText(default_shortcut)
            shortcut_edit.setPlaceholderText("点击设置")
            shortcut_edit.setReadOnly(True)
            shortcut_edit.setMaximumWidth(150)
            shortcut_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            shortcut_edit.mousePressEvent = lambda e, fid=feature_id: self._set_feature_shortcut(fid)
            self.feature_shortcuts[feature_id] = shortcut_edit
            feature_layout.addWidget(shortcut_edit, 1)
            
            scroll_layout.addLayout(feature_layout)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        features_layout.addWidget(scroll_area)
        
        # 快捷键格式说明
        hint_label = QLabel(
            "💡 快捷键格式示例：Ctrl+S, Alt+X, Shift+F, F1-F12, Ctrl+Shift+A\n"
            "留空表示不设置快捷键，只在右键菜单中显示"
        )
        hint_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px; background: #f0f0f0; border-radius: 3px;")
        hint_label.setWordWrap(True)
        features_layout.addWidget(hint_label)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # 自定义规则
        custom_rules_group = QGroupBox("自定义规则")
        custom_rules_layout = QVBoxLayout()
        
        # 规则列表
        self.custom_rules_list = QListWidget()
        self.custom_rules_list.setMaximumHeight(150)
        custom_rules_layout.addWidget(self.custom_rules_list)
        
        # 按钮
        custom_buttons_layout = QHBoxLayout()
        
        add_rule_btn = QPushButton("+ 新建规则")
        add_rule_btn.clicked.connect(self._add_custom_rule)
        custom_buttons_layout.addWidget(add_rule_btn)
        
        edit_rule_btn = QPushButton("✏️ 编辑")
        edit_rule_btn.clicked.connect(self._edit_custom_rule)
        custom_buttons_layout.addWidget(edit_rule_btn)
        
        delete_rule_btn = QPushButton("🗑️ 删除")
        delete_rule_btn.clicked.connect(self._delete_custom_rule)
        custom_buttons_layout.addWidget(delete_rule_btn)
        
        custom_buttons_layout.addStretch()
        custom_rules_layout.addLayout(custom_buttons_layout)
        
        custom_rules_group.setLayout(custom_rules_layout)
        layout.addWidget(custom_rules_group)
        
        layout.addStretch()
        return widget
    
    def _create_history_tab(self):
        """创建历史记录标签"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 历史列表
        self.history_list = QListWidget()
        self._load_history()
        layout.addWidget(self.history_list)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.load_history_btn = QPushButton("加载到贴卡")
        self.load_history_btn.clicked.connect(self._load_history_to_card)
        
        self.delete_history_btn = QPushButton("删除")
        self.delete_history_btn.clicked.connect(self._delete_history)
        
        self.clear_history_btn = QPushButton("清空全部")
        self.clear_history_btn.clicked.connect(self._clear_history)
        
        button_layout.addWidget(self.load_history_btn)
        button_layout.addWidget(self.delete_history_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_history_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_about_tab(self):
        """创建关于标签"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 应用图标/名称
        title_label = QLabel("📋 TextPin")
        title_label.setFont(QFont("", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 版本
        version_label = QLabel("版本 2.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 描述
        desc_label = QLabel(
            "轻量级桌面贴卡工具\n"
            "支持剪贴板监听、卡片贴图、历史记录管理\n\n"
            "技术栈: Python + PyQt6"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #666; margin: 20px;")
        layout.addWidget(desc_label)
        
        # 版权
        copyright_label = QLabel("© 2025 TextPin")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #999; margin-top: 20px;")
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        return widget
    
    def _init_system_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 创建简单的图标（使用系统图标）
        from PyQt6.QtWidgets import QStyle
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.tray_icon.setIcon(icon)
        
        # 设置提示文字
        self.tray_icon.setToolTip("TextPin 2.0 - 文字贴卡工具")
        
        # 托盘菜单
        tray_menu = QMenu()
        
        # 显示设置
        show_action = QAction("⚙️ 显示设置", self)
        show_action.triggered.connect(self._show_settings)
        tray_menu.addAction(show_action)
        
        # 创建贴卡
        create_card_action = QAction("📋 创建贴卡 (F4)", self)
        create_card_action.triggered.connect(self._create_card_from_tray)
        tray_menu.addAction(create_card_action)
        
        tray_menu.addSeparator()
        
        # 关于
        about_action = QAction("ℹ️ 关于", self)
        about_action.triggered.connect(self._on_about)
        tray_menu.addAction(about_action)
        
        tray_menu.addSeparator()
        
        # 退出
        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        # 显示托盘消息
        self.tray_icon.showMessage(
            "TextPin 2.0",
            "程序已启动，按 F4 创建贴卡",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def _tray_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_settings()
    
    def _show_settings(self):
        """显示设置窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def _create_card_from_tray(self):
        """从托盘创建贴卡"""
        print("从托盘创建贴卡")
        self.create_card_requested.emit()
    
    def _on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于 TextPin",
            "<h2>📋 TextPin 2.0</h2>"
            "<p>版本 2.0.0</p>"
            "<p>轻量级桌面贴卡工具</p>"
            "<p>支持剪贴板监听、卡片贴图、历史记录管理</p>"
            "<br>"
            "<p>技术栈: Python + PyQt6</p>"
            "<p>© 2025 TextPin</p>"
        )
    
    def _choose_font_color(self):
        """选择文字颜色"""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        current_color = QColor(self.font_color_input.text())
        color = QColorDialog.getColor(current_color, self, "选择文字颜色")
        
        if color.isValid():
            self.font_color_input.setText(color.name())
    
    def _choose_bg_color(self):
        """选择背景颜色"""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        current_color = QColor(self.bg_color_input.text())
        color = QColorDialog.getColor(current_color, self, "选择背景颜色")
        
        if color.isValid():
            self.bg_color_input.setText(color.name())
    
    def _on_auto_height_toggled(self, checked):
        """自动高度选项切换"""
        self.card_height_spin.setEnabled(not checked)
    
    def _load_settings(self):
        """加载设置"""
        # 常规设置
        self.auto_monitor_check.setChecked(
            self.config.get('clipboard.auto_monitor', True)
        )
        self.ignore_self_check.setChecked(
            self.config.get('clipboard.ignore_self', True)
        )
        
        # 贴卡设置
        self.card_width_spin.setValue(
            self.config.get('card.default_width', 300)
        )
        self.card_height_spin.setValue(
            self.config.get('card.default_height', 200)
        )
        auto_height = self.config.get('card.auto_height', False)
        self.auto_height_check.setChecked(auto_height)
        self.card_height_spin.setEnabled(not auto_height)
        
        self.card_opacity_spin.setValue(
            int(self.config.get('card.opacity', 0.95) * 100)
        )
        # 字体
        font_family = self.config.get('card.font_family', 'Consolas')
        index = self.font_family_combo.findText(font_family)
        if index >= 0:
            self.font_family_combo.setCurrentIndex(index)
        
        self.font_size_spin.setValue(
            self.config.get('card.font_size', 10)
        )
        self.font_color_input.setText(
            self.config.get('card.font_color', '#000000')
        )
        self.bg_color_input.setText(
            self.config.get('card.bg_color', '#FFFFFF')
        )
        
        # 历史记录
        self.max_history_spin.setValue(
            self.config.get('clipboard.max_history', 50)
        )
        
        # 快捷键
        self.global_hotkey_edit.setText(
            self.config.get('hotkey.create_card', 'F4')
        )
        
        # 功能配置
        enabled_features = self.config.get('menu.enabled_features', None)
        shortcuts = self.config.get('menu.shortcuts', {})
        
        # 加载功能启用状态
        if enabled_features is not None:
            for feature_id, checkbox in self.feature_checkboxes.items():
                checkbox.setChecked(feature_id in enabled_features)
        
        # 加载快捷键
        for feature_id, shortcut_edit in self.feature_shortcuts.items():
            if feature_id in shortcuts:
                shortcut_edit.setText(shortcuts[feature_id])
        
        # 加载自定义规则
        self._load_custom_rules()
        
        # 窗口位置
        width = self.config.get('settings_window.width', 600)
        height = self.config.get('settings_window.height', 500)
        
        # 检查是否有保存的位置
        x = self.config.get('settings_window.x', None)
        y = self.config.get('settings_window.y', None)
        
        if x is not None and y is not None:
            # 使用保存的位置
            self.setGeometry(x, y, width, height)
        else:
            # 首次打开，居中显示
            self.resize(width, height)
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - width) // 2
            y = (screen.height() - height) // 2
            self.move(x, y)
    
    def _apply_settings(self, show_message=True):
        """应用设置 - 立即生效"""
        # 获取旧值
        old_auto_monitor = self.config.get('clipboard.auto_monitor', True)
        old_ignore_self = self.config.get('clipboard.ignore_self', True)
        old_hotkey = self.config.get('hotkey.create_card', 'F4')
        old_width = self.config.get('card.default_width', 300)
        old_height = self.config.get('card.default_height', 200)
        old_opacity = self.config.get('card.opacity', 0.95)
        
        # 保存常规设置
        new_auto_monitor = self.auto_monitor_check.isChecked()
        new_ignore_self = self.ignore_self_check.isChecked()
        
        self.config.set('clipboard.auto_monitor', new_auto_monitor)
        self.config.set('clipboard.ignore_self', new_ignore_self)
        
        # 保存贴卡设置
        new_width = self.card_width_spin.value()
        new_height = self.card_height_spin.value()
        new_opacity = self.card_opacity_spin.value() / 100.0
        new_font_size = self.font_size_spin.value()
        new_font_color = self.font_color_input.text()
        new_bg_color = self.bg_color_input.text()
        
        old_font_size = self.config.get('card.font_size', 10)
        old_font_color = self.config.get('card.font_color', '#000000')
        old_bg_color = self.config.get('card.bg_color', '#FFFFFF')
        
        new_font_family = self.font_family_combo.currentText()
        
        self.config.set('card.default_width', new_width)
        self.config.set('card.default_height', new_height)
        auto_height_value = self.auto_height_check.isChecked()
        self.config.set('card.auto_height', auto_height_value)
        print(f"✓ 保存配置: card.auto_height = {auto_height_value}")
        self.config.set('card.opacity', new_opacity)
        self.config.set('card.font_family', new_font_family)
        self.config.set('card.font_size', new_font_size)
        self.config.set('card.font_color', new_font_color)
        self.config.set('card.bg_color', new_bg_color)
        
        # 保存历史记录设置
        self.config.set('clipboard.max_history', self.max_history_spin.value())
        
        # 保存快捷键
        new_hotkey = self.global_hotkey_edit.text().strip()
        if new_hotkey:
            self.config.set('hotkey.create_card', new_hotkey)
        
        # 保存功能配置
        enabled_features = []
        shortcuts = {}
        
        for feature_id, checkbox in self.feature_checkboxes.items():
            if checkbox.isChecked():
                enabled_features.append(feature_id)
        
        for feature_id, shortcut_edit in self.feature_shortcuts.items():
            shortcut = shortcut_edit.text().strip()
            if shortcut:
                shortcuts[feature_id] = shortcut
        
        self.config.set('menu.enabled_features', enabled_features)
        self.config.set('menu.shortcuts', shortcuts)
        
        # 发出菜单配置改变信号
        self.menu_config_changed.emit()
        
        # 只在设置真正改变时才发出信号
        if new_auto_monitor != old_auto_monitor:
            self.auto_monitor_changed.emit(new_auto_monitor)
        
        if new_ignore_self != old_ignore_self:
            self.ignore_self_changed.emit(new_ignore_self)
        
        if new_hotkey and new_hotkey != old_hotkey:
            self.hotkey_changed.emit(new_hotkey)
        
        # 贴卡样式改变 - 应用到所有现有贴卡
        if (new_width != old_width or new_height != old_height or new_opacity != old_opacity):
            self.card_style_changed.emit(new_width, new_height, new_opacity)
        
        # 贴卡外观改变 - 应用到所有现有贴卡
        old_font_family = self.config.get('card.font_family', 'Consolas')
        if (new_font_size != old_font_size or new_font_color != old_font_color or 
            new_bg_color != old_bg_color or new_font_family != old_font_family):
            self.card_appearance_changed.emit(new_font_size, new_font_color, new_bg_color)
        
        # 只在需要时显示提示
        if show_message:
            QMessageBox.information(self, "设置", "应用成功！")
    
    def _ok_clicked(self):
        """确定按钮"""
        self._apply_settings(show_message=False)  # 确定按钮不显示提示
        self.hide()
    
    def _load_history(self):
        """加载历史记录"""
        self.history_list.clear()
        records = self.storage.get_history(50)
        
        for record in records:
            preview = record['content'][:100]
            if len(record['content']) > 100:
                preview += "..."
            self.history_list.addItem(preview)
            # 存储完整记录ID
            item = self.history_list.item(self.history_list.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, record['id'])
    
    def refresh_history(self):
        """刷新历史记录（实时更新）"""
        # 保存当前选中项
        current_row = self.history_list.currentRow()
        
        # 重新加载历史
        self._load_history()
        
        # 恢复选中（如果还有效）
        if current_row >= 0 and current_row < self.history_list.count():
            self.history_list.setCurrentRow(current_row)
    
    def _load_history_to_card(self):
        """加载历史到贴卡"""
        current_item = self.history_list.currentItem()
        if current_item:
            history_id = current_item.data(Qt.ItemDataRole.UserRole)
            record = self.storage.get_history_by_id(history_id)
            if record:
                # 发送信号，让主应用创建贴卡
                self.load_to_card_requested.emit(record['content'])
                QMessageBox.information(self, "提示", "已加载到新贴卡")
    
    def _delete_history(self):
        """删除历史记录"""
        current_item = self.history_list.currentItem()
        if current_item:
            history_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.storage.delete_history(history_id)
            self._load_history()
    
    def _clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有历史记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.clear_history(keep_favorites=False)
            self._load_history()
    
    def _quit_app(self):
        """退出应用"""
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
    
    def _load_custom_rules(self):
        """加载自定义规则列表"""
        self.custom_rules_list.clear()
        
        # 断开信号，避免加载时触发
        try:
            self.custom_rules_list.itemChanged.disconnect(self._on_rule_check_changed)
        except:
            pass
        
        custom_rules = self.config.get('custom_rules', [])
        for rule in custom_rules:
            icon = rule.get('icon', '🧰')
            name = rule.get('name', '未命名')
            enabled = rule.get('enabled', True)
            shortcut = rule.get('shortcut', '')
            
            item_text = f"{icon} {name}"
            if shortcut:
                item_text += f"  ({shortcut})"
            
            from PyQt6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, rule)
            self.custom_rules_list.addItem(item)
        
        # 重新连接信号
        self.custom_rules_list.itemChanged.connect(self._on_rule_check_changed)
    
    def _on_rule_check_changed(self, item):
        """规则复选框状态改变"""
        rule = item.data(Qt.ItemDataRole.UserRole)
        rule['enabled'] = (item.checkState() == Qt.CheckState.Checked)
        
        # 更新配置
        custom_rules = self.config.get('custom_rules', [])
        for i, r in enumerate(custom_rules):
            if r.get('id') == rule['id']:
                custom_rules[i] = rule
                break
        
        self.config.set('custom_rules', custom_rules)
        
        # 通知所有贴卡重新加载配置
        self.menu_config_changed.emit()
        
        rule_name = rule.get('name', '未命名')
        status = "已启用" if rule['enabled'] else "已禁用"
        print(f"✓ 规则 '{rule_name}' {status}")
    
    def _set_global_hotkey(self):
        """设置全局快捷键"""
        from .shortcut_capture_dialog import ShortcutCaptureDialog
        
        current_shortcut = self.global_hotkey_edit.text()
        dialog = ShortcutCaptureDialog(current_shortcut=current_shortcut, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            shortcut = dialog.get_shortcut()
            self.global_hotkey_edit.setText(shortcut)
    
    def _set_feature_shortcut(self, feature_id):
        """设置功能快捷键"""
        from .shortcut_capture_dialog import ShortcutCaptureDialog
        
        shortcut_edit = self.feature_shortcuts.get(feature_id)
        if not shortcut_edit:
            return
        
        current_shortcut = shortcut_edit.text()
        dialog = ShortcutCaptureDialog(current_shortcut=current_shortcut, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            shortcut = dialog.get_shortcut()
            shortcut_edit.setText(shortcut)
    
    def _add_custom_rule(self):
        """新建自定义规则"""
        from .custom_rule_dialog import CustomRuleDialog
        
        dialog = CustomRuleDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            
            # 保存到配置
            custom_rules = self.config.get('custom_rules', [])
            custom_rules.append(rule)
            self.config.set('custom_rules', custom_rules)
            
            # 刷新列表
            self._load_custom_rules()
            
            QMessageBox.information(self, "成功", f"规则 '{rule['name']}' 已创建")
    
    def _edit_custom_rule(self):
        """编辑自定义规则"""
        current_item = self.custom_rules_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择一个规则")
            return
        
        from .custom_rule_dialog import CustomRuleDialog
        
        rule = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = CustomRuleDialog(rule=rule, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_rule = dialog.get_rule()
            
            # 更新配置
            custom_rules = self.config.get('custom_rules', [])
            for i, r in enumerate(custom_rules):
                if r.get('id') == updated_rule['id']:
                    custom_rules[i] = updated_rule
                    break
            
            self.config.set('custom_rules', custom_rules)
            
            # 刷新列表
            self._load_custom_rules()
            
            QMessageBox.information(self, "成功", f"规则 '{updated_rule['name']}' 已更新")
    
    def _delete_custom_rule(self):
        """删除自定义规则"""
        current_item = self.custom_rules_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择一个规则")
            return
        
        rule = current_item.data(Qt.ItemDataRole.UserRole)
        rule_name = rule.get('name', '未命名')
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除规则 '{rule_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 从配置中删除
            custom_rules = self.config.get('custom_rules', [])
            custom_rules = [r for r in custom_rules if r.get('id') != rule['id']]
            self.config.set('custom_rules', custom_rules)
            
            # 刷新列表
            self._load_custom_rules()
            
            QMessageBox.information(self, "成功", f"规则 '{rule_name}' 已删除")
    
    def closeEvent(self, event):
        """关闭事件 - 最小化到托盘"""
        event.ignore()
        self.hide()
        
        # 保存窗口位置
        self.config.set('settings_window.x', self.x())
        self.config.set('settings_window.y', self.y())
        self.config.set('settings_window.width', self.width())
        self.config.set('settings_window.height', self.height())
