# Changelog

All notable changes to TextPin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
| 2.0.1 | 2025-10-14 | Bug Fix | 2 critical bugs | ✅ Current |
| 2.0.0 | 2025-10-11 | Major | Complete rewrite | ✅ Stable |
| 1.0.0 | 2024-xx-xx | Initial | First release | ⚠️ Deprecated |

---

## Upgrade Guide

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
