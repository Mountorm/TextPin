"""
TextPin - 文字剪贴板工具
主入口文件
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from core import AppManager


def main():
    """应用程序入口"""
    # 设置高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("TextPin")
    app.setApplicationVersion("2.0.3")
    app.setOrganizationName("TextPin")
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出应用
    
    # 设置样式
    app.setStyle("Fusion")
    
    # 创建应用管理器
    app_manager = AppManager()
    
    # 显示设置窗口
    app_manager.show_settings()
    
    # 清理资源的处理
    app.aboutToQuit.connect(app_manager.cleanup)
    
    print("=" * 50)
    print("TextPin 2.0 已启动")
    print("按 F4 创建贴卡")
    print("=" * 50)
    
    # 运行应用程序事件循环
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
