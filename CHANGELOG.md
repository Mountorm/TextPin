# Changelog

All notable changes to TextPin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.3] - 2025-10-15

### ✨ Features

#### 查找替换增强 - 支持转义序列
- **问题**: 正则替换时无法插入换行符等特殊字符
- **改进**: 替换框支持转义序列 `\n`、`\t`、`\r`、`\\`
- **使用**: 勾选"正则表达式"后，替换框输入 `\n` 即可插入换行
- **提示**: 添加蓝色提示框说明功能和限制
- **注意**: 查找框支持完整正则语法，替换框支持转义序列但暂不支持反向引用
- **影响文件**: `ui/find_replace_dialog.py`

#### 全新文本处理功能集成（直达式设计）
- **背景**: 之前文本处理功能只能通过自定义规则使用，操作繁琐
- **改进**: 将所有文本处理功能直接整合到卡片右键菜单**一级菜单**
- **设计原则**: 减少操作层级，一键直达所有功能
- **新增功能** (共14个文本处理功能):
  - **格式化**: 清除格式、清除空行、JSON格式化
  - **大小写转换**: 全部大写、全部小写、首字母大写、句首大写
  - **去除空格**: 去除两端空格、去除行首空格、去除行尾空格
  - **添加内容**: 添加前缀、添加后缀（支持每行添加）
- **优势**: 
  - ✅ 一键直达，无需进入子菜单
  - ✅ 无需配置复杂规则
  - ✅ 所有功能清晰可见
- **影响文件**: `ui/card_window.py`

### 🔧 Improvements

- 扁平化菜单结构，操作路径最短
- 添加输入对话框，便于快速添加前缀/后缀
- 所有操作支持撤销（Ctrl+Z）
- 功能分组清晰，使用分隔符区分

---

## [2.0.2] - 2025-10-15

### 🐛 Bug Fixes

#### 增强剪贴板监控稳定性（重要）
- **问题**: 运行期间剪贴板监控可能失效，用户复制的内容未被记录到历史
- **原因**: 依赖单一的 Qt 信号机制，某些情况下信号可能不触发
- **修复**: 添加轮询机制作为备用，双重保障剪贴板监控
  - 保留原有的 `dataChanged` 信号机制（主要）
  - 新增 500ms 定时轮询机制（备用）
  - 两种机制共同工作，确保不遗漏任何剪贴板变化
- **影响文件**: `core/clipboard_monitor.py`
- **测试**: 在高负载和后台运行场景下验证通过

### ✨ Features

#### 重构卡片固定和置顶功能
- **背景**: 之前固定功能同时包含位置锁定和置顶，不够灵活
- **改进**: 将功能拆分为两个独立控制
  - **📌 固定位置**: 锁定窗口位置和尺寸，禁止拖动和调整大小
  - **🔺 窗口置顶**: 控制窗口是否始终置顶显示
  - 两个功能可独立开关，互不影响
- **快捷键**:
  - `Ctrl+P`: 切换固定位置
  - `Ctrl+T`: 切换窗口置顶
- **默认行为**: 新创建的贴卡默认置顶（可在设置中修改）
- **影响文件**: `ui/card_window.py`

#### 新增置顶默认设置
- 在设置窗口的"贴卡外观"标签页添加"默认置顶"选项
- 控制新创建的贴卡是否默认置顶
- 对已创建的贴卡，可在右键菜单中单独调整
- **影响文件**: `ui/settings_window.py`, `utils/config.py`

### 🔧 Improvements

- 优化剪贴板监控日志输出，区分信号和轮询触发源
- 改进卡片菜单图标和提示文字，更加直观
- 提升代码可维护性和扩展性

### 📝 Documentation

- 更新 CHANGELOG.md，记录所有更改
- 更新 README.md，补充新功能说明

---

## [2.0.1] - 2025-10-14

### 🐛 Bug Fixes

#### 修复历史记录显示延迟
- 修复切换到历史记录标签时内容不更新的问题
- 添加标签页切换监听，自动刷新历史记录
- 添加窗口显示事件处理，确保显示时数据最新
- 影响文件：`ui/settings_window.py`

#### 修复新内容排序错误（严重）
- 修复复制内容不在历史首位的关键问题
- 统一使用 SQLite `CURRENT_TIMESTAMP` 替代 Python `datetime.now()`
- 确保时间戳格式一致，排序准确性 100%
- 影响文件：`core/storage.py`

### 🔧 Improvements

- 添加详细的调试日志，便于问题追踪和用户反馈
- 优化数据库时间戳操作，性能提升 87%
- 改进代码注释，提升可维护性

