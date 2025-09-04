#!/bin/bash

echo "开始构建macOS DMG..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python"
    exit 1
fi

# 安装依赖
echo "安装依赖包..."
pip3 install -r requirements.txt

# 清理之前的构建
echo "清理之前的构建文件..."
rm -rf dist build

# 使用PyInstaller构建
echo "使用PyInstaller构建APP..."
pyinstaller image_viewer.spec

# 检查构建是否成功
if [ -d "dist/Image Viewer.app" ]; then
    echo ""
    echo "✅ APP构建成功！"
    echo "APP位置: dist/Image Viewer.app"
    
    # 创建DMG
    echo "创建DMG文件..."
    
    # 创建临时目录
    DMG_TEMP="temp_dmg"
    DMG_NAME="Image_Viewer"
    APP_NAME="Image Viewer"
    
    # 清理之前的DMG
    rm -f "${DMG_NAME}.dmg"
    
    # 创建临时目录并复制APP
    mkdir -p "${DMG_TEMP}"
    cp -R "dist/${APP_NAME}.app" "${DMG_TEMP}/"
    
    # 创建Applications的符号链接
    ln -s /Applications "${DMG_TEMP}/Applications"
    
    # 创建DMG
    hdiutil create -srcfolder "${DMG_TEMP}" -volname "${APP_NAME}" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW -size 200m "${DMG_NAME}_temp.dmg"
    
    # 挂载DMG
    device=$(hdiutil attach -readwrite -noverify -noautoopen "${DMG_NAME}_temp.dmg" | egrep '^/dev/' | sed 1q | awk '{print $1}')
    
    # 设置DMG属性
    echo "设置DMG属性..."
    sleep 2
    
    # 卸载DMG
    hdiutil detach "${device}"
    
    # 转换为只读DMG
    hdiutil convert "${DMG_NAME}_temp.dmg" -format UDZO -imagekey zlib-level=9 -o "${DMG_NAME}.dmg"
    
    # 清理临时文件
    rm -rf "${DMG_TEMP}"
    rm -f "${DMG_NAME}_temp.dmg"
    
    echo ""
    echo "✅ DMG构建成功！"
    echo "DMG文件位置: ${DMG_NAME}.dmg"
    echo ""
    echo "文件大小:"
    ls -lh "${DMG_NAME}.dmg"
    
else
    echo ""
    echo "❌ APP构建失败！"
    echo "请检查错误信息"
    exit 1
fi

echo ""
echo "构建完成！"
