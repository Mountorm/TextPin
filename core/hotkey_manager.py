"""
全局快捷键管理器
支持 Windows 平台的全局快捷键注册
"""
import sys
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QWindow

if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    
    # Windows API 常量
    WM_HOTKEY = 0x0312
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008
    MOD_NOREPEAT = 0x4000
    
    # Virtual Key Codes
    VK_F4 = 0x73
    VK_F5 = 0x74


class HotkeyManager(QObject):
    """全局快捷键管理器"""
    
    # 信号
    hotkey_pressed = pyqtSignal(str)  # 快捷键名称
    
    def __init__(self):
        super().__init__()
        self.hotkeys = {}  # {hotkey_id: hotkey_name}
        self.next_id = 1
        self.hidden_window = None
        
        if sys.platform == 'win32':
            self._init_windows()
        else:
            print("警告: 当前平台不支持全局快捷键")
    
    def _init_windows(self):
        """初始化 Windows 平台"""
        # 获取 Windows API 函数
        self.user32 = ctypes.windll.user32
        self.RegisterHotKey = self.user32.RegisterHotKey
        self.UnregisterHotKey = self.user32.UnregisterHotKey
        
        # 设置错误模式以获取详细错误信息
        ctypes.set_last_error(0)
        
        # 创建隐藏窗口用于接收消息
        self.hidden_window = HiddenHotkeyWindow(self)
        print("全局快捷键管理器已初始化")
    
    def register(self, hotkey_name, key_code, modifiers=0):
        """
        注册全局快捷键
        
        Args:
            hotkey_name: 快捷键名称（如 "create_card"）
            key_code: 虚拟键码
            modifiers: 修饰键（MOD_CONTROL, MOD_ALT, MOD_SHIFT, MOD_WIN）
        
        Returns:
            bool: 是否注册成功
        """
        if sys.platform != 'win32' or not self.hidden_window:
            return False
        
        hotkey_id = self.next_id
        self.next_id += 1
        
        # 获取窗口句柄
        winid = self.hidden_window.winId()
        
        # 转换为整数句柄
        if hasattr(winid, '__int__'):
            hwnd = int(winid)
        else:
            # PyQt6 返回的可能是 sip.voidptr
            hwnd = int(ctypes.c_void_p.from_buffer(winid).value) if winid else 0
        
        if hwnd == 0:
            print(f"✗ 无法获取窗口句柄")
            return False
        
        # 添加 MOD_NOREPEAT 防止重复触发
        modifiers |= MOD_NOREPEAT
        
        # 清除上一次的错误
        ctypes.set_last_error(0)
        
        # 注册快捷键
        print(f"正在注册快捷键: HWND=0x{hwnd:X}, ID={hotkey_id}, Modifiers=0x{modifiers:X}, KeyCode=0x{key_code:X}")
        result = self.RegisterHotKey(hwnd, hotkey_id, modifiers, key_code)
        
        if result:
            self.hotkeys[hotkey_id] = hotkey_name
            print(f"✓ 已注册快捷键: {hotkey_name} (ID: {hotkey_id}, HWND: 0x{hwnd:X})")
            return True
        else:
            error = ctypes.get_last_error()
            print(f"✗ 注册快捷键失败: {hotkey_name} (错误代码: {error})")
            
            # 详细错误信息
            if error == 1409:
                print("  原因: 快捷键已被其他程序占用")
            elif error == 5:
                print("  原因: 访问被拒绝，可能需要管理员权限")
            elif error == 0:
                print("  原因: RegisterHotKey 返回失败但没有设置错误代码")
                print("  建议: 尝试以管理员身份运行程序")
            else:
                print(f"  未知错误代码: {error}")
            
            return False
    
    def register_f4(self):
        """注册 F4 快捷键"""
        return self.register("create_card", VK_F4, 0)
    
    def register_from_string(self, hotkey_str):
        """
        从字符串注册快捷键（如 "F4", "Ctrl+Alt+V"）
        
        Args:
            hotkey_str: 快捷键字符串
        
        Returns:
            bool: 是否注册成功
        """
        if sys.platform != 'win32':
            return False
        
        # 解析快捷键字符串
        parts = hotkey_str.upper().split('+')
        
        modifiers = 0
        key = None
        
        for part in parts:
            part = part.strip()
            if part == 'CTRL' or part == 'CONTROL':
                modifiers |= MOD_CONTROL
            elif part == 'ALT':
                modifiers |= MOD_ALT
            elif part == 'SHIFT':
                modifiers |= MOD_SHIFT
            elif part == 'WIN':
                modifiers |= MOD_WIN
            else:
                key = part
        
        if not key:
            return False
        
        # 获取虚拟键码
        key_code = self._get_vk_code(key)
        if key_code is None:
            return False
        
        return self.register("create_card", key_code, modifiers)
    
    def _get_vk_code(self, key):
        """获取虚拟键码"""
        # F 功能键
        if key.startswith('F') and len(key) <= 3:
            try:
                f_num = int(key[1:])
                if 1 <= f_num <= 24:
                    return 0x70 + f_num - 1
            except:
                pass
        
        # 字母键
        if len(key) == 1 and key.isalpha():
            return ord(key)
        
        # 数字键
        if len(key) == 1 and key.isdigit():
            return ord(key)
        
        return None
    
    def unregister_all(self):
        """注销所有快捷键"""
        if sys.platform != 'win32' or not self.hidden_window:
            return
        
        hwnd = int(self.hidden_window.winId())
        
        for hotkey_id in list(self.hotkeys.keys()):
            self.UnregisterHotKey(hwnd, hotkey_id)
            print(f"已注销快捷键 ID: {hotkey_id}")
        
        self.hotkeys.clear()
    
    def _on_hotkey(self, hotkey_id):
        """快捷键触发回调"""
        if hotkey_id in self.hotkeys:
            hotkey_name = self.hotkeys[hotkey_id]
            print(f"快捷键触发: {hotkey_name}")
            self.hotkey_pressed.emit(hotkey_name)
    
    def cleanup(self):
        """清理资源"""
        self.unregister_all()
        if self.hidden_window:
            self.hidden_window.close()


class HiddenHotkeyWindow(QWidget):
    """隐藏窗口用于接收全局快捷键消息"""
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # 设置窗口属性
        self.setWindowTitle("TextPin Hotkey Window")
        
        # 设置为工具窗口，不显示在任务栏
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )
        
        # 设置最小尺寸
        self.setFixedSize(1, 1)
        
        # 移出屏幕
        self.move(-10000, -10000)
        
        # 显示窗口（必须显示才能接收消息，但移出屏幕外）
        self.show()
        
        # 强制处理事件，确保窗口创建完成
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # 获取句柄
        winid = self.winId()
        if hasattr(winid, '__int__'):
            hwnd = int(winid)
        else:
            try:
                hwnd = int(ctypes.c_void_p.from_buffer(winid).value) if winid else 0
            except:
                hwnd = 0
        
        if hwnd:
            print(f"隐藏窗口已创建, HWND: 0x{hwnd:X}")
        else:
            print("隐藏窗口已创建, 但无法获取句柄")
    
    def nativeEvent(self, eventType, message):
        """处理原生 Windows 消息"""
        if sys.platform == 'win32' and eventType == b'windows_generic_MSG':
            import ctypes
            
            # 解析消息
            msg = ctypes.wintypes.MSG.from_address(int(message))
            
            # 检查是否是热键消息
            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                print(f"接收到快捷键消息: ID={hotkey_id}")
                
                # 触发管理器的回调
                self.manager._on_hotkey(hotkey_id)
                
                return True, 0
        
        return False, 0
