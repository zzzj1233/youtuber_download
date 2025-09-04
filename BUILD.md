# 图片浏览器构建说明

## 环境要求

### 通用要求
- Python 3.8 或更高版本
- pip 包管理器

### Windows 要求
- Windows 10 或更高版本
- Visual Studio Build Tools (可选，用于某些依赖)

### macOS 要求
- macOS 10.14 或更高版本
- Xcode Command Line Tools

## 快速构建

### 方法1: 使用Python脚本（推荐）
```bash
python build.py
```

### 方法2: 使用平台特定脚本

#### Windows
```cmd
build_windows.bat
```

#### macOS
```bash
./build_macos.sh
```

## 手动构建

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 清理构建文件
```bash
# Windows
rmdir /s /q dist build

# macOS/Linux
rm -rf dist build
```

### 3. 使用PyInstaller构建
```bash
pyinstaller image_viewer.spec
```

### 4. 创建DMG (仅macOS)
```bash
# 创建临时目录
mkdir temp_dmg
cp -R "dist/Image Viewer.app" temp_dmg/

# 创建Applications链接
ln -s /Applications temp_dmg/Applications

# 创建DMG
hdiutil create -srcfolder temp_dmg -volname "Image Viewer" -fs HFS+ -format UDZO -o Image_Viewer.dmg

# 清理
rm -rf temp_dmg
```

## 构建输出

### Windows
- 输出文件: `dist/Image Viewer.exe`
- 文件大小: 约 50-100 MB

### macOS
- APP文件: `dist/Image Viewer.app`
- DMG文件: `Image_Viewer.dmg`
- 文件大小: 约 50-100 MB

## 常见问题

### 1. PyInstaller安装失败
```bash
# 升级pip
pip install --upgrade pip

# 安装PyInstaller
pip install pyinstaller
```

### 2. 缺少依赖模块
检查 `image_viewer.spec` 文件中的 `hiddenimports` 列表，确保包含所有必要的模块。

### 3. 构建文件过大
- 使用 `--exclude-module` 排除不需要的模块
- 考虑使用 `--onefile` 模式（但启动较慢）

### 4. macOS代码签名问题
如果遇到代码签名问题，可以临时禁用：
```bash
export CODESIGN_IDENTITY=""
```

## 自定义配置

### 修改应用名称
编辑 `image_viewer.spec` 文件中的 `name` 参数：
```python
name='Your App Name'
```

### 添加应用图标
1. 准备图标文件：
   - Windows: `icon.ico`
   - macOS: `icon.icns`

2. 取消注释 `image_viewer.spec` 中的图标配置：
```python
datas += [('icon.ico', '.')]  # Windows
datas += [('icon.icns', '.')]  # macOS
```

### 添加版本信息
在 `image_viewer.spec` 的 `exe` 部分添加：
```python
version='version_info.txt'
```

## 分发说明

### Windows
- 直接分发 `Image Viewer.exe` 文件
- 用户双击即可运行

### macOS
- 分发 `Image_Viewer.dmg` 文件
- 用户双击DMG，拖拽APP到Applications文件夹

## 性能优化

### 减小文件大小
1. 使用虚拟环境，只安装必要的包
2. 排除不需要的模块
3. 使用 `--strip` 选项

### 提高启动速度
1. 使用 `--onedir` 模式而不是 `--onefile`
2. 预编译Python文件
3. 优化导入语句

## 故障排除

### 构建失败
1. 检查Python版本
2. 确认所有依赖已安装
3. 查看错误日志
4. 尝试清理后重新构建

### 运行时错误
1. 检查是否缺少系统依赖
2. 确认所有资源文件已包含
3. 测试在不同系统上的兼容性

## 联系支持

如果遇到问题，请检查：
1. Python版本是否符合要求
2. 所有依赖是否正确安装
3. 构建环境是否完整
4. 错误日志中的具体信息
