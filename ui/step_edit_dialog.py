"""
步骤编辑对话框
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QCheckBox,
                             QFormLayout, QGroupBox, QTextEdit)
from PyQt6.QtCore import Qt
from core import TextProcessor


class StepEditDialog(QDialog):
    """步骤编辑对话框"""
    
    def __init__(self, step=None, parent=None):
        super().__init__(parent)
        # 深拷贝以避免修改原始数据
        import copy
        self.step = copy.deepcopy(step) if step else {'type': '', 'params': {}}
        self.param_widgets = {}
        self._init_ui()
        self._load_step()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑步骤")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 步骤类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("步骤类型:"))
        
        self.type_combo = QComboBox()
        step_types = TextProcessor.get_step_types()
        for st in step_types:
            self.type_combo.addItem(f"{st['icon']} {st['name']}", st['id'])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        layout.addLayout(type_layout)
        
        # 参数区域（动态生成）
        self.params_group = QGroupBox("参数设置")
        self.params_layout = QFormLayout()
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _load_step(self):
        """加载步骤数据"""
        print(f"[DEBUG] 加载步骤: type={self.step.get('type')}, params={self.step.get('params')}")
        
        # 临时断开信号连接，避免重复触发
        self.type_combo.currentIndexChanged.disconnect(self._on_type_changed)
        
        if self.step.get('type'):
            # 找到对应的索引
            for i in range(self.type_combo.count()):
                if self.type_combo.itemData(i) == self.step['type']:
                    self.type_combo.setCurrentIndex(i)
                    break
        else:
            # 默认选择第一个
            self.type_combo.setCurrentIndex(0)
        
        # 重新连接信号
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        
        # 手动触发一次类型改变，确保参数控件被创建
        self._on_type_changed(self.type_combo.currentIndex())
    
    def _on_type_changed(self, index):
        """步骤类型改变时"""
        # 清除旧的参数控件
        for i in reversed(range(self.params_layout.count())):
            widget = self.params_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.param_widgets.clear()
        
        # 根据类型创建参数控件
        step_type = self.type_combo.currentData()
        
        if step_type == 'find_replace':
            self._create_find_replace_params()
        elif step_type == 'regex_replace':
            self._create_regex_replace_params()
        elif step_type == 'remove_empty_lines':
            self._create_remove_empty_lines_params()
        elif step_type == 'case_transform':
            self._create_case_transform_params()
        elif step_type == 'strip_lines':
            self._create_strip_lines_params()
        elif step_type == 'add_prefix':
            self._create_add_prefix_params()
        elif step_type == 'add_suffix':
            self._create_add_suffix_params()
    
    def _create_find_replace_params(self):
        """查找替换参数"""
        params = self.step.get('params', {})
        print(f"[DEBUG] 创建查找替换参数控件: find={params.get('find')}, replace={params.get('replace')}")
        
        find_edit = QLineEdit()
        find_edit.setPlaceholderText("要查找的文本")
        find_edit.setText(params.get('find', ''))
        self.param_widgets['find'] = find_edit
        self.params_layout.addRow("查找:", find_edit)
        
        replace_edit = QLineEdit()
        replace_edit.setPlaceholderText("替换为")
        replace_edit.setText(params.get('replace', ''))
        self.param_widgets['replace'] = replace_edit
        self.params_layout.addRow("替换:", replace_edit)
        
        case_check = QCheckBox("区分大小写")
        case_check.setChecked(params.get('case_sensitive', True))
        self.param_widgets['case_sensitive'] = case_check
        self.params_layout.addRow("", case_check)
    
    def _create_regex_replace_params(self):
        """正则替换参数"""
        pattern_edit = QTextEdit()
        pattern_edit.setPlaceholderText("正则表达式，如: \\d+")
        pattern_edit.setMaximumHeight(60)
        pattern_edit.setText(self.step.get('params', {}).get('pattern', ''))
        self.param_widgets['pattern'] = pattern_edit
        self.params_layout.addRow("模式:", pattern_edit)
        
        replacement_edit = QLineEdit()
        replacement_edit.setPlaceholderText("替换内容，可使用 $1, $2 等")
        replacement_edit.setText(self.step.get('params', {}).get('replacement', ''))
        self.param_widgets['replacement'] = replacement_edit
        self.params_layout.addRow("替换:", replacement_edit)
        
        # 标志
        flags = self.step.get('params', {}).get('flags', [])
        
        ignore_case_check = QCheckBox("忽略大小写 (IGNORECASE)")
        ignore_case_check.setChecked('IGNORECASE' in flags or 'I' in flags)
        self.param_widgets['flag_ignorecase'] = ignore_case_check
        self.params_layout.addRow("", ignore_case_check)
        
        multiline_check = QCheckBox("多行模式 (MULTILINE)")
        multiline_check.setChecked('MULTILINE' in flags or 'M' in flags)
        self.param_widgets['flag_multiline'] = multiline_check
        self.params_layout.addRow("", multiline_check)
        
        dotall_check = QCheckBox(". 匹配换行符 (DOTALL)")
        dotall_check.setChecked('DOTALL' in flags or 'S' in flags)
        self.param_widgets['flag_dotall'] = dotall_check
        self.params_layout.addRow("", dotall_check)
        
        # 提示
        hint = QLabel("💡 常用模式:\n"
                     "  数字: \\d+\n"
                     "  邮箱: [\\w.-]+@[\\w.-]+\\.\\w+\n"
                     "  URL: https?://[^\\s]+")
        hint.setStyleSheet("color: #666; font-size: 10px;")
        self.params_layout.addRow("", hint)
    
    def _create_remove_empty_lines_params(self):
        """移除空行参数（无需参数）"""
        hint = QLabel("此操作将移除所有空白行")
        hint.setStyleSheet("color: #666;")
        self.params_layout.addRow("", hint)
    
    def _create_case_transform_params(self):
        """大小写转换参数"""
        mode_combo = QComboBox()
        mode_combo.addItem("全部大写", "upper")
        mode_combo.addItem("全部小写", "lower")
        mode_combo.addItem("标题格式", "title")
        mode_combo.addItem("首字母大写", "capitalize")
        
        current_mode = self.step.get('params', {}).get('mode', 'upper')
        for i in range(mode_combo.count()):
            if mode_combo.itemData(i) == current_mode:
                mode_combo.setCurrentIndex(i)
                break
        
        self.param_widgets['mode'] = mode_combo
        self.params_layout.addRow("模式:", mode_combo)
    
    def _create_strip_lines_params(self):
        """去除空格参数"""
        mode_combo = QComboBox()
        mode_combo.addItem("行首和行尾", "both")
        mode_combo.addItem("仅行首", "left")
        mode_combo.addItem("仅行尾", "right")
        
        current_mode = self.step.get('params', {}).get('mode', 'both')
        for i in range(mode_combo.count()):
            if mode_combo.itemData(i) == current_mode:
                mode_combo.setCurrentIndex(i)
                break
        
        self.param_widgets['mode'] = mode_combo
        self.params_layout.addRow("模式:", mode_combo)
    
    def _create_add_prefix_params(self):
        """添加前缀参数"""
        prefix_edit = QLineEdit()
        prefix_edit.setPlaceholderText("要添加的前缀")
        prefix_edit.setText(self.step.get('params', {}).get('prefix', ''))
        self.param_widgets['prefix'] = prefix_edit
        self.params_layout.addRow("前缀:", prefix_edit)
        
        per_line_check = QCheckBox("每行添加")
        per_line_check.setChecked(self.step.get('params', {}).get('per_line', True))
        self.param_widgets['per_line'] = per_line_check
        self.params_layout.addRow("", per_line_check)
    
    def _create_add_suffix_params(self):
        """添加后缀参数"""
        suffix_edit = QLineEdit()
        suffix_edit.setPlaceholderText("要添加的后缀")
        suffix_edit.setText(self.step.get('params', {}).get('suffix', ''))
        self.param_widgets['suffix'] = suffix_edit
        self.params_layout.addRow("后缀:", suffix_edit)
        
        per_line_check = QCheckBox("每行添加")
        per_line_check.setChecked(self.step.get('params', {}).get('per_line', True))
        self.param_widgets['per_line'] = per_line_check
        self.params_layout.addRow("", per_line_check)
    
    def get_step(self):
        """获取编辑后的步骤"""
        step_type = self.type_combo.currentData()
        params = {}
        
        # 根据控件类型获取值
        for key, widget in self.param_widgets.items():
            if isinstance(widget, QLineEdit):
                params[key] = widget.text()
            elif isinstance(widget, QTextEdit):
                params[key] = widget.toPlainText()
            elif isinstance(widget, QCheckBox):
                if key.startswith('flag_'):
                    # 正则标志
                    continue
                params[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                params[key] = widget.currentData()
        
        # 特殊处理：正则标志
        if step_type == 'regex_replace':
            flags = []
            if self.param_widgets.get('flag_ignorecase', QCheckBox()).isChecked():
                flags.append('IGNORECASE')
            if self.param_widgets.get('flag_multiline', QCheckBox()).isChecked():
                flags.append('MULTILINE')
            if self.param_widgets.get('flag_dotall', QCheckBox()).isChecked():
                flags.append('DOTALL')
            params['flags'] = flags
        
        return {
            'type': step_type,
            'params': params
        }
