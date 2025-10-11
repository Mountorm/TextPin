"""
TextPin 自动化打包脚本
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# 配置信息
APP_NAME = "TextPin"
APP_VERSION = "2.0.0"
AUTHOR = "TextPin Team"
DESCRIPTION = "桌面便签工具 - 轻量、高效、美观"

# 路径配置
ROOT_DIR = Path(__file__).parent
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"
ICON_FILE = ROOT_DIR / "resources" / "icon.ico"

# PyInstaller 配置模板
SPEC_TEMPLATE = """# -*- mode: python ; coding: utf-8 -*-
# TextPin PyInstaller 配置文件 - 自动生成
# 版本: {version}

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'pyperclip',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon}',
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{app_name}',
)
"""

# Inno Setup 配置模板
INNO_SETUP_TEMPLATE = """
; TextPin 安装程序脚本
; 使用 Inno Setup 编译

#define MyAppName "{app_name}"
#define MyAppVersion "{version}"
#define MyAppPublisher "{author}"
#define MyAppURL "https://github.com/yourusername/textpin"
#define MyAppExeName "{app_name}.exe"

[Setup]
; 应用信息
AppId={{A1B2C3D4-E5F6-4321-9876-ABCDEF123456}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README_INSTALL.txt
OutputDir=installer
OutputBaseFilename={app_name}_Setup_v{version}
SetupIconFile=resources\\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; 自定义安装路径
DisableDirPage=no
UsePreviousAppDir=yes

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "dist\\{{#MyAppName}}\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "dist\\{{#MyAppName}}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DataDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  // 创建数据目录选择页面
  DataDirPage := CreateInputDirPage(wpSelectDir,
    '选择数据存储位置', '请选择 TextPin 数据文件的存储位置',
    '配置文件和数据库将保存在此目录中。' + #13#10#13#10 +
    '默认位置：%APPDATA%\\TextPin' + #13#10 +
    '您也可以选择其他位置（如移动硬盘）以便数据同步。',
    False, '');
  
  // 设置默认数据目录
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{{userappdata}}\\TextPin');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DataPathFile: String;
begin
  if CurStep = ssPostInstall then
  begin
    // 保存数据目录配置
    DataPathFile := ExpandConstant('{{app}}') + '\\data_path.txt';
    SaveStringToFile(DataPathFile, DataDirPage.Values[0], False);
    
    // 创建数据目录
    ForceDirectories(DataDirPage.Values[0]);
  end;
end;

[UninstallDelete]
Type: files; Name: "{{app}}\\data_path.txt"
"""

def print_step(step, message):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step}: {message}")
    print('='*60)

def check_requirements():
    """检查打包所需的工具"""
    print_step(1, "检查环境")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("  安装命令: pip install pyinstaller")
        return False
    
    # 检查图标文件
    if not ICON_FILE.exists():
        print(f"⚠ 图标文件不存在: {ICON_FILE}")
        print("  将使用默认图标")
    else:
        print(f"✓ 图标文件存在: {ICON_FILE}")
    
    return True

def create_icon():
    """创建默认图标（如果不存在）"""
    resources_dir = ROOT_DIR / "resources"
    resources_dir.mkdir(exist_ok=True)
    
    if not ICON_FILE.exists():
        print("  创建默认图标...")
        # 这里可以使用 PIL 创建一个简单的图标
        # 或者提示用户手动添加
        print("  请手动添加 icon.ico 到 resources 目录")

def generate_spec_file():
    """生成 PyInstaller spec 文件"""
    print_step(2, "生成 PyInstaller 配置")
    
    icon_path = str(ICON_FILE) if ICON_FILE.exists() else ''
    spec_content = SPEC_TEMPLATE.format(
        version=APP_VERSION,
        app_name=APP_NAME,
        icon=icon_path
    )
    
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"
    spec_file.write_text(spec_content, encoding='utf-8')
    print(f"✓ 已生成: {spec_file}")
    
    return spec_file

def generate_inno_setup_script():
    """生成 Inno Setup 脚本"""
    print_step(3, "生成安装程序脚本")
    
    script_content = INNO_SETUP_TEMPLATE.format(
        app_name=APP_NAME,
        version=APP_VERSION,
        author=AUTHOR
    )
    
    script_file = ROOT_DIR / f"{APP_NAME}_Setup.iss"
    script_file.write_text(script_content, encoding='utf-8-sig')  # 使用 BOM
    print(f"✓ 已生成: {script_file}")
    
    return script_file

def create_readme_files():
    """创建安装说明文件"""
    print_step(4, "创建安装说明文件")
    
    # 创建 LICENSE.txt
    license_file = ROOT_DIR / "LICENSE.txt"
    if not license_file.exists():
        license_file.write_text("""MIT License

Copyright (c) 2025 TextPin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""", encoding='utf-8')
        print(f"✓ 已创建: {license_file}")
    
    # 创建安装前说明
    readme_install = ROOT_DIR / "README_INSTALL.txt"
    readme_install.write_text("""欢迎安装 TextPin！

TextPin 是一款轻量、高效、美观的桌面便签工具。

主要特性：
- 剪贴板自动监听，一键创建便签
- 完全自定义的文本处理规则
- 全局快捷键支持
- 历史记录管理
- 灵活的窗口置顶和拖拽

安装说明：
1. 选择安装位置（程序文件目录）
2. 选择数据存储位置（配置和数据库）
3. 完成安装

您可以将数据存储在任何位置，方便备份和同步。

""", encoding='utf-8')
    print(f"✓ 已创建: {readme_install}")

def build_executable():
    """使用 PyInstaller 打包"""
    print_step(5, "执行 PyInstaller 打包")
    
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"
    
    if not spec_file.exists():
        print("✗ spec 文件不存在")
        return False
    
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    
    if result.returncode == 0:
        print("✓ PyInstaller 打包成功")
        return True
    else:
        print("✗ PyInstaller 打包失败")
        return False

def build_installer():
    """使用 Inno Setup 创建安装程序"""
    print_step(6, "创建安装程序")
    
    # 检查 Inno Setup
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    
    iscc_exe = None
    for path in inno_paths:
        if Path(path).exists():
            iscc_exe = path
            break
    
    if not iscc_exe:
        print("⚠ Inno Setup 未安装")
        print("  下载地址: https://jrsoftware.org/isdl.php")
        print("  请安装后手动编译 .iss 文件")
        return False
    
    script_file = ROOT_DIR / f"{APP_NAME}_Setup.iss"
    cmd = [iscc_exe, str(script_file)]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    
    if result.returncode == 0:
        print("✓ 安装程序创建成功")
        return True
    else:
        print("✗ 安装程序创建失败")
        return False

def main():
    """主函数"""
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   TextPin 自动化打包工具                                  ║
║   版本: {APP_VERSION}                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # 1. 检查环境
    if not check_requirements():
        sys.exit(1)
    
    # 2. 创建图标
    create_icon()
    
    # 3. 生成配置文件
    generate_spec_file()
    generate_inno_setup_script()
    
    # 4. 创建说明文件
    create_readme_files()
    
    # 5. PyInstaller 打包
    if not build_executable():
        print("\n打包失败！")
        sys.exit(1)
    
    # 6. 创建安装程序
    build_installer()
    
    # 7. 完成
    print_step("完成", "打包流程结束")
    
    print(f"""
打包结果：
- 可执行文件: {DIST_DIR / APP_NAME / f'{APP_NAME}.exe'}
- 安装程序: {ROOT_DIR / 'installer' / f'{APP_NAME}_Setup_v{APP_VERSION}.exe'}

使用说明：
1. 直接运行: 解压 dist/{APP_NAME} 目录即可使用
2. 安装程序: 运行 .exe 安装程序，引导用户安装

下一步：
- 修改 version_info.txt 中的版本信息
- 替换 resources/icon.ico 为自定义图标
- 更新 LICENSE.txt 和 README_INSTALL.txt
- 运行此脚本重新打包
""")

if __name__ == '__main__':
    main()
