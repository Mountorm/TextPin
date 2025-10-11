"""
自定义规则编辑对话框
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QGroupBox, QFormLayout,
                             QListWidget, QListWidgetItem, QComboBox, QTextEdit,
                             QMessageBox, QCheckBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core import TextProcessor
import uuid


class CustomRuleDialog(QDialog):
    """自定义规则编辑对话框"""
    
    def __init__(self, rule=None, parent=None):
        super().__init__(parent)
        self.rule = rule or self._create_new_rule()
        self.processor = TextProcessor()
        self._init_ui()
        self._load_rule()
    
    def _create_new_rule(self):
        """创建新规则"""
        return {
            'id': f'custom_{uuid.uuid4().hex[:8]}',
            'name': '新建规则',
            'icon': '🧰',
            'shortcut': '',
            'enabled': True,
            'steps': []
        }
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑自定义规则")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("规则名称")
        info_layout.addRow("名称:", self.name_edit)
        
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("🧰")
        self.icon_edit.setMaximumWidth(50)
        icon_layout.addWidget(self.icon_edit)
        
        self.shortcut_edit = QLineEdit()
        self.shortcut_edit.setPlaceholderText("点击设置快捷键")
        self.shortcut_edit.setReadOnly(True)
        self.shortcut_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shortcut_edit.mousePressEvent = lambda e: self._set_shortcut()
        icon_layout.addWidget(QLabel("快捷键:"))
        icon_layout.addWidget(self.shortcut_edit)
        
        clear_shortcut_btn = QPushButton("清除")
        clear_shortcut_btn.setMaximumWidth(60)
        clear_shortcut_btn.clicked.connect(lambda: self.shortcut_edit.setText(""))
        icon_layout.addWidget(clear_shortcut_btn)
        
        icon_layout.addStretch()
        
        info_layout.addRow("图标:", icon_layout)
        
        self.enabled_check = QCheckBox("启用此规则")
        self.enabled_check.setChecked(True)
        info_layout.addRow("", self.enabled_check)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 处理步骤
        steps_group = QGroupBox("处理步骤")
        steps_layout = QVBoxLayout()
        
        # 步骤列表
        self.steps_list = QListWidget()
        self.steps_list.setMinimumHeight(200)
        self.steps_list.currentRowChanged.connect(self._on_step_selected)
        steps_layout.addWidget(self.steps_list)
        
        # 步骤控制按钮
        step_buttons_layout = QHBoxLayout()
        
        self.add_step_btn = QPushButton("+ 添加步骤")
        self.add_step_btn.clicked.connect(self._add_step)
        step_buttons_layout.addWidget(self.add_step_btn)
        
        self.edit_step_btn = QPushButton("✏️ 编辑")
        self.edit_step_btn.clicked.connect(self._edit_step)
        self.edit_step_btn.setEnabled(False)
        step_buttons_layout.addWidget(self.edit_step_btn)
        
        self.move_up_btn = QPushButton("↑ 上移")
        self.move_up_btn.clicked.connect(self._move_step_up)
        self.move_up_btn.setEnabled(False)
        step_buttons_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("↓ 下移")
        self.move_down_btn.clicked.connect(self._move_step_down)
        self.move_down_btn.setEnabled(False)
        step_buttons_layout.addWidget(self.move_down_btn)
        
        self.delete_step_btn = QPushButton("🗑️ 删除")
        self.delete_step_btn.clicked.connect(self._delete_step)
        self.delete_step_btn.setEnabled(False)
        step_buttons_layout.addWidget(self.delete_step_btn)
        
        step_buttons_layout.addStretch()
        steps_layout.addLayout(step_buttons_layout)
        
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)
        
        # 测试区域
        test_group = QGroupBox("测试区域")
        test_layout = QVBoxLayout()
        
        test_input_layout = QHBoxLayout()
        
        # 输入
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("输入文本:"))
        self.test_input = QTextEdit()
        self.test_input.setPlaceholderText("在此输入测试文本...")
        self.test_input.setMaximumHeight(100)
        input_layout.addWidget(self.test_input)
        test_input_layout.addLayout(input_layout)
        
        # 输出
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("处理结果:"))
        self.test_output = QTextEdit()
        self.test_output.setReadOnly(True)
        self.test_output.setMaximumHeight(100)
        output_layout.addWidget(self.test_output)
        test_input_layout.addLayout(output_layout)
        
        test_layout.addLayout(test_input_layout)
        
        test_btn = QPushButton("🧪 测试规则")
        test_btn.clicked.connect(self._test_rule)
        test_layout.addWidget(test_btn)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _load_rule(self):
        """加载规则到界面"""
        self.name_edit.setText(self.rule.get('name', ''))
        self.icon_edit.setText(self.rule.get('icon', '🧰'))
        self.shortcut_edit.setText(self.rule.get('shortcut', ''))
        self.enabled_check.setChecked(self.rule.get('enabled', True))
        
        self._refresh_steps_list()
    
    def _refresh_steps_list(self):
        """刷新步骤列表"""
        self.steps_list.clear()
        
        for i, step in enumerate(self.rule.get('steps', [])):
            step_type = step.get('type', '')
            step_name = self._get_step_display_name(step)
            item = QListWidgetItem(f"{i+1}. {step_name}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.steps_list.addItem(item)
    
    def _get_step_display_name(self, step):
        """获取步骤显示名称"""
        step_types = {s['id']: s for s in TextProcessor.get_step_types()}
        step_type = step.get('type', '')
        
        if step_type in step_types:
            icon = step_types[step_type]['icon']
            name = step_types[step_type]['name']
            
            # 添加参数摘要
            params = step.get('params', {})
            summary = self._get_params_summary(step_type, params)
            
            return f"{icon} {name}" + (f" - {summary}" if summary else "")
        
        return step_type
    
    def _get_params_summary(self, step_type, params):
        """获取参数摘要"""
        if step_type == 'find_replace':
            find = params.get('find', '')
            return f"'{find}'" if len(find) < 20 else f"'{find[:17]}...'"
        elif step_type == 'regex_replace':
            pattern = params.get('pattern', '')
            return f"/{pattern}/" if len(pattern) < 20 else f"/{pattern[:17]}.../"
        elif step_type == 'case_transform':
            mode = params.get('mode', 'upper')
            modes = {'upper': '大写', 'lower': '小写', 'title': '标题', 'capitalize': '首字母大写'}
            return modes.get(mode, mode)
        elif step_type == 'strip_lines':
            mode = params.get('mode', 'both')
            modes = {'left': '行首', 'right': '行尾', 'both': '首尾'}
            return modes.get(mode, mode)
        elif step_type == 'add_prefix':
            prefix = params.get('prefix', '')
            return f"'{prefix}'"
        elif step_type == 'add_suffix':
            suffix = params.get('suffix', '')
            return f"'{suffix}'"
        
        return ""
    
    def _on_step_selected(self, row):
        """步骤选中时"""
        has_selection = row >= 0
        step_count = len(self.rule.get('steps', []))
        
        self.edit_step_btn.setEnabled(has_selection)
        self.delete_step_btn.setEnabled(has_selection)
        self.move_up_btn.setEnabled(has_selection and row > 0)
        self.move_down_btn.setEnabled(has_selection and row < step_count - 1)
    
    def _add_step(self):
        """添加步骤"""
        from .step_edit_dialog import StepEditDialog
        
        dialog = StepEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            step = dialog.get_step()
            self.rule['steps'].append(step)
            self._refresh_steps_list()
    
    def _edit_step(self):
        """编辑步骤"""
        row = self.steps_list.currentRow()
        if row < 0:
            return
        
        from .step_edit_dialog import StepEditDialog
        
        step = self.rule['steps'][row]
        dialog = StepEditDialog(step=step, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.rule['steps'][row] = dialog.get_step()
            self._refresh_steps_list()
    
    def _move_step_up(self):
        """上移步骤"""
        row = self.steps_list.currentRow()
        if row <= 0:
            return
        
        steps = self.rule['steps']
        steps[row], steps[row-1] = steps[row-1], steps[row]
        self._refresh_steps_list()
        self.steps_list.setCurrentRow(row - 1)
    
    def _move_step_down(self):
        """下移步骤"""
        row = self.steps_list.currentRow()
        steps = self.rule['steps']
        if row < 0 or row >= len(steps) - 1:
            return
        
        steps[row], steps[row+1] = steps[row+1], steps[row]
        self._refresh_steps_list()
        self.steps_list.setCurrentRow(row + 1)
    
    def _delete_step(self):
        """删除步骤"""
        row = self.steps_list.currentRow()
        if row < 0:
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个步骤吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.rule['steps'][row]
            self._refresh_steps_list()
    
    def _test_rule(self):
        """测试规则"""
        test_input = self.test_input.toPlainText()
        
        if not test_input:
            QMessageBox.warning(self, "提示", "请输入测试文本")
            return
        
        # 保存当前编辑的规则
        self._save_to_rule()
        
        # 执行处理
        try:
            result = self.processor.process(test_input, self.rule)
            self.test_output.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理失败: {str(e)}")
    
    def _set_shortcut(self):
        """设置快捷键"""
        from .shortcut_capture_dialog import ShortcutCaptureDialog
        
        current_shortcut = self.shortcut_edit.text()
        dialog = ShortcutCaptureDialog(current_shortcut=current_shortcut, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            shortcut = dialog.get_shortcut()
            self.shortcut_edit.setText(shortcut)
    
    def _save_to_rule(self):
        """保存界面数据到规则"""
        self.rule['name'] = self.name_edit.text().strip()
        self.rule['icon'] = self.icon_edit.text().strip() or '🧰'
        self.rule['shortcut'] = self.shortcut_edit.text().strip()
        self.rule['enabled'] = self.enabled_check.isChecked()
    
    def accept(self):
        """确认保存"""
        self._save_to_rule()
        
        # 验证规则
        is_valid, error_msg = self.processor.validate_rule(self.rule)
        if not is_valid:
            QMessageBox.warning(self, "验证失败", error_msg)
            return
        
        super().accept()
    
    def get_rule(self):
        """获取编辑后的规则"""
        return self.rule
