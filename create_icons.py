#!/usr/bin/env python3
"""
创建应用图标的辅助脚本
使用PIL创建简单的图标文件
"""

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow未安装，无法创建图标文件")
    print("请运行: pip install Pillow")

def create_icon(size, filename):
    """创建指定大小的图标"""
    if not PIL_AVAILABLE:
        return False
    
    # 创建图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的图片图标
    # 外框
    margin = size // 8
    draw.rectangle([margin, margin, size-margin, size-margin], 
                   fill=(52, 152, 219, 255), outline=(41, 128, 185, 255), width=2)
    
    # 内部图片符号
    inner_margin = size // 4
    # 山峰
    points = [
        (inner_margin, size-inner_margin),
        (size//2, inner_margin),
        (size-inner_margin, size-inner_margin)
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # 太阳
    sun_size = size // 8
    sun_x = size - inner_margin - sun_size
    sun_y = inner_margin
    draw.ellipse([sun_x, sun_y, sun_x + sun_size, sun_y + sun_size], 
                 fill=(255, 255, 0, 255))
    
    # 保存图标
    try:
        if filename.endswith('.ico'):
            img.save(filename, format='ICO', sizes=[(size, size)])
        elif filename.endswith('.icns'):
            img.save(filename, format='ICNS')
        else:
            img.save(filename)
        print(f"✅ 创建图标: {filename} ({size}x{size})")
        return True
    except Exception as e:
        print(f"❌ 创建图标失败 {filename}: {e}")
        return False

def main():
    """主函数"""
    if not PIL_AVAILABLE:
        return
    
    print("创建应用图标...")
    
    # 创建Windows图标
    create_icon(256, 'icon.ico')
    
    # 创建macOS图标
    create_icon(512, 'icon.icns')
    
    print("图标创建完成！")

if __name__ == "__main__":
    main()