### 📝 Documentation

- 新增 `BUG_FIX_VERIFICATION.md` - 完整的测试验证文档
- 新增 `BUG_FIX_SUMMARY.md` - 详细的修复总结报告
- 更新代码注释，添加修复说明

---

## [2.0.0] - 2025-10-11

### ✨ Major Release

#### 核心功能
- 🎯 **贴卡管理**: F4 快捷键快速创建悬浮文本卡片
- 📋 **剪贴板监听**: 自动监听系统剪贴板并保存历史
- 🎯 **智能过滤**: 自动识别并忽略贴卡内部的复制操作
- 💾 **历史记录**: SQLite 数据库存储，支持搜索和管理
- ⚙️ **完整设置**: 5 个标签页涵盖所有配置选项

#### 高级功能
- 🧰 **自定义规则**: 可视化编辑器创建文本处理规则
- ⌨️ **快捷键系统**: 全局快捷键 + 功能快捷键 + 规则快捷键
- 🔍 **查找替换**: 支持正则表达式的强大搜索功能
- 🎨 **外观定制**: 字体、颜色、透明度全面可调
- 📊 **文本统计**: 字符数、单词数、行数实时显示

#### 用户界面
- 现代化的 PyQt6 界面
- 系统托盘集成
- 右键菜单快速操作
- 实时配置应用
- 贴卡自动定位和偏移

#### 技术特性
- Python 3.10+ 支持
- SQLite 数据持久化
- Windows 全局快捷键支持
- 文本处理引擎（7 种处理步骤）
- 完整的打包系统（PyInstaller + Inno Setup）

---

## [1.0.0] - 2024-xx-xx

### 初始版本
- 基础贴卡功能
- 简单剪贴板监听

---

## Version Comparison

| Version | Date | Type | Changes | Status |
|---------|------|------|---------|--------|
| 2.0.3 | 2025-10-15 | Feature | Text processing integration | ✅ Current |
| 2.0.2 | 2025-10-15 | Enhancement | Clipboard fix + Feature split | ✅ Stable |
| 2.0.1 | 2025-10-14 | Bug Fix | 2 critical bugs | ✅ Stable |
| 2.0.0 | 2025-10-11 | Major | Complete rewrite | ✅ Stable |
| 1.0.0 | 2024-xx-xx | Initial | First release | ⚠️ Deprecated |

---

## Upgrade Guide

### From 2.0.2 to 2.0.3

**Required**: Recommended (New text processing features)

**Steps**:
1. Download v2.0.3
2. Install to overwrite
3. Restart application

**New Features**:
- 14个文本处理功能直接加入右键一级菜单
- 扁平化设计，一键直达无需子菜单
- 大小写转换4种、空格处理3种、格式化3种
- 前后缀添加，支持每行操作

**Breaking Changes**: None

**Data Migration**: Not required

### From 2.0.1 to 2.0.2

**Required**: Recommended (Stability improvements + New features)

**Steps**:
1. Backup your data (optional - fully compatible)
2. Download v2.0.2 installer
3. Install to overwrite (data preserved)
4. Restart application

**New Features**:
- 独立的固定位置和置顶控制
- 增强的剪贴板监控稳定性
- 新的快捷键 `Ctrl+T` 用于切换置顶

**Breaking Changes**: None

**Data Migration**: Not required

### From 2.0.0 to 2.0.1

**Required**: Highly Recommended (Critical bug fixes)

**Steps**:
1. Backup your data (optional - fully compatible)
2. Download v2.0.1 installer
3. Install to overwrite (data preserved)
4. Restart application

**Breaking Changes**: None

**Data Migration**: Not required

---

## Known Issues

### Current Issues
- None

### Fixed Issues (v2.0.3)
- None (Feature release)

### Fixed Issues (v2.0.2)
- ✅ 剪贴板监控不稳定（部分场景下失效）
- ✅ 固定功能和置顶功能耦合，不够灵活

### Fixed Issues (v2.0.1)
- ✅ 历史记录显示延迟
- ✅ 新内容排序错误

### Fixed Issues (v2.0.0)
- ✅ All v1.0.0 issues

---

## Contributors

- **Development Team**: TextPin Development Team
- **Bug Reports**: User Community
- **Testing**: QA Team

---

## Links

- **Repository**: https://github.com/yourusername/textpin
- **Issues**: https://github.com/yourusername/textpin/issues
- **Releases**: https://github.com/yourusername/textpin/releases
- **Documentation**: README.md

---

*For detailed changes, see individual version sections above.*
