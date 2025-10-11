"""
快速创建 TextPin 图标
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_icon():
    """创建简单的 TextPin 图标"""
    
    # 确保 resources 目录存在
    resources_dir = Path(__file__).parent / 'resources'
    resources_dir.mkdir(exist_ok=True)
    
    # 图标尺寸
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        # 创建透明背景
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制渐变圆形背景
        padding = max(2, size // 20)
        
        # 主圆
        draw.ellipse(
            [padding, padding, size-padding, size-padding],
            fill='#2196F3',  # 蓝色
            outline='#1976D2',
            width=max(1, size // 64)
        )
        
        # 添加文字 "T"
        font_size = int(size * 0.55)
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", font_size)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
        
        # 绘制文字
        text = "T"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - bbox[1]
        
        # 文字阴影
        shadow_offset = max(1, size // 64)
        draw.text(
            (text_x + shadow_offset, text_y + shadow_offset),
            text,
            fill=(0, 0, 0, 100),
            font=font
        )
        
        # 文字主体
        draw.text(
            (text_x, text_y),
            text,
            fill='white',
            font=font
        )
        
        images.append(img)
    
    # 保存为 ICO
    icon_path = resources_dir / 'icon.ico'
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(s, s) for s in sizes]
    )
    
    print(f"✓ 图标已创建: {icon_path}")
    print(f"  包含尺寸: {', '.join(f'{s}x{s}' for s in sizes)}")
    
    # 同时保存为 PNG 以供预览
    png_path = resources_dir / 'icon.png'
    images[0].save(png_path, 'PNG')
    print(f"✓ 预览图已创建: {png_path}")
    
    return icon_path

if __name__ == '__main__':
    try:
        create_icon()
        print("\n成功！现在可以运行 build_installer.py 进行打包。")
    except Exception as e:
        print(f"✗ 创建图标失败: {e}")
        print("\n请确保已安装 Pillow:")
        print("  pip install Pillow")
