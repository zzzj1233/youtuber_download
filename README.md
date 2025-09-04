# 图片浏览器

一个基于PyQt6的现代化图片浏览工具，支持分页显示、懒加载和智能缓存。

## 功能特性

- 🖼️ **分页浏览**：每页显示9张图片，支持翻页和跳转
- ⚡ **懒加载**：图片按需加载，提高启动速度
- 💾 **智能缓存**：自动管理内存缓存，避免重复加载
- 🎨 **现代UI**：美观的界面设计，支持悬停效果
- 📁 **多格式支持**：支持JPG、PNG、GIF、BMP、WebP等格式

## 项目结构

```
image_viewer/
├── __init__.py              # 包初始化文件
├── main.py                  # 主入口文件
├── main_window.py           # 主窗口类
├── ui/                      # UI模块
│   ├── __init__.py
│   └── components.py        # UI组件
├── utils/                   # 工具模块
│   ├── __init__.py
│   └── image_loader.py      # 图片加载和缓存管理
└── resources/               # 资源文件（预留）
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1：使用启动脚本
```bash
python run_image_viewer.py
```

### 方法2：指定图片文件夹
```bash
python run_image_viewer.py /path/to/your/images
```

### 方法3：直接运行模块
```bash
python -m image_viewer.main
```

## 配置

默认图片文件夹路径：`/Users/jiangjie/Downloads/img`

可以通过以下方式修改：
1. 命令行参数：`python run_image_viewer.py /your/image/path`
2. 修改 `main.py` 中的 `image_folder` 变量

## 技术特点

- **模块化设计**：清晰的代码结构，易于维护和扩展
- **性能优化**：懒加载和智能缓存机制
- **用户体验**：现代化的UI设计和流畅的交互
- **错误处理**：优雅处理图片加载失败的情况

## 开发说明

### 添加新功能
1. UI组件：在 `ui/components.py` 中添加
2. 工具函数：在 `utils/` 目录下添加
3. 主逻辑：在 `main_window.py` 中修改

### 自定义样式
所有样式都在对应的组件文件中定义，使用Qt样式表语法。

## 许可证

MIT License


